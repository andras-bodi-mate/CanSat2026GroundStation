import pyqtgraph as pg
import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
from datetime import datetime
from data import MessageType, recievedPackets
from time import time
from random import random

pg.mkQApp()
startTime = datetime.now()

class LivePlot:
    plots = []
    def __init__(self, window: pg.GraphicsLayoutWidget, title, bufferDuration):
        self.timeBuffer = []
        self.bufferDuration = bufferDuration

        self.plot: pg.PlotItem = window.addPlot(title = title)
        self.plot.showGrid(y = True)

        LivePlot.plots.append(self)

    def getKeepIndex(self):
        if len(self.timeBuffer) > 0:
            maxTime = max(self.timeBuffer)
        else:
            return 0

        keepIndex = 0
        for time in self.timeBuffer:
            if (maxTime - time) > self.bufferDuration:
                keepIndex += 1
            else:
                break
        return keepIndex

class SingleLineLivePlot(LivePlot):
    def __init__(self, window, title, bufferDuration, lineColor):
        super().__init__(window, title, bufferDuration)

        self.dataBuffer = []
        self.curve = self.plot.plot(pen = lineColor)

    def update(self):
        self.curve.setData(x = self.timeBuffer, y = self.dataBuffer)

    def removeOldReadings(self):
        keepIndex = self.getKeepIndex()

        if keepIndex == 0:
            return
        
        self.timeBuffer = self.timeBuffer[keepIndex:]
        self.dataBuffer = self.dataBuffer[keepIndex:]

    def appendReading(self, timestamp, reading):
        self.timeBuffer.append(timestamp)
        self.dataBuffer.append(reading)

class MultiLineLivePlot(LivePlot):
    def __init__(self, window, title, bufferDuration, numLines, lineColors):
        super().__init__(window, title, bufferDuration)
        self.numLines = numLines
        self.dataBuffers = [[] for _ in range(numLines)]

        self.curves = []
        for lineIndex in range(self.numLines):
            self.curves.append(self.plot.plot(pen = lineColors[lineIndex]))

    def update(self):
        for curveIndex in range(self.numLines):
            self.curves[curveIndex].setData(x = self.timeBuffer, y = self.dataBuffers[curveIndex])

    def removeOldReadings(self):
        keepIndex = self.getKeepIndex()

        if keepIndex == 0:
            return
        
        self.timeBuffer = self.timeBuffer[keepIndex:]
        for lineIndex in range(self.numLines):
            self.dataBuffers[lineIndex] = self.dataBuffers[lineIndex][keepIndex:]

    def appendReading(self, timestamp, reading):
        self.timeBuffer.append(timestamp)
        for lineIndex in range(self.numLines):
            self.dataBuffers[lineIndex].append(reading[lineIndex])

class TopDownLivePlot(SingleLineLivePlot):
    def __init__(self, window, title, lineColor):
        super().__init__(window, title, 0, lineColor)
        self.plot.showGrid(x = True, y = True)
        self.plot.getViewBox().setAspectLocked(True)

        image = qtg.QImage("C:\\Users\\bodit\\Documents\\Python Projects\\CanSat2025GroundStation\\test.jpeg", "jpeg")
        image.convertToFormat(qtg.QImage.Format.Format_ARGB32_Premultiplied)
        imageArray = pg.imageToArray(image, copy = True)[:,::-1,:]
        imageItem = pg.ImageItem(imageArray)
        self.plot.addItem(imageItem)
        imageItem.setZValue(-100)
        imageItem.setRect(qtc.QRectF(0, 0, 1, 1))

        viewBox = self.plot.getViewBox()
        viewBox.sigRangeChanged.connect(lambda view, visibleRange: print(visibleRange))

    def update(self):
        return super().update()

    def removeOldReadings(self):
        pass

    def appendReading(self, latitude, longitude):
        return super().appendReading(latitude, longitude)

class Plotter:
    def __init__(self, readDataFunc):
        self.readDataFunc = readDataFunc
        self.lastNumRecievedPackets = 0
        self.timeOrigin = time()
        pg.setConfigOptions(antialias = False)
        print(f"Time used for origin: {self.timeOrigin} ({datetime.fromtimestamp(self.timeOrigin)})")


    def start(self):
        window = pg.GraphicsLayoutWidget(show=True, title="Sensor Readings")

        temperaturePlot = SingleLineLivePlot(window, "Temperature", 30, (255, 100, 0))
        airPressurePlot = SingleLineLivePlot(window, "Air pressure", 30, (0, 255, 100))
        window.nextRow()
        latLonPlot = TopDownLivePlot(window, "Top-down position", (0, 230, 230))
        altitudePlot = SingleLineLivePlot(window, "Altitude", 60, (255, 255, 255))

        def updatePlots():
            for plot in LivePlot.plots:
                plot.removeOldReadings()

            numPackets = len(recievedPackets)
            numNewPackets = numPackets - self.lastNumRecievedPackets
            self.lastNumRecievedPackets = numPackets

            if numNewPackets == 0:
                return
            
            for packet in recievedPackets[-numNewPackets:]:
                packetSendTimeSeconds = packet.sendTime / 1000

                if packet.messageType == MessageType.PrimaryData:
                    temperaturePlot.appendReading(packetSendTimeSeconds, packet.temperature)
                    airPressurePlot.appendReading(packetSendTimeSeconds, packet.humidity)
                    altitudePlot.appendReading(packetSendTimeSeconds, 101 + random() * 5)
                #else:
                    #latLonPlot.appendReading(packet.latitude, packet.longitude)
                    #altitudePlot.appendReading(packetSendTimeSeconds, packet.altitude)

            for plot in LivePlot.plots:
                plot.update()

        timer = qtc.QTimer()
        timer.timeout.connect(updatePlots)
        timer.start(100)

        data_timer = qtc.QTimer()
        data_timer.timeout.connect(self.readDataFunc)
        data_timer.start(50)


        pg.mkQApp().exec()