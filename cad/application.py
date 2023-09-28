import os

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PIL import Image
import ezdxf

from cad.sketch import Sketch
from cad.solver import *

# get the directory of the current file
directory = os.path.dirname(__file__)

# Function to get the path of an icon file
def icon_path(name: str) -> str:
    return os.path.join(directory, 'icons', name)

# Main application class
class Application(QMainWindow):

    def __init__(self, *args):
        super().__init__(*args)

        self.sketch = None

        self.menu = None
        self.toolBar = None
        self.toolBarGroup = None

        self.initSketch()
        # Initialize the sketch area
        self.initMenuBar()
        # Initialize the menu bar
        self.initToolBar()
        # Initialize the tool bar
        self.initStatusBar()
        # Initialize the status bar
        self.initGeometry()
        # Initialize the application window geometry 

        self.setWindowTitle('PIXOR-Cad')
        # Set the window title

    # Initialize the sketch area
    def initSketch(self):
        self.sketch = Sketch(self)
        self.setCentralWidget(self.sketch)

    # Initialize the menu bar
    def initMenuBar(self):
        self.menu = self.menuBar()

        # File menu
        file = self.menu.addMenu('File')
        file.addAction(self.exitAction())
        file.addAction(self.saveImageAction())
        file.addAction(self.saveDxfAction())
        file.addAction(self.importAction())
        file.addAction(self.shareAction())
        file.addAction(self.print())

        # Edit menu
        edit = self.menu.addMenu('Edit')
        edit.addAction(self.undoAction())
        edit.addAction(self.RedoAction())
        edit.addAction(self.cutAction())
        edit.addAction(self.copyAction())
        edit.addAction(self.pasteAction())

        # View menu
        view = self.menu.addMenu("View")
        view.addAction(self.CreateShortcuts())
        view.addAction(self.ChangeContrast())
        view.addAction(self.zoomi())
        view.addAction(self.zoomo())

        # Help menu
        help = self.menu.addMenu("Help")
        help.addAction(self.aboutus())
        help.addAction(self.VersionDetails())

        # Report bugs menu
        report_bugs = self.menu.addMenu("Report Bugs")
        report_bugs.addAction(self.report())

    # Define and configure the "Undo" action
    def undoAction(self):
        action = QAction('Undo', self.menu)
        action.setShortcut('Ctrl+Z')
        action.setStatusTip('Undo')
        action.setToolTip('Undo')
        return action
    
    # Define and configure the "Redo" action
    def RedoAction(self):
        action = QAction("Redo", self.menu)
        action.setStatusTip("Redo")
        action.setToolTip("Redo")
        action.setShortcut("Ctrl+Y")    
        return action



    # Define and configure the "Create Shortcuts" action
    def CreateShortcuts(self):
        action = QAction('Create Shortcuts', self)
        action.setStatusTip('Create Shortcuts')
        action.setToolTip('Create Shortcuts')
        return action

    # Define and configure the "Change Contrast" action
    def ChangeContrast(self):
        action = QAction('Change Contrast', self)
        action.setStatusTip('Change Contrast')
        action.setToolTip('Change Contrast')
        return action

    # Define and configure the "Save As" action
    def saveasAction(self):
        action = QAction("Save as", self)
        action.setShortcut('Ctrl+Shift+S')
        action.setStatusTip("Save as")
        action.setToolTip("Save as")
        return action


    # Define and configure the "Zoom In" action
    def zoomi(self):
        action = QAction('Zoom In', self)
        action.setStatusTip('Zoom In')
        action.setToolTip('Zoom In')
        return action

    # Define and configure the "Zoom Out" action
    def zoomo(self):
        action = QAction('Zoom Out', self)
        action.setStatusTip('Zoom Out')
        action.setToolTip('Zoom Out')
        return action

    # Define and configure the "About Us" action
    def aboutus(self):
        action = QAction('About Us', self)
        action.setStatusTip('About Us')
        action.setToolTip('About Us')
        return action

    # Define and configure the "Version Details" action
    def VersionDetails(self):
        action = QAction('Version Details', self)
        action.setStatusTip('Version Details')
        action.setToolTip('Version Details')
        return action

    # Define and configure the "Print" action
    def print(self):
        action = QAction('Print', self)
        action.setStatusTip('Print')
        action.setToolTip('Print')
        return action

    # Define and configure the "Report" action
    def report(self):
        action = QAction('Report', self)
        action.setStatusTip('Report')
        action.setToolTip('About Us')
        return action

    # Define and configure the "Cut" action
    def cutAction(self):
        action = QAction('Cut', self.menu)
        action.setShortcut('Ctrl+X')
        action.setStatusTip('Cut')
        action.setToolTip('Cut')
        return action
    
    # Define and configure the "Copy" action
    def copyAction(self):
        action = QAction('Copy', self.menu)
        action.setShortcut('Ctrl+C')
        action.setStatusTip('Copy')
        action.setToolTip('Copy')
        return action

    # Define and configure the "Paste" action
    def pasteAction(self):
        action = QAction('Paste', self.menu)
        action.setShortcut('Ctrl+V')
        action.setStatusTip('Paste')
        action.setToolTip('Paste')
        return action

    # Define and configure the "Delete" action (not implemented)
    def deleteAction(self):
        action = QAction('Delete', self.menu)
        action.setShortcut('Delete')
        action.setStatusTip('Delete')
        action.setToolTip('Delete')
        return action

    # Define and configure the "Exit" action
    def exitAction(self):
        action = QAction('Exit', self.menu)
        action.setShortcut('Ctrl+Q')
        action.setToolTip('Close application')
        action.setStatusTip('Close application')
        action.triggered.connect(self.close)
        return action

    def saveImageAction(self):
        action = QAction('Save as Image', self.menu)
        action.setShortcut('Ctrl+Shift+I')
        action.setStatusTip('Save as Image')
        action.setToolTip('Save as Image')
        action.triggered.connect(self.saveImage)
        return action

    def saveDxfAction(self):
        action = QAction('Save as DXF', self.menu)
        action.setShortcut('Ctrl+Shift+D')
        action.setStatusTip('Save as DXF')
        action.setToolTip('Save as DXF')
        action.triggered.connect(self.saveDxf)
        return action

    # Define and configure the "Import" action (not implemented)
    def importAction(self):
        action = QAction('Import as DXF', self.menu)
        action.setToolTip('Import as DXF')
        action.setStatusTip('Import as DXF')
        action.triggered.connect(self.importDxf)
        return action

    # Define and configure the "Share" action (not implemented)
    def shareAction(self):
        action = QAction('Share',self.menu)
        action.setToolTip('Share')
        action.setStatusTip('Share')
        return action


    # Initialize the tool bar and its actions
    def initToolBar(self):
        self.toolBar = self.addToolBar('Drawing')
        self.toolBarGroup = QActionGroup(self.toolBar)
        self.moveAction = self.moveObjectAction()
        default = self.disableAction()

        actions = [
            default,
            self.lineAction(),
            self.moveObjectAction(),
            self.pointAction(),
            self.parallelAction(),
            # self.perpendicularAction(),
            self.verticalAction(),
            self.horizontalAction(),
            self.coincidentAction(),
            self.fixedAction(),
            self.angleAction(),
            self.lengthAction(),
            self.rectangleAction(),
            self.polylineAction(),
            self.drawCircleAction(),
            self.drawArcwithtwopointsAction(),
            self.EraserAction(),
        ]

        for action in actions:
            action.setCheckable(True)
            action.setParent(self.toolBar)
            self.toolBar.addAction(action)
            self.toolBarGroup.addAction(action)

        default.setChecked(True)

    # Define and configure the "Point" action
    def pointAction(self):
        action = QAction('Point')
        action.setShortcut('Ctrl+P')
        action.setToolTip('Draw point')
        action.setStatusTip('Draw point')
        action.setIcon(QIcon(icon_path('point.png')))
        action.triggered.connect(self.pointActionHandler)
        return action
    
    # Handler for the "Point" action
    def pointActionHandler(self):
        self.sketch.handler = PointDrawing()

    def moveObjectAction(self):
        action = QAction('Move Object', self.toolBar)
        action.setCheckable(True)
        action.setToolTip('Move Object')
        action.setStatusTip('Move Object')
        action.setIcon(QIcon(icon_path('move.png')))
        action.triggered.connect(self.moveObjectActionHandler)
        return action

    def moveObjectActionHandler(self):
        self.sketch.handler = MoveObjectHandler()

    # Define and configure the "Line" action
    def lineAction(self):
        action = QAction('Line')
        action.setShortcut('Ctrl+L')
        action.setToolTip('Draw line')
        action.setStatusTip('Draw line')
        action.setIcon(QIcon(icon_path('line.png')))
        action.triggered.connect(self.lineActionHandler)
        return action

    # Handler for the "Line" action
    def lineActionHandler(self):
        self.sketch.handler = LineDrawing()

    # Define and configure the "Horizontal" action
    def horizontalAction(self):
        action = QAction('Horizontal')
        action.setToolTip('Horizontal constraint')
        action.setStatusTip('Horizontal constraint')
        action.setIcon(QIcon(icon_path('horizontal.png')))
        action.triggered.connect(self.horizontalActionHandler)
        return action

    # Handler for the "Horizontal" action
    def horizontalActionHandler(self):
        self.sketch.handler = HorizontalLineHandler()

    # Define and configure the "Vertical" action
    def verticalAction(self):
        action = QAction('Vertical')
        action.setToolTip('Vertical constraint')
        action.setStatusTip('Vertical constraint')
        action.setIcon(QIcon(icon_path('vertical.png')))
        action.triggered.connect(self.verticalActionHandler)
        return action

    # Handler for the "Vertical" action
    def verticalActionHandler(self):
        self.sketch.handler = VerticalLineHandler()

    # Define and configure the "Angle" action
    def angleAction(self):
        action = QAction('Angle')
        action.setToolTip('Angle constraint')
        action.setStatusTip('Angle constraint')
        action.setIcon(QIcon(icon_path('angle.png')))
        action.triggered.connect(self.angleActionHandler)
        return action

    # Handler for the "Angle" action
    def angleActionHandler(self):
        # Function to ask for angle value
        def askAngleValue():
            label = 'Input angle value:'
            title = 'Set angle constraint'
            return QInputDialog.getDouble(self.sketch.parent(), title, label, 0)

        angle, ok = askAngleValue()
        if ok:
            self.sketch.handler = AngleHandler(angle)

    # Define and configure the "Length" action
    def lengthAction(self):
        action = QAction('Length')
        action.setToolTip('Length constraint')
        action.setStatusTip('Length constraint')
        action.setIcon(QIcon(icon_path('length.png')))
        action.triggered.connect(self.lengthActionHandler)
        return action

    # Handler for the "Length" action
    def lengthActionHandler(self):
        # Function to ask for length value
        def askLengthValue():
            label = 'Input length value:'
            title = 'Set length constraint'
            return QInputDialog.getDouble(self.sketch.parent(), title, label, 0, 0)

        length, ok = askLengthValue()
        if ok:
            self.sketch.handler = LengthHandler(length)

    # Define and configure the "Parallel" action
    def parallelAction(self):
        action = QAction('Parallel')
        action.setToolTip('Parallel constraint')
        action.setStatusTip('Parallel constraint')
        action.setIcon(QIcon(icon_path('parallel.png')))
        action.triggered.connect(self.parallelsActionHandler)
        return action

    def rectangleAction(self):
        action = QAction('Rectangle')
        action.setToolTip('Rectangle constraint')
        action.setStatusTip('Rectangle constraint')
        action.setIcon(QIcon(icon_path('rectangle.png')))
        action.triggered.connect(self.rectangleActionHandler)
        return action

    def rectangleActionHandler(self):
        self.sketch.handler = RectangleHandler()

    
    # Handler for the "Parallel" action
    def parallelsActionHandler(self):
        self.sketch.handler = ParallelHandler()

    # Define and configure the "Perpendicular" action (not implemented)
    def perpendicularAction(self):
        action = QAction('Perpendicular')
        action.setToolTip('Perpendicular constraint')
        action.setStatusTip('Perpendicular constraint')
        action.setIcon(QIcon(icon_path('perpendicular.png')))
        action.triggered.connect(self.perpendicularActionHandler)
        return action

    # Handler for the "Perpendicular" action (not implemented)
    def perpendicularActionHandler(self):
        pass

    # Define and configure the "Coincident" action
    def coincidentAction(self):
        action = QAction('Coincident')
        action.setToolTip('Coincident constraint')
        action.setStatusTip('Coincident constraint')
        action.setIcon(QIcon(icon_path('coincident.png')))
        action.triggered.connect(self.coincidentActionHandler)
        return action

    # Handler for the "Coincident" action
    def coincidentActionHandler(self):
        self.sketch.handler = CoincidentHandler()

    # Define and configure the "Fixed" action
    def fixedAction(self):
        action = QAction('Fixed')
        action.setToolTip('Fixed constraint')
        action.setStatusTip('Fixed constraint')
        action.setIcon(QIcon(icon_path('fixed.png')))
        action.triggered.connect(self.fixedActionHandler)
        return action

    # Handler for the "Fixed" action
    def fixedActionHandler(self):

        # Function to ask for coordinate values
        def askCoordinateValue():
            label = 'Enter coordinate:'
            title = 'Set fixing constraint'
            return QInputDialog.getDouble(self.sketch.parent(), title, label, 0)

        x, ok = askCoordinateValue()
        if ok:
            y, ok = askCoordinateValue()
            if ok:
                self.sketch.handler = FixingHandler(x, y)

    # Define and configure the "Polyline" action
    def polylineAction(self):
        action = QAction('Polyline')
        action.setToolTip('Polyline constraint')
        action.setStatusTip('Polyline constraint')
        action.setIcon(QIcon(icon_path('polyline.png')))
        # action.triggered.connect(self.polylineActionHandler)
        return action
  
    ''' # Handler for the "Polyline" action
    def polylineActionHandler(self):
        self.sketch.handler = PolylineHandler()
    '''

     # Define and configure the "Circle" action
    def drawCircleAction(self):
        action = QAction('Draw Circle')
        action.setToolTip('Draw Circle')
        action.setStatusTip('Draw Circle')
        action.setIcon(QIcon(icon_path('circle.png')))
        action.triggered.connect(self.drawCircleActionHandler)
        return action
  
    # Handler for the "drawCircle" action
    def drawCircleActionHandler(self):
        self.sketch.handler = CircleDrawingHandler()

     # Define and configure the "Arc with two points" action
    def drawArcwithtwopointsAction(self):
        action = QAction('drawArcwithtwopoints')
        action.setToolTip('drawArcwithtwopoints constraint')
        action.setStatusTip('drawArcwithtwopoints constraint')
        action.setIcon(QIcon(icon_path('Arc.png')))
        # action.triggered.connect(self.drawArcwithtwopointsActionHandler)
        return action
  
    ''' # Handler for the "drawArcwithtwopoints" action
    def drawArcwithtwopointsHandler(self):
        self.sketch.handler = drawArcwithtwopointsHandler()
    '''

    # Define and configure the "Eraser" action
    def EraserAction(self):
        action = QAction('Eraser')
        action.setToolTip('Eraser constraint')
        action.setStatusTip('Eraser constraint')
        action.setIcon(QIcon(icon_path('Eraser.png')))
        action.triggered.connect(self.EraserActionHandler)
        return action

    def toggleEraserMode(self):
        eraserButton = self.toolBarGroup.checkedAction()
        if eraserButton.text() == 'Eraser':
            self.sketch.handler = EraserHandler(self.sketch)
        else:
            self.sketch.handler = DisableHandler()
    # Handler for the "Eraser" action
    def EraserActionHandler(self):
        self.sketch.handler = EraserHandler()


    # Define and configure the "Disable" action
    def disableAction(self):
        action = QAction('Disable')
        action.setToolTip('Choose action')
        action.setStatusTip('Choose action')
        action.setIcon(QIcon(icon_path('cursor.png')))
        action.triggered.connect(self.disableActionHandler)
        return action

    # Handler for the "Disable" action
    def disableActionHandler(self):
        for action in self.toolBarGroup.actions():
            action.setChecked(False)

        self.toolBarGroup.actions()[0].setChecked(True)

    # Initialize the status bar
    def initStatusBar(self):
        self.statusBar().showMessage('Ready')

    # Initialize the application window geometry
    def initGeometry(self):
        desktop = QDesktopWidget()
        self.setGeometry(desktop.availableGeometry())

    def importDxf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileName(self, 'Import DXF', '', 'DXF Files (*.dxf)', options=options)
        if files:
            doc = ezdxf.readfile(files)
            msp = doc.modelspace()
            self.sketch.lines.clear()  # Clear existing lines
            for entity in msp.query('LINE'):
                start_point = entity.dxf.start
                end_point = entity.dxf.end
                p1 = Point(start_point.x, -start_point.y)  # Invert Y-coordinate as needed
                p2 = Point(end_point.x, -end_point.y)      # Invert Y-coordinate as needed
                self.sketch.addLine(Line(p1, p2))
            self.sketch.update()

    # Show the save file as dxf dialog
    def saveImage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'PNG Image (*.png);;JPEG Image (*.jpg)',
                                               options=options)
        if files:
            pixmap = self.sketch.grab()
            pixmap.save(files)

    def saveDxf(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getSaveFileName(self, 'Save DXF', '', 'DXF Files (*.dxf)', options=options)
        if files:
            doc = ezdxf.new()
            msp = doc.modelspace()
            for line in self.sketch.lines:
                p1_tuple = (line.p1.x, line.p1.y)
                p2_tuple = (line.p2.x, line.p2.y)
                msp.add_lwpolyline([p1_tuple, p2_tuple])
            doc.saveas(files)

    # Show the save file as dialog (not implemented)
    def showSaveasDialog(self):
        title = "Save as"
        default = "/home/cad.json"
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files= QFileDialog().getSaveFileName(self, 'Save File', '', 'JPEG (*.JPEG);;All Files (*)', options=options)

        if files and files[0]:
            with open(files[0], 'w') as fp:
                fp.write('')

    # Handle key press events
    def keyPressEvent(self, event):
        self.sketch.keyPressEvent(event)

        if event.key() == Qt.Key_Escape:
            return self.disableActionHandler()

    # Handle close events
    def closeEvent(self, event):
        title = 'Close application'
        question = 'Are you sure you want to quit?'

        default = QMessageBox.No
        buttons = QMessageBox.No | QMessageBox.Yes

        answer = QMessageBox().question(self, title, question, buttons, default)
        if answer == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
