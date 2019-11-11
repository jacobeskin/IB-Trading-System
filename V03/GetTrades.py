"""
Get trades. Either action == 'BUY' or action == 'SELL' meanig get either buys or sells.
Only for the current trading sessions/day.
"""

# Import stuff 
import logging
from ib_insync import * 

def IB_GetTrades(action):

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IB_GetTrades')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBGetTrades.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB()

	try:

		log2.info('Starting IB trades fetching process')
		_=util.logToFile('IBGetTrades.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 7) # Connect to IB, last numer, used by TWS to identify the current calling procedure
		ib.sleep(1)
		log2.info('Connected to IB trades fetching process')

		# Get all positions
		trades=ib.trades()

		if len(trades)==0:
			log2.info('No trades.')
			return(0)

		data_dict={}

		# Loop through positions
		for i in range(len(trades)):
			if (trades[i].orderStatus.status=='Filled') and (trades[i].order.action==action):
				data_dict[trades[i].contract.symbol] = trades[i].fills[0].execution.avgPrice

		ib.disconnect()
		ib.sleep(2)
		log2.info('Open positions returned.')
		return(data_dict)

	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB trades fetching process.')
		log2.exception(e)
		return(0)