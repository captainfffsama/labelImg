'''
@Description: In User Settings Edit
@Author: your name
@Date: 2019-09-06 13:21:10
@LastEditTime : 2020-01-02 19:21:54
@LastEditors  : Please set LastEditors
'''
#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs
import glob
import json
import os
import shutil
import xml.etree.ElementTree as ET
import argparse
from lxml import etree
from xml.etree import ElementTree
from PIL import Image

source_path = '/Volumes/G/fire_control/unlabel/test_1'
target_path = '/Volumes/G/fire_control/unlabel/test_1'
drop_path = '/home/gpu-server/project/data/drop'
class_path = ''
data_path = ''
data_replace_path = ''
label_path = 'fire_control.ini'
# label_path = 'labels.ini'
source_format = 'voc'
target_format = 'config'
copy_image = True

format_suffix_map = {
    'config': '.config',
    'yolo': '.txt',
    'voc': '.xml',
}

label_idx_map = {
    "bl_on": 0,
    "bl_off": 1,
    "vol": 2,
    "s_up": 3,
    "s_down": 4,
    "yb_open": 5,
    "yb_close": 6,
    "handle": 7,
    "backup": 8,
    "digital_panel": 9,
    "zldlq_on": 10,
    "zldlq_off": 11,
}

idx_label_map = {v: k for k, v in label_idx_map.items()}

ignore_files = {'data.txt', 'classes.txt'}


def dict_sort_by_key(dict, reverse=False):
    new_dict = {}
    for k in sorted(dict.keys(), reverse=reverse):
        new_dict[k] = dict[k]
    dict = new_dict
    return dict


def dict_sort_by_value(dict, reverse=False):
    new_dict = {}
    sorted_by_value = sorted(
        dict.items(),
        key=lambda kv: kv[1],
        reverse=reverse)
    for item in sorted_by_value:
        key = item[0]
        value = item[1]
        new_dict[key] = value
    dict = new_dict
    return dict


def parse_ini():
    if not os.path.exists(label_path):
        print(label_path + ' ini file is not exist')
        return
    global label_idx_map, idx_label_map
    label_idx_map.clear()
    idx_label_map.clear()
    with open(label_path) as f:
        for line in f.read().split('\n'):
            if '=' in line and not str(line).startswith(';'):
                arr = line.replace('\r', '').split('=')
                label_idx_map[arr[1]] = int(arr[0])
    label_idx_map = dict_sort_by_value(label_idx_map)
    idx_label_map = {v: k for k, v in label_idx_map.items()}


def create_class_txt():
    if not os.path.exists(class_path):
        with open(class_path, 'w') as f:
            for k, v in sorted(label_idx_map.items(), key=lambda d: d[1]):
                f.write(k + '\n')


def get_source_files():
    suffix = format_suffix_map.get(source_format)
    return glob.glob(source_path + '/*' + suffix)


def convert_to_yolo_bbox(width, height, box):
    dw = 1. / width
    dh = 1. / height
    w = box[2]
    h = box[3]
    x = box[0] + w / 2.0
    # x = box[0] + w / 2.0 - 1
    y = box[1] + h / 2.0
    # y = box[1] + h / 2.0 - 1
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


def record_data_txt(file):
    with codecs.open(data_path, 'a', encoding='utf-8') as f:
        # txt_path = os.path.join(
        #     target_path, file.replace(
        #         '.jpg.config', '.txt'))
        txt_path = file.replace('.config', '.jpg')
        if data_replace_path:
            txt_path = os.path.join(
                data_replace_path,
                os.path.basename(txt_path))
        else:
            txt_path = os.path.abspath(txt_path)
        f.write(txt_path + '\n')


def get_Item(BoundingBox, label, label_num, polygon):
    item = {}
    item['BoundingBox'] = BoundingBox
    item['label'] = label
    item['labelNum'] = int(label_num)
    item['polygon'] = polygon
    return item


def save_config(txt_file, width, height, channels):
    txt = open(txt_file, 'r')
    lines = txt.readlines()
    num = 0
    MaskPolygonItem = {}
    for line in lines:
        arr = line.split(' ')
        if len(arr) != 5:
            print('{} format is not right!'.format(txt_file))
            continue
        label_num = arr[0]
        label = idx_label_map[int(label_num)]
        center_x = float(arr[1]) * width
        center_y = float(arr[2]) * height
        w = float(arr[3]) * width
        h = float(arr[4]) * height
        left = center_x - w / 2
        right = center_x + w / 2
        top = center_y - h / 2
        bottom = center_y + h / 2
        #增加边界判断逻辑
        if left < 0:
            left = 0
        elif top < 0:
            top = 0
        elif left+w>width:
            w = width-left
        elif top+h>height:
            h = height-top

        # print('data',left,top,w,h)


        BoundingBox = '{:.3f} {:.3f} {:.3f} {:.3f}'.format(left, top, w, h)
        polygon = '{:.3f} {:.3f},{:.3f} {:.3f},{:.3f} {:.3f},{:.3f} {:.3f}'\
            .format(left, top,
                    right, top,
                    right, bottom,
                    left, bottom)
        MaskPolygonItem[str(num)] = get_Item(
            BoundingBox, label, label_num, polygon)
        num = num + 1
    root = {}
    root['MaskPolygonItem'] = MaskPolygonItem
    root['height'] = height
    root['width'] = width
    root['channels'] = channels
    jsonStr = json.dumps(root, sort_keys=True, indent=4, )
    config_path = os.path.join(
        target_path, os.path.basename(txt_file).replace(
            '.txt', '.config'))
    with open(config_path, 'w') as f:
        f.write(jsonStr)
    txt.close()


def drop_file(img_name):
    img_name = img_name.replace('.jpg',' ')
    print("image_name",img_name)
    file_type_set = {'.jpg', '.txt', '.config', '.xml'}
    if not os.path.exists(drop_path):
        os.makedirs(drop_path)
    for file_type in file_type_set:
        file_path = img_name + file_type
        if os.path.exists(file_path):
            print("file_path",file_path)
            shutil.move(file_path, drop_path)


def get_image_info(file):
    img = os.path.splitext(file)[0] + '.jpg'
    if not os.path.exists(img):
        print("Can not find {}, and drop it".format(img))
        drop_file(img)
        return {}
    im = Image.open(img)
    width, height = im.size
    channels = len(im.getbands())
    return {'width': width, 'height': height, 'channels': channels}


def transfer_yolo_to_config(file):
    if file.endswith('data.txt') or file.endswith('classes.txt'):
        return
    image_info = get_image_info(file)
    if not image_info:
        return
    save_config(
        file,
        image_info['width'],
        image_info['height'],
        image_info['channels'])


def transfer_voc_to_config(file):
    in_file = open(file)
    tree = ET.parse(in_file)
    in_file.close()
    root = tree.getroot()
    image_info = get_image_info(file)
    if not image_info:
        return
    w = image_info['width']
    h = image_info['height']
    d = image_info['channels']

    num = 0
    MaskPolygonItem = {}
    for obj in root.iter('object'):
        label = obj.find('name').text
        label_num = label_idx_map.get(label)

        xmlbox = obj.find('bndbox')
        xmin = int(xmlbox.find('xmin').text)
        xmax = int(xmlbox.find('xmax').text)
        ymin = int(xmlbox.find('ymin').text)
        ymax = int(xmlbox.find('ymax').text)

        BoundingBox = '{} {} {} {}'.format(
            xmin, ymin, abs(xmax - xmin), abs(ymax - ymin))
        polygon = ',{} {},{} {},{} {},{} {}'.format(xmin, ymin,
                                                    xmax, ymin,
                                                    xmax, ymax,
                                                    xmin, ymax)
        MaskPolygonItem[str(num)] = get_Item(
            BoundingBox, label, label_num, polygon)
        num = num + 1
    root = {}
    root['MaskPolygonItem'] = MaskPolygonItem
    root['height'] = h
    root['width'] = w
    root['channels'] = d
    jsonStr = json.dumps(root, sort_keys=True, indent=4, )
    config_file_name = os.path.basename(file).replace('.xml', '.config')
    config_path = os.path.join(target_path, config_file_name)
    with open(config_path, 'w') as f:
        f.write(jsonStr)


def create_root(file_prefix, width, height, depth):
    root = ET.Element("annotation")
    ET.SubElement(root, "folder").text = target_path
    ET.SubElement(root, "filename").text = file_prefix
    size = ET.SubElement(root, "size")
    ET.SubElement(size, "width").text = str(width)
    ET.SubElement(size, "height").text = str(height)
    ET.SubElement(size, "depth").text = str(depth)
    return root


def create_object_annotation(root, voc_labels):
    for voc_label in voc_labels:
        obj = ET.SubElement(root, "object")
        ET.SubElement(obj, "name").text = voc_label[0]
        ET.SubElement(obj, "pose").text = "Unspecified"
        ET.SubElement(obj, "truncated").text = str(0)
        ET.SubElement(obj, "difficult").text = str(0)
        bbox = ET.SubElement(obj, "bndbox")
        xmin = int(voc_label[1])
        ymin = int(voc_label[2])
        w = int(voc_label[3])
        h = int(voc_label[4])
        ET.SubElement(bbox, "xmin").text = str(xmin)
        ET.SubElement(bbox, "xmax").text = str(xmin + w)
        ET.SubElement(bbox, "ymin").text = str(ymin)
        ET.SubElement(bbox, "ymax").text = str(ymin + h)
    return root


def prettify(elem):
    """
        Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf8')
    root = etree.fromstring(rough_string)
    return etree.tostring(root,
                          pretty_print=True,
                          encoding='utf-8').replace("  ".encode(),
                                                    "\t".encode())


def create_file(file_prefix, width, height, depth, voc_labels):
    file_name = os.path.basename(file_prefix)
    voc_file = os.path.join(target_path, file_name + '.xml')
    root = create_root(file_name, width, height, depth)
    root = create_object_annotation(root, voc_labels)
    prettify_result = prettify(root)
    with open(voc_file, 'w') as out_file:
        out_file.write(prettify_result.decode('utf8'))
        out_file.close()


def get_config_info(cfg_file_path):
    cfg_file = open(cfg_file_path)
    root = json.load(cfg_file)
    cfg_file.close()

    height = root['height']
    width = root['width']
    channels = ''
    if 'channels' in root:
        channels = root['channels']
    polygon_item = root['MaskPolygonItem']
    items = []
    for item in polygon_item.values():
        label = item['label']
        arr = item['BoundingBox'].split(' ')
        box = (float(arr[0]), float(arr[1]), float(arr[2]), float(arr[3]))
        voc = [label, box[0], box[1], box[2], box[3]]
        items.append(voc)
    return height, width, channels, items


def transfer_config_to_voc(cfg_file_path):
    file_prefix = cfg_file_path.split(".config")[0]
    height, width, channels, items = get_config_info(cfg_file_path)
    create_file(file_prefix, width, height, channels, items)


def transfer_config_to_yolo(cfg_file_path):
    create_class_txt()

    txt_file = os.path.join(
        target_path,
        os.path.basename(cfg_file_path).replace(
            '.config',
            '.txt'))
    out_file = open(txt_file, 'w')
    height, width, channels, items = get_config_info(cfg_file_path)
    for item in items:
        box = (item[1], item[2], item[3], item[4])
        bb = convert_to_yolo_bbox(width, height, box)
        #idx = label_idx_map[item[0].lower()]
        idx = label_idx_map[item[0]]
        yolo_str = '{} {:.4f} {:.4f} {:.4f} {:.4f}\n'.format(
            idx, bb[0], bb[1], bb[2], bb[3])
        # out_file.write(str(idx) + " " + " ".join([str(a) for a in bb]) + '\n')
        out_file.write(yolo_str)
    record_data_txt(cfg_file_path)


def get_config_file(file):
    file_name = os.path.basename(file).split('.')[0] + '.config'
    return os.path.join(target_path, file_name)


def clean_config(file):
    if os.path.exists(file):
        os.remove(file)


def transfer(file):
    global source_path, target_path
    assert source_format != target_format

    if os.path.basename(file) in ignore_files:
        print('ignore file :{}'.format(file))
        return

    if source_format == 'config':
        if target_format == 'yolo':
            transfer_config_to_yolo(file)
            return
        elif target_format == 'voc':
            transfer_config_to_voc(file)
            return

    if source_format == 'yolo':
        transfer_yolo_to_config(file)
    elif source_format == 'voc':
        transfer_voc_to_config(file)
    if target_format != 'config':
        config_file = get_config_file(file)
        if target_format == 'yolo':
            transfer_config_to_yolo(config_file)
        elif target_format == 'voc':
            transfer_config_to_voc(config_file)
        clean_config(config_file)


def rename_image():
    files = glob.glob(source_path + '/*')
    jpg_alias_set = {'jpeg', 'jpe', 'jfif', 'jif'}
    for f in files:
        if f.split('.')[-1].lower() in jpg_alias_set:
            new_image = f.split('.')[-2] + '.jpg'
            print(new_image)
            os.rename(f, new_image)


def copy_images():
    print('start copy_images')
    imgs = glob.glob(source_path + '/*.jpg')
    for img in imgs:
        new_img_path = os.path.join(target_path, os.path.basename(img))
        if not os.path.exists(new_img_path):
            shutil.copy(img, new_img_path)
    print('end copy_images')


def init():
    parse_ini()
    rename_image()

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    if copy_image:
        copy_images()

    if target_format == 'yolo':
        if os.path.exists(class_path):
            os.remove(class_path)
        if os.path.exists(data_path):
            os.remove(data_path)


def check_param():
    assert source_format in format_suffix_map.keys()
    assert target_format in format_suffix_map.keys()
    assert source_format != target_format


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def check_polygon():
    pass

def check_rect():
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.description = '标注格式转换工具' \
                         ' 范例：python format_transfer.py -sf yolo -tf voc -sp path/to/yolo -tp path/to/voc -ci True'
    parser.add_argument('-i', "--ini", help='path of labels.ini')
    parser.add_argument('-sp', "--source_path", help='source_path')
    parser.add_argument('-tp', "--target_path", help='target_path')
    parser.add_argument('-sf', "--source_format", help='source_format')
    parser.add_argument('-tf', "--target_format", help='target_format')
    parser.add_argument(
        '-ci',
        "--copy_image",
        type=str2bool,
        default=copy_image,
        help='if copy images to target path or not, default False')
    args = parser.parse_args()
    if args.ini:
        label_path = args.ini
    if args.source_path:
        source_path = args.source_path
        # target_path is same as source_path by default
        target_path = source_path
    if args.target_path:
        target_path = args.target_path
    if args.source_format:
        source_format = args.source_format
    if args.target_format:
        target_format = args.target_format
    if args.copy_image != copy_image:
        copy_image = args.copy_image
    class_path = os.path.join(target_path, 'classes.txt')
    data_path = os.path.join(target_path, 'data.txt')

    check_param()
    init()
    files = get_source_files()
    size = len(files)
    for n, file in enumerate(files):
        print('process {} {:.2%}'.format(file, (float(n + 1) / size)))
        transfer(file)
