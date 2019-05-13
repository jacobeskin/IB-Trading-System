# Import stuff
import sys, select, os, logging, json, time, datetime, pickle
import multiprocessing as mp
from IBDfeedS import IBDfeedS
from IBOrdersS import IBOrdersS

#import TailLogger as TL later for GUI

# Need this line for multiprocessing in Windows
if __name__=='__main__':

	#time.sleep(7200)
	# Set up logger ------------------------------------------------------------
	logger=logging.getLogger(__name__)
	logger.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBMainS.log')
	file_handler.setFormatter(formatter)

	stream_handler=logging.StreamHandler(sys.stdout)
	stream_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)
	#---------------------------------------------------------------------------

	# Set up the ticker list and stuff------------------------------------------
	file_flg=0
	while True:
		if file_flg: break
		logger.info('Disaster recovery? (y/n):')
		x=input().split()
		logger.info(x[0])
		if x[0]=='y':
			try:
				with open('positions.pickle', 'rb') as fp:
					data=pickle.load(fp)
				logger.info('Positions data successfully loaded!')
				logger.info('Path to JSON:')
				input_file=input().split()
				break
			except Exception as e:
				logger.error('Error in reading the positions JSON, might not exist!')
				logger.exception(e)
		elif x[0]=='n':
			logger.info('Not recovering positions.')
			while True:
				logger.info('Path to JSON:')
				input_file=input().split()
				logger.info(input_file[0])
				logger.info('Checking if input JSON exists.')
				if os.path.isfile(input_file[0]):
					try:
						with open(input_file[0],'rb') as fp:
							data=pickle.load(fp)
						logger.info('Ticker data succesfully loaded.')
						os.remove(input_file[0])
						file_flg=1
						break
					except Exception as e:
						logger.error('Something went wrong in reading the input JSON.')
						logger.exception(e)
						sys.exit()
				else: logger.info('File does not exist')
		else: logger.info('Please give y or n')

	tlist=[i[0] for i in data]
	for i in data:
		data[i]['position']=0
		data[i]['trailer']=0


	#---------------------------------------------------------------------------

	# Set up multiprocessing----------------------------------------------------

	logger.info('Preparing system...')

	# Set up the queues for data and message traffic.
	q_data=mp.Queue()
	q_json=mp.Queue()
	q_tlist_n=mp.Queue()
	q_msg_f=mp.Queue()
	q_msg_o=mp.Queue()
	q_err_f=mp.Queue()
	q_err_o=mp.Queue()

	# Set up the processes. Pass in ticker list and model dictionary.
	p_f=mp.Process(target=IBDfeedS,args=(tlist,q_data,q_tlist_n,q_msg_f,q_err_f))
	p_o=mp.Process(target=IBOrdersS,args=(data,q_data,q_json,q_msg_o,q_err_o))

	#---------------------------------------------------------------------------

	#Start the main process-----------------------------------------------------

	logger.info('Starting the process.')

	try:

		# Start the processes
		_=p_f.start()
		_=p_o.start()

		# Start the main loop
		logger.info('Check datetime.')

		# List of tuples of non-trading days
		no_trading=[]

		# Check if we are in trading day and time
		dt=datetime.datetime.now()
		weekday = 5>dt.weekday()
		msg_flg=0
		if ((dt.day,dt.month) not in no_trading) and weekday:
			hour=dt.hour
			minute=dt.minute
			if (9,00)<=(dt.hour,dt.minute)<=(16,00):
				_=q_msg_f.put('Start')
				_=q_msg_o.put('Start')
				msg_flg=1

		logger.info('Starting the main process loop.')
		print('Give \'s\' to exit program: ')

		while True:

			# Straight from SO
			i, o ,e=select.select([sys.stdin],[],[],5)
			if (i) and (sys.stdin.readline().split()[0]=='s'):
				_=q_msg_f.put('Exit')
				_=q_msg_o.put('Exit')
				for i in range(15,0,-1):
					logger.info(i)
					time.sleep(1)
				if (p_f.exitcode is None) and (not p_f.is_alive()):
					_=p_f.terminate()
				if (p_o.exitcode is None) and (not p_o.is_alive()):
					_=p_o.terminate()
				logger.info('Controlled shutdown')
				break

			# Check if we are in trading day
			dt=datetime.datetime.now()
			weekeday = 5>dt.weekday()
			if ((dt.day,dt.month) not in no_trading) and weekday:
				hour=dt.hour
				minute=dt.minute
				if (9,00)<=(dt.hour,dt.minute)<=(16,30):
					if msg_flg==0:
						_=q_msg_f.put('Start')
						_=q_msg_o.put('Start')
						msg_flg=1
				else:
					if msg_flg==1:
						_=q_msg_f.put('Stop')
						_=q_msg_o.put('Stop')
						time.sleep(15)
						msg_flg=0

			# Error in data feed
			if not q_err_f.empty():
				_=q_err_f.get()
				logger.warning('Error in datafeed')
				_=q_msg_f.put('Exit')
				_=q_msg_o.put('Exit')
				for i in range(15,0,-1):
					logger.info(i)
					time.sleep(i)
				if (p_f.exitcode is None) and (not p_f.is_alive()):
					_=p_f.terminate()
				if (p_o.exitcode is None) and (not p_o.is_alive()):
					_=p_o.terminate()
				logger.warning('Uncontrolled termination in datafeed')
				break

			# Error in ordering
			if not q_err_o.empty():
				_=q_err_o.get()
				logger.warning('Error in order placement')
				_=q_msg_f.put('Exit')
				_=q_msg_o.put('Exit')
				for i in range(15,0,-1):
					logger.info(i)
					time.sleep(1)
				if (p_o.exitcode is None) and (not p_o.is_alive()):
					_=p_o.terminate()
				if (p_f.exitcode is None) and (not p_f.is_alive()):
					_=p_f.terminate()
				logger.warning('Uncontrolled termination in datafeed')
				break

			# Check for new JSON
			if os.path.isfile(input_file[0]):
				try:
					with open(input_file[0],'rb') as fp:
						data_n=pickle.load(fp)
					logger.info('Ticker data succesfully loaded.')
					os.remove(input_file[0])
					tlist_n=[i[0] for i in data_n]
					tlist=list(set(tlist+tlist_n))
					for i in data_n:
						data_n[i]['position']=0
						data_n[i]['trailer']=0
					_=q_json.put(data_n)
					_=q_tlist_n.put(tlist)
				except Exception as e:
					logger.error('Something went wrong in reading the new input JSON.')
					logger.exception(e)

	# Uncontrolled exit
	except Exception as e:
		_=q_msg_f.put('Exit')
		_=q_msg_o.put('Exit')
		for i in range(15,0,-1):
			logger.info(i)
			time.sleep(1)
		if (p_f.exitcode is None) and (not p_f.is_alive()):
			_=p_f.terminate()
		if (p_o.exitcode is None) and (not p_o.is_alive()):
			_=p_o.terminate()
		logger.error('Uncontrolled termination of main function')
		logger.exception(e)