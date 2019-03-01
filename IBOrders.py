#Import stuff
import logging
from ib_insync import * # Bad practice, bad bad practice...soo vitun soo!
import json
import model
import DataUtilities

#import TailLogger as TL later for GUI


def IBOrders(d,q_data,q_msg_o,q_err_o):
	
	# Setup second logger-------------------------------------------------------
	log2=logging.getLogger('IBOrdersScript')
	log2.setLevel(logging.INFO)
	
	formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
	
	file_handler=logging.FileHandler('IBOrdersScript.log')
	file_handler.setFormatter(formatter)
	
	stream_handler=logging.StreamHandler()
	stream_handler.setFormatter(formatter)
	
	log2.addHandler(file_handler)
	log2.addHandler(stream_handler)
	#---------------------------------------------------------------------------
	
	ib=IB()
	
	try:
		
		# Start main process loop
		while True:
			
			# Check the message queue and either connect or quit
			if not q_msg_o.empty():
				
				message=q_msg_o.get() # Get the message
				
				if message=='Start':  # Start IB
				
					log2.info('Starting IB ordering process')
					_=util.logToFile('IBOrders.log',level=20,ibapiLevel=20) # Logger
					_=ib.connect('127.0.0.1', 7497, 2) # Connect to IB
					ib.sleep(1)
					log2.info('Connected to IB ordering process')
					
				elif message=='Stop':  # Stop IB
				
					if ib.isConnected():
						ib.disconnect()
						ib.sleep(1)
						log2.info('Controlled disconnection from IB ordering process')
					
			# While we are connected, do stuff
			if ib.isConnected():
				
				# If there is data in the queue, go through it and make trades
				if not q_data.empty():
				
					data=q_data.get()      # Get data
					ticker=data[0].symbol  # tikcer
					
					# Call the model, it should know your input JSON structure
					trd=model.Position(data,d[ticker])
					
					# Get model parameters, UNITS and stop percentage
					params=model.Parameters(d[ticker])
					
					# If we are going to open a position, check time of day here
					if trd==1:
								
						# Open position
						log2.info('Placing market order for '+ticker+' with ticktime '+str(data[1])+' and ask '+str(data[3]))
						order=MarketOrder('BUY',params[0])
						#contract=ib.qualifyContracts(Stock(,'Smart','USD'))
						trade=ib.placeOrder(data[0],order)
						
						# Update model dynamic parameters
						d[ticker][-1][0]=1                  # Position flag
						d[ticker][-1][1]=data[4]            # Open price 
						d[ticker][-1][2]=data[4]*params[1]  # Stop price
						
						# Write the updated model dict to JSON for safety
						_=DataUtilities.ModelOut(d)
					
					# If we are going to sell an open position
					elif trd==-1:
						
						# Close position
						log2.info('Closing position for '+ticker+' with ticktime '+str(data[1])+' and bid '+str(data[2]))
						order=MarketOrder('SELL',params[0])
						#contract=ib.qualifyContracts(Stock(str(data[0]),'Smart','USD'))
						trade=ib.placeOrder(data[0],order)
						
						# Update model dynamic parameters
						d[ticker][-1]=[0,0,0,0]
						
						# Write the updated model dict to JSON for safety
						_=DataUtilities.ModelOut(d)
						
					# Check if we need to adjust stop 
					elif trd==0:
						
						# Set trailing stop flg is needed
						if d[ticker][-1][0] and not d[ticker][-1][3]:
							d[ticker][-1][3]=model.SetTrail(data[4],d[ticker])
						
						# Adjust stop price (trailing stop) if needed
						if d[ticker][-1][0] and d[ticker][-1][3]:
							d[ticker][-1][2]=model.NewStop(data[4],d[ticker])
							
						# Write the updated model dict to JSON for safety
						_=DataUtilities.ModelOut(d)
						
	
	except KeyboardInterrupt:
		ib.disconnect()
		ib.sleep(1)
		log2.info('Controlled disconnection from IB ordering process')
	
	except Exception as e:
		ib.disconnect()
		ib.sleep(1)
		log2.error('Disconnected by exception IB ordering process')
		log2.exception(e)