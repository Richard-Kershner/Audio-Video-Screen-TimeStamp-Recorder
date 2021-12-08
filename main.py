# pyCharm and pyQT5 require significant setup
# https://pythonpyqt.com/how-to-install-pyqt5-in-pycharm/
# install pyqt5. pyqt5-sip, pyqt5-tools for use with pycharm
# PyCharm select File | Settings | Tools | PyCharm. External Tools, click + New Tools, Create QTdesigner and PyUIC tools

from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton
from PyQt5.QtGui import QPixmap

import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread

import os
import rec_audio
import rec_webcam

from multiprocessing import shared_memory, Process

from datetime import datetime, timedelta
import time

def newRecDir(**kwargs):
    fullPath = os.getcwd() + '\\'
    if 'path' in kwargs:
        fullPath = kwargs("path")
        if kwargs("path")[-1] != "\\":
            fullPath += '\\'

    now = datetime.now().date()
    now = str(now)
    now = "_" + now.replace("-","_")

    c = 97 # 97 to 122 is a-z
    while os.path.isdir(fullPath + now + "_" + chr(c)):
        c += 1
        if c > 122:
            now += "_"
            c = 97
    now += "_" + chr(c)

    print(fullPath, now)
    if fullPath[1] == ":": # must remove the c: drive designation crashes????
        os.mkdir(fullPath[2:] + now)
    else:
        os.mkdir(fullPath+ now)

    fullPath += now
    return fullPath

def startRecording(rec_controls):
    timeNow = (datetime.now() + timedelta(0, 3))
    timeSecond = timeNow.second
    # timeMinute = timeNow.minute
    print("start Second in startRecording", timeSecond)
    rec_controls[0] = 1  # start recording

def stopRecording(rec_controls):
    timeNow = (datetime.now() + timedelta(0, 3)) # set the stop recording
    timeSecond = timeNow.second
    #timeMinute = timeNow.minute
    rec_controls[1] = timeSecond  # end recording
    # rec_controls[2] = timeMinute
    rec_controls[0] = 0 # end recording recording
    print("stop second in stopRecording", datetime.now().second)

def close_ProcsMem(runningProcs, rec_controls_sm):
    for process in runningProcs:
        while process.is_alive():
            time.sleep(.2)
        process.join()
        process.terminate()
    time.wait(4)
    rec_controls_sm.close()
    rec_controls_sm.unlink()

class userInterface(QWidget):
    def __init__(self, rec_controls, runningProcs):
        super().__init__()
        self.setFixedHeight(300)
        self.setFixedWidth(600)
        self.rec_controls = rec_controls
        self.runningProcs = runningProcs
        #self.buttRecordStartPauseStop.clicked.connect(self.startStopPause)

        self.lay_controls = QHBoxLayout()
        self.butt_stopRec = QPushButton('stop recording')
        self.butt_stopRec.clicked.connect(self.stopRecording)
        self.lay_controls.addWidget(self.butt_stopRec)
        self.setLayout(self.lay_controls)

        for process in runningProcs:
            process.start()

        # embed in GUI to start recording
        startRecording(rec_controls)

    def startRecording(self):
        startRecording(self.rec_controls)
    def stopRecording(self):
        stopRecording(self.rec_controls)

    def closeEvent(self):
        print("closing user interface")
        close_ProcsMem(runningProcs, rec_controls_sm)


if __name__ == '__main__':

    saveFilesPath = newRecDir()

    init_rec_controls = [0,99,99] # max 255 int8
    rec_controls_sm = shared_memory.SharedMemory(create=True, size=len(init_rec_controls))
    rec_controls = rec_controls_sm.buf
    rec_controls[:] = bytearray(init_rec_controls)

    audioDevice = 1
    webCamDevice = 1

    runningProcs = []

    runningProcs.append(Process(target= \
            rec_audio.runCapture, args=(audioDevice, rec_controls_sm, saveFilesPath)))
    runningProcs.append(Process(target= \
            rec_webcam.runCapture, args=(webCamDevice, rec_controls_sm, saveFilesPath)))
    runningProcs.append(Process(target= \
            rec_webcam.runCapture, args=(2, rec_controls_sm, saveFilesPath)))

    # replace start and end recording with user interface
    app = QApplication(sys.argv)
    a = userInterface(rec_controls, runningProcs)
    a.show()
    sys.exit(app.exec_()) # auto shuts without this








