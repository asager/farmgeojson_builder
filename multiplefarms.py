import csv #import .csv manipulation libraries

def simplify(A):
	for i in range(len(A)):
		if (A[i] == ""): #get rid of any empty cells in the geodata
			A.pop(i)
	return A

def split_pipes(A,B,i):
	member_id = A[i][0]
	farm_id = A[i][1]
	temp = simplify(A[i][2].split("|"))
	for item in temp:
		B.append([member_id, farm_id, item]) #create a new entry for each plot of land but with correct farm and member ids

def sort_coords(A): #never needed to normalize to the NE coord, seems to work without it
	A.append(A[0])  #so i just added the first coord to the end, as required by .geojson conventions
	return A

def format_coords(s):
	A = s.split("),(") #we can't split by commas since we have interior and exterior commas, so I chose "),("
	B = []
	for i in range(len(A)):
		text = A[i].replace("(","").replace(")","") #sanitize
		str_coord = text.split(", ") #now we can split up the x and y so we can switch them
		coord = [float(str_coord[1]),float(str_coord[0])] #(y,x) => (x,y)
		B.append(coord)
	sort_coords(B)
	return B

def get_farms():
	smtfarmconf = "SMT_Farm_ID_{0}"
	farmloopconf = "FarmLoop_Farm{0}_GeoLocationFinal"
	A = []
	with open('AFF1601MF_GeoData.csv') as f:
		reader = csv.reader(f)
		r = False
		for row in reader:
			if (not r):
				r = True
				assert(row[1] == "SMT_ID")
				for i in range(5):
					try:
						assert(row[2+3*i] == smtfarmconf.format(i+1))
						assert(row[4+3*i] == farmloopconf.format(i+1))
					except AssertionError:
						print("Error with formatting of AFF1601MF_GeoData.csv")
			else:
				SMT_ID = row[1]
				for i in range(5):
					farmidx = row[2+3*i].strip()
					geolocationx = row[4+3*i].strip()
					if (farmidx == "" or geolocationx == ""):
						break
					else:
						A.append([SMT_ID,farmidx,geolocationx])
	B = []
	for i in range(len(A)):
		split_pipes(A,B,i) #split up the seperate plots of land the farmers gave us, delimited by pipes

	for i in range(len(B)):
		B[i][2] = format_coords(B[i][2]) #flip flop x and y and make into a 2D array (instead of a string)
		
	C = []
	for farm in B:
		if (3 < len(farm[2])): #FIXME: right now, we ignore singular or linear coordinates given to us by the farmers
			C.append(farm) #they must form a polygon! so four or more points (since start pt = end pt)
	return C