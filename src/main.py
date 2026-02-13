from loraLogger import LoraLogger, printAvailablePorts
from wakepy import keep
from data import PacketHandler
from plotter import Plotter

print("Available ports:")
printAvailablePorts()
port = input("Enter the port the LoRa is connected to: ").strip()

packetHandler = PacketHandler()

def loop():
    data = loraLogger.read()
    if data == None:
        return

    packetHandler.handleData(data)

loraLogger = LoraLogger(port)
plotter = Plotter(loop)

loraLogger.setup()

with keep.presenting():
    plotter.start()

loraLogger.close()
packetHandler.close()