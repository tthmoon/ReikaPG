import math
import numpy as np
import scipy.stats
from collections import defaultdict

class Calc:
	def __init__(self):
		self.focus = 8
		# self.radar_angle = -14
		self.cam_angle = 0
		# const_kai = 192.2
		# pixel_kai = 0.0055
		self.pixelMatrixImx265 = 0.00345
		self.pixelMatrixImx291 = 0.0029
		self.licNumSizeInMeters8 = 0.445
		self.licNumSizeInMeters9 = 0.46
		self.pxlSizeXInMeters = 0
		self.pxlSizeYInMeters = 0
		self.licNumSizeInMeters = 0
		self.matrixPxl = 0
		self.imageX = 0
		self.imageY = 0
		self.mid = 0

	def getLicumLikeDot(self, xList, yList):
		xMax = max(xList)
		xMin = min(xList)
		yMax = max(yList)
		yMin = min(yList)
		if self.imageX/2 < xMin:
			corner = xMax
		else:
			corner = xMin
		return xMin + (xMax-xMin)/2,  yMin + (yMax-yMin)/2, corner

	def correctCoordsWithAngle(self, x, y):
		x = float(x)
		y = float(y)
		if self.cam_angle < 0:
			xCor = x*math.cos(abs(math.radians(self.cam_angle))) - y*math.sin(abs(math.radians(self.cam_angle)))
			yCor = x * math.sin(abs(math.radians(self.cam_angle))) + y * math.cos(abs(math.radians(self.cam_angle)))
		else:
			xCor = x * math.cos(abs(math.radians(self.cam_angle))) + y * math.sin(abs(math.radians(self.cam_angle)))
			yCor = -x * math.sin(abs(math.radians(self.cam_angle))) + y * math.cos(abs(math.radians(self.cam_angle)))
		return xCor, yCor

	def getLicumCoordsInMeters(self, xList, yList, licum, id):
		x, y = self.getLicumLikeDot(xList, yList)
		if(x - self.mid) == 0:
			x += 1
		self.setLicSize(len(licum))
		self.setImageSize(1920, 1080)

		xOnMtx = (x - self.mid)*self.matrixPxl
		xAngle = math.atan(xOnMtx/self.focus)
		# print(math.degrees(xAngle))
		self.pxlSizeXInMeters = self.licNumSizeInMeters / ((max(xList) - min(xList))/math.cos(xAngle + math.radians(self.cam_angle)))
		distInMeters = self.focus / self.matrixPxl * self.pxlSizeXInMeters

		xInMeters = distInMeters * math.sin(xAngle + math.radians(self.cam_angle))
		yInMeters = distInMeters * math.cos(xAngle + math.radians(self.cam_angle))
		# xInMeters = self.pxlSizeXInMeters * (x - self.mid)/math.cos(xAngle + math.radians(self.cam_angle))
		# yInMeters = abs(xInMeters / math.tan(xAngle+ math.radians(self.cam_angle)))
		# print("n{} {}  {} f{}".format(xInMeters, yInMeters, math.degrees(xAngle), id))
		return xInMeters, yInMeters

	def getLicumCoordsInMetersAlter(self, xList, yList, licum, id):
		x, y, c = self.getLicumLikeDot(xList, yList)
		if (x - self.mid) == 0:
			x += 1
		self.setLicSize(len(licum))
		self.setImageSize(1920, 1080)
		size_x = self.imageX * self.matrixPxl
		angle_between_mid_edge = math.atan(size_x / 2 / self.focus)
		# print(math.degrees(angle_between_mid_edge))


		# print(self.cam_angle)
		xAngle = (abs(x) - self.imageX / 2) * angle_between_mid_edge / self.imageX*2
		# print(math.degrees(xAngle))
		fw = (max(xList) - min(xList)) / math.cos(xAngle + math.radians(self.cam_angle))
		gdist = self.focus / self.matrixPxl * self.licNumSizeInMeters / fw
		gx = gdist * math.sin(xAngle + math.radians(self.cam_angle))
		gy = gdist * math.cos(xAngle + math.radians(self.cam_angle))

		return gx, gy


	def getHalfOfMaxAngle(self):
		self.setImageSize(1920, 1080)
		self.angleBeetweenMiddAndAdge = math.atan(self.matrixPxl * (self.imageX / 2) / self.focus)

	def getLicumCoordsInMetersAlterN(self, xList, yList, licum, id):
		camAngle = math.radians(self.cam_angle)
		self.setLicSize(len(licum))
		x, y, licNearCorner = self.getLicumLikeDot(xList, yList)
		size_x = self.imageX * self.matrixPxl

		xAngle = math.atan(self.matrixPxl * (x - self.imageX/2) / self.focus)
		if abs(xAngle) > 0.7 * self.angleBeetweenMiddAndAdge:
			return None, None
		# print(math.degrees(xAngle) + self.cam_angle)
		fw = (max(xList) - min(xList))
		# self.pxlSizeXInMeters = (self.licNumSizeInMeters / math.cos(xAngle + math.radians(self.cam_angle))) / fw
		# self.pxlSizeXInMeters = (self.licNumSizeInMeters) / (fw * math.cos(xAngle + math.radians(self.cam_angle)))
		# self.pxlSizeXInMeters = (self.licNumSizeInMeters * math.cos(xAngle)) / fw
		self.pxlSizeXInMeters = self.licNumSizeInMeters / (fw * math.cos(xAngle) * math.cos(camAngle))

		gy = (self.focus/(size_x/2)) * ((self.imageX/2) * self.pxlSizeXInMeters)
		# gdist = gy / math.cos(xAngle)
		# gx = gdist * math.sin(xAngle)
		# gx = gy * math.tan(xAngle + math.radians(self.cam_angle))
		gx = gy * math.tan(xAngle)
		# return self.correctCoordsWithAngle(gx, gy)
		return gx, gy
		# return gxExp, gyExp

	def setImageSize(self, x, y):

		self.imageX = x
		self.imageY = y
		self.mid = self.imageX//2

	def setMatrixType(self, mtx):
		if mtx == 0:
			self.matrixPxl = self.pixelMatrixImx265
		elif mtx == 1:
			self.matrixPxl = self.pixelMatrixImx291

	def setLicSize(self, s):
		if s == 8:
			self.licNumSizeInMeters = self.licNumSizeInMeters8
		else:
			self.licNumSizeInMeters = self.licNumSizeInMeters9

	def fidnDeterm(self, y, yf, ym):
		top = [(yf[x] - ym)*(yf[x] - ym)for x in range(0, len(y))]
		bottom = [(y[x] - ym)*(y[x] - ym)for x in range(0, len(y))]
		return sum(top)/sum(bottom)

	def findFCr(self, d, n, m):
		return (d/(1-d))*((n-m-1)/m)

	def compareFcr(self, n, m, f):
		return f > scipy.stats.f.ppf(q=1-0.05, dfn=m, dfd=n)

	def trend(self, yList, t, licnum = ""):

		n = len(yList)
		tt = [x*x for x in t]
		ty = [t[x]*yList[x] for x in range(0, len(yList))]

		b = (n*sum(ty) - sum(yList)*sum(t))/(sum(tt)*n - sum(t) * sum(t))
		a = (sum(yList) - b*sum(t))/n
		yCalc = [(x*b + a) for x in t]
		# print(yList)
		subCalcForA = [abs((yList[x]-yCalc[x])/yList[x]) for x in range(0, len(yList)) if abs(yList[x]) >= 0.3]
		if licnum == "о003ур78":
			[print("{} {} {}".format(abs((yList[x] - yCalc[x]) / yList[x]), yList[x], yCalc[x])) for x in range(0, len(yList)) if abs(yList[x]) >= 0.3]
			# [print(abs((yList[x] - yCalc[x]))) for x in range(0, len(yList)) if yList[x] != 0]
		A = sum(subCalcForA)/n
		return A, yCalc, t

	def calcResultAngle1old(self, angles):
			deltaInRad = 0.0174533
			result = self.calcSimpleAvarage(angles)
			alter = self.calcSimpleAvarage(angles)
			for angle in angles:
				# print(math.degrees(angle))
				diff = abs(result-angle)
				if diff > deltaInRad:
					a = 0.9
				else:
					a = 0.1
				b = 1 - a
				# print("andgle {} result {} perc {}".format(math.degrees(angle), math.degrees(result), a))
				result = result * a + angle*b
			# print("{} {} ".format(math.degrees(result), math.degrees(alter)))
			# if abs(result) > abs(alter):
			# 	result = alter
			return result

	def calcResultAngle1(self, angles):
		anglesInLists = defaultdict()
		deltaInRad = 0.0174533
		result = self.calcSimpleAvarage(angles)
		alter = self.calcSimpleAvarage(angles)
		for angle in angles:
			angleInDeg = math.degrees(angle)
			angleInDegRounded = round(angleInDeg)
			if angleInDegRounded in anglesInLists.keys():
				anglesInLists[angleInDegRounded] += 1
			else:
				anglesInLists[angleInDegRounded] = 1
		xf = 0
		f = 0
		print(anglesInLists)
		for angle in angles:
			angleInDeg = math.degrees(angle)
			angleInDegRounded = round(angleInDeg)
			xf += angle * anglesInLists[angleInDegRounded]
			f += anglesInLists[angleInDegRounded]
		result = xf/f
		print("{} {}  {}".format(math.degrees(result), math.degrees(alter), math.degrees(self.calcResultAngle1old(angles))))
		# if abs(result) > abs(alter):
		# 	result = alter
		return result


	# def calcResultAngle1(self, angles):
	# 	# 	# deltaInRad = 0.0174533
	# 	# 	result = self.calcSimpleAvarage(angles)
	# 	# 	alter = self.calcSimpleAvarage(angles)
	# 	# 	for angle in angles:
	# 	# 		a = abs((result - angle)/result)**3
	# 	# 		print(a)
	# 	# 		if a >= 1:
	# 	# 			a = 0.95
	# 	# 		b = 1 - a
	# 	# 		print("andgle {} result {} perc {}".format(math.degrees(angle),math.degrees(result), a))
	# 	# 		result = result * a + angle*b
	# 	# 	print("{} {} ".format(math.degrees(result), math.degrees(alter)))
	# 	# 	# if abs(result) > abs(alter):
	# 	# 	# 	result = alter
	# 	# 	return result

	# def calcResultAngle1(self, angles):
	# 	# deltaInRad = 0.0174533
	# 	old = self.calcResultAngle1Old(angles)
	# 	result = self.calcSimpleAvarage(angles)
	# 	alter = self.calcSimpleAvarage(angles)
	# 	for angle in angles:
	# 		a = abs((result - angle)/result)
	# 		print(a)
	# 		if a >= 1:
	# 			a = 0.95
	# 		print(a)
	# 		a = 41.055*a**5 - 120.06*a**4 + 127.93*a**3 - 57.734*a**2 + 8.2996*a + 0.6062
	# 		b = 1 - a
	# 		print("andgle {} result {} perc {}\n_______________________".format(math.degrees(angle), math.degrees(result), a))
	# 		result = result * b + angle*a
	# 	print("{} {} {} ".format(math.degrees(result), math.degrees(alter), math.degrees(old)))
	# 	# if abs(result) > abs(alter):
	# 	# 	result = alter
	# 	return result

	def calcSimpleAvarage(self, angles):
		result = 0
		for angle in angles:
			# print(math.degrees(angle))
			result += angle
		return result/len(angles)

	def calcResultAngle3(self, angles):
		deltaInRad = 0.0174533
		mid = self.calcResultAngle2(angles)
		usefullList = []
		for angle in angles:
			diff = abs(mid-angle)
			if diff < deltaInRad:
				usefullList.append(angle)
		mid = self.calcResultAngle2(usefullList)
		# print(math.degrees(mid))
		usefullList1 = []
		for angle in usefullList:
			diff = abs(mid - angle)
			if diff < deltaInRad:
				usefullList1.append(angle)
		result =self.calcResultAngle2(usefullList1)
		return result

	def calcResultAngle4(self, angles):
		deltaInRad = 0.0872665
		trigExit = 0
		last= 0
		while True:
			mid = self.calcResultAngle2(angles)
			usefullList = []
			for angle in angles:
				diff = abs(mid - angle)
				if diff < deltaInRad:
					usefullList.append(angle)
			midN = self.calcResultAngle2(usefullList)
			if last == midN:
				trigExit += 1
			else:
				trigExit = 0
			if abs(mid - midN) < 0.0001 or trigExit == 3:
				break
			else:
				last = midN
		return midN
