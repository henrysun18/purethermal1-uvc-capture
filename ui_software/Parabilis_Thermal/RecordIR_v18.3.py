#!/usr/bin/env python3
# Author: Karl Parks, 2018

from PyQt5 import QtCore, QtGui, uic
print('Successful import of uic') #often reinstallation of PyQt5 is required

from PyQt5.QtCore import (QCoreApplication, QThread, QThreadPool, pyqtSignal, pyqtSlot, Qt, QTimer, QDateTime)
from PyQt5.QtGui import (QImage, QPixmap, QTextCursor)
from PyQt5.QtWidgets import (QWidget, QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, QGridLayout, QSizePolicy, QMessageBox, QFileDialog, QSlider, QComboBox, QProgressDialog)

import sys
import os.path
import cv2
from tifffile import imsave
import numpy as np
import h5py
import time
import psutil
from uvctypesParabilis_v2 import *
from multiprocessing  import Queue
import threading
from subprocess import call

print('Loaded Packages and Starting IR Data...')

qtCreatorFile = "ir_v11.ui"  # Enter file here.
postScriptFileName = "PostProcessIR_v11.py"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

BUF_SIZE = 2
q = Queue(BUF_SIZE)

def py_frame_callback(frame, userptr):
    array_pointer = cast(frame.contents.data, POINTER(c_uint16 * (frame.contents.width * frame.contents.height)))
    data = np.frombuffer(
        array_pointer.contents, dtype=np.dtype(np.uint16)).reshape(frame.contents.height, frame.contents.width)
    if frame.contents.data_bytes != (2 * frame.contents.width * frame.contents.height):
        return
    if not q.full():
        q.put(data)

PTR_PY_FRAME_CALLBACK = CFUNCTYPE(None, POINTER(uvc_frame), c_void_p)(py_frame_callback)

def generate_colour_map():
    """
    Conversion of the colour map from GetThermal to a numpy LUT:
        https://github.com/groupgets/GetThermal/blob/bb467924750a686cc3930f7e3a253818b755a2c0/src/dataformatter.cpp#L6
    """

    lut = np.zeros((256, 1, 3), dtype=np.uint8)

    colourmap_ironblack = [
        255, 255, 255, 253, 253, 253, 251, 251, 251, 249, 249, 249, 247, 247,
        247, 245, 245, 245, 243, 243, 243, 241, 241, 241, 239, 239, 239, 237,
        237, 237, 235, 235, 235, 233, 233, 233, 231, 231, 231, 229, 229, 229,
        227, 227, 227, 225, 225, 225, 223, 223, 223, 221, 221, 221, 219, 219,
        219, 217, 217, 217, 215, 215, 215, 213, 213, 213, 211, 211, 211, 209,
        209, 209, 207, 207, 207, 205, 205, 205, 203, 203, 203, 201, 201, 201,
        199, 199, 199, 197, 197, 197, 195, 195, 195, 193, 193, 193, 191, 191,
        191, 189, 189, 189, 187, 187, 187, 185, 185, 185, 183, 183, 183, 181,
        181, 181, 179, 179, 179, 177, 177, 177, 175, 175, 175, 173, 173, 173,
        171, 171, 171, 169, 169, 169, 167, 167, 167, 165, 165, 165, 163, 163,
        163, 161, 161, 161, 159, 159, 159, 157, 157, 157, 155, 155, 155, 153,
        153, 153, 151, 151, 151, 149, 149, 149, 147, 147, 147, 145, 145, 145,
        143, 143, 143, 141, 141, 141, 139, 139, 139, 137, 137, 137, 135, 135,
        135, 133, 133, 133, 131, 131, 131, 129, 129, 129, 126, 126, 126, 124,
        124, 124, 122, 122, 122, 120, 120, 120, 118, 118, 118, 116, 116, 116,
        114, 114, 114, 112, 112, 112, 110, 110, 110, 108, 108, 108, 106, 106,
        106, 104, 104, 104, 102, 102, 102, 100, 100, 100, 98, 98, 98, 96, 96,
        96, 94, 94, 94, 92, 92, 92, 90, 90, 90, 88, 88, 88, 86, 86, 86, 84, 84,
        84, 82, 82, 82, 80, 80, 80, 78, 78, 78, 76, 76, 76, 74, 74, 74, 72, 72,
        72, 70, 70, 70, 68, 68, 68, 66, 66, 66, 64, 64, 64, 62, 62, 62, 60, 60,
        60, 58, 58, 58, 56, 56, 56, 54, 54, 54, 52, 52, 52, 50, 50, 50, 48, 48,
        48, 46, 46, 46, 44, 44, 44, 42, 42, 42, 40, 40, 40, 38, 38, 38, 36, 36,
        36, 34, 34, 34, 32, 32, 32, 30, 30, 30, 28, 28, 28, 26, 26, 26, 24, 24,
        24, 22, 22, 22, 20, 20, 20, 18, 18, 18, 16, 16, 16, 14, 14, 14, 12, 12,
        12, 10, 10, 10, 8, 8, 8, 6, 6, 6, 4, 4, 4, 2, 2, 2, 0, 0, 0, 0, 0, 9,
        2, 0, 16, 4, 0, 24, 6, 0, 31, 8, 0, 38, 10, 0, 45, 12, 0, 53, 14, 0,
        60, 17, 0, 67, 19, 0, 74, 21, 0, 82, 23, 0, 89, 25, 0, 96, 27, 0, 103,
        29, 0, 111, 31, 0, 118, 36, 0, 120, 41, 0, 121, 46, 0, 122, 51, 0, 123,
        56, 0, 124, 61, 0, 125, 66, 0, 126, 71, 0, 127, 76, 1, 128, 81, 1, 129,
        86, 1, 130, 91, 1, 131, 96, 1, 132, 101, 1, 133, 106, 1, 134, 111, 1,
        135, 116, 1, 136, 121, 1, 136, 125, 2, 137, 130, 2, 137, 135, 3, 137,
        139, 3, 138, 144, 3, 138, 149, 4, 138, 153, 4, 139, 158, 5, 139, 163,
        5, 139, 167, 5, 140, 172, 6, 140, 177, 6, 140, 181, 7, 141, 186, 7,
        141, 189, 10, 137, 191, 13, 132, 194, 16, 127, 196, 19, 121, 198, 22,
        116, 200, 25, 111, 203, 28, 106, 205, 31, 101, 207, 34, 95, 209, 37,
        90, 212, 40, 85, 214, 43, 80, 216, 46, 75, 218, 49, 69, 221, 52, 64,
        223, 55, 59, 224, 57, 49, 225, 60, 47, 226, 64, 44, 227, 67, 42, 228,
        71, 39, 229, 74, 37, 230, 78, 34, 231, 81, 32, 231, 85, 29, 232, 88,
        27, 233, 92, 24, 234, 95, 22, 235, 99, 19, 236, 102, 17, 237, 106, 14,
        238, 109, 12, 239, 112, 12, 240, 116, 12, 240, 119, 12, 241, 123, 12,
        241, 127, 12, 242, 130, 12, 242, 134, 12, 243, 138, 12, 243, 141, 13,
        244, 145, 13, 244, 149, 13, 245, 152, 13, 245, 156, 13, 246, 160, 13,
        246, 163, 13, 247, 167, 13, 247, 171, 13, 248, 175, 14, 248, 178, 15,
        249, 182, 16, 249, 185, 18, 250, 189, 19, 250, 192, 20, 251, 196, 21,
        251, 199, 22, 252, 203, 23, 252, 206, 24, 253, 210, 25, 253, 213, 27,
        254, 217, 28, 254, 220, 29, 255, 224, 30, 255, 227, 39, 255, 229, 53,
        255, 231, 67, 255, 233, 81, 255, 234, 95, 255, 236, 109, 255, 238, 123,
        255, 240, 137, 255, 242, 151, 255, 244, 165, 255, 246, 179, 255, 248,
        193, 255, 249, 207, 255, 251, 221, 255, 253, 235, 255, 255, 24]

    def chunk(
            ulist, step): return map(
        lambda i: ulist[i: i + step],
        range(0, len(ulist),
               step))

    chunks = chunk(colourmap_ironblack, 3)

    red = []
    green = []
    blue = []

    for chunk in chunks:
        red.append(chunk[0])
        green.append(chunk[1])
        blue.append(chunk[2])

    lut[:, 0, 0] = blue

    lut[:, 0, 1] = green

    lut[:, 0, 2] = red

    return lut

def startStream():
  global devh
  ctx = POINTER(uvc_context)()
  dev = POINTER(uvc_device)()
  devh = POINTER(uvc_device_handle)()
  ctrl = uvc_stream_ctrl()

  res = libuvc.uvc_init(byref(ctx), 0)
  if res < 0:
    print("uvc_init error")
    #exit(1)

  try:
    res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
    if res < 0:
      print("uvc_find_device error")
      exit(1)

    try:
      res = libuvc.uvc_open(dev, byref(devh))
      if res < 0:
        print("uvc_open error")
        exit(1)

      print("device opened!")

      print_device_info(devh)
      print_device_formats(devh)

      frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
      if len(frame_formats) == 0:
        print("device does not support Y16")
        exit(1)

      libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
        frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
      )

      res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
      if res < 0:
        print("uvc_start_streaming failed: {0}".format(res))
        exit(1)

      print("done")
      print_shutter_info(devh)

    except:
      #libuvc.uvc_unref_device(dev)
      print('Failed to Open Device')
  except:
    #libuvc.uvc_exit(ctx)
    print('Failed to Find Device')
    exit(1)

toggleUnitState = 'F'

def ktof(val):
    return round(((1.8 * ktoc(val) + 32.0)), 2)

def ktoc(val):
    return round(((val - 27315) / 100.0), 2)

def display_temperatureK(img, val_k, loc, color):
    val = ktof(val_k)
    cv2.putText(img,"{0:.1f} degF".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
    x, y = loc
    cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
    cv2.line(img, (x, y - 2), (x, y + 2), color, 1)

def display_temperatureC(img, val_k, loc, color):
    val = ktof(val_c)
    cv2.putText(img,"{0:.1f} degC".format(val), loc, cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)
    x, y = loc
    cv2.line(img, (x - 2, y), (x + 2, y), color, 1)
    cv2.line(img, (x, y - 2), (x, y + 2), color, 1)

def raw_to_8bit(data):
    cv2.normalize(data, data, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(data, 8, data)
    return cv2.cvtColor(np.uint8(data), cv2.COLOR_GRAY2RGB)

camState = 'not_recording'
tiff_frame = 1
maxVal = 0
minVal = 0

fileNum = 1
@pyqtSlot(QImage)
def startRec():
    global camState
    global saveFilePath
    global mostRecentFile
    if camState == 'recording':
        print('Alredy Recording')
    else:
        file_nameH = str(('Lepton HDF5 Vid ' + QDateTime.currentDateTime().toString()))
        file_nameH = file_nameH.replace(" ", "_")
        file_nameH = str(file_nameH.replace(":", "-"))
    try:
        filePathAndName = str(saveFilePath + '/' + file_nameH)
        #saveFilePathSlash = str(saveFilePath + '/')
        startRec.hdf5_file = h5py.File(filePathAndName, mode='w')
        #startRec.hdf5_file = h5py.File(os.path.join(saveFilePathSlash, file_nameH))
        camState = 'recording'
        print('Started Recording')
    except:
        print('Incorrect File Path')
        camState = 'not_recording'
        print('Did Not Begin Recording')

def getFrame():
    global tiff_frame
    global camState
    global maxVal
    global minVal
    data = q.get(True, 500)
    if data is None:
        print('No Data')
    if camState == 'recording':
        startRec.hdf5_file.create_dataset(('image'+str(tiff_frame)), data=data)
        tiff_frame += 1
    #Cannot you cv2.resize on raspberry pi 3b+. Not enough processing power.
    #data = cv2.resize(data[:,:], (640, 480))
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
    img = cv2.LUT(raw_to_8bit(data), generate_colour_map())
    #display_temperature only works if cv2.resize is used
    #display_temperatureK(img, minVal, minLoc, (255, 0, 0)) #displays min temp at min temp location on image
    #display_temperatureK(img, maxVal, maxLoc, (0, 0, 255)) #displays max temp at max temp location on image
    #display_temperatureK(img, minVal, (10,55), (255, 0, 0)) #display in top left corner the min temp
    #display_temperatureK(img, maxVal, (10,25), (0, 0, 255)) #display in top left corner the max temp
    return img

def readTemp(unit, state):
    if state == 'max':
        if unit == 'F':
            return (str(ktof(maxVal)) + ' ' + unit)
        elif unit == 'C':
            return (str(ktoc(maxVal)) + ' ' + unit)
        else:
            print('What are you asking for?')
    elif state == 'min':
        if unit == 'F':
            return (str(ktof(minVal)) + ' ' + unit)
        elif unit == 'C':
            return (str(ktoc(minVal)) + ' ' + unit)
        else:
            print('What are you asking for?')
    elif state == 'none':
        if unit == 'F':
            return (str(ktof(cursorVal)) + ' ' + unit)
        elif unit == 'C':
            return (str(ktoc(cursorVal)) + ' ' + unit)
        else:
            print('What are you asking for?')
    else:
        print('What are you asking for?')

def updateMaxTempLabel():
    if toggleUnitState == 'F':
        return ktof(maxVal)
    elif toggleUnitState == 'C':
        return ktoc(maxVal)
    else:
        print('No Units Selected')

class MyThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        print('Start Stream')
        while True:
            frame = getFrame()
            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
            p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
            self.changePixmap.emit(p)

thread = "unactive"
saveFilePath = ""
fileNamingFull = ""
bFile = ""
class App(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.initUI()
        print('Always Run This Script as ADMIN')

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.displayFrame.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        global fileNamingFull
        self.startRec.clicked.connect(self.startRec2)
        self.stopRec.clicked.connect(self.stopRecAndSave)
        self.startRec.clicked.connect(self.displayRec)
        self.stopRec.clicked.connect(self.displayNotRec)
        self.displayC.clicked.connect(self.dispCDef)
        self.displayF.clicked.connect(self.dispFDef)
        self.runPost.clicked.connect(self.runPostScript)
        self.startStreamBut.clicked.connect(self.startThread)
        self.displayFrame.mousePressEvent = self.on_press

        self.w = QWidget()
        self.filePathBut.clicked.connect(self.getFiles)

        # time display
        self.timer = QTimer(self)
        self.timerFast = QTimer(self)
        self.timer.setInterval(1000)
        self.timerFast.setInterval(10)
        self.timer.timeout.connect(self.displayTime)
        self.timer.timeout.connect(self.displayStorage)
        self.timerFast.timeout.connect(self.displayTempValues)
        self.timer.start()
        self.timerFast.start()

        defaultName = 'IR_HDF5'
        fileNamingFull = defaultName
        self.lineEdit.setText(defaultName)
        self.lineEdit.textChanged.connect(self.fileNaming)
        self.ffcBut.clicked.connect(self.ffcFunction)
        self.comboGain.currentTextChanged.connect(self.gainFunction)
        self.comboFFCmode.currentTextChanged.connect(self.FFCmodeFunction)

        #self.connect(self, SIGNAL('triggered()'), self.closeEvent)

    def gainFunction(self):
        global devh
        global thread
        if thread == 'active':
            if (self.comboGain.currentText() == 'LOW'):
                set_gain_low(devh)
            elif (self.comboGain.currentText() == 'HIGH'):
                set_gain_high(devh)
                #print('Cannot set to back to HIGH yet')
            else:
                set_gain_auto(devh)
                #print('Cannot set to AUTO')

    def FFCmodeFunction(self):
        global devh
        global thread
        if thread == 'active':
            if (self.comboFFCmode.currentText() == 'MANUAL'):
                set_manual_ffc(devh)
            elif (self.comboFFCmode.currentText() == 'EXTERNAL'):
                set_external_ffc(devh)
            else:
                set_auto_ffc(devh)
                #print('Cannot set to back to AUTO yet. Unplug USB from Raspberry Pi to reset lepton.')
        print_shutter_info(devh)

    def ffcFunction(self):
        global devh
        global thread
        if thread == 'active':
            perform_manual_ffc(devh)

    def startRec2(self):
    	global thread
    	global camState
    	global saveFilePath
    	global fileNamingFull
    	if thread == 'active':
    		if camState == 'recording':
    			print('Already Recording')
    		else:
    			if fileNamingFull != "":
    				dateAndTime = str(QDateTime.currentDateTime().toString())
    				dateAndTime = dateAndTime.replace(" ", "_")
    				dateAndTime = dateAndTime.replace(":", "-")
    				filePathAndName = str(fileNamingFull + '_' + dateAndTime + '.HDF5')
    				print(filePathAndName)
    				self.filePathDisp.setText(filePathAndName)
    				try:
    					startRec.hdf5_file = h5py.File(filePathAndName, mode='w')
    					camState = 'recording'
    					print('Started Recording')
    					if saveFilePath == "":
    						self.history.insertPlainText('Saved ' + str(filePathAndName) + ' to ' + os.path.dirname(os.path.abspath(__file__)) + '\n')
    						self.history.moveCursor(QTextCursor.End)
    					else:
    						self.history.insertPlainText('Saved to ' + str(filePathAndName) + '\n')
    						self.history.moveCursor(QTextCursor.End)
    				except:
    					print('Incorrect File Path')
    					camState = 'not_recording'
    					print('Did Not Begin Recording')
    			else:
    				print('No FileName Specified')
    	else:
    		print('Remember to Start Stream')
    		self.history.insertPlainText('Remember to Start Stream\n')
    		self.history.moveCursor(QTextCursor.End)

    def stopRecAndSave(self):
    	global fileNum
    	global tiff_frame
    	global camState
    	global dataCollection
    	if tiff_frame > 1:
    		print('Ended Recording')
    		camState = 'not_recording'
    		try:
    		    startRec.hdf5_file.close()
    		    print('Saved Content to File Directory')
    		    #fileNum += 1
    		except:
    		    print('Save Failed')
    		tiff_frame = 1
    	else:
    		camState = 'not_recording'
    		print('Dont Forget to Start Recording')
    		self.history.insertPlainText('Dont Forget to Start Recording\n')
    		self.history.moveCursor(QTextCursor.End)

    def fileNaming(self):
    	global fileNamingFull
    	bFile = str(self.lineEdit.text())
    	if saveFilePath == "":
    		fileNamingFull = bFile
    		self.filePathDisp.setText('/' + bFile + ' ... Date & Time Will Append at Recording Start')
    	elif saveFilePath != "":
    		fileNamingFull = saveFilePath + '/' + bFile
    		self.filePathDisp.setText(saveFilePath + '/' + bFile + ' ... Date & Time Will Append at Recording Start')
    	else:
    		print('I am Confused')

    def startThread(self):
    	global thread
    	try:
    		if thread == "unactive":
    			try:
    				startStream()
    				self.th = MyThread()
    				self.th.changePixmap.connect(self.setImage)
    				self.th.start()
    				thread = "active"
    				print('Starting Thread')
    			except:
    				print('Failed!!!!')
    				exit(1)
    		else:
    			print('Already Started Camera')
    	except:
    		msgBox = QMessageBox()
    		reply = msgBox.question(self, 'Message', "Error Starting Camera - Plug or Re-Plug Camera into Computer, Wait at Least 10 Seconds, then Click Ok and Try Again.", QMessageBox.Ok)
    		print('Message Box Displayed')
    		if reply == QMessageBox.Ok:
    			print('Ok Clicked')
    		else:
    			event.ignore()

    def runPostScript(self):
    	try:
    		def thread_second():
    	    		call(["python3", postScriptFileName])
    		processThread = threading.Thread(target=thread_second)  # <- note extra ','
    		processThread.start()
    	except:
    		print('Post Processing Script Error - Most Likely Referencing Incorrect File Name')

    def dispCDef(self):
    	global toggleUnitState
    	toggleUnitState = 'C'
    	self.history.insertPlainText('Display ' + str(toggleUnitState) + '\n')
    	self.history.moveCursor(QTextCursor.End)

    def dispFDef(self):
    	global toggleUnitState
    	toggleUnitState = 'F'
    	self.history.insertPlainText('Display ' + str(toggleUnitState) + '\n')
    	self.history.moveCursor(QTextCursor.End)

    def displayTempValues(self):
        #global fileSelected
        global toggleUnitState
        #if fileSelected != "":
        self.maxTempLabel.setText('Current Max Temp: ' + readTemp(toggleUnitState, 'max'))
        #self.maxTempLocLabel.setText('Max Temp Loc: ' + str(maxLoc))
        self.minTempLabel.setText('Current Min Temp: ' + readTemp(toggleUnitState, 'min'))
        #self.minTempLocLabel.setText('Min Temp Loc: ' + str(minLoc))

    def displayTime(self):
        self.timeStatus.setText(QDateTime.currentDateTime().toString())

    def grabTempValue(self):
        global frame
        global lastFrame
        global fileSelected
        global xMouse
        global yMouse
        global thread
        if thread == 'active':
            data = q.get(True, 500)
            data = cv2.resize(data[:,:], (640, 480))
            return data[yMouse, xMouse]
        else:
            self.history.insertPlainText('ERROR: Please Start IR Camera Feed First\n')
            self.history.moveCursor(QTextCursor.End)

    def on_press(self, event):
        global xMouse
        global yMouse
        global cursorVal
        #print('you pressed', event.button, event.xdata, event.ydata)
        try:
            xMouse = event.pos().x()
            yMouse = event.pos().y()
            cursorVal = self.grabTempValue()
            self.cursorTempLabel.setText('Cursor Temp (On Mouse Click): ' + readTemp(toggleUnitState, 'none'))
        except:
            self.history.insertPlainText('ERROR: Please Start IR Camera Feed First\n')
            self.history.moveCursor(QTextCursor.End)

    def displayStorage(self):
        usage = psutil.disk_usage('/')
        oneMinVid = 20000000
        timeAvail = usage.free/oneMinVid
        self.storageLabel.setText('Recording Time Left: ' + str(round(timeAvail, 2)) + ' Minutes')

    def displayRec(self):
    	if camState == 'recording':
            	self.recLabel.setText('Recording')
    	else:
    	   self.recLabel.setText('Not Recording')

    def displayNotRec(self):
        if camState == 'not_recording':
            self.recLabel.setText('Not Recording')
        else:
            self.recLabel.setText('Recording')

    def getFiles(self):
    	global saveFilePath
    	saveFilePath = QFileDialog.getExistingDirectory(self.w, 'Open File Directory', '/')
    	self.filePathDisp.setText(saveFilePath)
    	self.fileNaming()

    def closeEvent(self, event):
        print("Close Event Called")
        if camState == 'recording':
            reply = QMessageBox.question(self, 'Message',
                                         "Recording still in progress. Are you sure you want to quit?", QMessageBox.Yes, QMessageBox.No)
            print('Message Box Displayed')
            if reply == QMessageBox.Yes:
                print('Exited Application, May Have Lost Raw Data')
                event.accept()
            else:
                event.ignore()
        else:
            print('Exited Application')
            event.accept()

def main():
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
