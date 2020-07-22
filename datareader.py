from collections import defaultdict
import struct

class DataReader:
	@classmethod
	def getRawData(cls, s, id):
		x = 0
		licumInfo = defaultdict(list)
		while x < len(s) - 8:
			curId = int(struct.unpack('h', s[x:x + 2])[0])
			curlen = int(struct.unpack('i', s[x + 2:x + 6])[0])
			if curId == 5 and curlen > 0 and curlen < 100000 and curlen % 92 == 0:
				fullRawdataInLine = s[x + 6: x + 6 + curlen]
				for dataSet in range(92, curlen+1, 92):
					rawdataInLine = fullRawdataInLine[dataSet-92:dataSet]
					ind = 0

					numFormat = struct.unpack('i', rawdataInLine[ind:ind+4])[0]
					ind += 4

					nSymbols = struct.unpack('i', rawdataInLine[ind:ind+4])[0]
					ind += 4

					licInUTF8 = []
					for numElem in range(0, 16):
						licInUTF8.append(struct.unpack('h', rawdataInLine[ind:ind+2])[0])
						ind += 2

					allCert = struct.unpack('h', rawdataInLine[ind:ind + 2])[0]
					ind += 2

					certList = []
					cert = ""
					for numElem in range(0, 16):
						crt = struct.unpack('h', rawdataInLine[ind:ind+2])[0]
						certList.append(crt)
						cert += str(crt)
						ind += 2

					xList = []
					for numElem in range(0, 4):
						xList.append(struct.unpack('h', rawdataInLine[ind:ind+2])[0])
						ind += 2

					yList = []
					for numElem in range(0, 4):
						yList.append(struct.unpack('h', rawdataInLine[ind:ind + 2])[0])
						ind += 2

					licum = ""
					for y in licInUTF8[0:nSymbols]:
						licum += struct.pack("h", y).decode("utf-16")
					licumInfo[licum+"_" + str(id)] = licum, numFormat, nSymbols, allCert, cert , xList, yList
				break
			x += 1
		return licumInfo
