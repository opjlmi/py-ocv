import cv2
import numpy as np,sys
import os
import time
from multiprocessing import Process, Pipe

#Frame
def dirINIT(height,width,zoom,z_level_down,z_level_up,speed):
	q_tmp = "G17\nM3 S1000\n$H\n"
    	q_tmp += "G0 Z0\n"
    	q_tmp += "G0 X0 Y0\n"
    	q_tmp += "G0 Z"+ z_level_down + "\n"
    	q_tmp += "G1 F"+ speed +" X" + str(-height/zoom) +" Y0" + "\n"
    	q_tmp += "G1 F"+ speed +" Y" + str(-width/zoom) + "\n"
    	q_tmp += "G1 F"+ speed +" X0 " + "\n"
    	q_tmp += "G1 F"+ speed +" Y0" + "\n"
    	q_tmp += "G0 Z"+ z_level_up + "\n"
    	return q_tmp

#produce G-code
def dirGCODE(q,list_total,line,zoom,z_level_down,z_level_up,speed):
	q_tmp=''
	for line_x in range(0,line):
               	# len() = list size
               	for line_y in range (0, len(list_total[line_x])):
                       	if (line_y%2==0):
                               	q_tmp += "G0 X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
                               	q_tmp += "G0 Z"+ z_level_down + "\n"
                       	else:
                               	q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
                               	q_tmp += "G0 Z"+ z_level_up + "\n"

#       print list_total[line_x][line_y]
	q.send(q_tmp)
	q.close()
#	return q_tmp

#direction top to bottom
def direction0(gimg,level,intr):
	color = GetLevel(level)
    	height, width = gimg.shape
    	q_tmp=''
	line=0
	list_total=[]
	
	for x in range(0,height,intr):
		list_total.append([])
		for y in range(0,width):
			if (gimg[x][y]<=color):
				if (gimg[x][y-1]>color or y==0):
					list_total[line].append([x,y])
				elif (y==(width//zoom)*3):
					list_total[line].append([x,y])
			elif (gimg[x][y-1]<=color and y>0):
				list_total[line].append([x,y])
		if (x%2!=0):
			list_total[line].reverse()
		line+=1

#	print list_total
#	print line

#	for line_x in range(0,line):
		# len() = list size
#		for line_y in range (0, len(list_total[line_x])):
#			if (line_y%2==0):
#				q_tmp += "G0 X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
#				q_tmp += "G0 Z"+ z_level_down + "\n"
#			else:
#				q_tmp += "G1 F" + speed + " X" + str(-list_total[line_x][line_y][0]/zoom) + " Y" + str(-list_total[line_x][line_y][1]/zoom) + "\n"
#	                        q_tmp += "G0 Z"+ z_level_up + "\n"

#			print list_total[line_x][line_y]
#	return 	list_total
#	q.send(list_total)
#	q.close
	return list_total,line

def direction1(gimg,level,intr):
	color = GetLevel(level)
        height, width = gimg.shape
        q_tmp=''
        line=0
        list_total=[]

        for y in range(0,width,intr):
                list_total.append([])
                for x in range(0,height):
                        if (gimg[x][y]<=color):
                                if (gimg[x-1][y]>color or x==0):
                                        list_total[line].append([x,y])
                                elif (y==(width//zoom)*3):
                                        list_total[line].append([x,y])
                        elif (gimg[x-1][y]<=color and x>0):
                                list_total[line].append([x,y])
                if (y%2!=0):
                        list_total[line].reverse()
                line+=1
	return list_total,line

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
	zoom=3
	intr0=3
	intr1=1
	z_level_down="4"
	z_level_up="0"
	speed="5000"
	g = cv2.imread('picture.jpg',cv2.IMREAD_GRAYSCALE)
	gimg=cv2.flip(g,0)
	height, width = gimg.shape
	
	q0x,q0 = Pipe()
	q1x,q1 = Pipe()
	q2x,q2 = Pipe()
	q3x,q3 = Pipe()
	
#	list_p0 = direction0(gimg,1,intr0,)
	list_p1 = direction1(gimg,1,intr0,)
#	print list_p0[0]
#	print list_p0[1]
	p0 = Process(target=dirGCODE,args=(q0,list_p1[0],list_p1[1],zoom,z_level_down,z_level_up,speed,))
#	p0 = dirGCODE(list_p0[0],list_p0[1],zoom,z_level_down,z_level_up,speed,)
	init_r = dirINIT(height,width,zoom,z_level_down,z_level_up,speed,)	
	p0.start()
	q0_r = q0x.recv()
#	print q0_r
	print("End of Get the Pipe....")

	p0.join()

	print("Enter the G-code.....")
	filename='revise'
	file_id = str(filename) + '.nc'
	f = open(file_id,'w')
	f.write(init_r)
	f.write(q0_r)
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
