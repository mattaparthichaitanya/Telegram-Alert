import pricedata
maxprofit = ((pricedata.PESELL+pricedata.CESELL)-(pricedata.PEBUY+pricedata.CEBUY))*25
exitprofit = 2000
print("profit",exitprofit)
# maxloss = ((pricedata.PEBUY+pricedata.CEBUY)+(pricedata.PESELL+pricedata.CESELL))*25
# print(round(int(float(maxprofit)),-2))
# print(maxprofit)
# print(exitprofit)
# print(exitloss)