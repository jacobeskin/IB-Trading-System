"""
Need to know basis.
"""

# import stuff

import GetData, MakeOrders, CancelAllOrders, GetPositions
from datetime import datetime
import pandas as pd

# Osku pistaa kellonajat
tunti1 = 
minuutti1 = 
tunti2 = 
minuutti2 = 

# Tanne voi laittaa kaikki aktiviteetti joka tapahtuu ennen ensimmaista aikaeventtia


# Venataan etta kello on (tunti1,minuutti1) kun kaikki muu on saatu valmiiksi
while (datetime.now().hour, datetime.now().minute)<(tunti1, minuutti1):
	continue

# Perutaan kaikki avoimet orderit jotak eivat tayttyneet
_=CancelAllOrders.IB_CancelAllOrders()

# Seuraavat askeleet ennen toista aikaeventtia




# Kun kaikki muu on valmista, odotetaan seuraavaa aikaeventtia
while (datetime.now().hour, datetime.now().minute)<(tunti2, minuutti2):
	continue

# Haetaan data IB:sta, tarvitsee tikkerilistan
IB_price_dataframe = GetData.IB_GetData(ticker_list)

# Tahan tulee datan murskaus yms portfolion rakennus osa


# Lahetetaan market orderit, tarvitsee data dictionaryn
_=MakeOrders.IB_MarketOrders(data_dict)

# Laske mitka on limit hinnat ja rakenna uusi data dictionary


# Lahetetaan Limit On Open tilaukse
_=MakeOrders.IB_LimitOnOpenOrders(data_dict_limit)






