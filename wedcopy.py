import time
from datetime import timedelta
from api_helper import ShoonyaApiPy
import credentials
import datetime
from datetime import date
import os
import WeddingWaitTime
from pathlib import Path
api = ShoonyaApiPy()
today = date.today()
yesterday = today-timedelta(days=1)
###########################
#########Main Login #############
# ret = api.login(userid=credentials.user, password=credentials.u_pwd, twoFA=credentials.factor2, vendor_code=credentials.vc, api_secret=credentials.app_key, imei=credentials.imei)
# ret = ret['susertoken']
# f = open('TOKEN','w+')
# f.write(ret)
# f.close()
########Token Login###########
k = open("TOKEN",'r')
l = (k.read())
ok = api.set_session(userid=credentials.user, password=credentials.u_pwd, usertoken=l)
token = api.get_quotes('NSE', 'Nifty Bank')['token']
lastBusDay = datetime.datetime.today()
lastBusDay = lastBusDay.replace(hour=WeddingWaitTime.hour, minute=WeddingWaitTime.minutes, second=0, microsecond=0)
# lastBusDay = lastBusDay.replace(hour=9, minute=58, second=0, microsecond=0)
k = lastBusDay.timestamp()
ret = api.get_time_price_series(exchange='NSE', token=token, starttime=lastBusDay.timestamp(),endtime=lastBusDay.timestamp(), interval=1)
bnclose = ret[0]['intc']
print("BANKNIFTY-BASE",bnclose)
option_ki_dari_edi = round((int(float(bnclose))), -2)
cehedge_ki_dari_edi = option_ki_dari_edi+1000
pehedge_ki_dari_edi = option_ki_dari_edi-1000
# print(cehedge_ki_dari_edi)
# print(pehedge_ki_dari_edi)
print("BANKNIFTY is at : ",option_ki_dari_edi)
puttoken = f'{"Nifty Bank"} {"PE"} {option_ki_dari_edi}'
calltoken = f'{"Nifty Bank"} {"CE"} {option_ki_dari_edi}'
puthedgetoken = f'{"Nifty Bank"} {"PE"} {pehedge_ki_dari_edi}'
callhedgetoken = f'{"Nifty Bank"} {"CE"} {cehedge_ki_dari_edi}'

put = api.searchscrip(exchange='NFO',searchtext=puttoken)['values'][0]['tsym']
call = api.searchscrip(exchange='NFO',searchtext=calltoken)['values'][0]['tsym']
puthedge = api.searchscrip(exchange='NFO',searchtext=puthedgetoken)['values'][0]['tsym']
callhedge = api.searchscrip(exchange='NFO',searchtext=callhedgetoken)['values'][0]['tsym']
print("ATM PUT :    ",(put))
print("ATM CALL :   ",call)
print("CALL HEDGE : ",callhedge)
print("PUT HEDGE :  ",puthedge)

########################################
optionsdatafile = datetime.datetime.today()
optionsdatafile = str(optionsdatafile.date())
print(optionsdatafile)
fileexist = Path(optionsdatafile)
file =open(optionsdatafile,'a+')
file.close()
file = open(optionsdatafile,'r')
fileinformation = file.read()
tpath = f'D://WEDDING-master//{today}'
ypath = f'D://WEDDING-master//{yesterday}'
purathanafile = os.path.exists(ypath)
kothafile = os.path.exists(tpath)
if purathanafile == False:
    s = open("strike.py",'w')
    s.write(f'PUT = "{put}"')
    s.write("\n" f'CALL = "{call}"')
    s.write("\n" f'CALLHEDGE = "{callhedge}"')
    s.write("\n" f'PUTHEDGE = "{puthedge}"')
    s.close()
if purathanafile == False:
    print("WEDDING STRATEGY STARTED")
    while True:
        ######################################################
        #Hedges
        CEHEDGE = api.place_order(buy_or_sell='B', product_type='M',
                        exchange='NFO', tradingsymbol=callhedge,
                        quantity=0, discloseqty=0, price_type='MKT',
                        retention='DAY', remarks=' CE BOUGHT')
        ret = api.get_order_book()
        cebuy = str(float(ret[0]['avgprc']))
        file = open("pricedata.py",'w')
        file.write(f"CEBUY = {cebuy}")
        file.close()
        PEHEDGE = api.place_order(buy_or_sell='B', product_type='M',
                        exchange='NFO', tradingsymbol=puthedge,
                        quantity=0, discloseqty=0, price_type='MKT',
                        retention='DAY', remarks=' PE BOUGHT')
        ret = api.get_order_book()
        pebuy = str(float(ret[0]['avgprc']))
        file = open("pricedata.py", 'a')
        file.write("\n" f"PEBUY = {pebuy}")
        file.close()
        time.sleep(1)
        ######################################################
        #ATM
        ATMCE = api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=call,
                        quantity=0, discloseqty=0, price_type='MKT',
                        retention='DAY', remarks=' CE SOLD')
        ret = api.get_order_book()
        cesell = str(float(ret[0]['avgprc']))
        file = open("pricedata.py", 'a')
        file.write("\n" f"CESELL = {cesell}")
        file.close()
        ATMPE = api.place_order(buy_or_sell='S', product_type='M',
                        exchange='NFO', tradingsymbol=put,
                        quantity=0, discloseqty=0, price_type='MKT',
                        retention='DAY', remarks=' PE SOLD')
        ret = api.get_order_book()
        pesell = float(ret[0]['avgprc'])
        file = open("pricedata.py", 'a')
        file.write("\n" f"PESELL = {pesell}")
        file.close()
        file = open(optionsdatafile, 'w+')
        file.write("WEDDING-DEPLOYED")
        file.close()
        exit()

else:
    print("EXPIRY-DAY MOWAA E ROJU")
    import strike
    tokenput = api.get_quotes('NFO', strike.PUT)['token']
    tokencall = api.get_quotes('NFO', strike.CALL)['token']
    tokenputhedge = api.get_quotes('NFO', strike.PUTHEDGE)['token']
    tokencallhedge = api.get_quotes('NFO', strike.CALLHEDGE)['token']
    # LTP of OPTIONS FETCHING from WEBSOCKET
    feed_opened = False
    feedJson = {}
    socket_opened = False
    orderJson = {}
    def evert_handler_feed_update(message):
        # print(message)
        if (('lp' in message) & ('tk' in message)):
            feedJson[message['tk']] = {'ltp': float(message['lp'])}
    def event_handler_order_update(inmessage):
        # print(inmessage)
        if (('norenordno' in inmessage) & ('status' in inmessage)):
            orderJson[inmessage['norenordno']] = {'status': inmessage['status']}
    def open_callback():
        global feed_opened
        feed_opened = True
    def setupWebSocket():
        global feed_opened
        api.start_websocket(order_update_callback=event_handler_order_update,
                            subscribe_callback=evert_handler_feed_update, socket_open_callback=open_callback)
        time.sleep(1)
        while (feed_opened == False):
            print("WAITING FOR WEBSOCKET TO OPEN MOWAA")
            pass
        return True
    setupWebSocket()
    api.subscribe([f'NFO|{tokenput}', f'NFO|{tokencall}', f'NFO|{tokenputhedge}', f'NFO|{tokencallhedge}'])
    time.sleep(1)
    # print('\n')
    while True:
        if purathanafile == True:
            import weddingexpirydaywaittime
            ###############################################################
            atmputltp = feedJson[tokenput]['ltp']
            atmcallltp = feedJson[tokencall]['ltp']
            otmcallltp = feedJson[tokencallhedge]['ltp']
            otmputltp = feedJson[tokenputhedge]['ltp']
            ######################################################################
            cp_pehedge = round(int(float(otmputltp)))
            cp_cehedge = round(int(float(otmcallltp)))
            cp_ceatm = round(int(float(atmcallltp)))
            cp_putatm = round(int(float(atmputltp)))
            # print(cp_pehedge)
            # print(cp_cehedge)
            # print(cp_ceatm)
            # print(cp_putatm)
            # print("CP HEDGE MOWAA",cp_pehedge)
            # print("################################")
            # print("################################")
            # print("################################")
            # print("################################")

            #################################################################
            import pricedata
            import plcalculation
            #################################################################
            if cp_pehedge >= pricedata.PEBUY:
                finalphedge = round(-(pricedata.PEBUY-cp_pehedge))
            if cp_pehedge <= pricedata.PEBUY:
                finalphedge = round(cp_pehedge-pricedata.PEBUY)
                ###################################
            if cp_cehedge >= pricedata.CEBUY:
                finalchedge = round(-(pricedata.CEBUY - cp_cehedge))
            if cp_cehedge <= pricedata.CEBUY:
                finalchedge = round(cp_cehedge-pricedata.CEBUY)
                ##################################
            if cp_ceatm >= pricedata.CESELL:
                finalce =  round(pricedata.CESELL-cp_ceatm)
            if cp_ceatm <= pricedata.CESELL:
                finalce =  round(pricedata.CESELL-cp_ceatm)
                #################################
            if cp_putatm >= pricedata.PESELL:
                finalpe =  round(pricedata.PESELL-cp_putatm)
            if cp_putatm <= pricedata.PESELL:
                finalpe =  round(pricedata.PESELL-cp_putatm)
                #################################
            # print("finalce",finalce)
            # print("finalpe",finalpe)
            # print("finalchedge",finalchedge)
            # print("finalphedge",finalphedge)
            atmpl = finalce+finalpe
            otmpl = finalchedge+finalphedge
            # print(atmpl)
            # print(otmpl)
            import colorama
            from colorama import Fore,Back,Style
            colorama.init()
            import os
            current_profit_or_loss = (atmpl+otmpl)*25
            if current_profit_or_loss >= 0:
                print(Style.BRIGHT+Fore.GREEN+"PROFIT of = ",current_profit_or_loss)
                time.sleep(1)
                # os.system('clr')
            if current_profit_or_loss <= 0:
                print(Style.BRIGHT+Fore.RED+"LOSS of = ",current_profit_or_loss)
                time.sleep(2)
                # os.system('clr')
            if current_profit_or_loss >= plcalculation.exitprofit:
                print(Style.BRIGHT,Fore.GREEN,"BOOKED PROFIT")
            #     #ATM BUY
            #     ATMCE = api.place_order(buy_or_sell='B', product_type='M',
            #                             exchange='NFO', tradingsymbol=call,
            #                             quantity=0, discloseqty=0, price_type='MKT',
            #                             retention='DAY', remarks=' CE BOUGHT')

            #     ATMPE = api.place_order(buy_or_sell='B', product_type='M',
            #                             exchange='NFO', tradingsymbol=put,
            #                             quantity=0, discloseqty=0, price_type='MKT',
            #                             retention='DAY', remarks=' PE BOUGHT')
            #     time.sleep(1)
            #     #OTM SELL
            #     CEHEDGE = api.place_order(buy_or_sell='S', product_type='M',
            #                               exchange='NFO', tradingsymbol=callhedge,
            #                               quantity=0, discloseqty=0, price_type='MKT',
            #                               retention='DAY', remarks=' CE BOUGHT')

            #     PEHEDGE = api.place_order(buy_or_sell='S', product_type='M',
            #                               exchange='NFO', tradingsymbol=puthedge,
            #                               quantity=0, discloseqty=0, price_type='MKT',
            #                               retention='DAY', remarks=' PE BOUGHT')
                exit()
            if current_profit_or_loss <= plcalculation.exitloss:
                print(Style.BRIGHT,Fore.RED,"BOOKED LOSS")
            #     #ATM BUY
            #     ATMCE = api.place_order(buy_or_sell='B', product_type='M',
            #                             exchange='NFO', tradingsymbol=call,
            #                             quantity=0, discloseqty=0, price_type='MKT',
            #                             retention='DAY', remarks=' CE BOUGHT')

            #     ATMPE = api.place_order(buy_or_sell='B', product_type='M',
            #                             exchange='NFO', tradingsymbol=put,
            #                             quantity=0, discloseqty=0, price_type='MKT',
            #                             retention='DAY', remarks=' PE BOUGHT')
            #     time.sleep(1)
            #     #OTM SELL
            #     CEHEDGE = api.place_order(buy_or_sell='S', product_type='M',
            #                               exchange='NFO', tradingsymbol=callhedge,
            #                               quantity=0, discloseqty=0, price_type='MKT',
            #                               retention='DAY', remarks=' CE BOUGHT')

            #     PEHEDGE = api.place_order(buy_or_sell='S', product_type='M',
            #                               exchange='NFO', tradingsymbol=puthedge,
            #                               quantity=0, discloseqty=0, price_type='MKT',
            #                               retention='DAY', remarks=' PE BOUGHT')
                exit()
            # if ((datetime.datetime.now()).time()).hour == 9 and (
            # (datetime.datetime.now()).time()).minute >= 45:
            #     print("SQUARED OFF")
            #     ATMCE = api.place_order(buy_or_sell='B', product_type='M',
            #                             exchange='NFO', tradingsymbol=call,
            #                             quantity=0, discloseqty=0, price_type='MKT',
            #                             retention='DAY', remarks=' CE BOUGHT')

            #     ATMPE = api.place_order(buy_or_sell='B', product_type='M',
            #                             exchange='NFO', tradingsymbol=put,
            #                             quantity=0, discloseqty=0, price_type='MKT',
            #                             retention='DAY', remarks=' PE BOUGHT')
            #     time.sleep(1)
            #     CEHEDGE = api.place_order(buy_or_sell='S', product_type='M',
            #                               exchange='NFO', tradingsymbol=callhedge,
            #                               quantity=0, discloseqty=0, price_type='MKT',
            #                               retention='DAY', remarks=' CE BOUGHT')

            #     PEHEDGE = api.place_order(buy_or_sell='S', product_type='M',
            #                               exchange='NFO', tradingsymbol=puthedge,
            #                               quantity=0, discloseqty=0, price_type='MKT',
            #                               retention='DAY', remarks=' PE BOUGHT')
            #     exit()
