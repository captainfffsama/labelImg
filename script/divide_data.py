'''
@Author: lijun
@Date: 2020-06-01 11:58:08
@LastEditors: lijun
@LastEditTime: 2020-06-02 10:11:12
@Description: file content
'''
import os
import shutil
import random
from concurrent import futures
from tqdm import tqdm
from collections import defaultdict
from statics_classnum import static_class_num
from util.deal_file import Dealfile
deal_file = Dealfile()
class divideDataTT(object):
    def __init__(self,data_map):
        global divide_data
        divide_data = {}
        for key,value in data_map.items():
            divide_data[os.path.basename(key)] = value
            if os.path.exists(key):
                shutil.rmtree(key)
                os.mkdir(key)
            else:
                os.mkdir(key)


    def divide_data_tt(self,ori_path,target_path):
        class_num,path_class_name,all_paths = static_class_num(ori_path)
        train_class_num = {}
        test_class_num = {}
        val_class_num = {}
        divide_class = {}
        train_filter_data = defaultdict(int)
        test_filter_data = defaultdict(int)
        global divide_data
        for class_num_data in class_num:
            train_class_num[class_num_data[0]] = round(class_num_data[1]*divide_data['train'])
            test_class_num[class_num_data[0]] = round(class_num_data[1]*divide_data['test'])
            val_class_num[class_num_data[0]] = round(class_num_data[1]*divide_data['val'])
        print(train_class_num,'\n',test_class_num,'\n',val_class_num)
        random.shuffle(all_paths)
        # for class_num in divide_class_num:
        
        for path in all_paths:
            for class_name,classs_count in path_class_name[path].items():
                if(train_class_num[class_name]>train_filter_data[class_name]):
                    train_filter_data[class_name]+=classs_count
                    is_train = True
                    is_test = False
                    is_val = False
                elif(test_class_num[class_name]>test_filter_data[class_name]):
                    test_filter_data[class_name]+=classs_count
                    is_train = False
                    is_test = True
                    is_val = False
                else:
                    is_train = False
                    is_test = False
                    is_val = True
            jpg_path = path.replace('xml','jpg')
            if is_train:
                divide_class.setdefault('train',[]).append(path)
                divide_class.setdefault('train',[]).append(jpg_path)
            elif is_test:
                divide_class.setdefault('test',[]).append(path)
                divide_class.setdefault('test',[]).append(jpg_path)
            elif is_val:
                divide_class.setdefault('val',[]).append(path)
                divide_class.setdefault('val',[]).append(jpg_path)
        for key,value in divide_class.items():
            new_target_path = os.path.join(target_path,key)
            with futures.ThreadPoolExecutor(16) as pool:
                task_list = (pool.submit(deal_file.copy_file,file_path,new_target_path) for file_path in value)
                for i in tqdm(futures.as_completed(task_list),total=len(value)):
                    pass
if __name__ == "__main__":
    base_path = r'C:\Users\lj893\Desktop\test'
    target_path = r'C:\Users\lj893\Desktop\test'
    data_map = {
        os.path.join(target_path,'train'):0.7,
        os.path.join(target_path,'test'):0.2,
        os.path.join(target_path,'val'):0.1
    }
    dividedata = divideDataTT(data_map)
    dividedata.divide_data_tt(base_path,target_path)