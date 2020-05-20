'''
@Author: lijun
@Date: 2020-05-18 11:23:27
@LastEditors: lijun
@LastEditTime: 2020-05-18 11:49:14
@Description: this file has some function
'''
import numpy as np
from cv2 import cv2 as cv
import hashlib
import os
def md5sum(filename:'str'):
    """[summary]

    Args:
        filename ([str]): [description]

    Returns:
        [type]: [return md5]
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