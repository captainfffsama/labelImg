#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import os.path
import platform
import sys
import subprocess
from functools import partial
from typing import Optional, Set
from pprint import pprint

try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except ImportError:
    # needed for py3+qt4
    # Ref:
    # http://pyqt.sourceforge.net/Docs/PyQt4/incompatible_apis.html
    # http://stackoverflow.com/questions/21217399/pyqt4-qtcore-qvariant-object-instead-of-a-string
    if sys.version_info.major >= 3:
        import sip

        sip.setapi('QVariant', 2)
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

from libs.resources import *
from libs.constants import *
from libs.utils import *
from libs.settings import Settings
from libs.shape import Shape, DEFAULT_LINE_COLOR, DEFAULT_FILL_COLOR
from libs.stringBundle import StringBundle
from libs.canvas import Canvas
from libs.zoomWidget import ZoomWidget
from libs.labelDialog import LabelDialog
from libs.colorDialog import ColorDialog
from libs.labelFile import LabelFile, LabelFileError
from libs.toolBar import ToolBar
from libs.pascal_voc_io import PascalVocReader
from libs.pascal_voc_io import XML_EXT
from libs.yolo_io import YoloReader
from libs.yolo_io import TXT_EXT
from libs.ustr import ustr
from libs.hashableQListWidgetItem import HashableQListWidgetItem
from libs.autodet import AutoDetThread, AutoDetCfgDialog
from libs.prompt_det import PromptDetCfgDialog, PromptDetThread
from libs.samdet import SAMModeCfgDialog, SAMThread

__appname__ = 'labelImg'


class FilePathValidator(QValidator):

    def __init__(self, string_model: QStringListModel):
        self.model = string_model
        super().__init__()

    def validate(self, s: str, pos):
        if s in self.model.stringList():
            return QValidator.State.Acceptable, s, pos
        else:
            return QValidator.State.Intermediate, s, pos


class WindowMixin(object):

    def menu(self, title, actions=None):
        menu = self.menuBar().addMenu(title)
        if actions:
            addActions(menu, actions)
        return menu

    def toolbar(self, title, actions=None):
        toolbar = ToolBar(title)
        toolbar.setObjectName(u'%sToolBar' % title)
        # toolbar.setOrientation(Qt.Vertical)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        if actions:
            addActions(toolbar, actions)
        self.addToolBar(Qt.LeftToolBarArea, toolbar)
        return toolbar


class UtilsFuncMixin(object):
    r"""这个类专门用来放一些和类方法不是强相关,比较通用,没有什么成员依赖的函数
    """
    preShortCutModeSetting: str = ''

    def str2dict(self, input: str) -> Optional[dict]:
        r"""将类似 a=xy,b=cat这种字符串转为字典 a,b为key,xy,cat为value
            这里遇到awsdAWSD 抛出异常,主要服务于setShortCutMode_slot函数
        """
        result = {}
        input = input.replace('，', ',')
        for item in input.split(','):
            k, *_, v = item.split('=')
            if k.isalpha():
                if len(k) != 1:
                    return None
                if k in ('a', 's', 'd', 'w', 'A', 'S', 'D', 'W'):
                    return None
                result[k.upper()] = v
            else:
                return None
        return result

    def getQStringListModelIndex(self, model: QStringListModel,
                                 value: str) -> Optional[QModelIndex]:
        if value in model.stringList():
            return model.index(model.stringList().index(value))
        else:
            return None

class MainWindow(QMainWindow, WindowMixin, UtilsFuncMixin):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self,
                 defaultFilename=None,
                 defaultPrefdefClassFile=None,
                 defaultSaveDir=None):
        super(MainWindow, self).__init__()
        self.setWindowTitle(__appname__)

        self.shortCutModeKeyMap = {
        }  # 用于在shortCutMode中帮助指示哪些快捷键可用,key为 Qt.key,value是标签名
        # 添加是否打开txt
        self.isTxt = False
        # 添加单类别显示
        self.only_show = set([])
        # Load setting in the main thread
        self.txtPath: Optional[str] = None
        self.saveTxtName = '1.txt'
        self.imgPath: Optional[str] = None
        self.isDelete = False

        self.settings = Settings()
        self.settings.load()
        settings = self.settings

        # Load string bundle for i18n
        self.stringBundle = StringBundle.getBundle()
        getStr = lambda strId: self.stringBundle.getString(strId)

        # Save as Pascal voc xml
        self.defaultSaveDir = defaultSaveDir
        self.usingPascalVocFormat = True
        self.usingYoloFormat = False

        # For loading all image under a directory
        self.fileListModel = QStringListModel(self)

        self.dirname = None
        self.labelHist = []  #记录所有标签名称
        self.lastOpenDir = None

        # Whether we need to save or not.
        self.dirty = False

        self._noSelectionSlot = False
        self._beginner = True
        self.screencastViewer = self.getAvailableScreencastViewer()
        self.screencast = "https://youtu.be/p0nR2YsCY_U"

        # Load predefined classes to the list
        self.loadPredefinedClasses(defaultPrefdefClassFile)

        # Main widgets and related state.
        self.labelDialog = LabelDialog(parent=self, listItem=self.labelHist)

        self.itemsToShapes = {}
        self.shapesToItems = {}
        self.prevLabelText = ''

        listLayout = QVBoxLayout()
        listLayout.setContentsMargins(0, 0, 0, 0)

        # Create a widget for using default label
        self.useDefaultLabelCheckbox = QCheckBox(getStr('useDefaultLabel'))
        self.useDefaultLabelCheckbox.setChecked(False)
        self.defaultLabelTextLine = QLineEdit()
        useDefaultLabelQHBoxLayout = QHBoxLayout()
        useDefaultLabelQHBoxLayout.addWidget(self.useDefaultLabelCheckbox)
        useDefaultLabelQHBoxLayout.addWidget(self.defaultLabelTextLine)
        useDefaultLabelContainer = QWidget()
        useDefaultLabelContainer.setLayout(useDefaultLabelQHBoxLayout)

        # Create a widget for edit and diffc button
        self.diffcButton = QCheckBox(getStr('useDifficult'))
        self.diffcButton.setChecked(False)
        self.diffcButton.stateChanged.connect(self.btnstate)
        self.editButton = QToolButton()
        self.editButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        # Add some of widgets to listLayout
        listLayout.addWidget(self.editButton)
        listLayout.addWidget(self.diffcButton)
        listLayout.addWidget(useDefaultLabelContainer)

        # Create and add a widget for showing current label items
        self.labelList = QListWidget()
        labelListContainer = QWidget()
        labelListContainer.setLayout(listLayout)
        self.labelList.itemActivated.connect(self.labelSelectionChanged)
        self.labelList.itemSelectionChanged.connect(self.labelSelectionChanged)
        self.labelList.itemDoubleClicked.connect(self.editLabel)
        # Connect to itemChanged to detect checkbox changes.
        self.labelList.itemChanged.connect(self.labelItemChanged)
        listLayout.addWidget(self.labelList)

        self.dock = QDockWidget(getStr('boxLabelText'), self)
        self.dock.setObjectName(getStr('labels'))
        self.dock.setWidget(labelListContainer)

        self.fileListView = QListView()
        self.fileListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fileListView.setSelectionRectVisible(True)
        self.fileListView.clicked.connect(self.fileSelect_slot)
        self.fileListView.doubleClicked.connect(self.fileSelect_slot)
        self.fileListView.setModel(self.fileListModel)

        self.fileListSearchBox = QComboBox()
        fileListSearchCompleter = QCompleter()
        fileListSearchCompleter.setModel(self.fileListModel)
        fileListSearchCompleter.setFilterMode(QtCore.Qt.MatchContains)
        fileListSearchCompleter.setCompletionMode(QCompleter.PopupCompletion)
        self.fileListSearchBox.setModel(self.fileListModel)
        self.fileListSearchBox.setEditable(True)
        self.fileListSearchBox.setValidator(
            FilePathValidator(self.fileListModel))
        self.fileListSearchBox.setCompleter(fileListSearchCompleter)
        self.fileListSearchBox.currentIndexChanged.connect(
            self.fileSearchActivate_slot)

        filelistLayout = QVBoxLayout()
        filelistLayout.setContentsMargins(0, 0, 0, 0)
        filelistLayout.addWidget(self.fileListSearchBox)
        filelistLayout.addWidget(self.fileListView)

        fileListContainer = QWidget()
        fileListContainer.setLayout(filelistLayout)
        self.filedock = QDockWidget(getStr('fileList'), self)
        self.filedock.setObjectName(getStr('files'))
        self.filedock.setWidget(fileListContainer)

        self.zoomWidget = ZoomWidget()
        self.colorDialog = ColorDialog(parent=self)

        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoomRequest)
        self.canvas.setDrawingShapeToSquare(
            settings.get(SETTING_DRAW_SQUARE, False))

        self.canvas.installEventFilter(self)

        scroll = QScrollArea()
        scroll.setWidget(self.canvas)
        scroll.setWidgetResizable(True)
        self.scrollBars = {
            Qt.Vertical: scroll.verticalScrollBar(),
            Qt.Horizontal: scroll.horizontalScrollBar()
        }
        self.scrollArea = scroll
        self.canvas.scrollRequest.connect(self.scrollRequest)

        self.canvas.newShape.connect(self.newShape)
        self.canvas.shapeMoved.connect(self.setDirty)
        self.canvas.selectionChanged.connect(self.shapeSelectionChanged)
        self.canvas.drawingPolygon.connect(self.toggleDrawingSensitive)
        self.canvas.send_message_signal.connect(self.status)

        self.setCentralWidget(scroll)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.filedock)
        self.filedock.setFeatures(QDockWidget.DockWidgetFloatable)

        self.dockFeatures = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        self.dock.setFeatures(self.dock.features() ^ self.dockFeatures)

        self._cahed_xmlTree = None  # 暂存xml，之前只读写objects的方式会导致其他信息的丢失

        # Actions
        action = partial(newAction, self)
        quit = action(getStr('quit'), self.close, None, 'quit',
                      getStr('quitApp'))

        open = action(getStr('openFile'), self.openFile, 'Ctrl+O', 'open',
                      getStr('openFileDetail'))

        opentxt = action(getStr('openTxt'), self.openTxt, 'Ctrl+T', 'open',
                         getStr('openTxt'))

        auto_detect = action(getStr('autoDet'), self.autoDet, 'Ctrl+D', 'AI',
                             getStr('autoDet'))

        prompt_detect = action(getStr('promptDet'), self.promptDet, 'Ctrl+Q',
                               'cortana', getStr('cortanaDet'))

        opendir = action(getStr('openDir'), self.openDirDialog, 'Ctrl+u',
                         'open', getStr('openDir'))

        changeSavedir = action(getStr('changeSaveDir'),
                               self.changeSavedirDialog, 'Ctrl+r', 'open',
                               getStr('changeSavedAnnotationDir'))

        openAnnotation = action(getStr('openAnnotation'),
                                self.openAnnotationDialog, 'Ctrl+Shift+O',
                                'open', getStr('openAnnotationDetail'))

        openNextImg = action(getStr('nextImg'), self.openNextImg, 'd', 'next',
                             getStr('nextImgDetail'))

        openPrevImg = action(getStr('prevImg'), self.openPrevImg, 'a', 'prev',
                             getStr('prevImgDetail'))

        verify = action(getStr('verifyImg'), self.verifyImg, 'space', 'verify',
                        getStr('verifyImgDetail'))

        save = action(getStr('save'),
                      self.saveFile,
                      'Ctrl+S',
                      'save',
                      getStr('saveDetail'),
                      enabled=False)

        save_format = action('&PascalVOC',
                             self.change_format,
                             'Ctrl+',
                             'format_voc',
                             getStr('changeSaveFormat'),
                             enabled=True)

        saveAs = action(getStr('saveAs'),
                        self.saveFileAs,
                        'Ctrl+Shift+S',
                        'save-as',
                        getStr('saveAsDetail'),
                        enabled=False)

        close = action(getStr('closeCur'), self.closeFile, 'Ctrl+W', 'close',
                       getStr('closeCurDetail'))

        resetAll = action(getStr('resetAll'), self.resetAll, None, 'resetall',
                          getStr('resetAllDetail'))

        color1 = action(getStr('boxLineColor'), self.chooseColor1, 'Ctrl+L',
                        'color_line', getStr('boxLineColorDetail'))

        createMode = action(getStr('crtBox'),
                            self.setCreateMode,
                            'w',
                            'new',
                            getStr('crtBoxDetail'),
                            enabled=False)
        editMode = action('&Edit\nRectBox',
                          self.setEditMode,
                          'Ctrl+J',
                          'edit',
                          u'Move and edit Boxs',
                          enabled=False)

        create = action(getStr('crtBox'),
                        self.createShape,
                        'w',
                        'new',
                        getStr('crtBoxDetail'),
                        enabled=False)
        delete = action(getStr('delBox'),
                        self.deleteSelectedShape,
                        'Delete',
                        'delete',
                        getStr('delBoxDetail'),
                        enabled=False)
        copy = action(getStr('dupBox'),
                      self.copySelectedShape,
                      'Ctrl+c',
                      'copy',
                      getStr('dupBoxDetail'),
                      enabled=False)

        advancedMode = action(getStr('advancedMode'),
                              self.toggleAdvancedMode,
                              'Ctrl+Shift+A',
                              'expert',
                              getStr('advancedModeDetail'),
                              checkable=True)

        hideAll = action('&Hide\nRectBox',
                         partial(self.togglePolygons, False),
                         'Ctrl+H',
                         'hide',
                         getStr('hideAllBoxDetail'),
                         enabled=False)
        showAll = action('&Show\nRectBox',
                         partial(self.togglePolygons, True),
                         'Ctrl+A',
                         'hide',
                         getStr('showAllBoxDetail'),
                         enabled=False)
        onlyShow = action('单一显示模式', self.setOnlyShow)
        resetAutoDetCfg = action("重设自动检测配置", self.setAutoDetCfg)
        resetPromptDetCfg = action("重设全知检测配置", self.setPromptDetCfg,
                                   "Ctrl+Shift+Q")

        help = action(getStr('tutorial'), self.showTutorialDialog, None,
                      'help', getStr('tutorialDetail'))
        showInfo = action(getStr('info'), self.showInfoDialog, None, 'help',
                          getStr('info'))

        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoomWidget)
        self.zoomWidget.setWhatsThis(
            u"Zoom in or out of the image. Also accessible with"
            " %s and %s from the canvas." %
            (fmtShortcut("Ctrl+[-+]"), fmtShortcut("Ctrl+Wheel")))
        self.zoomWidget.setEnabled(False)

        zoomIn = action(getStr('zoomin'),
                        partial(self.addZoom, 10),
                        'Ctrl++',
                        'zoom-in',
                        getStr('zoominDetail'),
                        enabled=False)
        zoomOut = action(getStr('zoomout'),
                         partial(self.addZoom, -10),
                         'Ctrl+-',
                         'zoom-out',
                         getStr('zoomoutDetail'),
                         enabled=False)
        zoomOrg = action(getStr('originalsize'),
                         partial(self.setZoom, 100),
                         'Ctrl+=',
                         'zoom',
                         getStr('originalsizeDetail'),
                         enabled=False)
        fitWindow = action(getStr('fitWin'),
                           self.setFitWindow,
                           'Ctrl+F',
                           'fit-window',
                           getStr('fitWinDetail'),
                           checkable=True,
                           enabled=False)
        fitWidth = action(getStr('fitWidth'),
                          self.setFitWidth,
                          'Ctrl+Shift+F',
                          'fit-width',
                          getStr('fitWidthDetail'),
                          checkable=True,
                          enabled=False)
        # Group zoom controls into a list for easier toggling.
        zoomActions = (self.zoomWidget, zoomIn, zoomOut, zoomOrg, fitWindow,
                       fitWidth)
        self.zoomMode = self.MANUAL_ZOOM
        self.scalers = {
            self.FIT_WINDOW:
            self.scaleFitWindow,
            self.FIT_WIDTH:
            self.scaleFitWidth,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM:
            lambda: 1,
        }

        edit = action(getStr('editLabel'),
                      self.editLabel,
                      'Ctrl+E',
                      'edit',
                      getStr('editLabelDetail'),
                      enabled=False)
        self.editButton.setDefaultAction(edit)

        shapeLineColor = action(getStr('shapeLineColor'),
                                self.chshapeLineColor,
                                icon='color_line',
                                tip=getStr('shapeLineColorDetail'),
                                enabled=False)
        shapeFillColor = action(getStr('shapeFillColor'),
                                self.chshapeFillColor,
                                icon='color',
                                tip=getStr('shapeFillColorDetail'),
                                enabled=False)

        labels = self.dock.toggleViewAction()
        labels.setText(getStr('showHide'))
        labels.setShortcut('Ctrl+Shift+L')

        # Label list context menu.
        labelMenu = QMenu()
        addActions(labelMenu, (edit, delete))
        self.labelList.setContextMenuPolicy(Qt.CustomContextMenu)
        self.labelList.customContextMenuRequested.connect(
            self.popLabelListMenu)

        # Draw squares/rectangles
        self.drawSquaresOption = QAction('Draw Squares', self)
        self.drawSquaresOption.setShortcut('Ctrl+Shift+R')
        self.drawSquaresOption.setCheckable(True)
        self.drawSquaresOption.setChecked(
            settings.get(SETTING_DRAW_SQUARE, False))
        self.drawSquaresOption.triggered.connect(self.toogleDrawSquare)

        # Store actions for further handling.
        self.actions = struct(save=save,
                              save_format=save_format,
                              saveAs=saveAs,
                              open=open,
                              close=close,
                              resetAll=resetAll,
                              lineColor=color1,
                              create=create,
                              delete=delete,
                              edit=edit,
                              copy=copy,
                              createMode=createMode,
                              editMode=editMode,
                              advancedMode=advancedMode,
                              shapeLineColor=shapeLineColor,
                              shapeFillColor=shapeFillColor,
                              zoom=zoom,
                              zoomIn=zoomIn,
                              zoomOut=zoomOut,
                              zoomOrg=zoomOrg,
                              fitWindow=fitWindow,
                              fitWidth=fitWidth,
                              zoomActions=zoomActions,
                              fileMenuActions=(open, opentxt, opendir, save,
                                               saveAs, close, resetAll, quit),
                              beginner=(),
                              advanced=(),
                              editMenu=(edit, copy, delete, None, color1,
                                        self.drawSquaresOption),
                              beginnerContext=(create, edit, copy, delete),
                              advancedContext=(createMode, editMode, edit,
                                               copy, onlyShow, delete,
                                               shapeLineColor, shapeFillColor),
                              onLoadActive=(close, create, createMode,
                                            editMode),
                              onShapesPresent=(saveAs, hideAll, showAll))

        self.menus = struct(file=self.menu('&File'),
                            edit=self.menu('&Edit'),
                            view=self.menu('&View'),
                            help=self.menu('&Help'),
                            recentFiles=QMenu('Open &Recent'),
                            labelList=labelMenu)

        # Auto saving : Enable auto saving if pressing next
        self.autoSaving = QAction(getStr('autoSaveMode'), self)
        self.autoSaving.setCheckable(True)
        self.autoSaving.setChecked(settings.get(SETTING_AUTO_SAVE, False))
        # Force Auto saving: 自动保存时不进行obj是否被修改过的检查，强制保存
        # 进行检查会导致标注新图时， 不存在任何obj的图片会直接跳过，不产生xml
        self.forceAutoSaving = QAction('&强制自动保存', self)
        self.forceAutoSaving.setCheckable(True)
        self.forceAutoSaving.setChecked(
            settings.get(SETTING_AUTO_SAVE_FORCE, False))
        # Sync single class mode from PR#106
        self.singleClassMode = QAction(getStr('singleClsMode'), self)
        self.singleClassMode.setShortcut("Ctrl+Shift+S")
        self.singleClassMode.setCheckable(True)
        self.singleClassMode.setChecked(
            settings.get(SETTING_SINGLE_CLASS, False))
        self.lastLabel: Optional[str] = None
        # 添加对指定类添加快捷键功能
        self.shortCutMode = QAction('shortCutMode', self)
        self.shortCutMode.setCheckable(True)
        self.shortCutMode.setChecked(
            settings.get(SETTING_SHORT_CUT_MODE, False))
        self.shortCutMode.triggered.connect(self.setShortCutMode_slot)

        # 添加生成渲染图的功能
        self.generateResultImg = QAction('generateResultImg', self)
        self.generateResultImg.setCheckable(True)
        self.generateResultImg.setChecked(False)

        # Add option to enable/disable labels being displayed at the top of bounding boxes
        self.displayLabelOption = QAction(getStr('displayLabel'), self)
        self.displayLabelOption.setShortcut("Ctrl+Shift+P")
        self.displayLabelOption.setCheckable(True)
        self.displayLabelOption.setChecked(
            settings.get(SETTING_PAINT_LABEL, False))
        self.displayLabelOption.triggered.connect(self.togglePaintLabelsOption)

        self.SAMMode = QAction("SAM模式", self)
        self.SAMMode.setCheckable(True)
        self.SAMMode.setChecked(settings.get(SETTING_SAM_MODE, False))
        self.SAMMode.changed.connect(self.setSAMMode_slot)

        self.currentSAMQThread = None
        self.sam_cfg = {}

        addActions(self.menus.file,
                   (open, opentxt, opendir, changeSavedir, openAnnotation,
                    self.menus.recentFiles, save, save_format, saveAs, close,
                    resetAll, resetAutoDetCfg, resetPromptDetCfg, quit))
        addActions(self.menus.help, (help, showInfo))
        addActions(self.menus.view,
                   (self.autoSaving, self.forceAutoSaving, onlyShow,
                    self.SAMMode, self.singleClassMode, self.shortCutMode,
                    self.generateResultImg, self.displayLabelOption, labels,
                    advancedMode, None, hideAll, showAll, None, zoomIn,
                    zoomOut, zoomOrg, None, fitWindow, fitWidth))

        self.menus.file.aboutToShow.connect(self.updateFileMenu)

        # Custom context menu for the canvas widget:
        addActions(self.canvas.menus[0], self.actions.beginnerContext)
        addActions(self.canvas.menus[1],
                   (action('&Copy here', self.copyShape),
                    action('&Move here', self.moveShape)))

        self.tools = self.toolbar('Tools')
        self.actions.beginner = (open, opentxt, opendir, changeSavedir,
                                 openNextImg, openPrevImg, verify, save,
                                 save_format, auto_detect, prompt_detect, None,
                                 create, copy, delete, None, zoomIn, zoom,
                                 zoomOut, fitWindow, fitWidth)

        self.actions.advanced = (open, opentxt, opendir, changeSavedir,
                                 openNextImg, openPrevImg, save, save_format,
                                 auto_detect, prompt_detect, None, createMode,
                                 editMode, None, hideAll, showAll)

        self.statusBar().showMessage('%s started.' % __appname__)
        self.statusBar().show()

        # Application state.
        self.image = QImage()
        self.filePath = ustr(defaultFilename)
        self.recentFiles = []
        self.maxRecent = 7
        self.lineColor = None
        self.fillColor = None
        self.zoom_level = 100
        self.fit_window = False
        # Add Chris
        self.difficult = False
        self.rpc_host = None
        self.autodet_previous_cfg = {}

        #prompt det member
        self.prompt_det_rpc_host = None
        self.prompt_det_previous_cfg = {}

        ## Fix the compatible issue for qt4 and qt5. Convert the QStringList to python list
        if settings.get(SETTING_RECENT_FILES):
            if have_qstring():
                recentFileQStringList = settings.get(SETTING_RECENT_FILES)
                self.recentFiles = [ustr(i) for i in recentFileQStringList]
            else:
                self.recentFiles = recentFileQStringList = settings.get(
                    SETTING_RECENT_FILES)

        size = settings.get(SETTING_WIN_SIZE, QSize(600, 500))
        position = QPoint(0, 0)
        saved_position = settings.get(SETTING_WIN_POSE, position)
        # Fix the multiple monitors issue
        for i in range(QApplication.desktop().screenCount()):
            if QApplication.desktop().availableGeometry(i).contains(
                    saved_position):
                position = saved_position
                break
        self.resize(size)
        self.move(position)
        saveDir = ustr(settings.get(SETTING_SAVE_DIR, None))
        self.lastOpenDir = ustr(settings.get(SETTING_LAST_OPEN_DIR, None))
        if self.defaultSaveDir is None and saveDir is not None and os.path.exists(
                saveDir):
            self.defaultSaveDir = saveDir
            self.statusBar().showMessage(
                '%s started. Annotation will be saved to %s' %
                (__appname__, self.defaultSaveDir))
            self.statusBar().show()

        self.restoreState(settings.get(SETTING_WIN_STATE, QByteArray()))
        Shape.line_color = self.lineColor = QColor(
            settings.get(SETTING_LINE_COLOR, DEFAULT_LINE_COLOR))
        Shape.fill_color = self.fillColor = QColor(
            settings.get(SETTING_FILL_COLOR, DEFAULT_FILL_COLOR))
        self.canvas.setDrawingColor(self.lineColor)
        # Add chris
        Shape.difficult = self.difficult

        def xbool(x):
            if isinstance(x, QVariant):
                return x.toBool()
            return bool(x)

        if xbool(settings.get(SETTING_ADVANCE_MODE, False)):
            self.actions.advancedMode.setChecked(True)
            self.toggleAdvancedMode()

        # Populate the File menu dynamically.
        self.updateFileMenu()

        # Since loading the file may take some time, make sure it runs in the background.
        if self.filePath and os.path.isdir(self.filePath):
            self.queueEvent(partial(self.importDirImages, self.filePath or ""))
        elif self.filePath:
            self.queueEvent(partial(self.loadFile, self.filePath or ""))

        # Callbacks:
        self.zoomWidget.valueChanged.connect(self.paintCanvas)

        self.populateModeActions()

        # Display cursor coordinates at the right of status bar
        self.labelCoordinates = QLabel('')
        self.statusBar().addPermanentWidget(self.labelCoordinates)

        # Open Dir if deafult file
        if self.filePath and os.path.isdir(self.filePath):
            self.openDirDialog(dirpath=self.filePath, silent=True)

    def setSAMModel_slot(self):
        if self.SAMMode.isChecked():
            pass

    def saveErrImg(self):
        if not self.imgPath:
            print('self.imgPath is empty')
            return
        if not self.txtPath:
            special_txt_path = os.path.join(os.path.dirname(self.filePath),
                                            'special_txt')
            if not os.path.exists(special_txt_path):
                os.makedirs(special_txt_path)
            self.txtPath = os.path.join(special_txt_path,
                                        os.path.basename(self.filePath))

        if self.txtPath is not None:
            absTxtPath = os.path.dirname(self.txtPath)
            saveTxtPath = os.path.join(absTxtPath, self.saveTxtName)
            #NOTE: 这里txtData可能是有None的
            txtData: Set[str] = set()
            if os.path.exists(saveTxtPath):
                r = open(saveTxtPath, 'r')
                txtData = set(r.readlines())
                r.close()
            if self.isDelete:
                if self.imgPath in txtData:
                    txtData.discard(self.imgPath)
                    self.status('{} 已从 {} 删除!'.format(
                        os.path.basename(self.imgPath),
                        os.path.basename(saveTxtPath)))
                else:
                    self.status('{} 不在 {} 中!'.format(
                        os.path.basename(self.imgPath),
                        os.path.basename(saveTxtPath)))
                    return
            else:
                if self.imgPath not in txtData:
                    txtData.add(self.imgPath)
                    self.status('{} 已记录到 {}!'.format(
                        os.path.basename(self.imgPath),
                        os.path.basename(saveTxtPath)))
                else:
                    self.status('{} 已在 {} 中!'.format(
                        os.path.basename(self.imgPath),
                        os.path.basename(saveTxtPath)))
                    return
            w = open(saveTxtPath, 'w')
            w.writelines(txtData)
            w.close()

    def keyReleaseEvent(self, event):
        self.isDelete = False
        # 这段代码要改表驱动
        if event.key() == Qt.Key_Control:
            self.canvas.setDrawingShapeToSquare(False)
        # 保存质量有问题的图片到以1~9命名的txt中
        if event.key() == Qt.Key_1:
            self.saveTxtName = '1.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_2:
            self.saveTxtName = '2.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_3:
            self.saveTxtName = '3.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_4:
            self.saveTxtName = '4.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_5:
            self.saveTxtName = '5.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_6:
            self.saveTxtName = '6.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_7:
            self.saveTxtName = '7.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_8:
            self.saveTxtName = '8.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_9:
            self.saveTxtName = '9.txt'
            self.saveErrImg()
        elif event.key() == Qt.Key_0:
            self.isDelete = True
            self.saveErrImg()
        else:
            if event.key() in self.shortCutModeKeyMap:
                self.lastLabel = self.shortCutModeKeyMap[event.key()]
                self.create()
                self.createShape()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Control:
            # Draw rectangle if Ctrl is pressed
            # this function has a big bug
            #convert True to False
            self.canvas.setDrawingShapeToSquare(False)

    ## Support Functions ##
    def set_format(self, save_format):
        if save_format == FORMAT_PASCALVOC:
            self.actions.save_format.setText(FORMAT_PASCALVOC)
            self.actions.save_format.setIcon(newIcon("format_voc"))
            self.usingPascalVocFormat = True
            self.usingYoloFormat = False
            LabelFile.suffix = XML_EXT

        elif save_format == FORMAT_YOLO:
            self.actions.save_format.setText(FORMAT_YOLO)
            self.actions.save_format.setIcon(newIcon("format_yolo"))
            self.usingPascalVocFormat = False
            self.usingYoloFormat = True
            LabelFile.suffix = TXT_EXT

    def change_format(self):
        if self.usingPascalVocFormat:
            self.set_format(FORMAT_YOLO)
        elif self.usingYoloFormat:
            self.set_format(FORMAT_PASCALVOC)

    def noShapes(self):
        return not self.itemsToShapes

    def toggleAdvancedMode(self, value=True):
        self._beginner = not value
        self.canvas.setEditing(True)
        self.populateModeActions()
        self.editButton.setVisible(not value)
        if value:
            self.actions.createMode.setEnabled(True)
            self.actions.editMode.setEnabled(False)
            self.dock.setFeatures(self.dock.features() | self.dockFeatures)
        else:
            self.dock.setFeatures(self.dock.features() ^ self.dockFeatures)

    def populateModeActions(self):
        if self.beginner():
            tool, menu = self.actions.beginner, self.actions.beginnerContext
        else:
            tool, menu = self.actions.advanced, self.actions.advancedContext
        self.tools.clear()
        addActions(self.tools, tool)
        self.canvas.menus[0].clear()
        addActions(self.canvas.menus[0], menu)
        self.menus.edit.clear()
        actions = (self.actions.create,) if self.beginner() \
            else (self.actions.createMode, self.actions.editMode)
        addActions(self.menus.edit, actions + self.actions.editMenu)

    def setBeginner(self):
        self.tools.clear()
        addActions(self.tools, self.actions.beginner)

    def setAdvanced(self):
        self.tools.clear()
        addActions(self.tools, self.actions.advanced)

    def setDirty(self):
        self.dirty = True
        self.actions.save.setEnabled(True)

    def setClean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.create.setEnabled(True)

    def toggleActions(self, value=True):
        """Enable/Disable widgets which depend on an opened image."""
        for z in self.actions.zoomActions:
            z.setEnabled(value)
        for action in self.actions.onLoadActive:
            action.setEnabled(value)

    def queueEvent(self, function):
        QTimer.singleShot(0, function)

    def status(self, message, delay=5000):
        self.statusBar().showMessage(message, delay)

    def resetState(self):
        self.itemsToShapes.clear()
        self.shapesToItems.clear()
        self.labelList.clear()
        self.filePath = None
        self.imageData = None
        self.labelFile = None
        self.canvas.resetState()
        self.labelCoordinates.clear()

    def currentItem(self):
        items = self.labelList.selectedItems()
        if items:
            return items[0]
        return None

    def addRecentFile(self, filePath):
        if filePath in self.recentFiles:
            self.recentFiles.remove(filePath)
        elif len(self.recentFiles) >= self.maxRecent:
            self.recentFiles.pop()
        self.recentFiles.insert(0, filePath)

    def beginner(self):
        return self._beginner

    def advanced(self):
        return not self.beginner()

    def getAvailableScreencastViewer(self):
        osName = platform.system()

        if osName == 'Windows':
            return ['C:\\Program Files\\Internet Explorer\\iexplore.exe']
        elif osName == 'Linux':
            return ['xdg-open']
        elif osName == 'Darwin':
            return ['open']

    ## Callbacks ##
    def showTutorialDialog(self):
        subprocess.Popen(self.screencastViewer + [self.screencast])

    def showInfoDialog(self):
        msg = u'Name:{0} \nApp Version:{1} \n{2} '.format(
            __appname__, 'chiebot', sys.version_info)
        QMessageBox.information(self, u'Information', msg)

    def createShape(self):
        assert self.beginner()
        self.canvas.setEditing(False)
        self.actions.create.setEnabled(False)

    def toggleDrawingSensitive(self, drawing=True):
        """In the middle of drawing, toggling between modes should be disabled."""
        self.actions.editMode.setEnabled(not drawing)
        if not drawing and self.beginner():
            # Cancel creation.
            print('Cancel creation.')
            self.canvas.setEditing(True)
            self.canvas.restoreCursor()
            self.actions.create.setEnabled(True)

    def toggleDrawMode(self, edit=True):
        self.canvas.setEditing(edit)
        self.actions.createMode.setEnabled(edit)
        self.actions.editMode.setEnabled(not edit)

    def setCreateMode(self):
        assert self.advanced()
        self.toggleDrawMode(False)

    def setEditMode(self):
        assert self.advanced()
        self.toggleDrawMode(True)
        self.labelSelectionChanged()

    def setOnlyShow(self):
        _label, ok = QInputDialog.getText(self, '单一类别显示',
                                          '类别名(多个类别用\';\'号间隔， 空值取消该模式):')
        if ok:
            if _label == "":
                self.only_show = None
            else:
                self.only_show = set(_label.split(';'))

    def updateFileMenu(self):
        currFilePath = self.filePath

        def exists(filename):
            return os.path.exists(filename)

        menu = self.menus.recentFiles
        menu.clear()
        files = [
            f for f in self.recentFiles if f != currFilePath and exists(f)
        ]
        for i, f in enumerate(files):
            icon = newIcon('labels')
            action = QAction(icon, '&%d %s' % (i + 1, QFileInfo(f).fileName()),
                             self)
            action.triggered.connect(partial(self.loadRecent, f))
            menu.addAction(action)

    def popLabelListMenu(self, point):
        self.menus.labelList.exec_(self.labelList.mapToGlobal(point))

    def editLabel(self):
        if not self.canvas.editing():
            return
        item = self.currentItem()
        if not item:
            return
        text = self.labelDialog.popUp(item.text())
        if text is not None:
            item.setText(text)
            item.setBackground(generateColorByText(text))
            self.setDirty()

    def fileSearchActivate_slot(self, idx: int):
        if 0 <= idx <= self.fileListModel.rowCount():
            self.fileSelect_slot(self.fileListModel.index(idx))

    def fileSelect_slot(self, qModelIndex: QModelIndex):
        file_path = qModelIndex.data()
        if file_path:
            self.defaultSaveDir = os.path.split(file_path)[0]
            self.loadFile(file_path)
            self.fileListSearchBox.setCurrentText(file_path)

    # Add chris
    def btnstate(self, item=None):
        """ Function to handle difficult examples
        Update on each object """
        if not self.canvas.editing():
            return

        item = self.currentItem()
        if not item:  # If not selected Item, take the first one
            item = self.labelList.item(self.labelList.count() - 1)

        difficult = self.diffcButton.isChecked()

        try:
            shape = self.itemsToShapes[item]
        except:
            pass
        # Checked and Update
        try:
            if difficult != shape.difficult:
                shape.difficult = difficult
                self.setDirty()
            else:  # User probably changed item visibility
                self.canvas.setShapeVisible(shape,
                                            item.checkState() == Qt.Checked)
        except:
            pass

    # React to canvas signals.
    def shapeSelectionChanged(self, selected=False):
        if self._noSelectionSlot:
            self._noSelectionSlot = False
        else:
            shape = self.canvas.selectedShape
            if shape:
                self.shapesToItems[shape].setSelected(True)
            else:
                self.labelList.clearSelection()
        self.actions.delete.setEnabled(selected)
        self.actions.copy.setEnabled(selected)
        self.actions.edit.setEnabled(selected)
        self.actions.shapeLineColor.setEnabled(selected)
        self.actions.shapeFillColor.setEnabled(selected)

    def addLabel(self, shape, **kwargs):
        shape.paintLabel = self.displayLabelOption.isChecked()
        item = HashableQListWidgetItem(shape.label)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        if "qt_unchecked" in kwargs:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
        item.setBackground(generateColorByText(shape.label))
        self.itemsToShapes[item] = shape
        self.shapesToItems[shape] = item
        self.labelList.addItem(item)
        for action in self.actions.onShapesPresent:
            action.setEnabled(True)

    def remLabel(self, shape):
        if shape is None:
            # print('rm empty label')
            return
        item = self.shapesToItems[shape]
        self.labelList.takeItem(self.labelList.row(item))
        del self.shapesToItems[shape]
        del self.itemsToShapes[item]

    def loadLabels(self, shapes):
        s = []
        for label, points, line_color, fill_color, difficult, imgsize in shapes:
            shape = Shape(label=label)
            for x, y in points:

                # Ensure the labels are within the bounds of the image. If not, fix them.
                x, y, snapped = self.canvas.snapPointToCanvas(x, y)
                if snapped:
                    self.setDirty()

                shape.addPoint(QPointF(x, y))
            shape.difficult = difficult
            shape.imgsize = imgsize
            shape.close()
            s.append(shape)

            if line_color:
                shape.line_color = QColor(*line_color)
            else:
                shape.line_color = generateColorByText(label)

            if fill_color:
                shape.fill_color = QColor(*fill_color)
            else:
                shape.fill_color = generateColorByText(label)

            if self.only_show and label not in self.only_show:
                self.canvas.setShapeVisible(shape, False)
                self.addLabel(shape, qt_unchecked=True)
            else:
                self.addLabel(shape)
        self.canvas.loadShapes(s)

    def saveLabels(self, annotationFilePath):
        annotationFilePath = ustr(annotationFilePath)
        if self.labelFile is None:
            self.labelFile = LabelFile()
            self.labelFile.verified = self.canvas.verified

        self.labelFile.drawResultImg = self.generateResultImg.isChecked()

        def format_shape(s):
            return dict(
                label=s.label,
                line_color=s.line_color.getRgb(),
                fill_color=s.fill_color.getRgb(),
                points=[(p.x(), p.y()) for p in s.points],
                # add chris
                difficult=s.difficult)

        shapes = [format_shape(shape) for shape in self.canvas.shapes]
        # Can add differrent annotation formats here
        try:
            if self.usingPascalVocFormat is True:
                if annotationFilePath[-4:].lower() != ".xml":
                    annotationFilePath += XML_EXT
                self.labelFile.savePascalVocFormat(
                    annotationFilePath,
                    shapes,
                    self.filePath,
                    self.imageData,
                    self.lineColor.getRgb(),
                    self.fillColor.getRgb(),
                    origin_xmlTree=self._cahed_xmlTree)
            elif self.usingYoloFormat is True:
                if annotationFilePath[-4:].lower() != ".txt":
                    annotationFilePath += TXT_EXT
                self.labelFile.saveYoloFormat(annotationFilePath, shapes,
                                              self.filePath, self.imageData,
                                              self.labelHist,
                                              self.lineColor.getRgb(),
                                              self.fillColor.getRgb())
            else:
                self.labelFile.save(annotationFilePath, shapes, self.filePath,
                                    self.imageData, self.lineColor.getRgb(),
                                    self.fillColor.getRgb())
            print('Image:{0} -> Annotation:{1}'.format(self.filePath,
                                                       annotationFilePath))
            return True
        except LabelFileError as e:
            self.errorMessage(u'Error saving label data', u'<b>%s</b>' % e)
            return False

    def copySelectedShape(self):
        self.addLabel(self.canvas.copySelectedShape())
        # fix copy and delete
        self.shapeSelectionChanged(True)

    def labelSelectionChanged(self):
        item = self.currentItem()
        if item and self.canvas.editing():
            self._noSelectionSlot = True
            self.canvas.selectShape(self.itemsToShapes[item])
            shape = self.itemsToShapes[item]
            # Add Chris
            self.diffcButton.setChecked(shape.difficult)

    def labelItemChanged(self, item):
        shape = self.itemsToShapes[item]
        label = item.text()
        if label != shape.label:
            shape.label = item.text()
            shape.line_color = generateColorByText(shape.label)
            self.setDirty()
        else:  # User probably changed item visibility
            self.canvas.setShapeVisible(shape, item.checkState() == Qt.Checked)

    # Callback functions:
    def newShape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        if not self.useDefaultLabelCheckbox.isChecked(
        ) or not self.defaultLabelTextLine.text():
            if len(self.labelHist) > 0:
                self.labelDialog = LabelDialog(parent=self,
                                               listItem=self.labelHist)

            if self.shortCutMode.isChecked():
                if self.lastLabel in self.shortCutModeKeyMap.values():
                    text = self.lastLabel
                    self.lastLabel = None
                else:
                    text = self.labelDialog.popUp(text=self.prevLabelText)
            else:
                # Sync single class mode from PR#106
                if self.singleClassMode.isChecked() and self.lastLabel:
                    text = self.lastLabel
                else:
                    text = self.labelDialog.popUp(text=self.prevLabelText)
                    self.lastLabel = text
        else:
            text = self.defaultLabelTextLine.text()

        # Add Chris
        self.diffcButton.setChecked(False)
        if text is not None:
            self.prevLabelText = text
            generate_color = generateColorByText(text)
            shape = self.canvas.setLastLabel(text, generate_color,
                                             generate_color)
            self.addLabel(shape)
            if self.beginner():  # Switch to edit mode.
                self.canvas.setEditing(True)
                self.actions.create.setEnabled(True)
            else:
                self.actions.editMode.setEnabled(True)
            self.setDirty()

            if text not in self.labelHist:
                self.labelHist.append(text)
        else:
            # self.canvas.undoLastLine()
            self.canvas.resetAllLines()

    def scrollRequest(self, delta, orientation):
        units = -delta / (8 * 15)
        bar = self.scrollBars[orientation]
        bar.setValue(bar.value() + bar.singleStep() * units)

    def setZoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.MANUAL_ZOOM
        self.zoomWidget.setValue(int(value))

    def addZoom(self, increment=10):
        self.setZoom(self.zoomWidget.value() + increment)

    def zoomRequest(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.scrollBars[Qt.Horizontal]
        v_bar = self.scrollBars[Qt.Vertical]

        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()

        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)

        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()

        w = self.scrollArea.width()
        h = self.scrollArea.height()

        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)

        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)

        # zoom in
        units = delta / (8 * 15)
        scale = 10
        self.addZoom(scale * units)

        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max

        # get the new scrollbar values
        new_h_bar_value = h_bar.value() + move_x * d_h_bar_max
        new_v_bar_value = v_bar.value() + move_y * d_v_bar_max

        h_bar.setValue(int(new_h_bar_value))
        v_bar.setValue(int(new_v_bar_value))

    def setFitWindow(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
        self.zoomMode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjustScale()

    def setFitWidth(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
        self.zoomMode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjustScale()

    def togglePolygons(self, value):
        for item, shape in self.itemsToShapes.items():
            item.setCheckState(Qt.Checked if value else Qt.Unchecked)

    def loadFile(self, filePath=None):
        """Load the specified file, or the last opened file if None."""

        self.resetState()
        self.canvas.setEnabled(False)
        self.imgPath = filePath + '\n'
        if filePath is None:
            filePath = self.settings.get(SETTING_FILENAME)

        # Make sure that filePath is a regular python string, rather than QString
        filePath = ustr(filePath)

        # Fix bug: An  index error after select a directory when open a new file.
        unicodeFilePath = ustr(filePath)
        unicodeFilePath = os.path.abspath(unicodeFilePath)

        if unicodeFilePath and self.fileListModel.rowCount() > 0:
            if unicodeFilePath in self.fileListModel.stringList():
                self.fileListView.setCurrentIndex(
                    self.getQStringListModelIndex(self.fileListModel,
                                                  unicodeFilePath))
            else:
                self.fileListModel.setStringList([])

        if unicodeFilePath and os.path.exists(unicodeFilePath):
            if LabelFile.isLabelFile(unicodeFilePath):
                try:
                    self.labelFile = LabelFile(unicodeFilePath)
                except LabelFileError as e:
                    self.errorMessage(
                        u'Error opening file',
                        (u"<p><b>%s</b></p>"
                         u"<p>Make sure <i>%s</i> is a valid label file.") %
                        (e, unicodeFilePath))
                    self.status("Error reading %s" % unicodeFilePath)
                    return False
                self.imageData = self.labelFile.imageData
                self.lineColor = QColor(*self.labelFile.lineColor)
                self.fillColor = QColor(*self.labelFile.fillColor)
                self.canvas.verified = self.labelFile.verified
            else:
                # Load image:
                # read data first and store for saving into label file.
                self.imageData = read(unicodeFilePath, None)
                self.labelFile = None
                self.canvas.verified = False

            print("imgdata:",unicodeFilePath)
            image = QImage.fromData(self.imageData)
            if image.isNull():
                self.errorMessage(
                    u'Error opening file',
                    u"<p>Make sure <i>%s</i> is a valid image file." %
                    unicodeFilePath)
                self.status("Error reading %s" % unicodeFilePath)
                return False
            self.status("Loaded %s" % os.path.basename(unicodeFilePath))
            self.image = image
            self.filePath = unicodeFilePath
            self.canvas.current_img_path=unicodeFilePath
            self.canvas.loadPixmap(QPixmap.fromImage(image))
            if self.labelFile:
                self.loadLabels(self.labelFile.shapes)
            self.setClean()
            self.canvas.setEnabled(True)
            self.adjustScale(initial=True)
            self.paintCanvas()
            self.addRecentFile(self.filePath)
            self.toggleActions(True)

            # Label xml file and show bound box according to its filename
            # if self.usingPascalVocFormat is True:
            if self.defaultSaveDir is not None:
                basename = os.path.basename(os.path.splitext(self.filePath)[0])
                xmlPath = os.path.join(self.defaultSaveDir, basename + XML_EXT)
                txtPath = os.path.join(self.defaultSaveDir, basename + TXT_EXT)
                """Annotation file priority:
                PascalXML > YOLO
                """
                if os.path.isfile(xmlPath):
                    self.loadPascalXMLByFilename(xmlPath)
                elif os.path.isfile(txtPath):
                    self.loadYOLOTXTByFilename(txtPath)
            else:
                xmlPath = os.path.splitext(filePath)[0] + XML_EXT
                txtPath = os.path.splitext(filePath)[0] + TXT_EXT
                if os.path.isfile(xmlPath):
                    self.loadPascalXMLByFilename(xmlPath)
                elif os.path.isfile(txtPath):
                    self.loadYOLOTXTByFilename(txtPath)

            self.setWindowTitle(__appname__ + ' ' + filePath)

            # Default : select last item if there is at least one item
            if self.labelList.count():
                self.labelList.setCurrentItem(
                    self.labelList.item(self.labelList.count() - 1))
                self.labelList.item(self.labelList.count() -
                                    1).setSelected(True)

            self.canvas.setFocus(True)
            if self.SAMMode.isChecked():
                self.canvas.setEditing(False)
                self.canvas.sam_open=True
            return True
        else:
            #修改filePath不存在时，保存错误图片路径到err_img_path.txt中
            print('{} is not in the img filde.'.format(filePath))
            absErrPath = os.path.dirname(self.txtPath)
            saveErrTxtPath = os.path.join(absErrPath, 'err_img_path.txt')
            err_img_data: Set[str] = set()
            if os.path.exists(saveErrTxtPath):
                with open(saveErrTxtPath, 'r') as err_r:
                    err_img_data = set(err_r.readlines())
            with open(saveErrTxtPath, 'w') as err_w:
                err_img_data.add(unicodeFilePath + '\n')
                err_w.writelines(err_img_data)
            self.filePath = unicodeFilePath
            self.addRecentFile(self.filePath)

        return False

    def resizeEvent(self, event):
        if self.canvas and not self.image.isNull() \
                and self.zoomMode != self.MANUAL_ZOOM:
            self.adjustScale()
        super(MainWindow, self).resizeEvent(event)

    def paintCanvas(self):
        assert not self.image.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoomWidget.value()
        self.canvas.adjustSize()
        self.canvas.update()

    def adjustScale(self, initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoomMode]()
        self.zoomWidget.setValue(int(100 * value))

    def scaleFitWindow(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scaleFitWidth(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()

    def closeEvent(self, event):
        if not self.mayContinue():
            event.ignore()
        settings = self.settings
        # If it loads images from dir, don't load it at the begining
        if self.dirname is None:
            settings[SETTING_FILENAME] = self.filePath if self.filePath else ''
        else:
            settings[SETTING_FILENAME] = ''

        settings[SETTING_WIN_SIZE] = self.size()
        settings[SETTING_WIN_POSE] = self.pos()
        settings[SETTING_WIN_STATE] = self.saveState()
        settings[SETTING_LINE_COLOR] = self.lineColor
        settings[SETTING_FILL_COLOR] = self.fillColor
        settings[SETTING_RECENT_FILES] = self.recentFiles
        settings[SETTING_ADVANCE_MODE] = not self._beginner
        if self.defaultSaveDir and os.path.exists(self.defaultSaveDir):
            settings[SETTING_SAVE_DIR] = ustr(self.defaultSaveDir)
        else:
            settings[SETTING_SAVE_DIR] = ''

        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            settings[SETTING_LAST_OPEN_DIR] = self.lastOpenDir
        else:
            settings[SETTING_LAST_OPEN_DIR] = ''

        settings[SETTING_AUTO_SAVE] = self.autoSaving.isChecked()
        settings[SETTING_AUTO_SAVE_FORCE] = self.forceAutoSaving.isChecked()
        settings[SETTING_SINGLE_CLASS] = self.singleClassMode.isChecked()
        settings[SETTING_PAINT_LABEL] = self.displayLabelOption.isChecked()
        settings[SETTING_DRAW_SQUARE] = self.drawSquaresOption.isChecked()
        settings.save()

    def setShortCutMode_slot(self):
        # TODO: 这里要考虑后续是否要记住上一次的设置
        if self.shortCutMode.isChecked():
            _label, ok = QInputDialog.getText(
                self,
                '快速标注方式',
                '使用设定的快捷键直接标注该类的框，格式为{快捷键}={类别名}, 以,号间隔，仅支持字母,注意不要设置\"awsdAWSD\".空值取消该模式,本模式和单例模式不兼容,启用成功会关闭单例模式',
                text=self.preShortCutModeSetting)
            if ok:
                if not _label:
                    self.shortCutModeSuccess(False)
                    return
                else:
                    self.preShortCutModeSetting = _label
                    keyLabelMap = self.str2dict(_label)
                    if keyLabelMap is None:
                        warningbox = QMessageBox.warning(
                            self, '输入的字符串不符合规则',
                            '输入的字符串不可尝试使用awsdAWSD作为快捷键!!!')
                        self.shortCutModeSuccess(False)
                        return

                    value_set = set(keyLabelMap.values())
                    label_set = set(self.labelHist)
                    #若手滑写了预设label没有的类
                    if value_set - label_set:
                        reply = QMessageBox.question(
                            self, '输入字符串有问题!', "\n".join([
                                "输入字串中包含了预设标签中没有的类:",
                                repr(value_set - label_set),
                                "确定添加?",
                                "取消的话,预设标签中不包含的类将不会被设置为快捷方式",
                            ]), QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No)

                        if reply == QMessageBox.Yes:
                            self.shortCutModeKeyMap = {
                                getattr(Qt, 'Key_' + k): v
                                for k, v in keyLabelMap.items()
                            }
                        else:
                            self.shortCutModeKeyMap = {
                                getattr(Qt, 'Key_' + k): v
                                for k, v in keyLabelMap.items()
                                if v in label_set
                            }
                        if not self.shortCutModeKeyMap:
                            warningbox = QMessageBox.warning(
                                self, '吐槽', '好好检查下输入字串,没有一个预设标签起作用哦!!!')
                            self.shortCutModeSuccess(False)
                        else:
                            self.shortCutModeSuccess(True)
                    else:
                        self.shortCutModeKeyMap = {
                            getattr(Qt, 'Key_' + k): v
                            for k, v in keyLabelMap.items()
                        }
                        self.shortCutModeSuccess(True)
        else:
            self.shortCutModeSuccess(False)

    def shortCutModeSuccess(self, sucess_flag: bool):
        if sucess_flag:
            self.shortCutMode.setChecked(True)
            self.singleClassMode.setChecked(False)
            self.singleClassMode.setCheckable(False)
            self.lastLabel = None
            self.status('启用快捷模式成功,单例模式将被强制关闭并禁用')
        else:
            self.shortCutModeKeyMap.clear()
            self.singleClassMode.setChecked(False)
            self.singleClassMode.setCheckable(True)
            self.lastLabel = None
            self.status('快捷模式取消,单例模式现在可用')

    def loadRecent(self, filename):
        if self.mayContinue():
            self.loadFile(filename)

    def scanAllImages(self, folderPath):
        extensions = [
            '.%s' % fmt.data().decode("ascii").lower()
            for fmt in QImageReader.supportedImageFormats()
        ]
        images = []

        for root, dirs, files in os.walk(folderPath):
            for file in files:
                if file.lower().endswith(tuple(extensions)):
                    relativePath = os.path.join(root, file)
                    path = ustr(os.path.abspath(relativePath))
                    images.append(path)
        natural_sort(images, key=lambda x: x.lower())
        return images

    def changeSavedirDialog(self, _value=False):
        if self.defaultSaveDir is not None:
            path = ustr(self.defaultSaveDir)
        else:
            path = '.'

        dirpath = ustr(
            QFileDialog.getExistingDirectory(
                self, '%s - Save annotations to the directory' % __appname__,
                path, QFileDialog.ShowDirsOnly
                | QFileDialog.DontResolveSymlinks))

        if dirpath is not None and len(dirpath) > 1:
            self.defaultSaveDir = dirpath

        self.statusBar().showMessage(
            '%s . Annotation will be saved to %s' %
            ('Change saved folder', self.defaultSaveDir))
        self.statusBar().show()

    def openAnnotationDialog(self, _value=False):
        if self.filePath is None:
            self.statusBar().showMessage('Please select image first')
            self.statusBar().show()
            return

        path = os.path.dirname(ustr(self.filePath)) \
            if self.filePath else '.'
        if self.usingPascalVocFormat:
            filters = "Open Annotation XML file (%s)" % ' '.join(['*.xml'])
            filename = ustr(
                QFileDialog.getOpenFileName(
                    self, '%s - Choose a xml file' % __appname__, path,
                    filters))
            if filename:
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]
            self.loadPascalXMLByFilename(filename)

    def openTxt(self, _value=False, dirpath=None, silent=False):
        self.isTxt = True
        if not self.mayContinue():
            return
        defaultOpenDirPath = dirpath if dirpath else '.'
        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            defaultOpenDirPath = self.lastOpenDir
        else:
            defaultOpenDirPath = '.'
        if silent != True:
            filters = '{}'.format('*')
            # TODO:这里defaultOpenDirPath若不是本地路径,会很慢,最好的解决方法是自己继承QFileDialog改成异步的,这里先脏修改了
            # 直接修改最后打开文件夹为txt文件所在文件夹
            targetDirPath = ustr(
                QFileDialog.getOpenFileName(self,
                                            '%s - Open Txt File' % __appname__,
                                            defaultOpenDirPath, filters, ""))
            if not os.path.isfile(targetDirPath[0]):
                if self.txtPath is not None:
                    targetDirPath = (self.txtPath, '*')
                    warningbox = QMessageBox.warning(
                        self, '注意',
                        '你没有选中任何文件列表,这里将使用之前的文件列表作为当前文件列表, 之前文件列表路径为: \n {}'.
                        format(self.txtPath))
                else:
                    warning = QMessageBox.warning(
                        self, '警告', '注意你没选中任何文件列表,且没有任何值能作为合理的文件列表')
            # targetDirPath = ustr(QFileDialog.getOpenFileName(self,
            #                                                  '%s - Open Txt File' % __appname__, defaultOpenDirPath,
            #                                                  filters,"",QFileDialog.DontUseNativeDialog))
        else:
            targetDirPath = ustr(defaultOpenDirPath)

        if os.path.isfile(targetDirPath[0]):
            self.lastOpenDir = os.path.dirname(targetDirPath[0])
        self.importTxtImages(targetDirPath)

    def reload_xml(self, img_path, flag):
        if flag == 0:
            self.statusBar().showMessage("{} 检测失败,你最好看看控制台信息".format(img_path))
            self.statusBar().show()
            print("{} det failed".format(img_path))
        elif flag == 1:
            if self.filePath.strip() == img_path.strip():
                img_ext = img_path.split('.')[-1]
                xml_path = img_path.replace('.' + img_ext, '.xml')
                self.loadPascalXMLByFilename(xml_path)
                # self.canvas.clearMask()
                self.canvas.setFocus(True)
            self.statusBar().showMessage("{} xml生成成功".format(img_path))
            self.statusBar().show()
        elif flag == 2:
            self.statusBar().showMessage(
                "{} 啥也没检测到,所以我也不生成标签文件了".format(img_path))
            self.statusBar().show()

    def setAutoDetCfg(self):
        self.rpc_host = None
        self.autoDet()

    def autoDet(self):
        if self.filePath:
            if not self.rpc_host:
                adc_dialog_cfg, self.class_thr = AutoDetCfgDialog.getAutoCfg(
                    self, self.autodet_previous_cfg)
                if adc_dialog_cfg:
                    self.autodet_previous_cfg = adc_dialog_cfg
                    self.rpc_host = self.autodet_previous_cfg[
                        'autoDet_host'] + ":" + self.autodet_previous_cfg[
                            'autoDet_port']
                else:
                    self.rpc_host = None
            if self.rpc_host:

                # XXX:
                save_dir = self.defaultSaveDir if self.defaultSaveDir else os.path.split(
                    self.filePath)[0]
                det_thr = AutoDetThread(
                    self.filePath, save_dir, self.rpc_host, self.class_thr,
                    self.autodet_previous_cfg['autoDet_rpc_flag'], self)
                # XXX fix
                det_thr.trigger.connect(self.reload_xml)
                det_thr.start()

        else:
            error = QMessageBox.critical(self, "拍头", "没读图片进来啊,咋检测?")

    def setPromptDetCfg(self):
        self.prompt_det_rpc_host = None
        self.promptDet()

    def promptDet(self):
        if self.filePath:
            if not self.prompt_det_rpc_host:
                pdc_dialog_cfg = PromptDetCfgDialog.getAutoCfg(
                    self, self.prompt_det_previous_cfg)
                if pdc_dialog_cfg:
                    self.prompt_det_previous_cfg = pdc_dialog_cfg
                    self.prompt_det_rpc_host = self.prompt_det_previous_cfg[
                        'promptdet_host'] + ":" + self.prompt_det_previous_cfg[
                            'promptdet_port']
                else:
                    self.prompt_det_rpc_host = None
            if self.prompt_det_rpc_host:
                # XXX:
                save_dir = self.defaultSaveDir if self.defaultSaveDir else os.path.split(
                    self.filePath)[0]
                det_thr = PromptDetThread(
                    self.filePath, save_dir, self.prompt_det_rpc_host,
                    float(self.prompt_det_previous_cfg['promptdet_boxthr']),
                    float(self.prompt_det_previous_cfg['promptdet_textthr']),
                    self.prompt_det_previous_cfg['promptdet_promptdict'],
                    self.prompt_det_previous_cfg['promptdet_class_dict'], self)
                # XXX fix
                det_thr.trigger.connect(self.reload_xml)
                det_thr.start()

        else:
            error = QMessageBox.critical(self, "拍头", "没读图片进来啊,咋检测?")

    def setSAMMode_slot(self):
        if self.filePath:
            if self.SAMMode.isChecked():
                sam_cfg = SAMModeCfgDialog.getAutoCfg(self, self.sam_cfg)
                if sam_cfg:
                    self.sam_cfg = sam_cfg
                    self._openSAMMode(self.sam_cfg['host'], self.sam_cfg['port'])

                    print("Main thread", QThread.currentThread())
                    return
        else:
            error = QMessageBox.critical(self, "拍头", "没读图片进来啊,咋检测?")
        self._closeSAMMode()

    def _openSAMMode(self, host, port):
        if self.currentSAMQThread is not None:
            self.currentSAMQThread.quit()
            self.currentSAMQThread = None
        self.currentSAMQThread = SAMThread(host, port)
        #TODO: connet work slot
        self.canvas.sam_send_points_signal.connect(self.currentSAMQThread.worker.sam_work)

        self.currentSAMQThread.worker.send_message_signal.connect(self.status)
        self.currentSAMQThread.worker.send_mask_signal.connect(self.canvas.setMaskShape)
        self.canvas.send_img_path_signal.connect(self.currentSAMQThread.worker.reset_img_info)
        self.currentSAMQThread.start()

        self.canvas.sam_open=True
        self.canvas.recover_sam_model()

    def _closeSAMMode(self):
        self.canvas.reset_sam_model()
        self.canvas.sam_open=False

        if self.currentSAMQThread is not None:
            self.canvas.sam_send_points_signal.disconnect(self.currentSAMQThread.worker.sam_work)
            self.canvas.send_img_path_signal.disconnect(self.currentSAMQThread.worker.reset_img_info)

            self.currentSAMQThread.worker.send_message_signal.disconnect(self.status)
            self.currentSAMQThread.worker.send_mask_signal.disconnect(self.canvas.setMaskShape)
            self.currentSAMQThread.quit()
            self.currentSAMQThread = None

    def openDirDialog(self, _value=False, dirpath=None, silent=False):
        self.isTxt = False
        if not self.mayContinue():
            return

        defaultOpenDirPath = dirpath if dirpath else '.'
        if self.lastOpenDir and os.path.exists(self.lastOpenDir):
            defaultOpenDirPath = self.lastOpenDir
        else:
            defaultOpenDirPath = os.path.dirname(
                self.filePath) if self.filePath else '.'
        if silent != True:
            targetDirPath = ustr(
                QFileDialog.getExistingDirectory(
                    self, '%s - Open Directory' % __appname__,
                    defaultOpenDirPath, QFileDialog.ShowDirsOnly
                    | QFileDialog.DontResolveSymlinks))
        else:
            targetDirPath = ustr(defaultOpenDirPath)

        self.importDirImages(targetDirPath)

    def importTxtImages(self, txtFile):
        if (not os.path.exists(txtFile[0])) or (not os.path.isfile(
                txtFile[0])):
            print('not open txt file,please check txt  path')
            return

        self.txtPath = txtFile[0]
        with open(txtFile[0], 'r', encoding='utf-8') as fr:
            ImgList = [x.strip() for x in fr.readlines()]

        self.defaultSaveDir = None

        self.fileListModel.setStringList(ImgList)
        self.filePath = None
        self.fileSelect_slot(self.fileListModel.index(0))

    def importDirImages(self, dirpath):
        if not self.mayContinue() or not dirpath:
            return

        self.lastOpenDir = dirpath
        self.dirname = dirpath
        self.filePath = None
        ImgList = self.scanAllImages(dirpath)
        self.fileListModel.setStringList(ImgList)
        self.fileSelect_slot(self.fileListModel.index(0))

    def verifyImg(self, _value=False):
        # Proceding next image without dialog if having any label
        if self.filePath is not None:
            try:
                self.labelFile.toggleVerify()
            except AttributeError:
                # If the labelling file does not exist yet, create if and
                # re-save it with the verified attribute.
                self.saveFile()
                if self.labelFile != None:
                    self.labelFile.toggleVerify()
                else:
                    return

            self.canvas.verified = self.labelFile.verified
            self.paintCanvas()
            self.saveFile()

    def openPrevImg(self, _value=False):
        # Proceding prev image without dialog if having any label
        if self.autoSaving.isChecked():
            if self.defaultSaveDir is not None:
                if self.forceAutoSaving.isChecked() or self.dirty is True:
                    self.saveFile()

        if not self.mayContinue():
            return
        self.fileSearchActivate_slot(self.fileListView.currentIndex().row() -
                                     1)

    def openNextImg(self, _value=False):
        # Proceding prev image without dialog if having any label
        if self.autoSaving.isChecked():
            if self.defaultSaveDir is not None:
                if self.forceAutoSaving.isChecked() or self.dirty is True:
                    self.saveFile()

        if not self.mayContinue():
            return

        self.fileSearchActivate_slot(self.fileListView.currentIndex().row() +
                                     1)

    def openFile(self, _value=False):
        self.isTxt = False
        if not self.mayContinue():
            return
        path = os.path.dirname(ustr(self.filePath)) if self.filePath else '.'
        formats = [
            '*.%s' % fmt.data().decode("ascii").lower()
            for fmt in QImageReader.supportedImageFormats()
        ]
        filters = "Image & Label files (%s)" % ' '.join(
            formats + ['*%s' % LabelFile.suffix])
        filename = QFileDialog.getOpenFileName(
            self, '%s - Choose Image or Label file' % __appname__, path,
            filters)
        if filename:
            if isinstance(filename, (tuple, list)):
                filename = filename[0]
            self.loadFile(filename)

    def saveFile(self, _value=False):
        if self.defaultSaveDir is not None and len(ustr(self.defaultSaveDir)):
            if self.filePath:
                imgFileName = os.path.basename(self.filePath)
                savedFileName = os.path.splitext(imgFileName)[0]
                savedPath = os.path.join(ustr(self.defaultSaveDir),
                                         savedFileName)
                self._saveFile(savedPath)
        else:
            imgFileDir = os.path.dirname(self.filePath)
            imgFileName = os.path.basename(self.filePath)
            savedFileName = os.path.splitext(imgFileName)[0]
            savedPath = os.path.join(imgFileDir, savedFileName)
            self._saveFile(savedPath if self.labelFile else self.
                           saveFileDialog(removeExt=False))

    def saveFileAs(self, _value=False):
        assert not self.image.isNull(), "cannot save empty image"
        self._saveFile(self.saveFileDialog())

    def saveFileDialog(self, removeExt=True):
        caption = '%s - Choose File' % __appname__
        filters = 'File (*%s)' % LabelFile.suffix
        openDialogPath = self.currentPath()
        dlg = QFileDialog(self, caption, openDialogPath, filters)
        dlg.setDefaultSuffix(LabelFile.suffix[1:])
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filenameWithoutExtension = os.path.splitext(self.filePath)[0]
        dlg.selectFile(filenameWithoutExtension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec_():
            fullFilePath = ustr(dlg.selectedFiles()[0])
            if removeExt:
                return os.path.splitext(fullFilePath)[
                    0]  # Return file path without the extension.
            else:
                return fullFilePath
        return ''

    def _saveFile(self, annotationFilePath):
        if annotationFilePath and self.saveLabels(annotationFilePath):
            self.setClean()
            self.statusBar().showMessage('Saved to  %s' % annotationFilePath)
            self.statusBar().show()

    def closeFile(self, _value=False):
        if not self.mayContinue():
            return
        self.resetState()
        self.setClean()
        self.toggleActions(False)
        self.canvas.setEnabled(False)
        self.actions.saveAs.setEnabled(False)

    def resetAll(self):
        self.settings.reset()
        self.close()
        proc = QProcess()
        proc.startDetached(os.path.abspath(__file__))

    def mayContinue(self):
        return not (self.dirty and not self.discardChangesDialog())

    def discardChangesDialog(self):
        yes, no = QMessageBox.Yes, QMessageBox.No
        msg = u'You have unsaved changes, proceed anyway?'
        return yes == QMessageBox.warning(self, u'Attention', msg, yes | no)

    def errorMessage(self, title, message):
        return QMessageBox.critical(self, title,
                                    '<p><b>%s</b></p>%s' % (title, message))

    def currentPath(self):
        return os.path.dirname(self.filePath) if self.filePath else '.'

    def chooseColor1(self):
        color = self.colorDialog.getColor(self.lineColor,
                                          u'Choose line color',
                                          default=DEFAULT_LINE_COLOR)
        if color:
            self.lineColor = color
            Shape.line_color = color
            self.canvas.setDrawingColor(color)
            self.canvas.update()
            self.setDirty()

    def deleteSelectedShape(self):
        self.remLabel(self.canvas.deleteSelected())
        self.setDirty()
        if self.noShapes():
            for action in self.actions.onShapesPresent:
                action.setEnabled(False)

    def chshapeLineColor(self):
        color = self.colorDialog.getColor(self.lineColor,
                                          u'Choose line color',
                                          default=DEFAULT_LINE_COLOR)
        if color:
            self.canvas.selectedShape.line_color = color
            self.canvas.update()
            self.setDirty()

    def chshapeFillColor(self):
        color = self.colorDialog.getColor(self.fillColor,
                                          u'Choose fill color',
                                          default=DEFAULT_FILL_COLOR)
        if color:
            self.canvas.selectedShape.fill_color = color
            self.canvas.update()
            self.setDirty()

    def copyShape(self):
        self.canvas.endMove(copy=True)
        self.addLabel(self.canvas.selectedShape)
        self.setDirty()

    def moveShape(self):
        self.canvas.endMove(copy=False)
        self.setDirty()

    def loadPredefinedClasses(self, predefClassesFile):
        if os.path.exists(predefClassesFile) is True:
            with codecs.open(predefClassesFile, 'r', 'utf8') as f:
                for line in f:
                    line = line.strip()
                    if self.labelHist is None:
                        self.labelHist = [line]
                    else:
                        self.labelHist.append(line)

    def loadPascalXMLByFilename(self, xmlPath):
        if self.filePath is None:
            return
        if os.path.isfile(xmlPath) is False:
            print("xml not existed")
            return

        self.set_format(FORMAT_PASCALVOC)

        tVocParseReader = PascalVocReader(xmlPath)
        shapes = tVocParseReader.getShapes()
        self._cahed_xmlTree = tVocParseReader.getXmlTree()
        self.loadLabels(shapes)
        self.canvas.verified = tVocParseReader.verified

    def loadYOLOTXTByFilename(self, txtPath):
        if self.filePath is None:
            return
        if os.path.isfile(txtPath) is False:
            return

        self.set_format(FORMAT_YOLO)
        tYoloParseReader = YoloReader(txtPath, self.image)
        shapes = tYoloParseReader.getShapes()
        self.loadLabels(shapes)
        self.canvas.verified = tYoloParseReader.verified

    def togglePaintLabelsOption(self):
        for shape in self.canvas.shapes:
            shape.paintLabel = self.displayLabelOption.isChecked()

    def toogleDrawSquare(self):
        self.canvas.setDrawingShapeToSquare(self.drawSquaresOption.isChecked())

    def eventFilter(self,watched,event):
        if event.type() == QEvent.MouseButtonPress:
            self.mousePressEvent(event)
        return super().eventFilter(watched,event)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.BackButton:
            self.openNextImg()
            ev.accept()
        elif ev.button() == Qt.ForwardButton:
            self.openPrevImg()
            ev.accept()
        else:
            ev.ignore()



def inverted(color):
    return QColor(*[255 - v for v in color.getRgb()])


def read(filename, default=None):
    try:
        with open(filename, 'rb') as f:
            return f.read()
    except:
        return default


def get_main_app(argv=[]):
    """
    Standard boilerplate Qt application code.
    Do everything but app.exec_() -- so that we can test the application in one thread
    """
    app = QApplication(argv)
    app.setApplicationName(__appname__)
    app.setWindowIcon(newIcon("app"))
    # Tzutalin 201705+: Accept extra agruments to change predefined class file
    # Usage : labelImg.py image predefClassFile saveDir
    win = MainWindow(
        argv[1] if len(argv) >= 2 else None,
        argv[2] if len(argv) >= 3 else os.path.join(
            os.path.dirname(sys.argv[0]), 'data', 'predefined_classes.txt'),
        argv[3] if len(argv) >= 4 else None)
    win.show()
    return app, win


def main():
    '''construct main app and run it'''
    app, _win = get_main_app(sys.argv)
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
