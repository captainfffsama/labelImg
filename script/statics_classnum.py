'''
@Author: lijun
@Date: 2020-05-28 16:52:43
@LastEditors: lijun
@LastEditTime: 2020-05-29 14:57:02
@Description: file content
'''
from util import read_file
from util import comm_function
from collections import defaultdict,Counter
from tqdm import tqdm
import time
from concurrent import futures
read_xml = read_file.Readxml()
def analyse_num_by_xml(xml_path,filter_name,is_filter,work_num):
    """[summary]

    Args:
        xml_path ([str]): [this is xml path contains more one file]
    """    
    all_paths = comm_function.traverse_files(xml_path,filter_name,is_filter)
    all_names = []
    all_names_dict = defaultdict(int)
    couter = 0
    # for path in tqdm(all_paths):
    #     xml_datas = read_xml.read_xml(path)
    #     # print(xml_datas)
    #     xml_names = list(map(lambda xml_data: xml_data['name'],xml_datas['object']))
    #     # print(xml_names)
    #     for xml_name in xml_names:
    #         # all_names.append(xml_name)
    #         all_names_dict[xml_name]+=1
    #     # all_names.append(xml_names)#!全部存储，数据量较大
    # print(all_names_dict)
    with futures.ThreadPoolExecutor(work_num) as pool:
        task_list = (pool.submit(deal_xml,path,all_names_dict) for path in all_paths)
        for i in tqdm(futures.as_completed(task_list),total=len(all_paths)):
            pass
    all_names_dict = sorted(all_names_dict.items(),key=lambda item: item[1])
    for all_names in all_names_dict:
        print('{:20s}---{:>10s}'.format(repr(all_names[0]),repr(all_names[1])))
    # print(all_names_dict)
def deal_xml(path,all_names_dict):
    xml_datas = read_xml.read_xml(path)
    # print(xml_datas)
    xml_names = list(map(lambda xml_data: xml_data['name'],xml_datas['object']))
    # print(xml_names)
    for xml_name in xml_names:
        # all_names.append(xml_name)
        all_names_dict[xml_name]+=1
if __name__ == "__main__":
    time_begin = time.time()
    xml_path = r'Y:\data\all_device\all'
    filter_name = ['xml']
    is_filter = True
    work_num = 32
    analyse_num_by_xml(xml_path,filter_name,is_filter,work_num)
    time_end = time.time()
    print('程序运行时间:{} s'.format(time_end-time_begin))