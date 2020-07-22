fN = "test.txt"
param = 'to_current_orientation'
f = open(fN, "r")
for line in f.readlines():
	if param in line:
		print(line.split("=")[1].replace(".", ",").rstrip())