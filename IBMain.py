# Import stuff
import sys
import multiprocessing as mp
import time
import datetime 
import logging
from IBDfeed import IBDfeed
from IBOrders import IBOrders

import DataUtilities

#import TailLogger as TL later for GUI

# Need this line for multiprocessing in Windows
if __name__=='__main__':

	# List of tuples of non-trading days
	no_trading=[]
	
	#time.sleep(7200)
	# Set up logger ------------------------------------------------------------
	logger=logging.getLogger(__name__)
	logger.setLevel(logging.INFO)
	
	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
	
	file_handler=logging.FileHandler('IBMain.log')
	file_handler.setFormatter(formatter)
	
	stream_handler=logging.StreamHandler()
	stream_handler.setFormatter(formatter)
	
	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)
	#---------------------------------------------------------------------------
	
	# Set up the ticker list and model------------------------------------------
	
	# Read in the JSON and get existing positions (if you want)
	tickerdata=DataUtilities.GetTickerDataCL()
	if tickerdata==0: sys.exit()
	tlist=list(tickerdata.keys()) 
	positions=DataUtilities.GetPositionsCL()
	if positions==0: positions={}
	
	# Build the "model", it is just a dictionary where tickers are keys and 
	# values are lists of trading related parameters
	d=DataUtilities.BuildModel(positions,tickerdata)  # Model dictionary
	#---------------------------------------------------------------------------
	
	# Set up multiprocessing----------------------------------------------------
	
	# Set up the queues for data and message traffic.	
	q_data=mp.Queue()
	q_msg_f=mp.Queue()
	q_msg_o=mp.Queue()
	q_err_f=mp.Queue()
	q_err_o=mp.Queue()
	
	# Set up the processes. Pass in ticker list and model dictionary.
	p_f=mp.Process(target=IBDfeed,args=(tlist,q_data,q_msg_f,q_err_f))
	p_o=mp.Process(target=IBOrders,args=(d,q_data,q_msg_o,q_err_o))
	
	# Start values for the queues, if it is time
	dt=datetime.datetime.now()
	msg_flg=0
	if ((dt.day,dt.month) not in no_trading) and (4<dt.hour<20):
		_=q_msg_f.put('Start')
		_=q_msg_o.put('Start')
		msg_flg=1
		
	#---------------------------------------------------------------------------
	
	try:
		
		# Start the processes
		_=p_f.start()
		_=p_o.start()
		
		# Start the main loop
		logger.info('Start main process loop')
		while True:
			
			# Check if we are in trading time
			dt=datetime.datetime.now()
			if ((dt.day,dt.month) not in no_trading) and (4<dt.hour<20):
				if msg_flg==0:
					_=q_msg_f.put('Start')
					_=q_msg_o.put('Start')
					msg_flg=1
			else:
				if msg_flg==1:
					_=q_msg_f.put('Stop')
					_=q_msg_o.put('Stop')
					msg_flg=0
			
			# Error in data feed, restart
			if not q_err_f.empty():
				_=q_err_f.get()
				logger.warning('Error in datafeed')
				logger.info('Restarting')
				if (p_f.exitcode is None) and (not p_f.is_alive()):
					_=p_f.terminate()
					_=time.sleep(1)
					_=q_msg_f.put('Start')
					p_f=mp.Process(target=IBDfeed,args=(tlist,q_data,q_msg_f,q_err_f))
					_=p_f.start()
				else:
					_=time.sleep(1)
					_=q_msg_f.put('Start')
					p_f=mp.Process(target=IBDfeed,args=(tlist,q_data,q_msg_f,q_err_f))
					_=p_f.start()
				
			# Error in ordering, restart 	
			if not q_err_o.empty():
				restart_d=q_err_o.get()
				logger.warning('Error in order placement')
				logger.info('Restarting')
				if (p_o.exitcode is None) and (not p_o.is_alive()):
					_=p_o.terminate()
					_=time.sleep(1)
					_=q_msg_o.put('Start')
					p_o=mp.Process(target=IBOrders,args=(restart_d,q_data,q_msg_o,q_err_o))
					_=p_o.start()
				else:
					_=time.sleep(1)
					_=q_msg_o.put('Start')
					p_o=mp.Process(target=IBOrders,args=(restart_d,q_data,q_msg_o,q_err_o))
					_=p_o.start()
	
	# Controlled exit
	except KeyboardInterrupt:
		_=q_msg_f.put('Stop')
		_=q_msg_o.put('Stop')
		for i in range(15,0,-1):
			print(i)
			time.sleep(1)
		if (p_f.exitcode is None) and (not p_f.is_alive()):
			_=p_f.terminate()
		if (p_o.exitcode is None) and (not p_o.is_alive()):
			_=p_o.terminate()
		logger.info('Controlled shutdown')
	
	# Uncontrolled exit
	except Exception as e:
		_=q_msg_f.put('Stop')
		_=q_msg_o.put('Stop')
		for i in range(15,0,-1):
			logger.info(i)
			print(i)
		if (p_f.exitcode is None) and (not p_f.is_alive()):
			_=p_f.terminate()
		if (p_o.exitcode is None) and (not p_o.is_alive()):
			_=p_o.terminate()
		logger.error('Uncontrolled termination')
		logger.exception(e)