"""
Script for downloading attachment files from Pace
Posted Stops Collector app via the RESTful API URL
for use as an ArcToolbox geoprocessing tool.
"""

import arcpy
import urllib2 as lib
import urllib
import json
import os

def json_read(link):
	"""
	Function to create python dict from json link.
	:param str link: link of JSON file
	:return: dict object
	"""
	data = lib.urlopen(link)
	string = data.read().decode('utf-8')
	json_obj = json.loads(string)
	return json_obj

def main():

	# read json file of Collector feature server
	featServName = arcpy.GetParameterAsText(0)
	featServerLink = 'http://maps.pacebus.com/arcgis/rest/services/' + featServName + '/FeatureServer?f=pjson'

	# read layers array of feature service json file
	try:
		layers = json_read(featServerLink)['layers']
	except:
		arcpy.AddError("No such feature service exists.")
		quit()
		
	# parameter for layer name
	layerName = arcpy.GetParameterAsText(1)
	
	# search for layer ID
	for layer in layers:
		if layer['name'] == layerName:
			layerID = layer['id']
			break
		else:
			layerID = 9999
	
	# error handling for non-existent layer name
	if layerID == 9999:
		arcpy.AddError("No such layer exists.")
		quit()
	
	# output dir for layer and check for existence
	outputDir = arcpy.GetParameterAsText(2) + '/' + layerName + '_attachments' + '/' 
	if not os.path.exists(outputDir):
		os.makedirs(outputDir)
	
	# link for feature layer
	featLayer = 'http://maps.pacebus.com/arcgis/rest/services/' + featServName + '/FeatureServer/' + str(layerID)
	
	# initialize feature objID
	featNo = 1
	
	# create feature JSON link
	featLayJSON = featLayer + '/' + str(featNo) + '?f=pjson'

	# retrieve attachment file
	try:
		while list(json_read(featLayJSON).keys()) != ['error']:

			# print feature no
			print(featNo)

			# construct link for feature attachments
			featAttLink = featLayer + '/' + str(featNo)
			
			# read json object
			json_obj = json_read(featAttLink + '/attachments?f=pjson')

			# retrieve attachment ID and construct att link
			for att in json_obj['attachmentInfos']:
				attID = att['id']
				attLink = featAttLink + '/attachments/' + str(attID)
				
				# download file
				attfile = urllib.urlretrieve(attLink, outputDir + 'obj' + str(featNo) + '_att' + str(att['id']) + '.' + att['contentType'][6:])
			
			# increment feature objID
			featNo += 1
			featLayJSON = featLayer + '/' + str(featNo) + '?f=pjson'
			
	except ValueError:
		print("Retrieval of attachment file failed.")
			
# call function
if __name__ == '__main__':
    main()
