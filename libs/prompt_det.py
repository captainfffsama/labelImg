import base64
from collections import defaultdict
import xml.etree.ElementTree as ET
import os

from PyQt5.QtWidgets import QWidget, QDialog
from .ui.ui_PromptDetDialog import Ui_PromptDetDialog
from PyQt5.QtCore import QThread, pyqtSignal, QByteArray
from PyQt5.QtGui import QImage
import grpc
from .proto import dldetection_pb2
from .proto.dldetection_pb2_grpc import AiServiceStub


class PromptDetThread(QThread):
    trigger = pyqtSignal(str, int)

    def __init__(self,
                 img_path,
                 save_dir,
                 host,
                 box_thr: float,
                 text_thr: float,
                 prompt_thr: dict,
                 new_cls_dict: dict,
                 parent=None):
        super(PromptDetThread, self).__init__(parent)
        self._img_path = img_path
        self._host = host
        self._cls_thr = prompt_thr
        self._new_cls = new_cls_dict
        self._save_dir = save_dir
        self._box_thr = box_thr
        self._text_thr = text_thr

    def _respo2dict(self, response):
        result = defaultdict(list)
        for i in response.results:
            if self._cls_thr:
                if i.classid not in self._cls_thr:
                    continue
                if i.score < float(self._cls_thr[i.classid]):
                    continue
            result[self._new_cls.get(i.classid, i.classid)].append(
                (i.score, i.rect.x, i.rect.y, i.rect.w, i.rect.h))
        return result

    def run(self):
        try:
            with grpc.insecure_channel(self._host) as channel:
                stub = AiServiceStub(channel)
                img_file = open(self._img_path, 'rb')  # 二进制打开图片文件
                img_b64encode = base64.b64encode(img_file.read())  # base64编码
                img_file.close()  # 文件关闭
                req = dldetection_pb2.ZeroShotRequest()
                req.prompt = ";".join(self._cls_thr.keys())
                req.imdata = img_b64encode
                req.boxThr = self._box_thr
                req.textThr = self._text_thr
                response = stub.ZeroShotDet(req)
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
            self.trigger.emit(self._img_path, 0)


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


class PromptDetCfgDialog(QDialog):

    def __init__(self, parent=None, previous_cfg=None):
        super().__init__(parent)
        self.ui = Ui_PromptDetDialog()
        self.ui.setupUi(self)

        self._cfg = {}

        if previous_cfg:
            self.ui.IPLineEdit.setText(previous_cfg["promptdet_host"])
            self.ui.portSpinBox.setValue(int(previous_cfg["promptdet_port"]))
            self.ui.thrDoubleSpinBox.setValue(
                float(previous_cfg["promptdet_dthr"]))
            self.ui.boxThrDoubleSpinBox.setValue(
                float(previous_cfg["promptdet_boxthr"]))
            self.ui.textThrDoubleSpinBox.setValue(
                float(previous_cfg["promptdet_textthr"]))
            self.ui.promptLineEdit.setText(
                self._thrcfg2str(previous_cfg["promptdet_promptdict"]))
            self.ui.classLineEdit.setText(
                self._thrcfg2str(previous_cfg['promptdet_class_dict']))

    def _thrcfg2str(self, cfg_dict: dict):
        line_list = [k + "=" + str(v) for k, v in cfg_dict.items()]
        return ";".join(line_list)

    def _str2thrdict(self, ss: str, default_v=None):
        ss = ss.replace("；", ";").replace("，", ",").strip()
        semicolon_list = ss.split(";")
        result = {}
        for i in semicolon_list:
            if not i:
                continue
            s = default_v
            c_t = i.split("=")
            if len(c_t) == 2 and c_t[-1]:
                s = c_t[-1]
            if s is not None:
                result[c_t[0]] = s
        return result

    def accept(self):
        self._cfg["promptdet_host"] = self.ui.IPLineEdit.text()
        self._cfg["promptdet_port"] = self.ui.portSpinBox.text()
        self._cfg["promptdet_dthr"] = self.ui.thrDoubleSpinBox.text()
        self._cfg["promptdet_boxthr"]=self.ui.boxThrDoubleSpinBox.text()
        self._cfg["promptdet_textthr"]=self.ui.textThrDoubleSpinBox.text()
        prompt_info = self.ui.promptLineEdit.text()
        new_class_str = self.ui.classLineEdit.text()
        print(prompt_info)
        self._cfg["promptdet_promptdict"] = self._str2thrdict(
            prompt_info, float(self._cfg["promptdet_dthr"]))
        self._cfg['promptdet_class_dict'] = self._str2thrdict(
            new_class_str, None)
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
    a = PromptDetCfgDialog.getAutoCfg()
    print(a)
    # base_w=AutoDetCfgDialog()
    # base_w.show()
    # sys.exit(app.exec_())