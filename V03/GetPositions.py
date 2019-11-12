"""
Get all open positions.

Returns a dictionary where key is the ticker symbol and value is the position value.
In case no open positions, return 0. For specific positions to the current market session,
you can also use GetTrades.py so as to not include positions held from previous sessions.
"""

# Import stuff 
import logging
from ib_insync import * 

def IB_GetPositions():

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IB_Get_Positions')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBGet_Positions.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB()

	try:

		log2.info('Starting IB position fetching process')
		_=util.logToFile('IBGetPositions.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 5) # Connect to IB, last numer, used by TWS to identify the current calling procedure
		ib.sleep(1)
		log2.info('Connected to IB position fetching process')

		# Get all positions
		portfolio=ib.portfolio()

		if len(portfolio)==0:
			log2.info('No open positions.')
			return(0)

		data_dict={}

		# Loop through positions
		for i in range(len(portfolio)):
			data_dict[portfolio[i].contract.symbol] = portfolio[i].averageCost

		ib.disconnect()
		ib.sleep(1)
		log2.info('Open positions returned.')
		return(data_dict)

	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB positions fetching process.')
		log2.exception(e)
		return(0)