# Import stuff
import logging, sys
from ib_insync import * # Bad practice, bad bad practice...soo vitun soo!
#import datetime
#import time
import math as m
from datetime import timezone

#import TailLogger as TL later for GUI


def IBOptions(ticker_dict):

	try:
		tickers=list(ticker_dict.keys())

		ib=IB()
		_=util.logToFile('IBOptions.log',level=20) # Logger
		_=ib.connect('127.0.0.1', 7497, 4) # Connect to IB
		ib.sleep(1)
		_=ib.reqMarketDataType(1)

		data={}

		for i in tickers:

			contract=Stock(i, 'SMART', 'USD')
			_=ib.qualifyContracts(contract)
			chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, contract.conId)
			chain = next(c for c in chains if c.exchange == 'SMART')
			strikes = [strike for strike in chain.strikes if strike<ticker_dict[i]*0.7]
			contracts = [Option(contract.symbol, expiration, strike, 'P', 'SMART') for expiration in chain.expirations for strike in strikes]
			contracts = ib.qualifyContracts(*contracts)
			ticks = ib.reqTickers(*contracts,regulatorySnapshot=False)

			if len(ticks)>0:
				maximum=0
				idx=0
				for j in range(len(ticks)-1):
					#mid1=(ticks[j].ask-ticks[j].bid)/2
					#mid2=(ticks[j+1].ask-ticks[j+1].bid)/2
					#spread=mid1-mid2
					spread=ticks[j].ask-ticks[j+1].bid
					if (ticks[j].contract.lastTradeDateOrContractMonth==ticks[j+1].contract.lastTradeDateOrContractMonth) and (spread>=maximum):
						maximum=spread
						idx=j
					if maximum>0: data[i]={'buy_ticker':ticks[idx].contract, 'sell_ticker':ticks[idx+1].contract,'spread':maximum}

		_=ib.disconnect()
		return(data)

	except Exception as e:
		_=ib.disconnect()
		raise(e)
		return([])
