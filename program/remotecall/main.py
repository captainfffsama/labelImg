from remotecall import ServiceCall
import json


if __name__ == "__main__":
    call = ServiceCall('192.168.0.213')
    input = {}
    input['cruise_point_id'] = 770010815
    input['detect_files'] = '/root/project/cbv7700/test.jpg'
    ret, output = call.excute('robot_cruise_detect', input)
    print(output['det_res'])
    print(output['data'])