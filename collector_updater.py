"""
Script for updating Pace Posted Stops Collector app
by unassigning stops in the system already installed/
marked. Prevents the duplication of sign install work.
"""

import urllib2
import urllib
import arcpy
import csv
import json
import xlrd
import glob
import os
import sys
import datetime

# status
print "Updating Pace Posted Stops Collector..."

# define Collector workspace
arcpy.env.workspace = "C:\Users\leexsh\AppData\Roaming\Esri\Desktop10.3\ArcCatalog\Connection to sde.sde\KATSGE.Collector_Posted_Stops"
arcpy.env.overwriteOutput = True

# define dump directory 
dir = "N:/Posted Stops Project/Collector/updater/dump/sde/"

def load_workbook(wkbkName, dir):
	"""
	Function for loading an Excel workbook.
	Parameters: workbook name, directory
	Output: first worksheet of workbook
	"""
	wkbk = xlrd.open_workbook(dir + wkbkName + ".xls")
	wksht = wkbk.sheet_by_index(0)
	return wksht

def main():

	# gets current date/time
	current = str(datetime.datetime.now())
	c_date = current[:10]
	c_time = current[11:13] + current[14:16]
	
	# prints log file
	sys.stdout = open("N:/Posted Stops Project/Collector/updater/dump/log/" + c_date + "_" + c_time + ".txt", 'w')	
	print "Collector update executed " + current + "."
	
	# list feature classes in workspace
	fClasses = arcpy.ListFeatureClasses()

	# loops through SDE workspace and exports table to csv
	for fClass in fClasses:
		try:			
			# download each feature class from SDE
			arcpy.TableToExcel_conversion(Input_Table="Database Connections\\Connection to sde.sde\\KATSGE.Collector_Posted_Stops\\" + fClass, Output_Excel_File=dir + fClass + ".xls", Use_field_alias_as_column_header="NAME", Use_domain_and_subtype_description="CODE")	
			
			# debug statement
			print "Download of " + fClass + " successful."
			
		except:
			# debug statement
			print "Download of " + fClass + " failed."

	# initialize merge as empty table (list of lists)
	merge = []

	# loops through feature class exports
	for filename in glob.iglob(dir + "*.xls"):
		# parses filename
		file = filename[-17:-4]
		
		# loads workbook
		wksht = load_workbook(file, dir)
		
		for row_idx in range(1, wksht.nrows):
			if len(wksht.cell_value(row_idx, 20).encode('utf-8')) > 3:
				merge.append(wksht.row(row_idx))
			# if wksht.cell_value(row_idx, 20).encode('utf-8') != "":	
				# if wksht.cell_value(row_idx, 20).encode('utf-8') != " ":
					# merge.append(wksht.row(row_idx))

	# initialize set of unique stops
	uniqueStops = set([])

	# loops through each table in merge
	for row in merge:
		uniqueStops.add(row[3].value)

	# initialize marked feature objects
	marked = {}

	# read json file of Collector feature server
	featServerLink = 'http://maps.pacebus.com/arcgis/rest/services/Posted_Stops/Collector_PS_SDE/FeatureServer?f=pjson'
	data = urllib2.urlopen(featServerLink)
	string = data.read().decode('utf-8')
	json_obj = json.loads(string)

	# get layer
	layers = json_obj['layers']

	for layer in layers:

		# initialize dictionary of marked stops
		marked[layer['id']] = {}
		
		# build workbook name to load
		fClass = "KATSGE." + layer['name']
		
		# loads workbook
		wksht = load_workbook(fClass, dir)
		
		for row_idx in range(1, wksht.nrows):
			# set OID and stop ID variables
			objectID = wksht.cell_value(row_idx, 0)
			stopID = wksht.cell_value(row_idx, 3)
			
			# mark stop if in set of installed stops
			if stopID in uniqueStops:
				marked[layer['id']][objectID] = stopID

	# loops through each layer in marked
	for layer in marked:
		
		# if layer contains marked stops
		if marked[layer] != {}:
			print "Marked stops in layer " + str(layer) + " flagged for update: " + str(marked[layer])
					
			# initialize json request list
			jsonRequest = []	
			
			# loops through marked stops in layer
			for obj in marked[layer]:
				objDict = {"attributes":{"OBJECTID":int(obj), "INSTALLATION_ACTION":"None"}}			
				jsonRequest.append(objDict)
				
			# dump to JSON file
			with open("N:/Posted Stops Project/Collector/updater/dump/json/layer_" + str(layer) + ".json", 'w') as applyEditsJSON:
				json.dump(jsonRequest, applyEditsJSON)
				
			# encodes and sends JSON request via REST	
			submitData = {'features': jsonRequest, 'f': 'json', 'rollbackOnFailure': True}
			jsonLink = 'http://maps.pacebus.com/arcgis/rest/services/Posted_Stops/Collector_PS_SDE/FeatureServer/' + str(layer) + '/updateFeatures'
			jsonData = urllib.urlencode(submitData)
			response = urllib.urlopen(jsonLink, jsonData)
			
	sys.stdout.close()
			
# call function
if __name__ == '__main__':
    main()