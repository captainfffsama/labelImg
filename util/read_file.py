'''
@Author: lijun
@Date: 2020-05-15 12:00:15
@LastEditors: lijun
@LastEditTime: 2020-05-15 18:40:46
@Description: read csv data
'''
import csv
class Readcsv(object):
    """[summary]
    this is a class,read csv file and return csv data

    Args:
        object ([None]): [None]
    """
    def __init__(self):
        pass
    def open_csv(self,csv_path:'str',has_head:'bool'=True)->list:
        """[summary]

        Args:
            csv_path ([str]): [input csv file path]
            has_head ([bool], optional): [whether has head]. Defaults to True.
        Returns:
            list: [description]
        """

        csv_data = open(csv_path)
        if has_head:
            next(csv_data)
        readers = csv.reader(csv_data)
        return readers
    def parse_data(self,head_data:'str')->list:
        """[summary]
        Args:
            head_data ([csv header]): [this is csv head data]
        Returns:
            list: [this is csv list(data)]
        """
        csv_datas = []
        for row_data in head_data:
            # print(type(row_data))
            csv_datas.append(row_data)
        return csv_datas

    def read_csv(self,csv_path:'str')->list:
        """[add open_csv with parse_data]
        Args:
            csv_path ([str]): [this is csv file path]
        Returns:
            [list]: [this is csv data]
        """
        return self.parse_data(self.open_csv(csv_path))

# if __name__ == "__main__":
#     csv_path = r'D:\cbv7700\bin\result.csv'
#     readcsv = Readcsv()
#     # print(type(readcsv.open_csv(csv_path)))
#     # print(readcsv.parse_data(readcsv.open_csv(csv_path)))
#     # a = readcsv.open_csv(csv_path)
#     # b = readcsv.parse_data(a)
#     # print(b)
#     print(readcsv.read_csv(csv_path))
