# -*- coding: utf-8 -*-
'''
@Author: captainfffsama
@Date: 2023-04-10 19:09:31
@LastEditors: captainfffsama tuanzhangsama@outlook.com
@LastEditTime: 2023-07-13 11:59:11
@FilePath: /labelImg/libs/proto/utils.py
@Description:
'''

import os
import base64

import numpy as np
import cv2

from . import dldetection_pb2

def cv2imread(img_path,flag=cv2.IMREAD_COLOR|cv2.IMREAD_IGNORE_ORIENTATION):
    img=cv2.imdecode(np.fromfile(img_path,dtype=np.uint8),flag)
    return img

def get_img(img_info):
    if os.path.isfile(img_info):
        if not os.path.exists(img_info):
            return None
        else:
            return cv2imread(img_info,cv2.IMREAD_COLOR|cv2.IMREAD_IGNORE_ORIENTATION)  #ignore
    else:
        img_str = base64.b64decode(img_info)
        img_np = np.fromstring(img_str, np.uint8)
        return cv2.imdecode(img_np, cv2.IMREAD_COLOR|cv2.IMREAD_IGNORE_ORIENTATION)


def np2tensor_proto(np_ndarray: np.ndarray):
    shape = list(np_ndarray.shape)
    data = np_ndarray.flatten().tolist()
    tensor_pb = dldetection_pb2.Tensor()
    tensor_pb.shape.extend(shape)
    tensor_pb.data.extend(data)
    return tensor_pb


def tensor_proto2np(tensor_pb):
    np_matrix = np.array(tensor_pb.data,
                         dtype=np.float).reshape(tensor_pb.shape)
    return np_matrix