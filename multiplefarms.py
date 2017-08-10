#Andrew Sager
#8/10/2017
#not the main file, run completeparse.py
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
	smtfarmconf = "SMT_Farm_ID_{0}" #{0} is formatting for each of the five farm columns
	farmloopconf = "FarmLoop_Farm{0}_GeoLocationFinal"
	A = []
	with open('AFF1601MF_GeoData.csv') as f:
		reader = csv.reader(f)
		r = False
		for row in reader:
			if (not r):
				r = True #flip bit to signify whether we are in the first row
				try:
					assert(row[1] == "SMT_ID") #need to have the document formatted a certain way
					for i in range(5):
						assert(row[2+3*i] == smtfarmconf.format(i+1)) #assert that 3rd column is "SMT_Farm_ID_1", 6th column is "SMT_Farm_ID_2", etc.
						assert(row[4+3*i] == farmloopconf.format(i+1)) #assert that 4th column, 7th column....
				except AssertionError:
					print("Error with formatting of AFF1601MF_GeoData.csv") #the file isnt in the right format
			else: #if we're not in the first row, grab the farmer id and all of the farm and geo data
				SMT_ID = row[1] 
				for i in range(5):
					farmidx = row[2+3*i].strip()
					geolocationx = row[4+3*i].strip()
					if (farmidx == "" or geolocationx == ""): #will stop if no geolocation exists, could cause problems if geolocations exist afterwards
						break
					else:
						A.append([SMT_ID,farmidx,geolocationx])
	#perform the same operations as for single farms...
	B = []
	for i in range(len(A)):
		split_pipes(A,B,i) #split up the seperate plots of land the farmers gave us, delimited by pipes

	for i in range(len(B)):
		B[i][2] = format_coords(B[i][2]) #flip flop x and y and make into a 2D array (instead of a string)
		
	C = []
	for farm in B:
		if (3 < len(farm[2])): #FIXME: right now, we ignore singular or linear coordinates given to us by the farmers
			C.append(farm) #they must form a polygon! so four or more points (since start pt = end pt)
	return C #return it to the completeparse.py file
