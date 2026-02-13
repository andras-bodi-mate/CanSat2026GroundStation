import serial
import time
import datetime
import serial.tools.list_ports
from os import makedirs, path


class LoraLogger:
    def __init__(self, port, baudRate = 115384, parity = serial.PARITY_NONE,
                 stopBits = serial.STOPBITS_ONE, byteSize = serial.EIGHTBITS,
                 timeout = 0):

        self.serialConnection = serial.Serial(
            port = port,
            baudrate = baudRate,
            parity = parity,
            stopbits = stopBits,
            bytesize = byteSize,
            timeout = timeout
        )
        self.lineBuffer = bytearray()

        if not path.exists(f"out"):
            makedirs(f"out")

        self.rawIncomingDataFile = open(f"out\\rawIncomingData.txt", 'a')

    def sendCommand(self, message: str):
        self.serialConnection.write(bytes(f"{message}\r\n", "ascii"))

    def setup(self):
        self.sendCommand("sys get ver")
        time.sleep(0.3)
        self.sendCommand("radio rx 0")

    def readline(self):
        for _ in range(self.serialConnection.in_waiting):
            byte = self.serialConnection.read()
            self.lineBuffer += byte
            if byte == b'\n':
                lineBuffer = self.lineBuffer.copy()
                self.lineBuffer.clear()
                return lineBuffer
        return b''

    def read(self):
        try:
            incomingData: bytes = self.readline()

            if incomingData != b'':
                dateTimeNow = datetime.datetime.now()
                strTimeStamp = f"{dateTimeNow.year}/{dateTimeNow.month:02d}/{dateTimeNow.day:02d} {dateTimeNow.hour:02d}:{dateTimeNow.minute:02d}:{(dateTimeNow.second + dateTimeNow.microsecond/1000000):.6f}"
                strippedData = incomingData.decode().rstrip()
                line = f"[{strTimeStamp}] Received: {strippedData}\n"
                self.rawIncomingDataFile.write(line)
                self.rawIncomingDataFile.flush()
                print(line, end='')
                return bytes(incomingData)

        except BaseException as e:
            print(f"Error during data logging: {e}")

    def close(self):
        self.serialConnection.close()
        print("Serial connection successfully closed")
        self.rawIncomingDataFile.close()
        print("File 'rawIncomingData.txt' successfully closed")

def printAvailablePorts():
    availablePorts = serial.tools.list_ports.comports()

    if len(availablePorts) == 0:
        print("No available ports found. Check connection and try again.")
        exit()

    for port in availablePorts:
        isRecommended = port.description.find("USB Serial Device") != -1
        description = "(recommended)" if isRecommended else ""
        print(f"{port} {description}")
