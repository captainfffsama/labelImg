'''
@Author: lijun
@Date: 2020-05-15 16:48:56
@LastEditors: lijun
@LastEditTime: 2020-05-27 20:16:36
@Description: hang zhou test ,analyse num error data,copy error image to train
'''
from util.read_file import Readcsv
from util.deal_file import Dealfile
from util import comm_function
readcsv = Readcsv()
dealfile = Dealfile()
def copy_img_by_csv():
    csv_path = r'D:\cbv7700\bin\result_all.csv'
    target_path = r'Y:\data\num\unsb'
    
    csv_datas = readcsv.read_csv(csv_path)
    # print(csv_datas)
    for row_data in csv_datas:
        if "电流数码表" in row_data[2]:
            print(row_data[7])
            dealfile.copy_file(row_data[7],target_path)
def copy_img_from_files():
    base_path = r'C:\Users\lj893\Desktop\cbsMode'
    target_path = r'C:\Users\lj893\Desktop\cbsMode\target'
    comm_function.mkdir(target_path)
    img_paths = comm_function.traverse_files(base_path)
    for img_path in img_paths:
        print(img_path)
        dealfile.copy_file(img_path,target_path)
if __name__ == "__main__":
    # copy_img_from_files()
    a = [1,2,3,4]
    b = list(map(lambda x: x*x,a))
    print(b)