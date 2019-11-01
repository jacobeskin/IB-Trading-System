"""
Cancel all orders. Nothing more, nothing less
"""

# Import stuff 
import logging
from ib_insync import * 

def IB_CancelAllOrders():

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IB_Cancel_All_Orders')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBCancel_all_orders.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB()

	try:

		log2.info('Starting IB ordering cancelling process')
		_=util.logToFile('IBCancelOrders.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 4) # Connect to IB, last numer, 4, used by TWS to identify the current calling procedure
		ib.sleep(1)
		log2.info('Connected to IB order cancelling process')

		# Get all open orders
		orders_list=ib.reqAllOpenOrders()

		# Cancel all open orders
		for order in orders_list:
			_=ib.cancelOrder(order)

		ib.disconnect()
		ib.sleep(1)
		log2.info('Open orders cancelled.')
		return(1)

	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception from the IB order cancel process')
		log2.exception(e)
		return(0)

	
		
