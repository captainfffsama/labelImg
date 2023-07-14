# -*- coding: utf-8 -*-
'''
@Author: captainfffsama
@Date: 2023-07-12 17:12:00
@LastEditors: captainfffsama tuanzhangsama@outlook.com
@LastEditTime: 2023-07-12 17:13:14
@FilePath: /labelImg/libs/proto/__init__.py
@Description:
'''
import grpc

def _version_gt(version_current:str,version_benchmark:str="1.37.0") -> bool:
    for i,j in zip(version_current.split("."),version_benchmark.split(".")):
        if int(i)>int(j):
            return True

    return False

if _version_gt(grpc.__version__,"1.37.0"):
    from .new import dldetection_pb2_grpc
    from .new import dldetection_pb2
else:
    from .v1370 import dldetection_pb2_grpc
    from .v1370 import dldetection_pb2

from . import utils

__all__=["dldetection_pb2_grpc","dldetection_pb2","utils"]