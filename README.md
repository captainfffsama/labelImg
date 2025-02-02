# 简介
LabelImg plus pro max ultra

# TODO
- [ ] 修改全知检测和自动检测的线程使用方式

# windows 编译
```shell
pip install pyinstaller
pyinstaller --hidden-import=pyqt5 --hidden-import=lxml --hidden-import=grpcio --hidden-import=opencv-python-headless --hidden-import=sam-grpc -F -n "labelImg" -c labelImg.py -p ./libs -p ./
```

# 新增功能说明
### 2023/04/26
结合[SAM](https://github.com/facebookresearch/segment-anything)(需要[sam_rpc](https://github.com/captainfffsama/sam_grpc)),船新标注体验,是兄弟就来标图!
![SAM模式演示](https://github.com/captainfffsama/MarkDownPics/blob/master/%E5%85%B6%E4%BB%96%E5%9C%B0%E6%96%B9%E5%9B%BE%E7%89%87/new_function.gif?raw=true)

view里面点击`SAM模式`,设置 SAM服务的IP和端口.鼠标变成一个click图片.此时左键是标记点为前景,右键标记点为背景,双击左键完成标记,同时画布切换到普通模式,可以对标注进行编辑.
单击鼠标滚轮,可以切换再次进入"SAM模式"

### 2023/04/11
更新全知检测功能,使用方式类似自动检测,快捷键`Ctrl+Shift+D`,需要配合 grounding dino grpc服务使用.
对于常见的公开数据集中的类,clip可以较好对齐特征的类,可以设置text阈值高一点,比如0.5,防止误检.
text阈值低的时候更加类似显著性检测,会优先检测突出的物体.

![全知检测演示](./doc/cortana%20detection.gif)
### 2023/03.15

将文件框改成ListView,上面添加一个搜索框来快速定位文件,大幅精简读图代码

### 2023/02/15

复制标签快捷键更变为 `ctrl+c`,自动检测快捷键标签更变为 `ctrl+d`

### 2022/11/09

更新了自动检测目标生成标签的功能.

#### 后端开发说明

参见proto文件,和`mmdet_grpc`通用

#### 使用说明

初次使用点击工具栏上的按钮之后,弹出配置对话框.
其中关于阈值的写法示例如下:

```
wcaqm,aqmzc=0.6;xy=0.3;bj_bpmh;
```

其中wcaqm,aqmzc的阈值为0.6,xy阈值0.3,bj_bpmh使用默认阈值,使用 `;`分隔

之后再次点按钮将不会在弹出配置对话框而是直接检测了...

若需要重置自动检测功能配置,单击菜单栏中file里面 `重设自动检测配置`,**注意设置完之后会针对当前图片自动进行一次检测**

#### 预期行为说明

- 若在后端检测期间切换图片,那么之前图片的xml会完全被检测结果覆盖
- 注意后端检测完成之后,若此时没有进行保存,那么xml中只会有后端检测生成的结果
- 生成的xml和软件原始官方行为一致,会优先生成在默认保存位置,即改变存储目录那个按钮所指向的目录(这个目录可能并不是图片所在的目录),而使用txt导入待标图片时,默认保存位置被设置为None,此时xml会保存在和图片同一目录

### 2022/3/28

优化了单一类别显示功能的实现,提高了显示效率(现在只会遍历一遍标签)

使用方法:
菜单栏 `view` 中 `单一显示模式`

### 2020/11/6

### 新增快捷模式

即,确定要进行快速标注的类别,将除开awds之外的任意字母设置成该类别的快捷键,按该键的效果等同于临时开启单例模式,同时完全兼容现有的标注方式.
使用方法:

1. 选择`view -> shortCut`
2. 在弹出的文本框中输入以逗号分隔的键值对来设定快捷方式中的快捷键,如将字符串设定为 `q=aqmzc,e=wcaqm,r=gzzc,f=wcgz`,即将qerf四个键设置成 `aqmzc`,`wcaqm`,`gzzc`,`wcgz` 四个类别的快捷键.按对应快捷键便会直接画框,并设置对应的标签,省去了选择标签的操作.

**注意事项:**

- 开启快捷方式是否成功的信息会显示在最下方的状态栏中
- 设置成空值可以关闭该功能
- 快捷模式和单例模式互斥

**现在记录样本到1~9的txt时,会在最下方的状态栏中提示**


