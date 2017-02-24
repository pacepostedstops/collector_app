"""
Script for downloading attachment files from Pace
Posted Stops Collector app via the RESTful API URL.
"""

import urllib.request as lib
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
	featServName = 'Collector_PS_SDE'
	featServerLink = 'http://maps.pacebus.com/arcgis/rest/services/Posted_Stops/' + featServName + '/FeatureServer?f=pjson'
	
	# output root dir and check for existence
	rootDir = 'J:/Posted Stop Program/Sign Installation/Collector/attachments/files/' + featServName + '/'
	if not os.path.exists(rootDir):
		os.makedirs(rootDir)

	# read json file of Collector feature server
	layers = json_read(featServerLink)
	
	# loop through layers in feature service
	for layer in layers['layers']:
		print('Processing layer ' + layer['name'] + '...')
		
		# output dir for layer and check for existence
		outputDir = rootDir + layer['name'] + '/'
		if not os.path.exists(outputDir):
			os.makedirs(outputDir)
		
		# link for feature layer
		featLayer = 'http://maps.pacebus.com/arcgis/rest/services/Posted_Stops/' + featServName + '/FeatureServer/' + str(layer['id'])
		
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
					attfile = lib.urlretrieve(attLink, outputDir + str(att['id']) + '.' + att['contentType'][6:])
				
				# increment feature objID
				featNo += 1
				featLayJSON = featLayer + '/' + str(featNo) + '?f=pjson'
				
		except ValueError:
			print("Retrieval of attachment file failed.")
			
# call function
if __name__ == '__main__':
    main()
