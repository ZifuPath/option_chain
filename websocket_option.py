import pandas as pd
import os
import websocket
import ast
import json
import datetime
from dotenv import load_dotenv
from py5paisa import FivePaisaClient
import warnings
warnings.filterwarnings('ignore')
alist = []
load_dotenv()


class OptionChain:

    def __init__(self, expiry: str, symbol: str):
        self.expiry = expiry
        self.email = os.getenv('email')
        self.password = os.getenv('passwd')
        self.dob = os.getenv('dob')
        self.cred = ast.literal_eval(os.getenv('cred'))
        self.symbol = symbol
        base = os.getcwd()
        base = os.path.join(base, 'dataset')
        if not os.path.exists(os.path.join(base, self.expiry)):
            os.mkdir(f'dataset/{self.expiry}')
            os.mkdir(f'dataset/{self.expiry}/OI')
            os.mkdir(f'dataset/{self.expiry}/LTP')

    def __str__(self):
        return f'{self.__dict__}'

    def client_login(self):
        # GET PY5PAISA OBJECT  return py5paisa object
        client = FivePaisaClient(email=self.email, passwd=self.password, dob=self.dob, cred=self.cred)
        client.login()
        return client

    @staticmethod
    def convert_string_literal(message):
        message = ast.literal_eval(message)
        if isinstance(message,dict):
            oi = message['OpenInterest'],
            ltp = 0
        else:
            message = message[0]
            ltp = message['LastRate']
            oi = 0
        return message, oi, ltp

    @staticmethod
    def get_payload(df: pd.DataFrame):
        feature = ['Exch', 'ExchType', 'Scripcode']
        df1 = df[feature]
        adict = df1.to_dict('records')
        return adict

    def get_dataframe(self, symbol, exch):
        df = pd.read_csv('dataset/scripmaster-csv-format.csv')
        if self.symbol == symbol:
            df = df[(df.Exch == exch) & (df.ExchType == 'D') & (df.Expiry == f'{self.expiry} 14:30:00')]
        df = df[df.Name.str.contains(f'{self.symbol}')]
        df['Symbol'] = df.Name.str.split(' ', expand=True)[0]
        df['StrikePrice'] = df.Name.str.split(' ', expand=True)[5]
        df['OptionType'] = df.Name.str.split(' ', expand=True)[4]
        return df

    def get_wspayload(self, symbol, exch, market='oi'):
        client = self.client_login()
        df = self.get_dataframe(symbol, exch)
        req_list = self.get_payload(df)
        req_data = client.Request_Feed(market, 's', req_list)
        return req_data, df

def get_expiry_date(symbol):
    df = pd.read_csv('dataset/scripmaster-csv-format.csv')
    df = df[df.Root == symbol]
    df.Expiry = pd.to_datetime(df.Expiry)
    df = df[df.Expiry > datetime.datetime.now()]
    df = df.sort_values('Expiry')
    expiry = df.Expiry.iloc[0].strftime('%Y-%m-%d')
    return expiry

def get_websocket(wsPayload, oc_scrapper: OptionChain, df: pd.DataFrame, client,OI=True):
    client.web_url = f'wss://openfeed.5paisa.com/Feeds/api/chat?Value1={client.Jwt_token}|{client.client_code}'
    auth = client.Login_check()
    alist = []
    def on_message(ws, message):

        global alist
        st, oi ,ltp = oc_scrapper.convert_string_literal(message)
        if st['Token'] not in alist:
            df.loc[df['Scripcode'] == st['Token'], 'OI'] = oi
            df.loc[df['Scripcode'] == st['Token'], 'ltp'] = ltp
            alist.append(st['Token'])
            print(len(alist),len(df))
            if len(alist) >= len(df):
                print('run completed')
                strike_list = list(df['Name'].unique())
                df['datetime'] = datetime.datetime.now()
                for item in strike_list:
                    df1 = df.query(f'Name=="{item}"')
                    symbol = f'{item}'
                    if OI:
                        df1.to_csv(f'dataset/{oc_scrapper.expiry}/OI/{symbol}.csv', mode='a', index=False, header=False)
                    else:
                        df1.to_csv(f'dataset/{oc_scrapper.expiry}/LTP/{symbol}.csv', mode='a', index=False, header=False)
                alist = []
                on_close(ws)

    def on_error(ws, error):
        print(error)

    def on_close(ws):
        print(f"Streaming Stopped {datetime.datetime.now()}")
        ws.close()

    def on_open(ws):
        print("Streaming Started")
        ws.send(json.dumps(wsPayload))

    ws = websocket.WebSocketApp(client.web_url,
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                cookie=auth)

    ws.run_forever()


def run_websockets(symbol, exch, expiry , oc_scrapper):
    payload, df = oc_scrapper.get_wspayload(symbol, exch)
    client = oc_scrapper.client_login()
    get_websocket(oc_scrapper=oc_scrapper, wsPayload=payload, df=df, client=client)
    payload1, df1 = oc_scrapper.get_wspayload(symbol, exch, market='mf')
    get_websocket(oc_scrapper=oc_scrapper, wsPayload=payload1, df=df1, client=client,OI=False)
    COL = ['Exch', 'ExchType', 'Scripcode', 'Name', 'Series', 'Expiry', 'CpType', 'Strikerate', 'WireCat', 'ISIN',
           'Fullname', 'LotSize', 'AllowedToTrade', 'QtyLimit', 'Multiplier', 'Underlyer', 'Root', 'TickSize', 'Symbol',
           'StrikePrice', 'OptionType', 'OI', 'LTP', 'datetime']
    COL1 = [ 'datetime','Symbol','StrikePrice', 'OptionType', 'OI', 'LTP', ]
    for i in os.listdir(f'dataset/{expiry}/OI'):
        df = pd.read_csv(f'dataset/{expiry}/OI/{i}', names=COL)
        df1 = pd.read_csv(f'dataset/{expiry}/LTP/{i}', names=COL)
        df['LTP'] = df1['LTP']
        df = df[COL1]
        df.to_csv(f'dataset/{expiry}/OC/{i}', index=False,mode='a',header=False)
    get_option_chain(expiry)


def get_option_chain(expiry):
    alist = []
    for i in os.listdir(f'dataset/{expiry}/OC'):
        if i.__contains__('CE'):
            b = i.replace('CE', 'PE')
            df = pd.read_csv(f'dataset/{expiry}/OC/{i}')
            df1 = pd.read_csv(f'dataset/{expiry}/OC/{b}')
            alist.append([df['datetime'].iloc[-1],
                          df['OI'].iloc[-1],
                          df['LTP'].iloc[-1],
                          df['StrikePrice'].iloc[-1],
                          df1['LTP'].iloc[-1],
                          df1['OI'].iloc[-1]])
    oc = pd.DataFrame(alist,columns = ['datetime','OI_CE', 'LTP_CE', 'STRIKE', 'LTP_PE', 'OI_PE'])
    oc['datetime'] = datetime.datetime.now()
    dates = datetime.datetime.now().strftime('%Y-%m-%d %H-%M')
    oc.to_csv(f'oc/option_chain_{dates}.csv',index=False)

def app():
    symbol = 'BANKNIFTY'
    exch = 'N'
    expiry = get_expiry_date(symbol)
    oc_scrapper = OptionChain(expiry=expiry, symbol= symbol)
    run_websockets(symbol, exch, expiry, oc_scrapper)


if __name__ == '__main__':
    app()
