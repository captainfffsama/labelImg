'''
@Author: lijun
@Date: 2020-05-18 11:03:59
@LastEditors: lijun
@LastEditTime: 2020-05-18 13:34:30
@Description: this file tailor img
'''
import comm_function
import os
from cv2 import cv2 as cv
from read_file import Readxml
import glob
class Tailor(object):
    """[summary]
    this class tailor img by file data
    Args:
        object ([type]): [description]
    """    
    def __init__(self):
        pass
    def tailor_img(self, xml_path:'str',target_path:'str',xml_data:'dict',label_name:'list'):
        """[summary]

        Args:
            xml_path ([str]): [this is xml path]
            xml_data ([dict]): [thi is xml data]
        """        
        img_path = xml_path.replace('xml','jpg')
        img = comm_function.open_img(img_path)

        object_datas = xml_data['object']
        for object_data in object_datas:
            name = object_data['name']
            if name not in label_name:
                continue
            bndbox = object_data['bndbox']
            roi_img = img[bndbox[1]:bndbox[3],bndbox[0]:bndbox[2]]
            md5 = comm_function.md5sum(roi_img)
            save_path = os.path.join(target_path,str(md5))
            cv.imwrite(save_path+'_'+name+'.jpg',roi_img)
        print(img_path)

if __name__ == "__main__":
    base_path = r'Y:\data\num\unsb'
    target_path = r'Y:\data\num\unsb\roi'
    label_names = ['dlsmb']
    xml_paths = glob.glob(base_path+'/*.xml',recursive = True)
    readxml = Readxml()
    tailor = Tailor()
    for xml_path in xml_paths:
        xml_data = readxml.read_xml(xml_path)
        tailor.tailor_img(xml_path,target_path,xml_data,label_names)

        