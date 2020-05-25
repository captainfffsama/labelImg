'''
@Author: lijun
@Date: 2020-05-18 11:03:59
@LastEditors: lijun
@LastEditTime: 2020-05-30 20:07:34
@Description: this file tailor img
'''
from util import comm_function
import os
from cv2 import cv2 as cv
from util.read_file import Readxml
import glob
import random
class Tailor(object):
    """[summary]
    this class tailor img by file data
    Args:
        object ([type]): [description]
    """    
    def __init__(self):
        pass
    def tailor_img(self, xml_path:'str',target_path:'str',xml_data:'dict',label_name:'list',israndom = False):
        """[summary]

        Args:
            xml_path ([str]): [this is xml path]
            xml_data ([dict]): [thi is xml data]
        """        
        img_path = xml_path.replace('xml','jpg')
        img = comm_function.open_img(img_path)

        object_datas = xml_data['object']
        img_width = xml_data['imgsize'][0]
        img_height = xml_data['imgsize'][1]
        img_channel = xml_data['imgsize'][2]
        for object_data in object_datas:
            name = object_data['name']
            if name not in label_name:
                continue
            bndbox = object_data['bndbox']
            if israndom:
                bias_x = random.randint(-2,2)
                bias_y = random.randint(-2,2)
            else:
                bias_x = 0
                bias_y = 0
            top = bndbox[1] + bias_x
            bottom = bndbox[3] + bias_y
            left = bndbox[0] + bias_x
            right = bndbox[2] + bias_y

            # roi_img = img[bndbox[1]:bndbox[3],bndbox[0]:bndbox[2]]
            left,top,right,bottom = comm_function.board_judge(left,top,right,bottom,img_width,img_height)
            roi_img = img[top:bottom,left:right]
            md5 = comm_function.md5sum(roi_img)
            save_path = os.path.join(target_path,str(md5))
            save_path = str(save_path)+'_'+str(name)+'.png'
            print(save_path)
            if(cv.imwrite(save_path,roi_img)):
                print('save img sucess')

        print(img_path)

if __name__ == "__main__":
    base_path = r'C:\Users\lj893\Desktop\all'
    target_path = r'C:\Users\lj893\Desktop\all_roi'
    comm_function.mkdir(target_path)
    label_names = ['alllighton','alllightoff','alllightright','alllightleft']
    israndom = True
    xml_paths = glob.glob(base_path+'/**/*.xml',recursive = True)
    readxml = Readxml()
    tailor = Tailor()
    for xml_path in xml_paths:
        xml_data = readxml.read_xml(xml_path)
        tailor.tailor_img(xml_path,target_path,xml_data,label_names,israndom)

        