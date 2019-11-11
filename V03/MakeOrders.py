"""
Module for submitting orders.

Input for market order:

- Dictionary where ticker symbol is the key, value is a tuple with number shares and 'BUY' or 'SELL',
  for example

  data_dict = {'GOOG' : (10,'SELL'),
               'AAPL' : (20,'BUY')}

Input for limit on open order, note this will be submitted at market open:

- Dictionary where ticker symbol is the key, value is a tuple with number of shares, 'BUY' or 'SELL' 
  and limit price, for example

  data_dict = {'GOOG' : (10,'BUY',1001)
               'AAPL' : (20,'SELL',500)}

Output:

- List of symbols that orders were commited for (market order) or 1 for LOO
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

def IB_MarketOrders(data_dict):

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IB_Submit_Market_Orders_log')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IB_Submit_Market_Orders.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB() # Initialize IB object

	# Put this whole thing in a try-except block in order not to crash the whole program 
	# in the event of an error
	try:

		log2.info('Starting IB ordering process')
		_=util.logToFile('IBMKT.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 2) # Connect to IB, last numer, 2, used by TWS to identify the current calling procedure
		ib.sleep(1)
		log2.info('Connected to IB ordering process')

		tickers=list(data_dict.keys()) # Get the ticker symbols

		if len(tickers)>0:
			contract=[Stock(i, 'SMART', 'USD') for i in tickers]
			_=ib.qualifyContracts(*contract)
		else:
			ib.disconnect()
			ib.sleep(1)
			log2.info('No tickers given. IB ordering process disconnected. Function terminated.')
			return(1)
		
		# Return list of symbols for opened positions
		return_list=[]

		# In order to avoid too many msgs sent, chunk ticker list up
		x=m.ceil(len(tickers)/49)

		log2.info('Starting to loop over securities.')
		for i in range(x):

			contracts=contract[49*i:min(len(tickers),49+49*i)]

			# Loop over all the tickers
			for k in range(len(contracts)):
				
				symbol=contracts[k].symbol # Get the ticker symbol again
				order=MarketOrder(data_dict[symbol][1],data_dict[symbol][0]) # Create the order
				trade=ib.placeOrder(contracts[k],order)                      # Place the order
				return_list.append(symbol)
				ib.sleep(1)
				log2.info('Placing '+str(data_dict[symbol][1])+' order for '+symbol+' for '+str(data_dict[symbol][0])+' shares') 

		# If we completed safe and sound
		log2.info('All orders placed.')
		ib.disconnect()
		ib.sleep(1)
		return(return_list)

	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB market order submission process')
		log2.exception(e)
		return(0)


def IB_LimitOnOpenOrders(data_dict):

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IB_Submit_Limit_On_Open_Orders_log')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IB_Submit_Limit_On_Open_Orders.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB() # Initialize IB object

	# Put this whole thing in a try-except block in order not to crash the whole program 
	# in the event of an error
	try:

		log2.info('Starting IB ordering process')
		_=util.logToFile('IBLOO.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 3) # Connect to IB, last numer, 2, used by TWS to identify the current calling procedure
		ib.sleep(1)
		log2.info('Connected to IB ordering process')

		tickers=list(data_dict.keys()) # Get the ticker symbols

		if len(tickers)>0:
			contract=[Stock(i, 'SMART', 'USD') for i in tickers]
			_=ib.qualifyContracts(*contract)
		else:
			ib.disconnect()
			ib.sleep(1)
			log2.info('No tickers given. IB ordering process disconnected. Function terminated.')
			return(1)
		
		# In order to avoid too many msgs sent, chunk ticker list up
		x=m.ceil(len(tickers)/49)

		log2.info('Starting to loop over securities.')
		for i in range(x):

			contracts=contract[49*i:min(len(tickers),49+49*i)]

			# Loop over all the tickers
			for k in range(len(contracts)):
				
				symbol=contracts[k].symbol # Get the ticker symbol again
				
				# Create the order
				order=Order()
				order.action=data_dict[symbol][1]
				order.tif='OPG'
				order.orderType='LMT'
				order.totalQuantity=data_dict[symbol][0]
				order.lmtPrice=data_dict[symbol][2]

				# Place the order
				trade=ib.placeOrder(contracts[k],order)                      # Place the order
				ib.sleep(1)
				log2.info('Placing '+str(data_dict[symbol][1])+' order for '+symbol+' for '+str(data_dict[symbol][0])+' shares') 

		# If we completed safe and sound
		log2.info('All orders placed.')
		ib.disconnect()
		ib.sleep(1)
		return(1)

	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB limit order submission process')
		log2.exception(e)
		return(0)


