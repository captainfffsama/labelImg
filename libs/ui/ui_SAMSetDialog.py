# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SAMSetDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SAMModeDialog(object):
    def setupUi(self, SAMModeDialog):
        SAMModeDialog.setObjectName("SAMModeDialog")
        SAMModeDialog.resize(311, 89)
        self.gridLayout = QtWidgets.QGridLayout(SAMModeDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(SAMModeDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.IPlineEdit = QtWidgets.QLineEdit(SAMModeDialog)
        self.IPlineEdit.setObjectName("IPlineEdit")
        self.horizontalLayout.addWidget(self.IPlineEdit)
        self.label_2 = QtWidgets.QLabel(SAMModeDialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.portSpinBox = QtWidgets.QSpinBox(SAMModeDialog)
        self.portSpinBox.setMaximum(99999)
        self.portSpinBox.setProperty("value", 52018)
        self.portSpinBox.setObjectName("portSpinBox")
        self.horizontalLayout.addWidget(self.portSpinBox)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(SAMModeDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(SAMModeDialog)
        self.buttonBox.accepted.connect(SAMModeDialog.accept)
        self.buttonBox.rejected.connect(SAMModeDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SAMModeDialog)

    def retranslateUi(self, SAMModeDialog):
        _translate = QtCore.QCoreApplication.translate
        SAMModeDialog.setWindowTitle(_translate("SAMModeDialog", "SAM 看一看"))
        self.label.setText(_translate("SAMModeDialog", "IP:"))
        self.IPlineEdit.setInputMask(_translate("SAMModeDialog", "000.000.000.000"))
        self.IPlineEdit.setText(_translate("SAMModeDialog", "192.168.0.98"))
        self.label_2.setText(_translate("SAMModeDialog", "端口:"))