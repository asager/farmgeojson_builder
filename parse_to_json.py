#Andrew Sager
#7/13/2017

import csv

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
	A = s.split("),(") #we can't split by commas since we have interior and exterior commas, so i chose "),("
	B = []
	for i in range(len(A)):
		text = A[i].replace("(","").replace(")","") #sanitize
		str_coord = text.split(", ") #now we can split up the x and y so we can switch them
		coord = [float(str_coord[1]),float(str_coord[0])] #(y,x) => (x,y)
		B.append(coord)
	sort_coords(B)
	return B

def add_feature(A): #performs json formatting for each individual row
	#I've setup the formatting so that it looks clean.
	#The string itself is denoted by """ """ while the modular parts are denoted by %s
	# The three-tuple that follows the string are the three data points inserted
	#into the %s's in order
	out = """
{
	\"type\": \"Feature\",
	\"geometry\": {
		\"type\": \"Polygon\",
		\"coordinates\": [
			%s
		]
	},
	\"properties\": {
		\"Member_id\": %s,
		\"Farm_id\": %s
	}
}""" % (str(A[2]),str(A[0]),str(A[1])) #in order: coordinates, member_id, farm_id
	return out #return the new string we've made


A = []
SMT_ID_INDEX = -1 #-1 implies improper index, these indexes are for columns in the csv
SMT_FARM_ID_INDEX = -1 #if we can't find one of these
GeoLocationFinal_INDEX = -1 #then the csv we were given is improper
with open('farmdata.csv') as f:
	reader = csv.reader(f)
	for row in reader:
		if ("SMT_ID" in row and "SMT_Farm_ID" in row and "GeoLocationFinal" in row): #if we're in the header row
			SMT_ID_INDEX = row.index("SMT_ID") #identify column of member_ids
			SMT_FARM_ID_INDEX = row.index("SMT_Farm_ID") #identify column of farm_ids
			GeoLocationFinal_INDEX = row.index("GeoLocationFinal") #identify column of geodata
		elif ("SMT_ID" not in row and row[GeoLocationFinal_INDEX].strip() != ""): #otherwise, if we're not in the header and the farmer provided geodata
			e = [row[SMT_ID_INDEX],row[SMT_FARM_ID_INDEX],row[GeoLocationFinal_INDEX]] #create the three-tuple (member_id, farm_id, geodata)
			A.append(e) #add that three-tuple to the storage array

B = []
for i in range(len(A)):
	split_pipes(A,B,i) #split up the seperate plots of land the farmers gave us, delimited by pipes

for i in range(len(B)):
	B[i][2] = format_coords(B[i][2]) #flip flop x and y and make into a 2D array (instead of a string)
	
C = []
for farm in B:
	if (3 < len(farm[2])): #FIXME: right now we ignore singular or linear coordinates given to us by the farmers
		C.append(farm) #they must form a polygon! so four or more points (since start pt = end pt in .geojson format)

#setting up syntax for the .geojson:
s  = "{\n"
s += "	\"type\": \"FeatureCollection\",\n"
s += "	\"features\" : [\n"

#add each farmer's coordinates and details
for i in range(len(C)):
	s += add_feature(C[i])
	if (i != len(C)-1): s += ", \n\n" #last farmer doesn't need a comma after his details

s += "\n	]\n}" #cap the .geojson

output_file = open("treefarm_coordinates.geojson", "w") #writing the .geojson file
output_file.write(s)
output_file.close()
print("All coordinates were added to the file \'treefarm_coordinates.geojson\'.") #confirmation message
