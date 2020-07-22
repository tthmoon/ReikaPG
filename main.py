#!/usr/bin/env python3
import sys
from PyQt4 import QtCore, QtGui
import time
import os
import struct
import matplotlib
import io
matplotlib.use('QT4Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
from datareader import DataReader as datareader
import calc
from matplotlib.widgets import Slider,  TextBox
import matplotlib.animation as animation
import math
import random
import PIL.Image
import scipy.stats

class MainWindow(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		self.initUI()
		self.setAcceptDrops(True)


	def initUI(self):
		self.additionalDrawCounter = 1
		self.delay = 100
		self.path = os.getcwd()
		self.grid = QtGui.QGridLayout()
		self.grid.setSpacing(10)
		self.indexArray = []
		deviceType = ["IMX 265", "IMX 291"]
		self.infoChooseFile = QtGui.QLabel("Выберите файл обработки")

		self.selectFileButton = QtGui.QPushButton("...")
		self.selectFileButton.clicked.connect(self.selectFile)
		self.selectFileButton.setMaximumWidth(50)
		self.filePathLine = QtGui.QLineEdit()
		self.gridFile = QtGui.QGridLayout()
		self.filePathLine.setMinimumWidth(500)

		self.infoTypes = QtGui.QLabel("TYPES")
		self.deviceTypeList = QtGui.QComboBox()
		self.deviceTypeList.addItems(deviceType)
		self.deviceTypeList.setMaximumWidth(350)

		self.angleLine = QtGui.QLineEdit()
		self.angleLine.setMaximumWidth(350)
		self.angleLine.setText(str(calc.cam_angle))
		self.infoAngle = QtGui.QLabel("ANGLE")

		self.focusLine = QtGui.QLineEdit()
		self.focusLine.setMaximumWidth(350)
		self.focusLine.setText(str(calc.focus))
		self.infoFocus = QtGui.QLabel("FOCUS")

		self.gridFile.addWidget(self.infoChooseFile, 1, 0)
		self.gridFile.addWidget(self.filePathLine, 1, 1)
		self.gridFile.addWidget(self.selectFileButton, 1, 2)
		self.gridFile.addWidget(self.infoTypes, 2, 0)
		self.gridFile.addWidget(self.deviceTypeList, 2, 1)
		self.gridFile.addWidget(self.angleLine, 3, 1)
		self.gridFile.addWidget(self.infoAngle, 3, 0)
		self.gridFile.addWidget(self.focusLine, 4, 1)
		self.gridFile.addWidget(self.infoFocus, 4, 0)

		self.chooseFileGroup = QtGui.QGroupBox("Шаг №1")
		self.chooseFileGroup.setLayout(self.gridFile)
		self.chooseFileGroup.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed))

		self.gridStart = QtGui.QGridLayout()
		self.gridStart.setSpacing(10)
		self.startButton = QtGui.QPushButton("Запустить обработку")
		self.startButton.setStyleSheet("font: bold 10px;padding: 10px;min-width: 10em;")
		self.startButton.clicked.connect(self.startT)


		self.gridStart.addWidget(self.startButton, 1, 1, QtCore.Qt.AlignCenter)

		self.startGroup = QtGui.QGroupBox("Шаг №2")
		self.startGroup.setLayout(self.gridStart)
		self.startGroup.setSizePolicy(
			QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed))


		self.grid.addWidget(self.chooseFileGroup, 1, 0)
		self.grid.addWidget(self.startGroup, 2, 0)

		self.setLayout(self.grid)


	def btnstate(self, b):
		if b.isChecked():
			return 1
		else:
			return 0

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls():
			event.accept()
		else:
			event.ignore()

	def dropEvent(self, event):
		for url in event.mimeData().urls():
			path = url.toLocalFile()
			if os.path.isfile(path):
				self.selectFile(path)

	def selectFile(self, path=None):
		oldContent = self.filePathLine.text()
		if path is False:
			path = QtGui.QFileDialog.getOpenFileName()
		self.filePathLine.setText(path)

	def indexies(self, path):
		self.indexArray.clear()
		self.indexArray.append(0)
		file = io.FileIO(path)
		firstIndex = file.read(8)
		magic = firstIndex[:4]
		firstIndex = firstIndex[4:]

		firstIndex = struct.unpack('i', firstIndex)[0]
		lastIndexIntSum = firstIndex
		lastIndexint = firstIndex
		nextIndex = b''

		if magic == b'\x063"\x11' or magic == b'E3"\x11':
			file.close()
			file = io.FileIO(path)
			TotalSum = 0
			while True:
				nextIndex = file.read(16432)
				jpglen = nextIndex[16396:16400]
				if len(jpglen) != 4:
					break
				try:
					jpglen = int(struct.unpack('i', jpglen)[0])
				except:
					break
				nextIndexSum = jpglen + 16432
				TotalSum = TotalSum + nextIndexSum
				self.indexArray.append(TotalSum)
				toEnd = file.read(jpglen)

		if magic == b'\x073"\x11':
			while b'\xff\xd9' not in nextIndex:
				self.indexArray.append(lastIndexIntSum)
				nextIndex = file.read(lastIndexint)
				nextIndex = nextIndex[-4:]
				try:
					nextIndexint = struct.unpack('i', nextIndex)[0]
				except:
					break
				lastIndexIntSum = lastIndexIntSum + nextIndexint
				lastIndexint = nextIndexint
		file.close()

	def get_cmap(self, n, name='hsv'):
		return plt.cm.get_cmap(name, n)

	def appendLists(self,dict ,number):
		for i in range(0, number):
			dict.append([])
		return dict

	def autoUpdate(self):
		# for x in range(self.player.val, self.framesCount):
		# 	print(x)
		# 	self.player.set_val(x)
		x = self.player.val
		while x < 200:
			if self.updatee(x):
				x+=1
			else:
				time.sleep(0.03)

	def updateChoosenNumbers(self, numbers):
		preparedLicums = defaultdict(list)
		preparedTrends = defaultdict(list)
		val = int(self.player.val)
		cmap = self.get_cmap(50)
		for indx in range(val - self.delay, val):
			# iterr = 0
			if indx in self.preparedLicumsForGraph.keys():
				for licum in numbers:
					licum = licum.split("_")[0]
					if licum in self.preparedLicumsForGraph[indx][0]:
						preparedLicums[licum] = self.appendLists(preparedLicums[licum], 3)
						color = cmap(random.randint(0, 50))
						color = color[:-1] + (color[-1] * 0.5,)
						color = color[:1] + (color[1] * 0.5,) + color[2:]
						preparedLicums[licum][2] = color
						pos = self.preparedLicumsForGraph[indx][0].index(licum)
						preparedLicums[licum][0].append(self.preparedLicumsForGraph[indx][1][pos])
						preparedLicums[licum][1].append(self.preparedLicumsForGraph[indx][2][pos])
						# iterr += 1

		for licum in preparedLicums.keys():
			# a = [it for it, xx in enumerate(preparedLicums[licum][0]) if abs(xx) < 3]
			# x = [preparedLicums[licum][0][xx] for xx in a]
			# y = [preparedLicums[licum][1][xx] for xx in a]
			x = preparedLicums[licum][0]
			y = preparedLicums[licum][1]
			addInfo = ""
			if len(x) > 4:
				uselessPart = round(len(x) * 0.10)
				uselessPartEnd = len(x) - uselessPart
				dataSetX = x
				dataSetY = y
				a, x, y = calc.trend(dataSetX, dataSetY)
				d = calc.fidnDeterm(dataSetX, x, sum(dataSetX) / len(dataSetX))
				fTest = calc.findFCr(d, len(dataSetX), 1)
				angle = math.degrees(math.atan((max(x) - min(x)) / (max(y) - min(y))))
				addInfo = "\na {} \nd {}\nangle {}".format(round(a, 3), round(d, 3), round(angle, 3))
				# if a < 0.3 and d > 0.7 and calc.compareFcr(len(x), 1, fTest):
				angl = math.atan((max(x) - min(x)) / (max(y) - min(y)))
				trkLen = (max(y) - min(y)) / math.cos(angl)

				if a < 0.3 and trkLen > 4:
					preparedTrends[licum + "_trend"] = self.appendLists(preparedTrends[licum + "_trend"], 3)
					preparedTrends[licum + "_trend"][0].extend(x)
					preparedTrends[licum + "_trend"][1].extend(y)
					preparedTrends[licum + "_trend"][2] = "black"
		self.deploy(preparedLicums, preparedTrends)
		return addInfo

	def updatee(self, val):
		preparedLicums = defaultdict(list)
		preparedTrends = defaultdict(list)
		val = int(val)

		if val >= self.framesCount:
			val = 0
			self.player.set_val(0)
		cmap = self.get_cmap(50)

		if time.time() - self.clickTimout > 0.05:
			for indx in range(val-self.delay, val):
				iterr = 0
				if indx in self.preparedLicumsForGraph.keys():
					for licum in self.preparedLicumsForGraph[indx][0]:
						if not len(preparedLicums[licum]):
							preparedLicums[licum] = self.appendLists(preparedLicums[licum], 3)
							if not len(self.lastDict[licum]):
								color = cmap(random.randint(0, 50))
								color = color[:-1] + (color[-1] * 0.5,)
								color = color[:1] + (color[1] * 0.5,) + color[2:]
								preparedLicums[licum][2] = color
							else:
								preparedLicums[licum][2] = self.lastDict[licum][2]
						preparedLicums[licum][0].append(self.preparedLicumsForGraph[indx][1][iterr])
						preparedLicums[licum][1].append(self.preparedLicumsForGraph[indx][2][iterr])

						iterr += 1

			for licum in preparedLicums.keys():
				# a = [it for it, xx in enumerate(preparedLicums[licum][0]) if abs(xx) < 3]
				# x = [preparedLicums[licum][0][xx] for xx in a]
				# y = [preparedLicums[licum][1][xx] for xx in a]
				x = preparedLicums[licum][0]
				y = preparedLicums[licum][1]
				if len(x) > 4:
					uselessPart = round(len(x) * 0.10)
					uselessPartEnd = len(x) - uselessPart
					dataSetX = x
					dataSetY = y
					a, x, y = calc.trend(dataSetX, dataSetY)
					d = calc.fidnDeterm(dataSetX, x, sum(dataSetX) / len(dataSetX))
					fTest = calc.findFCr(d, len(dataSetX), 1)
					# if a < 0.3 and d > 0.7 and calc.compareFcr(len(x), 1, fTest):
					angl = math.atan((max(x) - min(x)) / (max(y) - min(y)))
					trkLen = (max(y) - min(y)) / math.cos(angl)
					if a < 0.3 and trkLen > 4:
						preparedTrends[licum + "_trend"] = self.appendLists(preparedTrends[licum + "_trend"], 3)
						preparedTrends[licum+"_trend"][0].extend(x)
						preparedTrends[licum + "_trend"][1].extend(y)
						preparedTrends[licum+"_trend"][2] = "black"

			self.clickTimout = time.time()
			self.deploy(preparedLicums, preparedTrends)

	def tryFindAngle(self):
		preparedLicums = defaultdict(list)
		for indx in self.preparedLicumsForGraph.keys():
			iterr = 0
			for licum in self.preparedLicumsForGraph[indx][0]:
				if not len(preparedLicums[licum]):
					preparedLicums[licum] = self.appendLists(preparedLicums[licum], 2)
				preparedLicums[licum][0].append(self.preparedLicumsForGraph[indx][1][iterr])
				preparedLicums[licum][1].append(self.preparedLicumsForGraph[indx][2][iterr])
				iterr += 1
		angles = []
		# print(len(preparedLicums.keys()))
		# print(len(preparedLicums.keys()))
		for licum in preparedLicums.keys():
			# a = [it for it, xx in enumerate(preparedLicums[licum][0]) if abs(xx) < 3]
			# x = [preparedLicums[licum][0][xx] for xx in a]
			# y = [preparedLicums[licum][1][xx] for xx in a]
			x = preparedLicums[licum][0]
			y = preparedLicums[licum][1]
			if len(x) > 4:
				uselessPart = round(len(x) * 0.10)
				uselessPartEnd = len(x) - uselessPart
				dataSetX = x
				dataSetY = y
				a, x, y = calc.trend(dataSetX, dataSetY, licum)
				d = calc.fidnDeterm(dataSetX, x, sum(dataSetX)/len(dataSetX))
				fTest = calc.findFCr(d, len(dataSetX), 1)
				angl = math.atan((max(x) - min(x)) / (max(y) - min(y)))
				trkLen = (max(y) - min(y)) / math.cos(angl)

				if a < 0.3 and trkLen > 4:
				# if a < 0.3 and d > 0.7 and f:
					if y[x.index(max(x))] > y[x.index(min(x))]:
						direct = 1
					else:
						direct = -1
					# if math.atan((max(x) - min(x))/(max(y) - min(y))) < 0.872665:
					angles.append(math.atan((max(x) - min(x))/(max(y) - min(y)))*direct)
					# print(math.degrees(angles[-1]))
		if len(angles):
			# print(len(angles))
			anglesInDeg = [math.degrees(xx) for xx in angles]
			self.additionalDraw(anglesInDeg, "track angles")
			self.angle = math.degrees(calc.calcResultAngle1(angles))
		else:
			self.angle = 999


	def test(self):
		for x in range(0, self.framesCount):
			time.sleep(0.03)
			self.q.put(x)

	def changeKey(self, event):
		if event.key == "enter":
			self.updateAngle("test")
		if event.key == "d":
			self.player.set_val(self.player.val+1)
		if event.key == "a":
			self.player.set_val(self.player.val - 1)

	def updateAngle(self,event):
		try:
			angleCorrected = float(self.angleField.text) - calc.cam_angle
			angleReal = float(self.angleField.text)

		except:
			self.angleField.set_val("error")
			return

		calc.cam_angle = angleCorrected
		for ind in self.preparedLicumsForGraph.keys():
			iterr = 0
			for licum in self.preparedLicumsForGraph[ind][0]:
				self.preparedLicumsForGraph[ind][1][iterr], self.preparedLicumsForGraph[ind][2][iterr] = calc.correctCoordsWithAngle(self.preparedLicumsForGraph[ind][1][iterr], self.preparedLicumsForGraph[ind][2][iterr])
				iterr += 1
		calc.cam_angle = angleReal
		self.updatee(self.player.val)

	def additionalDraw(self, data, name):
		fig = plt.figure(self.additionalDrawCounter)
		ax = fig.add_subplot(111)
		ax.set_title(name)
		# self.fig, self.ax = self.plt.subplots()
		ax.grid(True)
		fig.tight_layout()
		ax.scatter(range(0, len(data)), data, s=50, color="green")
		self.additionalDrawCounter += 1


	def drawGraph(self):
		self.pill2kill = True
		self.clickTimout = 0
		self.plt = plt

		self.fig = self.plt.figure(self.additionalDrawCounter)
		self.ax = self.fig.add_subplot(111)
		# self.fig, self.ax = self.plt.subplots()
		self.ax.clear()
		self.fig.tight_layout()
		self.ax.set_autoscaley_on(False)
		# self.ax.callbacks.connect('xlim_changed', self.axLimsChange)
		# self.ax.callbacks.connect('ylim_changed', self.axLimsChange)
		self.plt.axis([0, 1, -11, 11])
		self.plt.autoscale(False)

		axSlider = self.fig.add_axes([0.1, 0.005, 0.65, 0.03])
		# self.axCheckboxAS = self.fig.add_axes([0.05, 0.005, 0.05, 0.03], facecolor="red")
		self.axAngleField = self.fig.add_axes([0.85, 0.005, 0.05, 0.03])
		# self.axChangeButton = self.fig.add_axes([0.91, 0.005, 0.05, 0.03])

		self.player = Slider(axSlider, 'Time line', 0, self.framesCount, valinit=0, valfmt='%0.0f')
		# self.autostartWidget = CheckButtons(self.axCheckboxAS, ['Autostart'], [0])
		self.angleField = TextBox(self.axAngleField, "Angle")
		self.angleField.set_val(round(self.angle,3))
		# self.changeButton = Button(self.axChangeButton, "update")
		# self.changeButton.on_clicked(self.updateAngle)

		self.player.on_changed(self.updatee)

		self.fig.canvas.mpl_connect('key_press_event', self.changeKey)
		# self.fig.canvas.mpl_connect('button_press_event', self.checkAutostart)
		self.fig.canvas.mpl_connect('pick_event', self.onpick)
		self.fig.canvas.mpl_connect('button_press_event', self.onclick)
		self.xlims = [-35, 35]
		self.ylims = [-10, 60]
		self.ax.set_xlim(self.xlims)
		self.ax.set_ylim(self.ylims)
		self.updatee(0)
		self.plt.get_current_fig_manager().window.showMaximized()
		self.plt.show()
		self.additionalDrawCounter += 1

		# ani = animation.FuncAnimation(self.fig, self.autoUpdate, interval=300)

	def onclick(self, event):
		if event.dblclick:
			x, y = event.xdata , event.ydata
			self.ax.plot([0, x], [0, y], color="green", picker=2, label="additional line")
			self.textBox.set_text(
				"X: {}\nY: {}\nDIST: {}\nANGLE: {}".format(x, y, round(math.sqrt(x**2 + y**2), 3), math.degrees(math.atan(x/ y))))
			self.plt.draw()

	def onpick(self, event):
		thisline = event.artist
		ind = event.ind
		xdata = []
		ydata = []
		label = []
		dist = []
		for x in ind[:5]:
			xdata.append(round(thisline.get_xdata()[x], 3))
			ydata.append(round(thisline.get_ydata()[x], 3))
			dist.append(round(math.sqrt(xdata[-1]**2 + ydata[-1]**2), 3))
			label.append(thisline.get_label())
		addInfo = self.updateChoosenNumbers(label)
		self.textBox.set_text(
			"X: {}\nY: {}\nDIST: {}\nLINE: {}{}".format(xdata, ydata, dist, label, addInfo))
		self.plt.draw()

	def deploy(self, preparedTargets, trends):
		self.xlims = self.ax.get_xlim()
		self.ylims = self.ax.get_ylim()
		self.lastDict = preparedTargets
		self.ax.clear()
		self.plt.ion()
		self.ax.set_xlabel("X")
		self.ax.set_ylabel("Y")
		self.ax.set_title(self.fileForProcessing)
		self.ax.set_xlim(self.xlims)
		self.ax.set_ylim(self.ylims)
		self.props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
		self.textBox = self.ax.text(0.01, 0.98, str("NONE"),
									transform=self.ax.transAxes,
									fontsize=14,
									verticalalignment="top",
									bbox=self.props)
		for licum in preparedTargets.keys():
			self.ax.plot(preparedTargets[licum][0], preparedTargets[licum][1], '-o', color=preparedTargets[licum][2],  alpha=0.8, picker=5, label=licum)
		if len(trends.keys()):
			for licum in trends.keys():
				self.ax.plot(trends[licum][0], trends[licum][1], color=trends[licum][2],  picker=2, label=licum)

		self.ax.scatter(0, 0, color="green", s=100, picker=5, label="CAMERA")

		self.ax.grid(True)
		self.ax.legend(loc="upper right")
		self.plt.draw()
		self.plt.show()

	def setAngle(self):
		try:
			angle = float(self.angleLine.text())

		except:
			self.angleLine.setText("ERROR")
			return
		calc.cam_angle = angle

	def setFocus(self):
		try:
			focus = float(self.focusLine.text())

		except:
			self.focusLine.setText("ERROR")
			return
		calc.focus = focus

	def getImageSize(self, bdata):
		jpe = io.BytesIO(bdata)
		ima = PIL.Image.open(jpe)
		calc.setImageSize(ima.size[0], ima.size[1])

	def rawSearch(self):
		inputpath = self.fileForProcessing
		filerc = io.FileIO(inputpath)
		magic = filerc.read(4)
		filerc.close()
		self.preparedLicumsForGraph = defaultdict(list)
		self.framesCount = len(self.indexArray) - 2
		self.setAngle()
		self.setFocus()
		calc.setMatrixType(self.deviceTypeList.currentIndex())
		calc.getHalfOfMaxAngle()
		if magic == b'\x073"\x11':
			# filerc = io.FileIO(inputpath)
			# frameLen = self.indexArray[1] - self.indexArray[0]
			# rcFrame = filerc.read(frameLen)
			# startMarker = rcFrame.find(b'\xff\xd8')
			# self.getImageSize(rcFrame[startMarker:])
			filerc = io.FileIO(inputpath)
			for ind in range(0, self.framesCount):
				##Открытие рс и чтение его через IO контейнер(начало и длина региона)
				frameLen = self.indexArray[ind + 1] - self.indexArray[ind]
				rcFrame = filerc.read(frameLen)
				startMarker = rcFrame.find(b'\xff\xd8')
				radarData = rcFrame[:startMarker]

				licumsList = datareader.getRawData(radarData, ind)
				for target in licumsList.keys():

					xCoord, yCoord = calc.getLicumCoordsInMetersAlterN(licumsList[target][5], licumsList[target][6], licumsList[target][0], ind)
					if xCoord == None:
						continue
					self.preparedLicumsForGraph[ind] = self.appendLists(self.preparedLicumsForGraph[ind], 3)
					self.preparedLicumsForGraph[ind][0].append(licumsList[target][0])
					self.preparedLicumsForGraph[ind][1].append(xCoord)
					self.preparedLicumsForGraph[ind][2].append(yCoord)

		self.tryFindAngle()
		# self.delay = self.framesCount
		calc.cam_angle = 0
		self.delay = 500
		self.drawGraph()

	def startT(self):
		self.fileForProcessing = self.filePathLine.text().replace("\\", "/")
		self.nameOfFileForProcessing = self.filePathLine.text().replace("\\", "/").rsplit(".", 1)[0]
		self.indexies(self.fileForProcessing)
		self.rawSearch()

def main():
	app = QtGui.QApplication(sys.argv)
	app.setWindowIcon(QtGui.QIcon('icon.png'))
	GUI = MainWindow()
	GUI.show()
	os._exit(app.exec_())

if __name__ == '__main__':
	calc = calc.Calc()
	main()