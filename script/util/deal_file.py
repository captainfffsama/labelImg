'''
@Author: lijun
@Date: 2020-05-15 15:28:21
@LastEditors: lijun
@LastEditTime: 2020-05-15 16:39:47
@Description: deal file
'''
import shutil
class Dealfile(object):
    """[summary]

    Args:
        object ([type]): [this is deal file class]
    """
    def __init__(self):
        """[summary]
        """
        pass
    def copy_file(self,file_path:'str',dst_path:'str'):
        """[summary]

        Args:
            self ([type]): [description]
            file_path ([str]): [need to copy file path]
            dst_path ([str]): [dst file]
        """
        try:
            shutil.copy2(file_path,dst_path)
        except Exception as e:
            print(e)

    def move_file(self,file_path:'str',dst_path:'str'):
        """[summary]

        Args:
            file_path ([str]): [need to move path]
            dst_path ([str]): [dst file]
        """
        try:
            shutil.move(file_path,dst_path)
        except Exception as e:
            print(e)