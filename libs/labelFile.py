# Copyright (c) 2016 Tzutalin
# Create by TzuTaLin <tzu.ta.lin@gmail.com>

try:
    from PyQt5.QtGui import QImage,QPainter,QPen,QColor,QFont
    from PyQt5.QtCore import QPoint,Qt
except ImportError:
    from PyQt4.QtGui import QImage,QPainter,QPen,QColor,QFont
    from PyQt4.QtCore import QPoint,Qt
from base64 import b64encode, b64decode
from libs.pascal_voc_io import PascalVocWriter
from libs.yolo_io import YOLOWriter
from libs.pascal_voc_io import XML_EXT
import os
import sys


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = XML_EXT

    def __init__(self, filename=None):
        self.shapes = ()
        self.imagePath = None
        self.imageData = None
        self.verified = False
        self.drawResultImg=False

    def _drawResultImage(self,imagePath:str,shapes,img:QImage=None):
        if img is None:
            img = QImage()
            img.load(imagePath)
        painter=QPainter(img)
        # painter.setCompositionMode(QPainter.Comp)
        painter.setPen(QPen(Qt.green,  5, Qt.SolidLine))
        for shape in shapes:
            points = shape['points']
            label = shape['label']
            bndbox = LabelFile.convertPoints2BndBox(points)
            tx,ty,w,h=bndbox[0],bndbox[1],bndbox[2]-bndbox[0],bndbox[3]-bndbox[1]
            painter.drawRect(tx,ty,w,h)
            painter.setFont(QFont('SimSun', max(10,w//20)))
            painter.drawText(QPoint(tx,ty),label)

        dd,filename=os.path.split(imagePath)
        save_dir=os.path.join(dd,"result_img")
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        img.save(os.path.join(save_dir,filename),"JPG",100)



    def savePascalVocFormat(self, filename, shapes, imagePath, imageData,
                            lineColor=None, fillColor=None, databaseSrc=None, origin_xmlTree=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        # imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        image = QImage()
        image.load(imagePath)
        imageShape = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]
        writer = PascalVocWriter(imgFolderName, imgFileName,
                                 imageShape, localImgPath=imagePath, origin_xmlTree=origin_xmlTree)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bndbox = LabelFile.convertPoints2BndBox(points)
            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, difficult)

        writer.save(targetFile=filename)
        if self.drawResultImg:
            self._drawResultImage(imagePath,shapes,image)
        return

    def saveYoloFormat(self, filename, shapes, imagePath, imageData, classList,
                       lineColor=None, fillColor=None, databaseSrc=None):
        imgFolderPath = os.path.dirname(imagePath)
        imgFolderName = os.path.split(imgFolderPath)[-1]
        imgFileName = os.path.basename(imagePath)
        # imgFileNameWithoutExt = os.path.splitext(imgFileName)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        image = QImage()
        image.load(imagePath)
        imageShape = [image.height(), image.width(),
                      1 if image.isGrayscale() else 3]
        writer = YOLOWriter(imgFolderName, imgFileName,
                            imageShape, localImgPath=imagePath)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bndbox = LabelFile.convertPoints2BndBox(points)
            writer.addBndBox(bndbox[0], bndbox[1], bndbox[2], bndbox[3], label, difficult)

        writer.save(targetFile=filename, classList=classList)
        if self.drawResultImg:
            self._drawResultImage(imagePath,shapes,image)
        return

    def toggleVerify(self):
        self.verified = not self.verified

    ''' ttf is disable
    def load(self, filename):
        import json
        with open(filename, 'rb') as f:
                data = json.load(f)
                imagePath = data['imagePath']
                imageData = b64decode(data['imageData'])
                lineColor = data['lineColor']
                fillColor = data['fillColor']
                shapes = ((s['label'], s['points'], s['line_color'], s['fill_color'])\
                        for s in data['shapes'])
                # Only replace data after everything is loaded.
                self.shapes = shapes
                self.imagePath = imagePath
                self.imageData = imageData
                self.lineColor = lineColor
                self.fillColor = fillColor

    def save(self, filename, shapes, imagePath, imageData, lineColor=None, fillColor=None):
        import json
        with open(filename, 'wb') as f:
                json.dump(dict(
                    shapes=shapes,
                    lineColor=lineColor, fillColor=fillColor,
                    imagePath=imagePath,
                    imageData=b64encode(imageData)),
                    f, ensure_ascii=True, indent=2)
    '''

    @staticmethod
    def isLabelFile(filename):
        fileSuffix = os.path.splitext(filename)[1].lower()
        return fileSuffix == LabelFile.suffix

    @staticmethod
    def convertPoints2BndBox(points):
        xmin = float('inf')
        ymin = float('inf')
        xmax = float('-inf')
        ymax = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            xmin = min(x, xmin)
            ymin = min(y, ymin)
            xmax = max(x, xmax)
            ymax = max(y, ymax)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if xmin < 1:
            xmin = 1

        if ymin < 1:
            ymin = 1

        return (int(xmin), int(ymin), int(xmax), int(ymax))
