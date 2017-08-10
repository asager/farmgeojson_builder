#Andrew Sager
#8/10/2017
#run this file, not the other .py files!\
import csv
import singlefarms
import multiplefarms

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

all_farms = [] #grab data from the other .py files
all_farms.extend(singlefarms.get_farms()) 
all_farms.extend(multiplefarms.get_farms())

#setting up syntax for the JSON:
s  = "{\n"
s += "	\"type\": \"FeatureCollection\",\n"
s += "	\"features\" : [\n"
#add each farmer's coordinates and details
for i in range(len(all_farms)):
	s += add_feature(all_farms[i])
	if (i != len(all_farms)-1): s += ", \n\n" #last farmer doesn't need a comma after his details

s += "\n	]\n}" #cap the JSON

output_file = open("treefarm_coordinates.geojson", "w") #writing the .geojson file
output_file.write(s)
output_file.close()
print("All coordinates were added to the file treefarm_coordinates.geojson\'.") #confirmation message
