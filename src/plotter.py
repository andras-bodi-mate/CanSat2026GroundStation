import pyqtgraph as pg
import PyQt6.QtCore as qtc
from datetime import datetime
from data import MessageType, PacketHandler
from time import time
from random import random

from core import Core
from plots import LivePlot, SingleLineLivePlot, GpsLivePlot

pg.setConfigOptions(antialias=True)
pg.mkQApp()
startTime = datetime.now()

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
        latLonPlot = GpsLivePlot(window, "Top-down position", (0, 230, 230))
        altitudePlot = SingleLineLivePlot(window, "Altitude", 60, (255, 255, 255))

        def updatePlots():
            for plot in LivePlot.plots:
                plot.removeOldReadings()

            numPackets = len(PacketHandler.recievedPackets)
            numNewPackets = numPackets - self.lastNumRecievedPackets
            self.lastNumRecievedPackets = numPackets

            if numNewPackets == 0:
                return
            
            for packet in PacketHandler.recievedPackets[-numNewPackets:]:
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