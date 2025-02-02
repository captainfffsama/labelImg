import base64
from collections import defaultdict
import xml.etree.ElementTree as ET
import os
import traceback

from PyQt5.QtWidgets import QWidget, QDialog
from .ui.ui_AutoDetDialog import Ui_AutoDetCfgDialog
from PyQt5.QtCore import QThread, pyqtSignal, QByteArray
from PyQt5.QtGui import QImage
import grpc
from .proto import dldetection_pb2
from .proto import dldetection_pb2_grpc



class AutoDetThread(QThread):
    trigger = pyqtSignal(str, int)

    def __init__(self,
                 img_path,
                 save_dir,
                 host,
                 cls_thr,
                 rpc_flag,
                 parent=None):
        super(AutoDetThread, self).__init__(parent)
        self._img_path = img_path
        self._host = host
        self._cls_thr = cls_thr
        self._save_dir = save_dir
        self._rpc_flag = rpc_flag

    def _respo2dict(self, response):
        result = defaultdict(list)
        for i in response.results:
            if self._cls_thr:
                if i.classid not in self._cls_thr:
                    continue
                if i.score < float(self._cls_thr[i.classid]):
                    continue
            result[i.classid].append(
                (i.score, i.rect.x, i.rect.y, i.rect.w, i.rect.h))
        return result

    def run(self):
        error_info=None
        try:
            with grpc.insecure_channel(self._host) as channel:
                stub = dldetection_pb2_grpc.AiServiceStub(channel)
                img_file = open(self._img_path, 'rb')  # 二进制打开图片文件
                img_b64encode = base64.b64encode(img_file.read())  # base64编码
                img_file.close()  # 文件关闭
                req = dldetection_pb2.DlRequest()
                req.imdata = img_b64encode
                req.type = int(self._rpc_flag)
                response = stub.DlDetection(req)
                result_dict = self._respo2dict(response)
                img = QImage()
                img.loadFromData(QByteArray.fromBase64(img_b64encode))
                if result_dict:
                    dump2xml(self._img_path, self._save_dir, img, result_dict)
                    self.trigger.emit(self._img_path, 1)
                    print("{} have generated xml".format(self._img_path))
                    print("detect result is:", result_dict)
                else:
                    self.trigger.emit(self._img_path, 2)
        except Exception as e:
            print("{} have error:{}".format(self._img_path, e))
            print(traceback.format_exc(limit=-1))
            self.trigger.emit(self._img_path, 0)

    def __del__(self):
        self.wait()

def dump2xml(img_path: str, save_dir: str, img: QImage, obj_info):
    img_name, img_ext = os.path.basename(img_path).split('.')
    out_path = os.path.join(save_dir, img_name + ".xml")
    root = ET.Element('annotation')
    folder = ET.SubElement(root, 'folder')
    folder.text = save_dir
    filename = ET.SubElement(root, 'filename')
    filename.text = img_name + "." + img_ext
    path = ET.SubElement(root, 'path')
    path.text = os.path.join(save_dir, img_name + "." + img_ext)
    size = ET.SubElement(root, 'size')
    width = ET.SubElement(size, 'width')
    height = ET.SubElement(size, 'height')
    depth = ET.SubElement(size, 'depth')
    width.text = str(img.width())
    height.text = str(img.height())
    depth.text = str(1 if img.isGrayscale() else 3)

    for obj_name, bbox in obj_info.items():
        for box in bbox:
            object_root = ET.SubElement(root, 'object')
            name = ET.SubElement(object_root, 'name')
            name.text = obj_name
            pose = ET.SubElement(object_root, 'pose')
            pose.text = "Unspecified"
            trunc = ET.SubElement(object_root, 'truncated')
            trunc.text = "0"
            diff = ET.SubElement(object_root, 'difficult')
            diff.text = "0"
            bndbox = ET.SubElement(object_root, 'bndbox')

            s, x, y, w, h = box
            xmin = ET.SubElement(bndbox, 'xmin')
            xmin.text = str(int(x))
            ymin = ET.SubElement(bndbox, 'ymin')
            ymin.text = str(int(y))
            xmax = ET.SubElement(bndbox, 'xmax')
            xmax.text = str(int(x + w))
            ymax = ET.SubElement(bndbox, 'ymax')
            ymax.text = str(int(y + h))
    indent(root)
    tree = ET.ElementTree(root)
    tree.write(out_path)


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level + 1)
        if not e.tail or not e.tail.strip():
            e.tail = i
    if level and (not elem.tail or not elem.tail.strip()):
        elem.tail = i
    return elem


class AutoDetCfgDialog(QDialog):

    def __init__(self, parent=None, previous_cfg=None):
        super().__init__(parent)
        self.ui = Ui_AutoDetCfgDialog()
        self.ui.setupUi(self)

        self._cfg ={}
        self.class_thr={}
        if previous_cfg:
            self.ui.IPLineEdit.setText(previous_cfg["autoDet_host"])
            self.ui.portSpinBox.setValue(int(previous_cfg["autoDet_port"]))
            self.ui.thrDoubleSpinBox.setValue(
                float(previous_cfg['autoDet_default_thr']))
            self.ui.flagSpinBox.setValue(int(previous_cfg['autoDet_rpc_flag']))
            print(previous_cfg['autoDet_class_thr'])
            self.ui.detClassLineEdit.setText(
                previous_cfg['autoDet_class_thr'])

    def _thrcfg2str(self, cfg_dict: dict):
        line_list = [k + "=" + str(v) for k, v in cfg_dict.items()]
        return ";".join(line_list)

    def _deal_classes_info(self, classes_info: str, dthr):
        classes_info = classes_info.replace("；", ";").replace("，", ",").strip()
        semicolon_list = classes_info.split(";")
        result = {}
        for i in semicolon_list:
            s = dthr
            if not i:
                continue
            c_t = i.split("=")
            if len(c_t) == 2 and c_t[-1]:
                s = c_t[-1]
            for j in c_t[0].split(","):
                if j:
                    result[j] = s
        return result

    def accept(self):
        self._cfg["autoDet_host"] = self.ui.IPLineEdit.text()
        self._cfg["autoDet_port"] = self.ui.portSpinBox.text()
        self._cfg['autoDet_default_thr'] = self.ui.thrDoubleSpinBox.text()
        self._cfg['autoDet_class_thr'] = self.ui.detClassLineEdit.text(
        ).replace("；", ";").replace("，", ",").strip()
        self._cfg['autoDet_rpc_flag'] = (self.ui.flagSpinBox.text())
        self.class_thr = self._deal_classes_info(
            self._cfg['autoDet_class_thr'], self._cfg['autoDet_default_thr'])
        super().accept()

    def reject(self):
        super().reject()

    def _getCfg(self) -> dict:
        return self._cfg

    @classmethod
    def getAutoCfg(cls, parent=None, previous_cfg=None):
        dialog = cls(parent, previous_cfg)
        a = dialog.exec()
        # if a== QDialog.Accepted:
        # elif a==QDialog.rejected:
        # else:
        return dialog._getCfg(),dialog.class_thr


if __name__ == '__main__':
    from PyQt5 import QtWidgets
    import sys
    app = QtWidgets.QApplication(sys.argv)
    a = AutoDetCfgDialog.getAutoCfg()
    print(a)
    # base_w=AutoDetCfgDialog()
    # base_w.show()
    # sys.exit(app.exec_())