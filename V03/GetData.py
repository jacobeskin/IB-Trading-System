"""
Module for getting IB data for securities.

Input:

- List of tickers

Output:

- Pandas dataframe (when successful)
- 1 if zero tickers passed
- 0 in case of an actual error
"""

# Import stuff 
import logging
from ib_insync import * 
#import datetime
#import time
import math as m
import pandas as pd
from datetime import timezone

def IB_GetData(tickers):

	# Setup first logger-------------------------------------------------------
	log2=logging.getLogger('IB_Get_Data_log')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IB_Get_Data.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB() # Initialize ib object

	# Put this into try except block so not to crash the complete process
	try:

		log2.info('Starting IB data request process')
		_=util.logToFile('IBDFeed.log',level=20) # IB logger
		_=ib.connect('127.0.0.1', 7497, 1) # Connect to IB, change the last number for a different process
		ib.sleep(1)
		_=ib.reqMarketDataType(1)          # Live data is 1, delayed would be 3

		log2.info('Connected to IB datafeed process')

		if len(tickers)>0:
			contract=[Stock(i, 'SMART', 'USD') for i in tickers]
			_=ib.qualifyContracts(*contract)
		else:
			if ib.isConnected():
				ib.disconnect()
				ib.sleep(1)
				log2.info('Empty ticker list. IB datafeed disconnected. Function terminated.')
			return(1)

		# In order to avoid too many msgs sent, chunk ticker list up
		x=m.ceil(len(tickers)/49)
		data=[]
		idx=[]
		columns=['Price', 'Volume']

		for i in range(x):

			log2.info('Getting ticker data.')
			contracts=contract[49*i:min(len(tickers),49+49*i)]
			tick=ib.reqTickers(*contracts,regulatorySnapshot=False)
			ib.sleep(1)
			# Loop over all the tickers
			for k in range(len(tick)):

				if tick[k].time!=None: # Serves as a guard for tickers in list that are not in IB

					# Ticker timestamp, if needed in the future.
					#time=tick[k].time.replace(tzinfo=timezone.utc).astimezone(tz=None)
					#time=time.strftime('%Y%m%d%H%M%S')

					# Put data into the data list
					_=data.append([tick[k].marketPrice(), tick[k].volume])
					
					# Other possible data if needed in the future
					#_=q_data.put([tick[k].contract,   # Contract
					#			time,                 # Timestamp
					#			tick[k].bid,          # well guess the rest...
					#			tick[k].ask,
					#			tick[k].marketPrice(),
					#			tick[k].volume,
					#			tick[k].high,
					#			tick[k].low])

					# Symbol into the index list
					_=idx.append(contracts[k].symbol)

			# Unsubscribe so as not to go over 100 contract limit
			_=[ib.cancelMktData(contract=j) for j in contracts[49*i:min(len(tickers),49+49*i)]]
			

		# Construct the dataframe and return
		data_frame=pd.DataFrame(data,columns=columns, index=idx)
		ib.disconnect()
		ib.sleep(1)
		log2.info('Data request complete.')
		return(data_frame)

	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB data request process')
		log2.exception(e)
		return(0)

