'''
@Author: lijun
@Date: 2020-06-02 10:24:50
@LastEditors: lijun
@LastEditTime: 2020-06-02 12:33:34
@Description: file content
'''
import numpy as np
a = np.arange(24)
# print(a.ndim)
b = a.reshape(2,3,4)
# print(b.ndim)


# 使用 range 函数创建列表对象  
list=range(5)
print(list)
it=iter(list)
# print(it)
# 使用迭代器创建 ndarray 
x=np.fromiter(it, dtype=float)
# print(x)

#!创建等差数列
'''
参数	描述
start	序列的起始值
stop	序列的终止值，如果endpoint为true，该值包含于数列中
num	要生成的等步长的样本数量，默认为50
endpoint	该值为 true 时，数列中包含stop值，反之不包含，默认是True。
retstep	如果为 True 时，生成的数组中会显示间距，反之不显示。
dtype	ndarray 的数据类型
'''
c = np.linspace(1, 100, num=50, endpoint=True, retstep=True, dtype=None)
# print(c)


#!创建等比数列
'''
参数	描述
start	序列的起始值为：base ** start
stop	序列的终止值为：base ** stop。如果endpoint为true，该值包含于数列中
num	要生成的等步长的样本数量，默认为50
endpoint	该值为 true 时，数列中中包含stop值，反之不包含，默认是True。
base	对数 log 的底数。
dtype	ndarray 的数据类型
'''
d=np.logspace(1, 200, num=50, endpoint=True, base=10.0, dtype=None)
# print(d)


#!切片slice,左闭右开
e = np.arange(10)  
f = e[2:8:2]   # 从索引 2 开始到索引 8 停止，间隔为 2
# print(f)

x = np.array([[  0,  1,  2],[  3,  4,  5],[  6,  7,  8],[  9,  10,  11]])  
print ('我们的数组是：' )
print (x)
print ('\n')
rows = np.array([[0,0],[3,3]]) 
cols = np.array([[0,2],[0,2]]) 
print(rows,cols)
y = x[rows,cols]  
print  ('这个数组的四个角元素是：')
# print (y)


x=np.arange(32).reshape((8,4))
print(x)
print (x[[4,2,1,7]])

a = np.arange(9).reshape(3,3) 
print ('原始数组：')
for row in a:
    print (row)
print ('迭代后的数组：')
print(a.ravel())#!ravel对展开的数组进行修改会改变原数组
print(a.flatten())#!flatten只是做了一次拷贝，对展开后数组进行修改不会改变原值
for element in a.flat:
    print (element)


a = np.arange(12).reshape(3,4)
print ('原数组：')
print (a )
print ('\n')
 
print ('对换数组：')
print (np.transpose(a))#!相当于转制T


#!numpy.rollaxis,numpy.swapaxes
'''
numpy.rollaxis 函数向后滚动特定的轴到一个特定位置，格式如下：

numpy.rollaxis(arr, axis, start)
参数说明：

arr：数组
axis：要向后滚动的轴，其它轴的相对位置不会改变
start：默认为零，表示完整的滚动。会滚动到特定位置。
'''

'''
numpy.swapaxes 函数用于交换数组的两个轴，格式如下：

numpy.swapaxes(arr, axis1, axis2)
arr：输入的数组
axis1：对应第一个轴的整数
axis2：对应第二个轴的整数
'''

'''
#!
numpy.expand_dims
numpy.expand_dims 函数通过在指定位置插入新的轴来扩展数组形状，函数格式如下:
numpy.expand_dims(arr, axis)
参数说明：
arr：输入数组
axis：新轴插入的位置
'''
a = np.array(([1,2,3],[4,5,6]))
print(a)
print(np.expand_dims(a,axis = 0))

'''
#!
numpy.squeeze
numpy.squeeze 函数从给定数组的形状中删除一维的条目，函数格式如下：
numpy.squeeze(arr, axis)
参数说明：
arr：输入数组
axis：整数或整数元组，用于选择形状中一维条目的子集
'''
x = np.arange(9).reshape(1,3,3)
print ('数组 x：')
print (x)
print ('\n')
y = np.squeeze(x)
print ('数组 y：')
print (y)
print ('\n')

'''
numpy.concatenate
numpy.concatenate 函数用于沿指定轴连接相同形状的两个或多个数组，格式如下：

numpy.concatenate((a1, a2, ...), axis)
参数说明：

a1, a2, ...：相同类型的数组
axis：沿着它连接数组的轴，默认为 0
#!axis=0时，是垂直，axis=1时，是水平
'''
a = np.array([[1,2],[3,4]])
 
print ('第一个数组：')
print (a)
print ('\n')
b = np.array([[5,6],[7,8]])
 
print ('第二个数组：')
print (b)
print ('\n')
# 两个数组的维度相同
 
print ('沿轴 0 连接两个数组：')
print (np.concatenate((a,b)))
print ('\n')
 
print ('沿轴 1 连接两个数组：')
print (np.concatenate((a,b),axis = 1))

'''
numpy.stack
numpy.stack 函数用于沿新轴连接数组序列，格式如下：

numpy.stack(arrays, axis)
参数说明：

arrays相同形状的数组序列
axis：返回数组中的轴，输入数组沿着它来堆叠
'''

a = np.array([[1,2],[3,4]])
print ('第一个数组：')
print (a)
print ('\n')
b = np.array([[5,6],[7,8]])
print ('第二个数组：')
print (b)
print ('\n')
print ('沿轴 0 堆叠两个数组：')
print (np.stack((a,b),0))
print ('\n')
print ('沿轴 1 堆叠两个数组：')
print (np.stack((a,b),1))

'''
numpy.split
numpy.split 函数沿特定的轴将数组分割为子数组，格式如下：

numpy.split(ary, indices_or_sections, axis)
参数说明：

ary：被分割的数组
indices_or_sections：如果是一个整数，就用该数平均切分，如果是一个数组，为沿轴切分的位置（左开右闭）
axis：沿着哪个维度进行切向，默认为0，横向切分。为1时，纵向切分
'''
#!np.resize和np.reshape不改变原始数组
#!a.resize改变原始数组
a = np.array([[1,2,3],[4,5,6]])
print(np.resize(a,(3,2)))
print(a)
print(a.resize(3,2))
print(a)