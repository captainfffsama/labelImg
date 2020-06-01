'''
@Author: lijun
@Date: 2020-05-29 14:08:40
@LastEditors: lijun
@LastEditTime: 2020-05-29 18:44:30
@Description: file content
'''
import numpy as np
import matplotlib.pyplot as plt
import glob
from cv2 import cv2 as cv
import os
from concurrent import futures
from tqdm import tqdm
def fourier_numpy(path):
    img = plt.imread(path)
    plt.subplot(231),plt.imshow(img),plt.title('picture')
    #根据公式转成灰度图
    img = 0.2126 * img[:,:,0] + 0.7152 * img[:,:,1] + 0.0722 * img[:,:,2]
    
    #显示灰度图
    plt.subplot(232),plt.imshow(img,'gray'),plt.title('original')
    
    
    #进行傅立叶变换，并显示结果
    fft2 = np.fft.fft2(img)
    plt.subplot(233),plt.imshow(np.abs(fft2),'gray'),plt.title('fft2')


    #将图像变换的原点移动到频域矩形的中心，并显示效果
    shift2center = np.fft.fftshift(fft2)
    plt.subplot(234),plt.imshow(np.abs(shift2center),'gray'),plt.title('shift2center')
    
    
    #对傅立叶变换的结果进行对数变换，并显示效果
    log_fft2 = np.log(1 + np.abs(fft2))
    plt.subplot(235),plt.imshow(log_fft2,'gray'),plt.title('log_fft2')

    log_shift2center = np.log(1 + np.abs(shift2center))
    plt.subplot(236),plt.imshow(log_shift2center,'gray'),plt.title('log_shift2center')
    save_path = path.split('.')[0]+'_np_result.png'
    plt.savefig(save_path)
    plt.show()
def fourier_cv(img):
 
    # print(path,'\n')
    img = cv.imread(img,0)
    # cv.imshow('ori.jpg',img)
    # img = img[360:720,640:1280]
    # cv.imshow('dst.jpg',img)
    # cv.waitKey(0)
    dft = cv.dft(np.float32(img),flags = cv.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = 20*np.log(cv.magnitude(dft_shift[:,:,0],dft_shift[:,:,1]))
    global mid_data
    mid_data = magnitude_spectrum[540][960]
    # mid_data = magnitude_spectrum[180][320]
    # result_data = list(filter(lambda data:abs(data-mid_data)<35,magnitude_spectrum.flatten()))
    magnitude_spectrum = magnitude_spectrum.flatten()
    # dst_data = magnitude_spectrum-mid_data
    result = []
    # for data in magnitude_spectrum:
    #     deal_data(data,mid_data,result)
    # with futures.ThreadPoolExecutor(32) as pool:
    #     task_list = (pool.submit(deal_data,data,mid_data,result) for data in magnitude_spectrum)
    #     for i in tqdm(futures.as_completed(task_list),total=len(magnitude_spectrum)):
    #         pass
    # for i in range(len(magnitude_spectrum)):
    #     for index,data in enumerate(magnitude_spectrum[i]):
    #         bias = abs(mid_data-data)
    #         if bias<35:
    #             print('x:{} y:{} bias:{} mid_data:{}'.format(index,i,bias,mid_data))

    result = list(filter(deal_data,magnitude_spectrum))
    print(result)
    # plt.subplot(121),plt.imshow(img, cmap = 'gray')
    # plt.title('Input Image'), plt.xticks([]), plt.yticks([])
    # plt.subplot(122),plt.imshow(magnitude_spectrum, cmap = 'gray')
    # plt.title('Magnitude Spectrum'), plt.xticks([]), plt.yticks([])
    # save_path = path.split('.')[0]+'_cv_result.png'
    # plt.savefig(save_path,dpi = 300,bbox_inches = 'tight')
    # plt.show()
def deal_data(data):
    bias = abs(data-mid_data)
    return bias<35
    # if(bias<35):
    #     result.append(data)
    #     print(bias)

if __name__ == "__main__":
    base_path = r'C:\Users\lj893\Desktop\candidate'
    # img_paths = glob.glob(base_path+'/*.jpg',recursive = True)
    # for img_path in img_paths:
    img_path = r'C:\Users\lj893\Desktop\candidate\8.jpg'
    fourier_cv(img_path)
    # video_path = r'C:\Users\lj893\Desktop\test.avi'
    # video = cv.VideoCapture(video_path)
    # if video.isOpened(): #判断是否正常打开
    #     rval , frame = video.read()
    #     print("视频打开成功！")
    # else:
    #     rval = False
    #     print("视频打开失败！")
    # while rval:   #循环读取视频帧
    #     rval, frame = video.read()
    #     # cv.imshow('ori.jpg',frame)
    #     # cv.waitKey(0)
    #     frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    #     fourier_cv(frame)