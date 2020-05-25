'''
@Author: lijun
@Date: 2020-05-18 11:23:27
@LastEditors: lijun
@LastEditTime: 2020-05-30 20:03:20
@Description: this file has some function
'''
import numpy as np
from cv2 import cv2 as cv
import hashlib
import os
from tqdm import tqdm
def md5sum(filename:'str'):
    """[summary]

    Args:
        filename ([str]): [description]

    Returns:
        [type]: [description]
    """    
    m = hashlib.md5()
    m.update(filename.tostring())
    return m.hexdigest()

def mkdir(target_path:'str'):
    """[summary]

    Args:
        target_path ([str]): [description]
    """    
    if not os.path.exists(target_path):
        os.mkdir(target_path)

def open_img(img_path:'str'):
    """[summary]

    Args:
        img_path ([str]): [this is img path]
    """    
    img_np = np.fromfile(img_path,np.uint8)
    img = cv.imdecode(img_np,cv.IMREAD_COLOR)
    return img

def traverse_files(base_path:'str',filter_class:'list',is_filter_eff:'bool'=True):
    """[summary]

    Args:
        base_path ([type]): [description]
        filter_class ([type]): [description]
        is_filter_eff ([type], optional): [description]. Defaults to True.

    Returns:
        [type]: [description]
    """
    paths = []
    for dirpath, dirnames, filenames in os.walk(base_path):
        for filename in filenames:
            if is_filter_eff:
                if(filename.split('.')[-1] in filter_class):
                    paths.append(os.path.join(dirpath,filename))
            else:
                paths.append(os.path.join(dirpath,filename))
    if paths:
        return paths
    else:
        print('files is None')

def board_judge(left,top,right,bottom,width,height):
    left = max(left,0)
    top = max(top,0)
    right = min(right,width)
    bottom = min(bottom,height)
    return left,top,right,bottom