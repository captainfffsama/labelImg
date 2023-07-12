###
 # @Author: captainfffsama
 # @Date: 2023-07-12 17:26:37
 # @LastEditors: captainfffsama tuanzhangsama@outlook.com
 # @LastEditTime: 2023-07-12 17:26:38
 # @FilePath: /labelImg/libs/proto/generate_code.sh
 # @Description:
###
python -m grpc_tools.protoc -I./ --python_out=. --pyi_out=. --grpc_python_out=. ./dldetection.proto
