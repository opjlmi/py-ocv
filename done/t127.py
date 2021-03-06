import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe

#Frame
def dirINIT(height,width,zoom,z_level_down,z_level_up,speed):
	q_tmp = "G17\nM3 S1000\n$H\n"
    	q_tmp += "G0 X0 Y0\n"
    	q_tmp += "G0 Z"+ z_level_down + "\n"
    	q_tmp += "G1 F"+ speed +" X" + str(-height/zoom) +" Y0" + "\n"
    	q_tmp += "G1 F"+ speed +" Y" + str(-width/zoom) + "\n"
    	q_tmp += "G1 F"+ speed +" X0 " + "\n"
    	q_tmp += "G1 F"+ speed +"0 Y0" + "\n"
    	q_tmp += "G0 Z"+ z_level_up + "\n"
    	return q_tmp

#direction top to bottom
def direction0(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
	color = GetLevel(level)
    	height, width = gimg.shape
    	q_tmp=''

    	for x in range(0,height,intr):
        	if x%2==0:
            		for y in range(width):
                		if gimg[x][y]<=color: # black
                    			if (gimg[x][y-1]>color or y==0): # white || y=0
                        			q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                        			q_tmp += "G0 Z"+ z_level_down + "\n"                                            #pen down
                    			elif y==(width-1): # if y has gone end.
                        			q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"        #draw
                        			q_tmp += "G0 Z"+ z_level_up + "\n"                                              #pen up
                		elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                    			q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\n"                #draw
                    			q_tmp += "G0 Z"+ z_level_up + "\n"                                                  #pen up
        	else:
            		for y in range((width-1),-1,-1):
                		if gimg[x][y]<=color: # black
                    			if (gimg[x][y-1]>color or y==0): # white || y=0
                        			q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"                #draw
                        			q_tmp += "G0 Z"+ z_level_up + "\n"                                              #pen up
                    			elif y==(width-1):
                        			q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\n"
                        			q_tmp += "G0 Z"+ z_level_down + "\n"                                                    #pen down
                		elif (gimg[x][y-1]<=color and y>0): # black && y > 0
                    			q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-(y-1)/zoom) + "\n"
                    			q_tmp += "G0 Z"+ z_level_down + "\n"                                                #pen down
    	q.send(q_tmp)
    	q.close

def direction1(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    	color = GetLevel(level)
    	height, width = gimg.shape
    	q_tmp=''

    	for y in range(0,width,intr):
        	if y%2==0:
            		for x in range(height):
                		if gimg[x][y]<=color: # black
                    			if (gimg[x-1][y]>color or x==0): # white || y=0
                        			q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
                        			q_tmp += "G0 Z"+ z_level_down + "\n"                                            #pen down
                    			elif x==(height-1): # if y has gone end.
                        			q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"        #draw
                        			q_tmp += "G0 Z"+ z_level_up + "\n"                                              #pen up
                		elif (gimg[x-1][y]<=color and x>0): # black && y > 0
                    			q_tmp += "G1 F"+ speed +" X" + str(-(x-1)/zoom) + " Y" + str(-y/zoom) + "\n"                #draw
                    			q_tmp += "G0 Z"+ z_level_up + "\n"                                                  #pen up
        	else:
            		for x in range((height-1),-1,-1):
                		if gimg[x][y]<=color: # black
                    			if (gimg[x-1][y]>color or x==0): # white || y=0
                        			q_tmp += "G1 F"+ speed +" X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"        #draw
                        			q_tmp += "G0 Z"+ z_level_up + "\n"                                              #pen up
                    			elif x==(height-1): # if y has gone end.
                       				q_tmp += "G0 X" + str(-x/zoom) + " Y" + str(-y/zoom) + "\n"
 	                       			q_tmp += "G0 Z"+ z_level_down + "\n"                                            #pen down
                		elif (gimg[x-1][y]<=color and x>0): # black && y > 0
                    			q_tmp += "G0 X" + str(-(x-1)/zoom) + " Y" + str(-y/zoom) + "\n"
                    			q_tmp += "G0 Z"+ z_level_down + "\n"                                                        #pen down
    	q.send(q_tmp)
    	q.close

def direction2(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    	color = GetLevel(level)
    	height, width = gimg.shape
    	q_tmp=''
    	the_range=[]

    	for x in range(0,height-1,intr):
        	the_range.append([x,0])
    	for y in range(0,width-1,intr):
        	the_range.append([0,y])
    	for t_range in the_range:
        	tx=t_range[0]
        	ty=t_range[1]
        	q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
        	while (tx>=0 and tx<height and ty>=0 and ty<width):
            		if gimg[tx][ty]<=color: # black
				if (gimg[tx-intr][ty-intr]>color or tx==0 or ty==0):
					q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
					q_tmp += "G0 Z"+ z_level_down + "\n"
                		elif (tx==((height//3)*3) or ty==((width//3)*3)) :
                        		q_tmp += "G1 F"+ speed +" X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
                        		q_tmp += "G0 Z"+ z_level_up + "\n"
            		elif (gimg[tx-intr][ty-intr]<=color and tx>0 and ty>0):
                    		q_tmp += "G1 F"+ speed +" X" + str(-(tx-intr)/zoom) + " Y" + str(-(ty-intr)/zoom) + "\n"
                    		q_tmp += "G0 Z"+ z_level_up + "\n"
            		tx+=intr
           		ty+=intr

    	q.send(q_tmp)
    	q.close

def direction3(q,gimg,level,intr,zoom,z_level_down,z_level_up,speed):
    	color = GetLevel(level)
    	height, width = gimg.shape
    	q_tmp=''
    	the_range=[]

    	for x in range((height//3)*3,0,-intr):
        	the_range.append([x,0])
    	for y in range(0,width,intr):
        	the_range.append([(height//3)*3,y])
    	for t_range in the_range:
        	tx=t_range[0]
        	ty=t_range[1]
        	q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
        	while (tx>=0 and ty>=0 and tx<height and ty<width):
            		if gimg[tx][ty]<=color: # black
                		if (tx+intr<=height and ty-intr>=0) :
                    			if (gimg[tx+intr][ty-intr]>color):
                        			q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
                        			q_tmp += "G0 Z"+ z_level_down + "\n"
						if ty==(width//3)*3:
							q_tmp += "G0 Z"+ z_level_up + "\n"
                    			elif (tx==0 or ty==(width//3)*3 or tx==(height//3)*3 or ty==0):
                        			q_tmp += "G1 F"+ speed +" X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
                        			q_tmp += "G0 Z"+ z_level_up + "\n"
				elif (tx==(height//3)*3 or ty==0):
                                                q_tmp += "G0 X" + str(-tx/zoom) + " Y" + str(-ty/zoom) + "\n"
                                                q_tmp += "G0 Z"+ z_level_down + "\n"
            		elif (tx+intr<height and ty-intr>0):
                		if (gimg[tx+intr][ty-intr]<=color and tx<height and ty>0):
                    			q_tmp += "G1 F"+ speed +" X" + str(-(tx+intr)/zoom) + " Y" + str(-(ty-intr)/zoom) + "\n"
                    			q_tmp += "G0 Z"+ z_level_up + "\n"
			
            		tx-=intr
            		ty+=intr
    	q.send(q_tmp)
    	q.close

def GetLevel(level):
	if level == 1 :	
		return 223
	elif level == 2 :
		return 191
	elif level == 3 :
		return 159
	elif level == 4 :
		return 127
	elif level == 5 :
		return 95
	elif level == 6 :
		return 63
	elif level == 7 :
		return 31


if __name__ == '__main__':
#set up
	zoom=3.0
	intr0=3
	intr1=1
	z_level_down="5"
	z_level_up="0"
	speed="5000"
	g = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
	gimg=cv2.flip(g,0)
	height, width = gimg.shape
	
	gimg_tmp=0
	w_tmp=0
	for x in range(0,height,1):
		for y in range(0,width,1):
			if (gimg[x][y]<=223):
				gimg_tmp += gimg[x][y]
			else:
				w_tmp+=1

	gimg_av=gimg_tmp//((height*width)-w_tmp)
	print gimg_av
	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	q3x,q3 = Pipe()
	
	if gimg_av >=100  :
		color_index=[1,3,5]
	else :
		color_index=[3,5,6]

	p0 = Process(target=direction0,args=(q0,gimg,color_index[0],intr0,zoom,z_level_down,z_level_up,speed,))
	p1 = Process(target=direction1,args=(q1,gimg,color_index[1],intr0,zoom,z_level_down,z_level_up,speed,))
	p2 = Process(target=direction2,args=(q2,gimg,color_index[2],intr0,zoom,z_level_down,z_level_up,speed,))
#	p3 = Process(target=direction3,args=(q3,gimg,6,intr0,zoom,z_level_down,z_level_up,speed,))

	init_r = dirINIT(height,width,zoom,z_level_down,z_level_up,speed,)	
	p0.start()
	p1.start()
	p2.start()
#	p3.start()

	q0_r = q0x.recv()
	q1_r = q1x.recv()
	q2_r = q2x.recv()
#	q3_r = q3x.recv()
	print("End of Get the Pipe....")

	p0.join()
	p1.join()
	p2.join()
#	p3.join()

	print("Enter the G-code.....")
	filename='t127'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
	f.write(init_r)
	f.write(q0_r)
	f.write(q1_r)
	f.write(q2_r)
#	f.write(q3_r)
	f.write("G0 Z0\rG0 X0 Y0\r")
	f.close()

#cv2.imshow('pic-gray',gimg)
#cv2.waitKey(0)
#0-31 black
#32-63
#64-95
#96-127
#128-159
#160-191
#192-223
#224-255 white
