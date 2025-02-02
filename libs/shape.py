#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import numpy as np
import copy
import cv2
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.utils import distance
import sys

DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QColor(255, 255, 255)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QColor(255, 0, 0)
MIN_Y_LABEL = 10


class Shape(object):
    P_SQUARE, P_ROUND = range(2)

    MOVE_VERTEX, NEAR_VERTEX = range(2)

    # The following class variables influence the drawing
    # of _all_ shape objects.
    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    hvertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR
    point_type = P_ROUND
    point_size = 8
    scale = 1.0

    def __init__(self,
                 label=None,
                 line_color=None,
                 difficult=False,
                 paintLabel=False,
                 imgsize=None):
        self.label = label
        self.points = []
        self.fill = False
        self.selected = False
        self.difficult = difficult
        self.paintLabel = paintLabel
        self.imgsize = imgsize

        self._highlightIndex = None
        self._highlightMode = self.NEAR_VERTEX
        self._highlightSettings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }

        self._closed = False

        if line_color is not None:
            # Override the class line_color attribute
            # with an object attribute. Currently this
            # is used for drawing the pending line a different color.
            self.line_color = line_color

    def close(self):
        self._closed = True

    def __repr__(self):
        return "label:{}, \n\
                point:{}, \n\
                paintLabel:{}, \n\
                hightlightIndex:{},\n\
                highlightMode:{},\n\
                highlightSettings:{}".format(self.label, self.points,
                                             self.paintLabel,
                                             self._highlightIndex,
                                             self._highlightMode,
                                             self._highlightSettings)

    def reachMaxPoints(self):
        if len(self.points) >= 4:
            return True
        return False

    def addPoint(self, point):
        if not self.reachMaxPoints():
            self.points.append(point)

    def popPoint(self):
        if self.points:
            return self.points.pop()
        return None

    def isClosed(self):
        return self._closed

    def setOpen(self):
        self._closed = False

    def paint(self, painter):
        if self.points:
            imgsize = self.imgsize
            if imgsize is not None:
                width = int(imgsize[0][0])
                height = int(imgsize[0][1])
                area = math.sqrt(width * height)
                # print(area)
                #1920*1080é˘ç§Ż
                ratio = area / 1440
                pointsize = int(25 * ratio)
            else:
                pointsize = 25
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vrtx_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            #self.drawVertex(vrtx_path, 0)

            for i, p in enumerate(self.points):
                line_path.lineTo(p)
                self.drawVertex(vrtx_path, i)
            if self.isClosed():
                line_path.lineTo(self.points[0])

            painter.drawPath(line_path)
            painter.drawPath(vrtx_path)
            painter.fillPath(vrtx_path, self.vertex_fill_color)

            # Draw text at the top-left
            if self.paintLabel:
                min_x = sys.maxsize
                min_y = sys.maxsize
                for point in self.points:
                    min_x = min(min_x, point.x())
                    min_y = min(min_y, point.y())
                if min_x != sys.maxsize and min_y != sys.maxsize:
                    font = QFont()
                    # font.setPointSize(8)
                    font.setPointSize(pointsize)
                    font.setBold(True)
                    painter.setFont(font)
                    if (self.label == None):
                        self.label = ""
                    if (min_y < MIN_Y_LABEL):
                        min_y += MIN_Y_LABEL
                    painter.drawText(min_x, min_y, self.label)

            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                painter.fillPath(line_path, color)

    def drawVertex(self, path, i):
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.points[i]
        if i == self._highlightIndex:
            size, shape = self._highlightSettings[self._highlightMode]
            d *= size
        if self._highlightIndex is not None:
            self.vertex_fill_color = self.hvertex_fill_color
        else:
            self.vertex_fill_color = Shape.vertex_fill_color
        if shape == self.P_SQUARE:
            path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"

    def nearestVertex(self, point, epsilon):
        for i, p in enumerate(self.points):
            if distance(p - point) <= epsilon:
                return i
        return None

    def containsPoint(self, point):
        return self.makePath().contains(point)

    def makePath(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def boundingRect(self):
        return self.makePath().boundingRect()

    def moveBy(self, offset):
        self.points = [p + offset for p in self.points]

    def moveVertexBy(self, i, offset):
        self.points[i] = self.points[i] + offset

    def highlightVertex(self, i, action):
        self._highlightIndex = i
        self._highlightMode = action

    def highlightClear(self):
        self._highlightIndex = None

    def copy(self):
        shape = Shape("%s" % self.label)
        shape.points = [p for p in self.points]
        shape.fill = self.fill
        shape.selected = self.selected
        shape._closed = self._closed
        if self.line_color != Shape.line_color:
            shape.line_color = self.line_color
        if self.fill_color != Shape.fill_color:
            shape.fill_color = self.fill_color
        shape.difficult = self.difficult
        return shape

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value


class MaskShape(object):
    mask_color = np.array([0, 0, 255, 64], np.uint8)
    boundary_color = np.array([0, 0, 255, 128], np.uint8)

    def __init__(self,
                 label=None,
                 group_id=None,
                 flags=None,
                 description=None):
        self.label = label
        self.group_id = group_id
        self.fill = False
        self.selected = False
        self.flags = flags
        self.description = description
        self.other_data = {}
        self.rgba_mask = None
        self.mask = None
        self.logits = None
        self.scale = 1
        self.box = None

    def setScaleMask(self, scale, mask: np.ndarray):
        self.scale = scale
        self.mask = mask.squeeze()
        self.qimage = self.getQImageMask()
        yt, xt = np.where(self.mask)
        self.box = QRect(min(xt), min(yt),
                         max(xt) - min(xt),
                         max(yt) - min(yt))

    def getQImageMask(self, ):
        if self.mask is None:
            return None
        mask = (self.mask * 255).astype(np.uint8)
        # mask = cv2.resize(mask,
        #                   None,
        #                   fx=1 / self.scale,
        #                   fy=1 / self.scale,
        #                   interpolation=cv2.INTER_NEAREST)
        if self.rgba_mask is not None and mask.shape[0] == self.rgba_mask.shape[
                0] and mask.shape[1] == self.rgba_mask.shape[1]:
            self.rgba_mask[:] = 0
        else:
            self.rgba_mask = np.zeros([mask.shape[0], mask.shape[1], 4],
                                      dtype=np.uint8)
        self.rgba_mask[mask > 128] = self.mask_color
        kernel = np.ones([5, 5], dtype=np.uint8)
        bound = mask - cv2.erode(mask, kernel, iterations=1)
        self.rgba_mask[bound > 128] = self.boundary_color
        qimage = QImage(self.rgba_mask.data, self.rgba_mask.shape[1],
                        self.rgba_mask.shape[0], QImage.Format_RGBA8888)
        # qimage.save("/tmp/mask.png", "PNG",100)
        return qimage

    def paint(self, painter):
        if self.qimage is not None:
            # image = self.pixmap.toImage().copy()
            # img_size = image.size()
            # s = image.bits().asstring(img_size.height() * img_size.width() * image.depth()//8)
            # image = np.frombuffer(s, dtype=np.uint8).reshape([img_size.height(), img_size.width(),image.depth()//8])
            # cv2.imwrite('test.png', image)
            painter.drawImage(QPoint(0, 0), self.qimage)

            ori_pen = painter.pen()
            ori_brush = painter.brush()
            pen = QPen()
            pen.setColor(QColor("pink"))
            pen.setWidth(5)
            # brush = QBrush(color, Qt.SolidPattern)

            # painter.setBrush(brush)
            painter.setPen(pen)
            painter.drawRect(self.box)

            painter.setPen(ori_pen)
            painter.setBrush(ori_brush)

    def copy(self):
        return copy.deepcopy(self)


class PointShape(object):
    scale = 1.0

    def __init__(self, pos=None, label=None):
        self.label = label
        self.pos = pos

    @property
    def x(self):
        return self.pos.x()

    @property
    def y(self):
        return self.pos.y()

    def paint(self, painter):
        if self.label is None or self.pos is None:
            return
        if self.label == 1:
            color = Qt.green
        else:
            color = Qt.red

        ori_pen = painter.pen()
        ori_brush = painter.brush()
        pen = QPen()
        pen.setColor(QColor("white"))
        pen.setWidth(3)
        brush = QBrush(color, Qt.SolidPattern)

        painter.setBrush(brush)
        painter.setPen(pen)

        point_size = 10 / self.scale
        point_size = int(min(point_size, 30))
        point_size = int(max(point_size, 10))
        painter.drawEllipse(
            QRect(self.pos.x() - point_size // 2,
                  self.pos.y() - point_size // 2, point_size, point_size))

        painter.setPen(ori_pen)
        painter.setBrush(ori_brush)
