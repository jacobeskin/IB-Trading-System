"""
Model that knows what the input JSON looks like and what are the list elements.
Contain the following small tools:

- Position, buy sell or do nothing
- Parameters, model parameters relevant for doing a trade and updating the dict
- SetTrail, sets trailing stop
- NewStop, updates stop price

"""


def Position(data,d_data):
	"""
	Returns 1 for opening a position, 0 for do nothing, -1 for selling a position. 
	In case of an error with the shape of the JSON value list, return -2.
	"""
	
	mid = (data[3]-data[2])/2
	
	# Check if the length of d_data is correct
	if len(d_data)!=7: return(-2)
	
	# If there is no open position
	if d_data[6][0]==0:
		
		# Check conditions for buying
		if (data[4]>d_data[0]) and (d_data[1]<=data[5]): return(1)
	
	# If there is a position open	
	elif d_data[6][0]==1:
		
		# Check condition for selling that position
		if (data[5]<=d_data[6][2]): return(-1)
		
	return(0)
	

def Parameters(d_data):
	"""
	Returns the list [UNITS, stop%]
	"""
	return([d_data[2],d_data[3]])


def SetTrail(price,d_data):
	"""
	Set trailing stop flag
	"""
	if (d_data[6][3]==0) and (price>=d_data[6][1]*(1+d_data[5])): return(1)
	else: return(0)
	

def NewStop(price,d_data):
	"""
	Return adjusted stop or just the original stop
	"""
	if (price*(1-d_data[4]))>d_data[-1][2]: return(price*(1-d_data[4]))
	else: return(d_data[-1][2])
	