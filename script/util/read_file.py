'''
@Author: lijun
@Date: 2020-05-15 12:00:15
@LastEditors: lijun
@LastEditTime: 2020-05-18 13:29:54
@Description: read csv data
'''
import csv
import xml.etree.ElementTree as ET

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

class Readxml(object):
    """[summary]
    this is a class,read and read xml file 
    Args:
        object ([type]): [description]
    """
    def __init__(self):       
        pass
    def read_xml(self, xml_path:'str')->dict:
        """[summary]

        Args:
            csv_path ([str]): [this is csv path]

        Returns:
            [dict]: [xml data by dict]
        """             
        tree=ET.parse(xml_path)
        root=tree.getroot()
        xml_data = {}
        """
        xml_data:{'object':[{'name':'','bndbox':[xmin,ymin,xmax,ymax]}],'size':'img_w,img_h,img_channel'}
        """
        all_object_data = []
        for img_size in root.findall('size'):
            img_width = int(img_size.findtext('width'))
            img_height = int(img_size.findtext('height'))
            img_channel = int(img_size.findtext('depth'))
        for obj in root.findall('object'):
            object_data = {}
            name = obj.findtext('name')
            for bndbox in obj.findall('bndbox'):
                xmin = int(bndbox.findtext('xmin'))
                ymin = int(bndbox.findtext('ymin'))
                xmax = int(bndbox.findtext('xmax'))
                ymax = int(bndbox.findtext('ymax'))
                w = xmax-xmin
                h = ymax-ymin
            object_data['name'] = name
            object_data['bndbox'] = [xmin,ymin,xmax,ymax]
            object_data['size'] = [w,h]
            all_object_data.append(object_data)
        xml_data['object'] = all_object_data
        xml_data['imgsize'] =[img_width,img_height,img_channel]
        return xml_data
if __name__ == "__main__":
    pass
    # csv_path = r'D:\cbv7700\bin\result.csv'
    # readcsv = Readcsv()
    # print(type(readcsv.open_csv(csv_path)))
    # print(readcsv.parse_data(readcsv.open_csv(csv_path)))
    # a = readcsv.open_csv(csv_path)
    # b = readcsv.parse_data(a)
    # print(b)
    # print(readcsv.read_csv(csv_path))
    
    # xml_path = r'Y:\data\all_device\train\00a1a9372d219f53eef4418819ab6709.xml'
    # dealxml = Dealxml()
    # a = dealxml.read_xml(xml_path)
    # print(a)