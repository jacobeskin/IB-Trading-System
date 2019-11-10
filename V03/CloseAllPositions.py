"""
Close all open positions. 
"""

# Import stuff 
import logging
from ib_insync import * 

def IB_CloseAllPositions():

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IB_Close_All_Positions')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBClose_All_Positions.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB()

	try:

		log2.info('Starting IB position closing process')
		_=util.logToFile('IBCloseAllPositions.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 6) # Connect to IB, last numer, 4, used by TWS to identify the current calling procedure
		ib.sleep(1)
		log2.info('Connected to IB positions closing process')

		# Get all positions
		portfolio=ib.portfolio()

		if len(portfolio)==0:
			log2.info('No open positions.')
			return(0)

		# Make contracts
		contracts=[Stock(portfolio[i].contract.symbol,'SMART','USD') for i in range(len(portfolio))]
		_=ib.qualifyContracts(*contracts)

		# Send close orders
		for i in range(len(portfolio)):

			position=portfolio[i].position

			if position>0: side='SELL'
			elif position<0: side='BUY'
			else: continue

			symbol=portfolio[i].contract.symbol
			contract=contracts[i]

			order=MarketOrder(side,position)
			_=ib.placeOrder(contract,order)

			log2.info('Placing '+side+' order for '+symbol+' for '+str(position)+' shares')

		# Request trades and get the closing prices
		#close_prices={}
		#trades=ib.trades()

		ib.disconnect()
		ib.sleep(1)
		log2.info('Position closing orders sent.')
		return(1)


		
	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB position closing process.')
		log2.exception(e)
		return(0)