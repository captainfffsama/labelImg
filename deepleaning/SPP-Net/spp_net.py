'''
@Author: lijun
@Date: 2020-06-11 11:01:56
@LastEditors: lijun
@LastEditTime: 2020-06-11 14:35:07
@Description: file content
'''
import tensorflow as tf
import numpy as np
import cv2 as cv

def spp_layer(intput,levels = 4,name = 'spp',pool_type = 'max_pool'):
    print(intput)
    intput = tf.expand_dims(intput,0)
    shape = intput.get_shape().as_list()

    # shape = intput.shape().as_list()
    """[summary]
    当i=1时，表示使用网格大小与图片大小一样的进行max_pooling
    当i=2时，表示使用图片大小一半的网格进行max_pooling
    当i=3时，表示使用图片大小1/3的网格进行max_pooling
    """
    for i in range(levels):
        i +=1
        ksize = [1,np.ceil(shape[1]/i+1),np.ceil(shape[1]/i+1),1]#向上取整的目的表示整张图不会出现多余的部分未被pooling
        strides = [1,np.floor(shape[1]/i+1),np.floor(shape[1]/i+1),1]
        if pool_type=='max_pool':
            pool = tf.nn.max_pool(intput,ksize,strides,padding='SAME')
            pool = tf.reshape(pool,(shape[0],-1))
        else:
            pool = tf.nn.avg_pool(intput,ksize,strides,padding='SAME')
            pool = tf.reshape(pool,(shape[0],-1))
        print('Pool Level {} shape {}'.format(i,pool.get_shape().as_list()))
            
        if i ==1:
            x_flatten = tf.reshape(pool,(shape[0],-1))
        else:
            x_flatten = tf.concat((x_flatten,pool),axis=1)
        print('Pool Level {} x_flatten {}'.format(i,x_flatten.get_shape().as_list()))
if __name__ == "__main__":
    # x = tf.ones((4,16,16,3))
    img_path = r'D:\pycharm\project\algorithm\0_1.jpg'
    img_value = tf.io.read_file(img_path)
    img = tf.image.decode_jpeg(img_value)
    spp_layer(img)