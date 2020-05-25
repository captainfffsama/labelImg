'''
@Author: lijun
@Date: 2020-05-20 15:48:47
@LastEditors: lijun
@LastEditTime: 2020-05-20 18:41:53
@Description: file content
'''
from cv2 import cv2 as cv
import glob
import os
class Interceptvideo(object):
    def __init__(self):
        pass
    def read_video(self,video_paths:'str'):
        paths = glob.glob(video_paths+'/*.mp4',recursive = True)
        if(paths):
            for path in paths:
                count = 0
                timeF = 20 #视频帧计数间隔
                video_data = cv.VideoCapture(path)
                if video_data.isOpened():
                    print('mp4 video open sucess.')
                    rval,frame = video_data.read()
                else:
                    rval = False
                    print('mp4 video open fail.')
                while rval:
                    rval,frame = video_data.read()
                    if(count%timeF==0):
                        num = int()
                
        else:
            print('no mp4 file')