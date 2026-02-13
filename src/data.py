from time import time
import re

class MessageType:
    PrimaryData = 0
    SecondaryData = 1

class Packet:
    @staticmethod
    def toHexStr(char):
        return hex(ord(char))[2:]

class Packet:
    integerCapturePattern = r"(\d+)"
    decimalPattern = r"\d+(?:\.\d+)"
    payloadCapturePattern = rf"((?:{decimalPattern},)+{decimalPattern})"
    pattern = re.compile(rf"^\[{integerCapturePattern}\]\({integerCapturePattern}\)/(1|2),{payloadCapturePattern}$") # Captures the following: [%i](%i)/%i,%f,%f,%f...

    @staticmethod
    def trimData(data: str):
        # HACK THIS IS A VERY BAD FIX. REMOVE BEFORE COMMIT
        return data[9:].strip() # Previously was 10

    @staticmethod
    def decodeHexStr(hexStr: str):
        groups = [hexStr[2*i] + hexStr[2*i+1] for i in range(len(hexStr)//2)]
        ints = [int(s, 16) for s in groups]
        chars = [chr(i) for i in ints]
        output = ''.join(chars)
        return output
    
    @staticmethod
    def validateHexStr(hexStr: str):
        if hexStr == None:
            return False
        try:
            decoded = Packet.decodeHexStr(hexStr)
        except:
            print("Error: Couldn't decode hex string")
            return False
        if len(decoded) < 8:
            return False
        print(decoded)
        result = Packet.pattern.match(decoded)
        if not result or len(result.groups()) < 4:
            return False
        return True
    
    @staticmethod
    def vecToStr(vec):
        return ','.join(map(str, vec))

    def __init__(self, hexStr: str):
        self.messageIndex = -1
        self.messageType = 0
        self.temperature = 0.0
        self.humidity = 0.0
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0

        recieveTime = time()
        decoded: str = Packet.decodeHexStr(hexStr)
        result = Packet.pattern.match(decoded)

        self.messageIndex = int(result.group(1))
        self.sendTime = int(result.group(2))
        self.messageType = MessageType.PrimaryData if result.group(3) == "1" else MessageType.SecondaryData
        messagePayload = result.group(4).split(',')

        if self.messageType == MessageType.PrimaryData:
            self.temperature = float(messagePayload[0])
            self.humidity = float(messagePayload[1])
        else:
            self.latitude = float(messagePayload[0])
            self.longitude = float(messagePayload[1])
            self.altitude = float(messagePayload[2])

        self.recieveTime = recieveTime

    def toString(self):
        if self.messageType == MessageType.PrimaryData:
            return f"type: primary, index: {self.messageIndex}, send time: {self.sendTime}, temperature: {self.temperature}, humidity: {self.humidity}"
        else:
            return f"type: secondary, index: {self.messageIndex}, send time: {self.sendTime}, latitude: {self.latitude}, longitude: {self.longitude}, altitude: {self.altitude}"

    def __repr__(self):
        return f"({self.toString()})"

recievedPackets: list[Packet] = []

class PacketHandler:
    def __init__(self):
        self.recievedPacketsFile = open("out\\recievedPackets.txt", "a")

    def close(self):
        self.recievedPacketsFile.close()
        print("File 'recievedPackets.txt' successfully closed.")

    def storeNewPacket(self, packet):
        recievedPackets.append(packet)
    
    def saveNewPacketToFile(self, packet):
        self.recievedPacketsFile.write(f"{packet.toString()}\n")

    def handleData(self, data):
        hexStr = Packet.trimData(data.decode())
        if Packet.validateHexStr(hexStr):
            packet = Packet(hexStr)
            print(packet)
            self.storeNewPacket(packet)
            self.saveNewPacketToFile(packet)
        else:
            print("Invalid packet, skipping")
