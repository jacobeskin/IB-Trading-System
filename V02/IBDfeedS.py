# Import stuff
import logging, sys
from ib_insync import * # Bad practice, bad bad practice...soo vitun soo!
#import datetime
#import time
import math as m
from datetime import timezone

#import TailLogger as TL later for GUI


def IBDfeedS(tickers,q_data,q_tlist_n,q_msg_f,q_err_f):

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IBDFeedScriptS')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBDfeedScriptS.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB()
	try:

		# Start main process loop
		while True:

			# Check for new tickers
			if not q_tlist_n.empty():
				tlist=q_tlist_n.get()
				if len(tlist)>0:
					tickers=tlist
					contract=[Stock(i, 'SMART', 'USD') for i in tickers]
					_=ib.qualifyContracts(*contract)

			# Check the message queue and either connect or quit
			if not q_msg_f.empty():

				message=q_msg_f.get()  # Get message

				if message=='Start':   # Start IB

					log2.info('Starting IB datafeed process')
					_=util.logToFile('IBDFeed.log',level=20) # IB logger
					_=ib.connect('127.0.0.1', 7497, 1) # Connect to IB
					ib.sleep(1)
					_=ib.reqMarketDataType(3)          # Delayed ticks

					# List of contracts, and qualifying them
					contract=[Stock(i, 'SMART', 'USD') for i in tickers]
					_=ib.qualifyContracts(*contract)

					log2.info('Connected to IB datafeed process')

				elif message=='Stop':  # Disconnect

					if ib.isConnected():
						ib.disconnect()
						ib.sleep(1)
						log2.info('Datafeed disconnected')

				elif message=='Exit':  # Exit from process

					if ib.isConnected():
						ib.disconnect()

					ib.sleep(1)
					log2.info('Datafeed process terminated')
					sys.exit()
					break

			# While we are connected, do stuff
			if ib.isConnected():

				# In order to avoid too many msgs sent, chunk ticker list up
				x=m.ceil(len(tickers)/49)

				for i in range(x):

					# Get tick
					#tick=[ib.reqMktData(contract=j,snapshot=False) for j in contract[49*i:min(len(tickers),49+49*i)]]
					#ib.sleep(2) # Wait for it to fill
					# For multiple contracts get many elements in tick
					log2.info('Getting ticker data.')
					contracts=contract[49*i:min(len(tickers),49+49*i)]
					tick=ib.reqTickers(*contracts,regulatorySnapshot=False)

					# Loop over all the tickers
					for k in range(len(tick)):
						if tick[k].time!=None: # Serves as a guard for tickers in list that are not in IB

							# Ticker timestamp
							time=tick[k].time.replace(tzinfo=timezone.utc).astimezone(tz=None)
							time=time.strftime('%Y%m%d%H%M%S')

							# Put data into the data queue, (one instrument at a time)
							_=q_data.put([tick[k].contract,   # Contract
										time,                 # Timestamp
										tick[k].bid,          # well guess the rest...
										tick[k].ask,
										tick[k].marketPrice(),
										tick[k].volume,
										tick[k].high,
										tick[k].low])

					log2.info('Ticker data sent.')
					# Unsubscribe so as not to go over 100 contract limit
					_=[ib.cancelMktData(contract=j) for j in contracts[49*i:min(len(tickers),49+49*i)]]
					ib.sleep(1)

	except Exception as e:
		_=q_err_f.put('Error')
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception IB datafeed process')
		log2.exception(e)
