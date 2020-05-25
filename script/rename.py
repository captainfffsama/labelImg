'''
@Author: lijun
@Date: 2020-05-24 02:26:05
@LastEditors: lijun
@LastEditTime: 2020-05-30 20:15:43
@Description: file content
'''
import glob
import os
class Rename(object):
    def __init__(self):
        pass
    def rename_file(self,filePath:str,ori_key_name:str,dst_key_name:str):
        img_paths= glob.glob(filePath+'/*',recursive = True)
        for img_path in img_paths:
            dst_img_path = img_path.replace(ori_key_name,dst_key_name)
            try:
                os.rename(img_path,dst_img_path)
                print('rename {} sucess'.format(img_path))
            except:
                print('rename {} fail'.format(img_path))

if __name__ == "__main__":
    file_path = r'C:\Users\lj893\Desktop\all_roi'
    ori_key_name = 'alllighton'
    dst_key_name = 'allon'
    rename = Rename()
    rename.rename_file(file_path,ori_key_name,dst_key_name)
    