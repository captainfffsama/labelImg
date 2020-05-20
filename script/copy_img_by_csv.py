'''
@Author: lijun
@Date: 2020-05-15 16:48:56
@LastEditors: lijun
@LastEditTime: 2020-05-20 16:57:05
@Description: hang zhou test ,analyse num error data,copy error image to train
'''
from util.read_file import Readcsv
from util.deal_file import Dealfile
if __name__ == "__main__":
    csv_path = r'D:\cbv7700\bin\result_all.csv'
    target_path = r'Y:\data\num\unsb'
    readcsv = Readcsv()
    dealfile = Dealfile()
    csv_datas = readcsv.read_csv(csv_path)
    # print(csv_datas)
    for row_data in csv_datas:
        if "电流数码表" in row_data[2]:
            print(row_data[7])
            # dealfile.copy_file(row_data[7],target_path)