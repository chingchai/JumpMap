#การเรียกข้อมูลจากไฟล์ที่เขียนไว้มาใช้เพิ่มเติม รวมถึงการเรียกใช้ฟังก์ชั่นต่างๆ
from qgis.PyQt.QtCore import Qt, QTimer, QUrl, QSettings, Qt
from qgis.PyQt.QtGui import * 
from qgis.PyQt.QtWidgets import * 
from . import reference
from qgis.core import Qgis,QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsProject
from qgis.gui import QgsMapToolEmitPoint
import webbrowser
import os

#พิกัดอ้างอิงของระบบพิกัด
Coordinate = QgsCoordinateReferenceSystem('EPSG:4326')

class ToolGT(QgsMapToolEmitPoint):
    '''เป็นคลาสที่เมื่อใช้เมาส์คลิกที่แผนที่ที่มีพิกัดและจะนำค่าที่ได้มาแสดงบนแถบสถานะด้านบน
    พร้อมส่งค่าพิกัดไปวางในลิงก์เพื่อส่งออกค่าไปยังบราวเซอร์'''
    def __init__(self, settings, iface):
        QgsMapToolEmitPoint.__init__(self, iface.mapCanvas())
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.settings = settings
        self.canvasClicked.connect(self.clicked)
        
    def activate(self):
        '''เรียกการใช้เคอร์เซอร์เม้าส์'''
        self.canvas.setCursor(Qt.CrossCursor)
        
    def clicked(self, pt):
        '''เก็บพิกัดเมื่อมีการคลิกเมาส์ที่แผนที่พร้อมส่งค่าไปยังคลิปบอร์ก่อนจะส่งออกค่าไปที่บราวเซอร์'''
        canvasCRS = self.canvas.mapSettings().destinationCrs()
        transform = QgsCoordinateTransform(canvasCRS, Coordinate, QgsProject.instance())
        pt4326 = transform.transform(pt.x(), pt.y())
        lat = pt4326.y()
        lon = pt4326.x()
        referencemap = self.settings.GetReferenceMap(lat, lon)
        url = QUrl(referencemap).toString()
        webbrowser.open(url, new=2)
        self.iface.messageBar().pushMessage("Let's go", "Recently Coordinate %f,%f in External map" % (lat,lon), level=Qgis.Info, duration=0)


class WidgetSetting:
    '''การตั้งค่าการใช้ปุ่มกด'''
    #อินเตอร์เฟซต่างๆที่ใช้ในคลาสนี้จะถูกจัดการโดยโปรแกรมผ่านฟังก์ชั่นนี้
    def __init__(self, lltools, iface, parent):
        self.lltools = lltools
        self.iface = iface
        self.LoadSetting()
        
      
    def LoadSetting(self):
        '''ฟังก์ชั่นนี้จะโหลดการตั้งค่าที่ได้ทำไว้แล้วตลอดถึงแม้จะปิดโปรแกรมไปแล้ว'''
        settings = QSettings()
        ### EXTERNAL MAP ###
        self.showPlacemark = int(settings.value('/JumpMap/ShowPlacemark', Qt.Checked))
        self.reference = int(settings.value('/JumpMap/reference', 0))
        self.mapZoom = int(settings.value('/JumpMap/MapZoom', 13))
       
    def GetReferenceMap(self, lat, lon):
        '''ฟังก์ชั่นนี้จะรับค่าจากแผนที่ในรูปแบบข้อมูล Lat, Lon'''
        if self.showPlacemark:
            ms = reference.Refer_Map[self.reference][2]
        else:
            ms = reference.Refer_Map[self.reference][1]
        ms = ms.replace('@LAT@', str(lat))
        ms = ms.replace('@LON@', str(lon))
        ms = ms.replace('@Z@', str(self.mapZoom))
        return ms


class JumpMapTool:
    '''เป็นคลาสสำหรับหน้าต่างอินเตอร์เฟซ'''
    def __init__(self, iface):
        self.iface = iface
        self.canvas = iface.mapCanvas()        
        self.toolbar = self.iface.addToolBar('Jump Map Toolbar')

    def initGui(self):
        '''เริ่มต้นการทำงานGui'''
        # เริ่มต้นการทำงาน
        self.settingsDialog = WidgetSetting(self, self.iface, self.iface.mainWindow())
        self.showMapTool = ToolGT(self.settingsDialog, self.iface)
        
        # เพิ่มปุ่มที่Toolbar
        icon = QIcon(os.path.dirname(__file__) + "/images/mapicon.png")
        self.externMapAction = QAction(icon, "Jump Map", self.iface.mainWindow())
        self.externMapAction.triggered.connect(self.SetCheckMap)
        self.toolbar.addAction(self.externMapAction)
       # self.iface.addPluginToMenu("Jump Map Tools", self.externMapAction)

    def unload(self):
        '''ยกเลิกการโหลดคลาสนี้จากโปรแกรม'''
        self.canvas.unsetMapTool(self.showMapTool)
        self.iface.removeToolBarIcon(self.externMapAction)
        # remove the toolbar
        del self.toolbar
        


    def SetCheckMap(self):
        '''ฟังก์ชั่นนี้เซ็ทและตรวจสอบค่าในแผนที่'''
        self.externMapAction.setChecked(True)
        self.canvas.setMapTool(self.showMapTool)