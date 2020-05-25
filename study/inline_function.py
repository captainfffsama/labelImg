'''
@Author: lijun
@Date: 2020-05-27 20:37:14
@LastEditors: lijun
@LastEditTime: 2020-05-28 17:40:10
@Description: this file is python's inlinefunctions
'''
import os
import time
def all_f():
    """[summary]
        all()函数:用于判断给定的可迭代参数 iterable 中的所有元素是否都为 TRUE，如果是返回 True，否则返回 False。元素除了是 0、空、None、False 外都算 True。
        参数:iterable -- 元组或列表。
        注意：空元组、空列表返回值为True，这里要特别注意。
    """    
    a = ['1','2','3','4']
    b = ['1','2','','4']
    c = []
    print(all(a))
    print(all(b))
    print(all(c))

def any_f():
    """[summary]
    any()函数:用于判断给定的可迭代参数 iterable 是否全部为 False，则返回 False，如果有一个为 True，则返回 True。元素除了是 0、空、FALSE 外都算 TRUE。
    参数iterable -- 元组或列表。
    返回值：如果都为空、0、false，则返回false，如果不都为空、0、false，则返回true。
    """    
    a = ['1','2','3','4']
    b = ['1','2','','4']
    c = [0,'',False,0]
    print(any(a))
    print(any(b))
    print(any(c))

def isinstance_f():
    """[summary]
    isinstance() 与 type() 区别：
    type() 不会认为子类是一种父类类型，不考虑继承关系。
    isinstance() 会认为子类是一种父类类型，考虑继承关系。
    如果要判断两个类型是否相同推荐使用 isinstance()。

    语法
    以下是 isinstance() 方法的语法:
    isinstance(object, classinfo)
    参数
    object -- 实例对象。
    classinfo -- 可以是直接或间接类名、基本类型或者由它们组成的元组。
    返回值
    如果对象的类型与参数二的类型（classinfo）相同则返回 True，否则返回 False。
    """   
    a = 3
    b = '3'
    print(isinstance(a,int)) 
    print(isinstance(b,int))
    print(isinstance(a,(str,int)))

def complex_f():
    """[summary]
    语法
    complex 语法：
    class complex([real[, imag]])

    参数说明：
    real -- int, long, float或字符串；
    imag -- int, long, float；

    返回值
    返回一个复数。
    """    
def execfile_f():
    """[summary]
    语法,以下是 exec 的语法:exec obj
    参数:obj -- 要执行的表达式。
    返回值:exec 返回值永远为 None。
    """    
    print(os.getcwd())
    f = open('./study/hello.py')
    exec(f.read())

class attr_test(object):
    """[summary]
    语法:setattr()
    setattr(object, name, value)

    参数:
    object -- 对象。
    name -- 字符串，对象属性。
    value -- 属性值。

    返回值:无。


    getattr() 函数用于返回一个对象属性值。

    语法
    getattr 语法：

    getattr(object, name[, default])
    参数
    object -- 对象。
    name -- 字符串，对象属性。
    default -- 默认返回值，如果不提供该参数，在没有对应属性时，将触发 AttributeError。
    返回值
    返回对象属性值。
    ########
    #!对于函数，getattr（）的返回值是一个指针，指针赋值给接受它的变量，以后call这个变量就等于调用变量指向的函数
    """     


    def __init__(self):
        print('program is beginning...')
        self.name = 'lj'
        print(getattr(self,'name'))
    def test1(self,para):
        print('test1')
        print(para)
    def test2(self):
        fun = getattr(self,'test1')
        print(type(fun))
        fun('zqj')

def sort_sorted():
    """[summary]
    语法
    sorted 语法：
    sorted(iterable, key=None, reverse=False)  
    参数说明：
    iterable -- 可迭代对象。
    key -- 主要是用来进行比较的元素，只有一个参数，具体的函数的参数就是取自于可迭代对象中，指定可迭代对象中的一个元素来进行排序。
    reverse -- 排序规则，reverse = True 降序 ， reverse = False 升序（默认）。
    返回值
    返回重新排序的列表。

    #!你也可以使用 list 的 list.sort() 方法。这个方法会修改原始的 list（返回值为None）
    """    
    a = [1,3,7,2,9,10,4]
    b = [1,3,7,2,9,10,4]

    aa = sorted(a)
    print(a)
    print(aa)
    
    print(b)
    b.sort()
    print(b)

class C(object):
    """[summary]
        类中静态方法不需要创建实例
        静态方法类似普通方法，参数里面不用self。这些方法和类相关，但是又不需要类和实例中的任何信息、属性
    Args:
        object ([type]): [description]
    """    
    def __init__(self):
        pass
    @staticmethod
    def fun(para):
        print(para)

def filter_f():
    """[summary]
    描述
    filter() 函数用于过滤序列，过滤掉不符合条件的元素，返回一个迭代器对象，如果要转换为列表，可以使用 list() 来转换。

    该接收两个参数，第一个为函数，第二个为序列，序列的每个元素作为参数传递给函数进行判，
    #!然后返回 True 或 False，最后将返回 True 的元素放到新列表中。

    语法
    以下是 filter() 方法的语法:

    filter(function, iterable)
    参数
    function -- 判断函数。
    iterable -- 可迭代对象。
    返回值
    返回一个迭代器对象
    """    
    def is_odd(n):
        return n % 2 == 1
    tmplist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    newlist = list(tmplist)
    print(newlist)
def map_f():
    """[summary]
    描述
    map() 会根据提供的函数对指定序列做映射。

    #!第一个参数 function 以参数序列中的每一个元素调用 function 函数，返回包含每次 function 函数返回值的新列表。

    语法
    map() 函数语法：

    map(function, iterable, ...)
    参数
    function -- 函数
    iterable -- 一个或多个序列
    返回值
    Python 2.x 返回列表。

    Python 3.x 返回迭代器。
    """    
    def is_odd(n):
        return n % 2 == 1
    tmplist = filter(is_odd, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    newlist = list(tmplist)
    print(newlist)
def issubclass_f():
    """[summary]
    描述
    issubclass() 方法用于判断参数 class 是否是类型参数 classinfo 的子类。

    语法
    以下是 issubclass() 方法的语法:

    issubclass(class, classinfo)
    参数
    class -- 类。
    classinfo -- 类。
    返回值
    如果 class 是 classinfo 的子类返回 True，否则返回 False。
    """    
    pass
def print_f():
    """[summary]

    """    
    print("Loading",end = "")
    for i in range(10):
        print('.',end = "",flush = True)
        time.sleep(0.5)

############
from functools import wraps
def new_fun(f):
    @wraps(f)
    def fn(x):
        print('this is extral fun')
        print(x+1)
        return f(x)
    return fn

@new_fun
def fn_aaa(para):
    print('this is base fun')
    print(para)
#!python 中的装饰器类似于C++中的virtual函数
######################

class A(object):
    """[summary]

    classmethod 修饰符对应的函数不需要实例化，不需要 self 参数，但第一个参数需要是表示自身类的 cls 参数，可以来调用类的属性，类的方法，实例化对象等。
    """    
    aaa = 'aaaaaa'
    @classmethod
    def fun(cls):
        print(cls.aaa)
def locals_f(para):
    """[summary]
    locals() 函数会以字典类型返回当前位置的全部局部变量。
    """
    a = 1
    b = 2
    c = ['a','2','c']
    print(locals())

def repr_f(para):
    """[summary]
    描述
    repr() 函数将对象转化为供解释器读取的形式。
    """
    print(repr(para))
    print(type(repr(para)))


def zip_f():
    """[summary]
    zip() 函数用于将可迭代的对象作为参数，将对象中对应的元素打包成一个个元组，然后返回由这些元组组成的对象，这样做的好处是节约了不少的内存。
    """    
    a = ['a',1,'b']
    b= [1,'b','2',3]
    c = [11,33,'ddd',231,'cdv']
    dd = zip(a,b,c)
    print(list(dd))

def global_f():
    """[summary]
    globals() 函数会以字典类型返回当前位置的全部全局变量。
    """    
    print(globals())

def hash_f(para):
    """[summary]
    hash() 用于获取取一个对象（字符串或者数值等）的哈希值。
    """    
    print(hash(para))
    print(hex(hash(para)))



####################额外计数使用
from collections import defaultdict
from collections import Counter
def count_f():
    a = [1,2,3,4,5,5,4,3,2,4,5,3,21,434,56,78]
    count_dict = defaultdict(int)
    for item in a:
        count_dict[item]+=1
    # print(count_dict)
    print(Counter(a))
if __name__ == "__main__":
    # all_f()
    # any_f()
    # isinstance_f()
    # execfile_f()
    # test = attr_test()
    # test.test2()
    # sort_sorted()
    # C.fun('aaaa')
    # filter_f()
    # fn_aaa(5)
    # print(fn_aaa.__name__)
    # A.fun()
    # locals_f(7)
    # repr_f(['1','2',3,4,5,10,{1:1,2:3}])
    # zip_f()
    # global_f()
    # hash_f(repr(['1',2,3,'7']))
    # count_f()
    a = []
    if(a):
        print(a)
    else:
        print('a is None')