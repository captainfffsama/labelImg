'''
@Author: lijun
@Date: 2020-06-08 14:29:57
@LastEditors: lijun
@LastEditTime: 2020-06-08 20:42:50
@Description: file content
'''
from cv2 import cv2 as cv
import numpy as np
import os
import matplotlib.pyplot as plt
from skimage.feature import hog
from skimage import data,exposure
import math
print(os.getcwd())
def gamma():
    img = cv.imread(r'D:\pycharm\project\algorithm\0_1.jpg',0)
    img1 = np.power(img/float(np.max(img)),1/1.5)
    img2 = np.power(img/float(np.max(img)),1.5)
    cv.imshow('src',img)
    cv.imshow('img1',img1)
    cv.imshow('img2',img2)
    cv.waitKey(0)
def gradient():
    img = cv.imread(r'D:\pycharm\project\algorithm\0_1.jpg',0)
    img = np.float32(img)/255.0
    gx = cv.Sobel(img,cv.CV_32F,1,0,ksize = 1)
    gy = cv.Sobel(img,cv.CV_32F,0,1,ksize = 1)
    gxy = cv.Sobel(img,cv.CV_32F,1,1,ksize = 1)
    mag,angle = cv.cartToPolar(gx,gy,angleInDegrees=True)

    cv.imshow("absolute x-gradient",gx)
    cv.imshow("absolute y-gradient",gy)
    cv.imshow("absolute xy-gradient",gxy)
    cv.imshow("gradient magnitude",mag)
    cv.imshow("gradient direction",angle)
    cv.waitKey(0)

#?此处使用ski-image中现成函数
def hog_fun():
    img = cv.imread(r'D:\pycharm\project\algorithm\0_1.jpg')
    # cv.imshow('img',img)
    fd,hog_img = hog(img,orientations = 8,pixels_per_cell = (16,16),cells_per_block = (1,1),visualize = True,multichannel = True)
    fig,(ax1,ax2) = plt.subplots(1,2,figsize=(8,4),sharex = True,sharey = True)
    ax1.axis('off')
    ax1.imshow(img,cmap = plt.cm.gray)
    ax1.set_title("input img")
    hog_img_rescaled = exposure.rescale_intensity(hog_img,in_range=(0,10))
    ax2.axis("off")
    ax2.imshow(hog_img_rescaled,cmap = plt.cm.gray)
    ax2.set_title('Histogram of Oriented Gradients')
    plt.show()
    # cv.waitKey(0)


class Hog(object):
    """[summary]
    手动实现Hog特征
    Args:
        object ([type]): [description]
    """    
    def __init__(self,img,cell_size=16,bin_size=8):
        """[summary]

        Args:
            img ([type]): [description]
            cell_size (int, optional): [每一个cell的大小]]. Defaults to 16.
            bin_size (int, optional): [使用n个bin的直方图统计梯度信息]. Defaults to 8.
        """        
        self.img = img
        self.img = np.sqrt(img/np.max(img))
        self.img = img*255
        self.cell_size = cell_size
        self.bin_size = bin_size
        self.angle_uint = 360/self.bin_size
        if(not(isinstance(cell_size,int) or isinstance(bin_size,int))):
            print('bin_size or cell_size should be integer')
    def global_gradient(self):
        """[summary]
        计算幅值和角度（梯度）
        """        
        gradient_x = cv.Sobel(self.img,cv.CV_64F,1,0,ksize=5)
        gradient_y = cv.Sobel(self.img,cv.CV_64F,0,1,ksize=5)
        # gradient_magnitude = cv.addWeighted(gradient_x,0.5,gradient_y,0.5,0)
        # gradient_angle = cv.phase(gradient_x,gradient_y,angleInDegrees=True)
        gradient_magnitude,gradient_angle = cv.cartToPolar(gradient_x,gradient_y,angleInDegrees=True)
        return gradient_magnitude,gradient_angle
    def get_closest_bins(self,gradient_angle):
        index,mod = divmod(gradient_angle,self.angle_uint)
        index_1 = (index+1)%self.bin_size
        return index,index_1,mod
    def cell_gradient(self,cell_magnitude,cell_angle):
        orientation_centers = [0]*self.bin_size
        for i in range(cell_magnitude.shape[0]):
            for j in range(cell_magnitude.shape[1]):
                gradient_strength = cell_magnitude[i][j]
                gradient_angle = cell_angle[i][j]
                min_angle,max_angle,mod = self.get_closest_bins(gradient_angle)
                orientation_centers[min_angle] +=(gradient_strength*(1-(mod/self.angle_uint)))
                orientation_centers[max_angle] +=(gradient_strength*(mod/self.angle_uint))
        return orientation_centers
    def render_gradient(self,img,cell_gradient):
        cell_width = self.cell_size/2
        max_mag = np.array(cell_gradient).max()
        for x in range(cell_gradient.shape[0]):
            for y in range(cell_gradient.shape[1]):
                cell_grad = cell_gradient[x][y]
                cell_grad /=max_mag
                angle = 0
                angle_gap = self.angle_uint
                for magnitude in cell_grad:
                    angle_radian = math.radians(angle)
                    x1 = int(x * self.cell_size + magnitude * cell_width * math.cos(angle_radian))
                    y1 = int(y * self.cell_size + magnitude * cell_width * math.sin(angle_radian))
                    x2 = int(x * self.cell_size - magnitude * cell_width * math.cos(angle_radian))
                    y2 = int(y * self.cell_size - magnitude * cell_width * math.sin(angle_radian))
                    cv2.line(img, (y1, x1), (y2, x2), int(255 * math.sqrt(magnitude)))
                    angle += angle_gap
        return img

    def extract(self):
        height, width = self.img.shape
        gradient_magnitude, gradient_angle = self.global_gradient()
        gradient_magnitude = abs(gradient_magnitude)
        cell_gradient_vector = np.zeros((height / self.cell_size, width / self.cell_size, self.bin_size))
        for i in range(cell_gradient_vector.shape[0]):
            for j in range(cell_gradient_vector.shape[1]):
                cell_magnitude = gradient_magnitude[i * self.cell_size:(i + 1) * self.cell_size,
                                 j * self.cell_size:(j + 1) * self.cell_size]
                cell_angle = gradient_angle[i * self.cell_size:(i + 1) * self.cell_size,
                             j * self.cell_size:(j + 1) * self.cell_size]
                cell_gradient_vector[i][j] = self.cell_gradient(cell_magnitude, cell_angle)

        hog_image = self.render_gradient(np.zeros([height, width]), cell_gradient_vector)
        hog_vector = []
        for i in range(cell_gradient_vector.shape[0] - 1):
            for j in range(cell_gradient_vector.shape[1] - 1):
                block_vector = []
                block_vector.extend(cell_gradient_vector[i][j])
                block_vector.extend(cell_gradient_vector[i][j + 1])
                block_vector.extend(cell_gradient_vector[i + 1][j])
                block_vector.extend(cell_gradient_vector[i + 1][j + 1])
                mag = lambda vector: math.sqrt(sum(i ** 2 for i in vector))
                magnitude = mag(block_vector)
                if magnitude != 0:
                    normalize = lambda block_vector, magnitude: [element / magnitude for element in block_vector]
                    block_vector = normalize(block_vector, magnitude)
                hog_vector.append(block_vector)
        return hog_vector, hog_image

if __name__ == "__main__":
    hog_fun()