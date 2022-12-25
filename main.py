import requests
from api_helper import ShoonyaApiPy
import credentials
import time
api = ShoonyaApiPy()

#################################
PUT = "BANKNIFTY29DEC22P41000"
CALL = "BANKNIFTY29DEC22C42300"
PUTHEDGE = "BANKNIFTY29DEC22P40500"
CALLHEDGE = "BANKNIFTY29DEC22C42700"
#################################
# NEWCALL = "BANKNIFTY29DEC22C42700"
# NEWPUT = "BANKNIFTY29DEC22P40500"
################################
trade=0
bookedpoints = 0

TARGET = "2K TARGET REACHED MOWAAA"
ADJUSTCE = "CE ADJUST CHEYY MOWAA"
ADJUSTPE = "PE ADJUST CHEYY MOWAA"

TTOKEN = "5845408044:AAHiVh3g2EicS8ZyDnWxS_JA5qtZzluhVCo"
# url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
# print(requests.get(url).json())
chatid = '5294427850'
#Main login
# ret = api.login(userid=credentials.user, password=credentials.u_pwd, twoFA=credentials.factor2, vendor_code=credentials.vc, api_secret=credentials.app_key, imei=credentials.imei)
# ret = ret['susertoken']
# f = open('TOKEN','w+')
# f.write(ret)
# f.close()
#Token Login
k = open("TOKEN",'r')
l = (k.read())
ret = api.set_session(userid=credentials.user, password=credentials.u_pwd, usertoken=l)

# url = f"https://api.telegram.org/bot{TTOKEN}/sendMessage?chat_id={chatid}&text={ADJUSTPE}    {LTP}  BELOW PREMIUM SELL CHEYY MOWAA"
# print(requests.get(url).json()) # this sends the message

#CHECKING DIFFERENCE BETWEEN LTP
puttoken = api.get_quotes('NFO', PUT)['token']
calltoken = api.get_quotes('NFO', CALL)['token']
newcalltoken = api.get_quotes('NFO', NEWCALL)['token']
newputtoken = api.get_quotes('NFO', NEWPUT)['token']
puthedgetoken = api.get_quotes('NFO', PUTHEDGE)['token']
callhedgetoken = api.get_quotes('NFO', CALLHEDGE)['token']
#######
#WEB-SOCKET

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
api.subscribe([f'NFO|{puttoken}',f'NFO|{calltoken}',f'NFO|{puthedgetoken}',f'NFO|{callhedgetoken}'])
time.sleep(1)
if trade == 0:
    while True:
        # PUTLTP = feedJson[puttoken]['ltp']
        # time.sleep(1)
        # CALLLTP = feedJson[calltoken]['ltp']
        # time.sleep(1)
        atmputltp = feedJson[puttoken]['ltp']
        time.sleep(1)
        print(atmputltp)
        atmcallltp = feedJson[calltoken]['ltp']
        time.sleep(1)
        otmcallltp = feedJson[callhedgetoken]['ltp']
        time.sleep(1)
        otmputltp = feedJson[puthedgetoken]['ltp']
        time.sleep(1)
        ######################################################################
        cp_pehedge = round(int(float(otmputltp)))
        cp_cehedge = round(int(float(otmcallltp)))
        cp_ceatm = round(int(float(atmcallltp)))
        cp_putatm = round(int(float(atmputltp)))
        ####################################################################
        celtp_2 = round(int(float(atmcallltp / atmputltp) * 100))
        peltp_2 = round(int(float(atmputltp / atmcallltp) * 100))
        # print(celtp_2)
        # print(peltp_2)
        # exit()
        #################################################################
        import pricedata
        import plcalculation

        #################################################################
        if cp_pehedge >= pricedata.PEBUY:
            finalphedge = round(-(pricedata.PEBUY - cp_pehedge))
        if cp_pehedge <= pricedata.PEBUY:
            finalphedge = round(cp_pehedge - pricedata.PEBUY)
            ###################################
        if cp_cehedge >= pricedata.CEBUY:
            finalchedge = round(-(pricedata.CEBUY - cp_cehedge))
        if cp_cehedge <= pricedata.CEBUY:
            finalchedge = round(cp_cehedge - pricedata.CEBUY)
            ##################################
        if cp_ceatm >= pricedata.CESELL:
            finalce = round(pricedata.CESELL - cp_ceatm)
        if cp_ceatm <= pricedata.CESELL:
            finalce = round(pricedata.CESELL - cp_ceatm)
            #################################
        if cp_putatm >= pricedata.PESELL:
            finalpe = round(pricedata.PESELL - cp_putatm)
        if cp_putatm <= pricedata.PESELL:
            finalpe = round(pricedata.PESELL - cp_putatm)
            #################################
        # print("finalce",finalce)
        # print("finalpe",finalpe)
        # print("finalchedge",finalchedge)
        # print("finalphedge",finalphedge)
        atmpl = finalce + finalpe
        otmpl = finalchedge + finalphedge
        current_profit_or_loss = (atmpl + otmpl+ bookedpoints) * 25
        print(current_profit_or_loss)
        if current_profit_or_loss >= 2000:
            print("TARGET REACHED")
            url = f"https://api.telegram.org/bot{TTOKEN}/sendMessage?chat_id={chatid}&text={TARGET}"
            requests.get(url).json()  # this sends the message
            break
        if celtp_2 < 50:
            print("BOOK CE LEG")
            url = f"https://api.telegram.org/bot{TTOKEN}/sendMessage?chat_id={chatid}&text={ADJUSTCE}    {atmputltp}  BELOW PREMIUM SELL CHEYY MOWAA"
            requests.get(url).json() # this sends the message
            break
        if peltp_2 < 50:
            print("BOOK PE LEG")
            url = f"https://api.telegram.org/bot{TTOKEN}/sendMessage?chat_id={chatid}&text={ADJUSTPE}    {atmcallltp}  BELOW PREMIUM SELL CHEYY MOWAA"
            requests.get(url).json()  # this sends the message
            break

