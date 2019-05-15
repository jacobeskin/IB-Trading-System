# Import stuff
from ib_insync import * # Bad practice, bad bad practice...soo vitun soo!
#import datetime
#import time
import math as m
from datetime import timezone


def IBOpenData(tickers):

	from ib_insync import * # Bad practice, bad bad practice...soo vitun soo!
	#import datetime
	#import time
	import math as m
	from datetime import timezone

	try:
		prices={}

		ib=IB()
		_=util.logToFile('IBOpenData.log',level=20)
		_=ib.connect('127.0.0.1', 7497, 3) # Connect to IB
		ib.sleep(1)
		_=ib.reqMarketDataType(1) # Real time data

		# List of contracts, and qualifying them
		contract=[Stock(i, 'SMART', 'USD') for i in tickers]
		_=ib.qualifyContracts(*contract)

		x=m.ceil(len(tickers)/49)
		for i in range(x):

		# Get tick
		#tick=[ib.reqMktData(contract=j,snapshot=True) for j in contract[49*i:min(len(tickers),49+49*i)]]
		#ib.sleep(2) # Wait for it to fill
			tick=ib.reqTickers(*contract,regulatorySnapshot=False)

			# Loop over all the tickers
			k = 0
			length=len(tick)
			while k<=length-1:
				if (tick[k].time!=None) and (not m.isnan(tick[k].open)):
					prices[tick[k].contract.symbol]=tick[k].open
					k+=1
				else: length-=1

			# Unsubscribe so as not to go over 100 contract limit
			_=[ib.cancelMktData(contract=j) for j in contract[49*i:min(len(tickers),49+49*i)]]
			ib.sleep(1)

		_=ib.disconnect()
		return(prices)

	except Exception as e:
		_=ib.disconnect()
		raise(e)
		return([])
