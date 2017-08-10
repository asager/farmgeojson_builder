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
	A = []
	SMT_ID_INDEX = -1 #-1 implies improper index, these indexes are for columns in the csv
	SMT_FARM_ID_INDEX = -1 #if we can't find one of these
	GeoLocationFinal_INDEX = -1 #then the csv we were given is improper
	with open('AFF1601_GeoData.csv') as f:
		reader = csv.reader(f)
		for row in reader:
			if ("SMT_ID" in row and "SMT_Farm_ID" in row and "GeoLocationFinal" in row): #if we're in the header row
				SMT_ID_INDEX = row.index("SMT_ID") #identify column of member_ids
				SMT_FARM_ID_INDEX = row.index("SMT_Farm_ID") #identify column of farm_ids
				GeoLocationFinal_INDEX = row.index("GeoLocationFinal") #identify column of geodata
			elif ("SMT_ID" not in row and row[GeoLocationFinal_INDEX].strip() != ""): #otherwise, if we're not in the header and the farmer provided geodata
				if (SMT_FARM_ID_INDEX == -1 or SMT_ID_INDEX == -1 or GeoLocationFinal_INDEX == -1):
					print("Didn't find report fields for single farms.")
					exit()
				e = [row[SMT_ID_INDEX],row[SMT_FARM_ID_INDEX],row[GeoLocationFinal_INDEX]] #create the three-tuple (member_id, farm_id, geodata)
				A.append(e) #add that three-tuple to the storage array

	B = []
	for i in range(len(A)):
		split_pipes(A,B,i) #split up the seperate plots of land the farmers gave us, delimited by pipes

	for i in range(len(B)):
		B[i][2] = format_coords(B[i][2]) #flip flop x and y and make into a 2D array (instead of a string)
		
	C = []
	for farm in B:
		if (3 < len(farm[2])): #FIXME: right now, we ignore singular or linear coordinates given to us by the farmers
			C.append(farm) #they must form a polygon! so four or more points (since start pt = end pt)
	return C #return sorted data to completeparse.py
