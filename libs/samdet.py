# -*- coding: utf-8 -*-
'''
@Author: captainfffsama
@Date: 2023-04-24 18:21:59
@LastEditors: captainfffsama tuanzhangsama@outlook.com
@LastEditTime: 2023-07-13 11:57:55
@FilePath: /labelImg/libs/samdet.py
@Description:
'''

from collections import defaultdict
import cv2
import numpy as np

from PyQt5.QtWidgets import QWidget, QDialog
from .ui.ui_SAMSetDialog import Ui_SAMModeDialog
from PyQt5.QtCore import QThread, pyqtSignal, QByteArray, QObject
from PyQt5.QtGui import QImage

from sam_grpc import SAMClient


class SAMWorker(QObject):
    send_message_signal = pyqtSignal(str, int)
    send_mask_signal = pyqtSignal(str,np.ndarray)

    def __init__(self, host, port):
        super().__init__()
        self.client = SAMClient(host, port)
        self.current_img_path = None
        self.current_img_embedding = None
        self.mask_cache = None
        self.img_max_size = 512
        self.img_scale = None
        self.img_ori_hw=None

    def print_thread(self):
        print("worker thread:", QThread.currentThread())

    def reset_img_info(self, img_path) -> bool:
        if self.current_img_path!=img_path:
            try:
                self.mask_cache = None
                self.current_img_path = img_path
                current_img = cv2.imread(img_path,cv2.IMREAD_COLOR|cv2.IMREAD_IGNORE_ORIENTATION)
                self.img_ori_hw=current_img.shape[:2][::-1]
                if max(current_img.shape)>self.img_max_size:
                    self.img_scale=self.img_max_size/max(current_img.shape)
                    current_img=cv2.resize(current_img,None,fx=self.img_scale,fy=self.img_scale)
                else:
                    self.img_scale=1
                with self.client:
                    self.current_img_embedding = self.client.SAMGetImageEmbeddingUseCache(
                        current_img)
                self.send_message_signal.emit("获取图片嵌入成功", 5000)
                return True
            except:
                self.current_img_path = None
                self.current_img_embedding = None
                self.mask_cache = None
                self.send_message_signal.emit("获取图片嵌入失败", 5000)
                return False
        return True

    def _sam_get_mask(self,img_path,points, point_type, use_cache=True):
        try:
            with self.client:
                if use_cache:
                    mask_cache = self.mask_cache
                else:
                    mask_cache = None

                points=points*self.img_scale
                points=points.astype(int)
                masks, scores, logits, self.mask_cache = self.client.SAMPredictUseCache(
                    self.current_img_embedding[-1],
                    points,
                    point_type,
                    mask_input=mask_cache,
                    multimask_output=False)

                print(masks.shape)
                if masks is not None:
                    # cv2.imwrite("mask.png",masks.squeeze()*255)
                    if self.img_scale !=1:
                        m_t=cv2.resize(masks.astype(np.uint8).squeeze()*255,tuple(self.img_ori_hw))
                        m_t[m_t>=128]=255
                        m_t[m_t<128]=0
                        masks=m_t.astype(bool)[None,:,:]
                    self.send_mask_signal.emit(img_path,masks)
                else:
                    self.send_message_signal.emit("SAM失败,可能服务端有问题", 5000)
        except Exception as e:
            self.send_message_signal.emit("SAM失败,可能服务端有问题", 5000)

    def sam_work(self,img_path, points, point_type, use_cache=True):
        if self.current_img_embedding is not None:
            if img_path==self.current_img_path:
                self._sam_get_mask(img_path,points,point_type,use_cache)
                return
        if self.reset_img_info(img_path):
            self._sam_get_mask(img_path,points,point_type,use_cache)



class SAMThread(QThread):

    def __init__(self, host, port) -> None:
        super().__init__()
        self.worker = SAMWorker(host, port)
        self.worker.moveToThread(self)

    def run(self):
        print("worker son thread:", QThread.currentThread())
        self.exec_()

    def __del__(self):
        self.quit()


class SAMModeCfgDialog(QDialog):

    def __init__(self, parent=None, previous_cfg=None):
        super().__init__(parent)
        self.ui = Ui_SAMModeDialog()
        self.ui.setupUi(self)

        self._cfg = {}

        if previous_cfg:
            self.ui.IPlineEdit.setText(previous_cfg["host"])
            self.ui.portSpinBox.setValue(int(previous_cfg["port"]))

    def accept(self):
        self._cfg["host"] = self.ui.IPlineEdit.text()
        self._cfg["port"] = self.ui.portSpinBox.text()
        super().accept()

    def reject(self):
        super().reject()

    def _getCfg(self):
        return self._cfg

    @classmethod
    def getAutoCfg(cls, parent=None, previous_cfg=None):
        dialog = cls(parent, previous_cfg)
        a = dialog.exec()
        # if a== QDialog.Accepted:
        # elif a==QDialog.rejected:
        # else:
        return dialog._getCfg()


if __name__ == '__main__':
    from PyQt5 import QtWidgets
    import sys
    app = QtWidgets.QApplication(sys.argv)
    a = SAMModeCfgDialog.getAutoCfg()
    print(a)
    # base_w=AutoDetCfgDialog()
    # base_w.show()
    # sys.exit(app.exec_())