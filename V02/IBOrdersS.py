#Import stuff
import logging
from ib_insync import * # Bad practice, bad bad practice...soo vitun soo!
import json
import pickle
import datetime

#import TailLogger as TL later for GUI


def IBOrdersS(d,q_data,q_json,q_msg_o,q_err_o):

	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IBOrdersScriptS')
	log2.setLevel(logging.INFO)

	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

	file_handler=logging.FileHandler('IBOrdersScriptS.log')
	file_handler.setFormatter(formatter)

	log2.addHandler(file_handler)
	#---------------------------------------------------------------------------

	ib=IB()

	try:

		# Start main process loop
		while True:

			# If there is a new dicitionary in pipeline
			if not q_json.empty():
				d_n=q_json.get()
				d.update(d_n)

			# Check the message queue and either connect or quit
			if not q_msg_o.empty():

				message=q_msg_o.get() # Get the message

				if message=='Start':  # Start IB

					log2.info('Starting IB ordering process')
					_=util.logToFile('IBOrders.log',level=20) # Logger
					_=ib.connect('127.0.0.1', 7497, 2) # Connect to IB
					ib.sleep(1)
					log2.info('Connected to IB ordering process')

				elif message=='Stop':  # Disconnect IB

					if ib.isConnected():
						ib.disconnect()
						ib.sleep(1)
						log2.info('Controlled disconnection from IB ordering process')

				elif message=='Exit':  # Exit from process

					if ib.isConnected():
						ib.disconnect()

					ib.sleep(1)
					log2.info('Ordering process terminated')
					break

			# While we are connected, do stuff
			if ib.isConnected():

				# If there is data in the queue, go through it and make trades
				if not q_data.empty():

					data=q_data.get()      # Get data
					ticker=data[0].symbol  # ticker
					avain=[i for i in d if ticker in i] # Get the keys of d we need

					for i in avain: # Loop over all keys that have the ticker

						# If we have a position open
						if d[i]['position']:

							# Close long position
							if (data[4]<=d[i]['stop_loss_price']):# or (d[i]['time_limit']<=datetime.datetime.now()):
								log2.info('Closing long position for '+ticker+' with ticktime '+str(data[1])+' and price '+str(data[4]))
								order=MarketOrder('SELL',d[i]['quantity'])
								trade=ib.placeOrder(data[0],order)
								_=d.pop(i,None)

								# Write the updated data dict to JSON for safety
								with open('positions.pickle','wb') as fp:
									_=pickle.dump(d,fp)

							# Else adjust stop parameter
							else:
								if (d[i]['trailer']==0):
									if (data[4]>=d[i]['trail_price']):                         # Set trailer
										d[i]['stop_loss_price']=0.99*data[4]
										d[i]['trailer']=1

										# Write the updated data dict to JSON for safety
										with open('positions.pickle','wb') as fp:
											_=pickle.dump(d,fp)

									elif (d[i]['trail_price']>data[4]>d[i]['stop_win_price']): # Adjust stop loss
										d[i]['stop_loss_price']=d[i]['stop_win_price']

										# Write the updated data dict to JSON for safety
										with open('positions.pickle','wb') as fp:
											_=pickle.dump(d,fp)

								elif (d[i]['trailer']==1) and (0.99*data[4]>d[i]['stop_loss_price']): # Adjust trailer
									d[i]['stop_loss_price']=0.99*data[4]

									# Write the updated data dict to JSON for safety
									with open('positions.pickle','wb') as fp:
										_=pickle.dump(d,fp)

						else:

							# Open long position
							log2.info('Placing long market order for '+ticker+' with ticktime '+str(data[1])+' and price '+str(data[4]))
							order=MarketOrder('BUY',d[i]['quantity'])
							trade=ib.placeOrder(data[0],order)
							d[i]['position']=1

							# Write the updated data dict to JSON for safety
							with open('positions.pickle','wb') as fp:
								_=pickle.dump(d,fp)

	except Exception as e:
		_=q_err_o.put(d)
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception IB ordering process')
		log2.exception(e)

