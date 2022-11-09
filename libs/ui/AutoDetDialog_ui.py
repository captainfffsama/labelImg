# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/AutoDetDialog.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AutoDetCfgDialog(object):
    def setupUi(self, AutoDetCfgDialog):
        AutoDetCfgDialog.setObjectName("AutoDetCfgDialog")
        AutoDetCfgDialog.resize(388, 150)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AutoDetCfgDialog.sizePolicy().hasHeightForWidth())
        AutoDetCfgDialog.setSizePolicy(sizePolicy)
        AutoDetCfgDialog.setAccessibleName("")
        self.gridLayout = QtWidgets.QGridLayout(AutoDetCfgDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.IPLabel = QtWidgets.QLabel(AutoDetCfgDialog)
        self.IPLabel.setObjectName("IPLabel")
        self.horizontalLayout.addWidget(self.IPLabel)
        self.IPLineEdit = QtWidgets.QLineEdit(AutoDetCfgDialog)
        self.IPLineEdit.setInputMethodHints(QtCore.Qt.ImhNone)
        self.IPLineEdit.setObjectName("IPLineEdit")
        self.horizontalLayout.addWidget(self.IPLineEdit)
        self.portLabel = QtWidgets.QLabel(AutoDetCfgDialog)
        self.portLabel.setObjectName("portLabel")
        self.horizontalLayout.addWidget(self.portLabel)
        self.portSpinBox = QtWidgets.QSpinBox(AutoDetCfgDialog)
        self.portSpinBox.setMinimumSize(QtCore.QSize(70, 0))
        self.portSpinBox.setMaximum(99999)
        self.portSpinBox.setSingleStep(1)
        self.portSpinBox.setProperty("value", 52007)
        self.portSpinBox.setObjectName("portSpinBox")
        self.horizontalLayout.addWidget(self.portSpinBox)
        self.thrLabel = QtWidgets.QLabel(AutoDetCfgDialog)
        self.thrLabel.setObjectName("thrLabel")
        self.horizontalLayout.addWidget(self.thrLabel)
        self.thrDoubleSpinBox = QtWidgets.QDoubleSpinBox(AutoDetCfgDialog)
        self.thrDoubleSpinBox.setMinimum(0.0)
        self.thrDoubleSpinBox.setMaximum(1.0)
        self.thrDoubleSpinBox.setSingleStep(0.05)
        self.thrDoubleSpinBox.setProperty("value", 0.3)
        self.thrDoubleSpinBox.setObjectName("thrDoubleSpinBox")
        self.horizontalLayout.addWidget(self.thrDoubleSpinBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.detClassLabel = QtWidgets.QLabel(AutoDetCfgDialog)
        self.detClassLabel.setObjectName("detClassLabel")
        self.verticalLayout.addWidget(self.detClassLabel)
        self.detClassLineEdit = QtWidgets.QLineEdit(AutoDetCfgDialog)
        self.detClassLineEdit.setObjectName("detClassLineEdit")
        self.verticalLayout.addWidget(self.detClassLineEdit)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(AutoDetCfgDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)

        self.retranslateUi(AutoDetCfgDialog)
        self.buttonBox.accepted.connect(AutoDetCfgDialog.accept)
        self.buttonBox.rejected.connect(AutoDetCfgDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AutoDetCfgDialog)

    def retranslateUi(self, AutoDetCfgDialog):
        _translate = QtCore.QCoreApplication.translate
        AutoDetCfgDialog.setWindowTitle(_translate("AutoDetCfgDialog", "自动检测配置"))
        self.IPLabel.setText(_translate("AutoDetCfgDialog", "IP:"))
        self.IPLineEdit.setInputMask(_translate("AutoDetCfgDialog", "000.000.000.000"))
        self.IPLineEdit.setText(_translate("AutoDetCfgDialog", "192.168.0.63"))
        self.portLabel.setText(_translate("AutoDetCfgDialog", "端口:"))
        self.thrLabel.setText(_translate("AutoDetCfgDialog", "默认阈值:"))
        self.detClassLabel.setText(_translate("AutoDetCfgDialog", "待检类型和阈值(;分隔类型,=分隔阈值,默认输出所有类型)"))
        self.detClassLineEdit.setText(_translate("AutoDetCfgDialog", "wcaqm,aqmzc=0.6;xy=0.3;bj_bpmh;"))
