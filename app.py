import time

from controllers import *


def app(symbol):
    exch = 'N'
    expiry = get_expiry_date(symbol)
    oc_scrapper = OptionChain(expiry=expiry, symbol=symbol)
    oc = run_websockets(symbol, exch, expiry, oc_scrapper)


if __name__ == '__main__':
    now = datetime.datetime.now().strftime('%A')
    L1 = ['26-Jan-2022', '19-Feb-2022', '01-Mar-2022', '18-Mar-2022',
          '01-Apr-2022', '02-Apr-2022', '10-Apr-2022', '14-Apr-2022',
          '15-Apr-2022', '01-May-2022', '03-May-2022', '16-May-2022',
          '10-Jul-2022', '09-Aug-2022', '15-Aug-2022', '31-Aug-2022',
          '02-Oct-2022', '05-Oct-2022', '09-Oct-2022', '23-Oct-2022',
          '26-Oct-2022', '08-Nov-2022', '25-Dec-2022']
    L1 = [datetime.datetime.strptime(x, "%d-%b-%Y").date() for x in L1]
    today = (datetime.datetime.today().date())
    if now in ['Sunday', 'Saturday']:
        print(f'NO TRADING BECOZ OF {now}')
    elif today in L1:
        print(f'Today is Holiday')
    else:
        while datetime.time(9, 11) < datetime.datetime.now().time() < datetime.time(15, 28):
            if datetime.datetime.now().minute % 3 == 0:
                app(symbol='BANKNIFTY')
                app(symbol='NIFTY')
                time.sleep(60)


