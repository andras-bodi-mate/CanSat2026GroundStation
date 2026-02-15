import pyqtgraph as pg
import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import requests

from core import Core

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

    def update(self):
        return super().update()

    def removeOldReadings(self):
        pass

    def appendReading(self, latitude, longitude):
        return super().appendReading(latitude, longitude)
    
class GpsLivePlot(TopDownLivePlot):
    def __init__(self, window, title, lineColor):
        super().__init__(window, title, lineColor)

        image = qtg.QImage(Core.getPath("test.jpeg").as_posix(), "jpeg")
        image.convertToFormat(qtg.QImage.Format.Format_ARGB32_Premultiplied)
        imageArray = pg.imageToArray(image, copy = True)[:,::-1,:] # Flip on horizontal axis
        imageItem = pg.ImageItem(imageArray)
        self.plot.addItem(imageItem)
        imageItem.setZValue(-100)
        imageItem.setRect(qtc.QRectF(0, 0, 1, 1))

        viewBox = self.plot.getViewBox()
        viewBox.sigRangeChanged.connect(self.onRangeChanged)

    def onRangeChanged(self, view, visibleRange):
        pass


# url = "https://nta-map.fomi.hu/orto/service.php?project=xwG12A&SERVICE=WMTS&VERSION=1.0.0&REQUEST=GetTile&LAYER=ortofoto_lf&STYLE=default&TILEMATRIXSET=EOV&TILEMATRIX=9&TILEROW=73&TILECOL=511&FORMAT=image/jpeg"

# headers = {
#     "Referer": "https://nta-map.fomi.hu/orto/",
#     "User-Agent": "Mozilla/5.0"
# }

# response = requests.get(url = url, headers = headers)
# with open(Core.getPath("test2.jpeg"), 'wb') as file:
#     file.write(response.content)