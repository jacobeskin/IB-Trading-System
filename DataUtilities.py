"""
Utilities for:

- Reading in the JSON, should be quite self evident
- Reading in the possible positions pickle, should be quite self evident
- Building the model dictionary
 
"""

import os
import json


def GetTickerDataCL():
	while True:
		print('Name of JSON:')
		x=input().split()
		if os.path.isfile(x[0]):
			try:
				with open(x[0],'r') as fp:
					tickerdata=json.load(fp)
				return(tickerdata)
			except Exception as e:
				print('Error in reading in the JSON!')
				return(0)
		else: print('File does not seem to exist.')


def GetPositionsCL():
	while True:
		print('Get dictionary of existing positions? (y/n)')
		x=input().split()
		if x[0]=='y':
			try:
				with open('positions.json', 'r') as fp:
					positions=json.load(fp)
				print('Positions successfully loaded!')
				return(positions)
			except Exception as e:
				print('Error in reading the positions JSON, might not exist!')
				return(0) 
		elif x[0]=='n': 
			print('Not loading positions.')
			return(0)
		else: print('Please give y or n')
		

def BuildModel(positions,tickerdata):
	
	# Loop through all the tickers and if that ticker does not exist in 
	# positions dictionary, then add it there. And append the value list as 
	# well with a list [position flg,stop price, trailing on flg]
	for i in tickerdata.keys():
		if i not in positions:
			positions[i]=tickerdata[i]    # positions dict gets all the parameters
			positions[i].append([0,0,0,0])  # positions dict gets appended with list
			
	return(positions)
	

def ModelOut(dict):
	with open('positions.json','w') as fp:
		_=json.dump(dict,fp)

			
					
		