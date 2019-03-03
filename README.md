# IB-Trading-System
Automatic trading system with IB

3/3/2019:

Made changes to the README. Keeping it more as a journal and the step by step instructions are refined as the project advances. The basic high level layout of the functionality is as follows:

The IBMain.py functon is the main funciton that is run. It reads in the model JSON and converts it to a dictionary where keys are tickers and values are parameter LISTS specific for the model used. These parameters are inteded to be static parameters of the model. Those lists are then appended with a list of dynamic parameters that are not model specific, namely [position flg, position open price, stop price, trailing stop flg]. The resulting dicionary will be the model dictionary. The function then spawns 2 sub-processes, IBDFeed.py and IBOrders.py.

IBDfeed.py connects to IB, makes data requests and puts that data to a data queue. 

IBOrders connects to IB, reads data from the data queue, passes the data to the MODEL and based on the feedbac from the MODEL submits buy and sell orders. CURRENTLY CODE IS HARD CODED FOR BUY ONLY STRATEGY, THIS WILL BE CHANGED SHORTLY (legacy behavior).

MODEL is independent functionality that is inteded to be replacable and can be (at least in the future) whatever type of model that the user wants. The MODEL knows what the parameters are in the model dictionary and where. The only requirements for the model sript/object/whatever is that the following function calls have to make sense: 

trd=model.Position(data,d[ticker]), i.e. the model has to have a Position method that gives 1 for opening a position, -1 for closing a position or 0 for "do nothing".

params=model.Parameters(d[ticker]), i.e. the model has to have a Parameters method that gives a list where params[0] is the UNITS to be bought/sold and params[1] is the persentage (e.g. 0.02) for stoploss (this stoploss will not be submited to IB but followed locally)

d[ticker][-1][3]=model.SetTrail(data[4],d[ticker]), i.e. the model has to have a method SetTrail that sets trailing stop flag to 1 or 0 (initially it is 0) whenever applicable. This can be a method that returns always 0 if model does not have a trailing stop.

d[ticker][-1][2]=model.NewStop(data[4],d[ticker]), i.e. the model has to have a method NewStop that updates the StopLoss price if trailing stop is on. The method can return only the current stop price which is one of the dynamic parameters (see above) if trailing stop is not used.

No limit orders or stoploss orders are submitted to IB, only market orders, limits and stops are tracked locally.

Updates to README to follow with more detailed descriptions.
