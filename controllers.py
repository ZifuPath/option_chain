from option_scrapper.websocket_option import *


def get_per_change(df):
    df['datetime'] = pd.to_datetime(df.datetime)
    for i in df.datetime.dt.date.unique():
        data = df[df.datetime.dt.date == i]
        data = data.reset_index()
        oi = data.OI.iloc[0]
        ltp = data.LTP.iloc[0]
        df.loc[df.datetime.dt.date == i, 'OIC'] = (df['OI'] - oi)/oi * 100 if oi != 0 else 0
        df.loc[df.datetime.dt.date == i, 'LTPC'] = (df['LTP'] - ltp) / ltp * 100 if ltp != 0 else 0
    return df['OIC'], df['LTPC']


def run_websockets(symbol, exch, expiry, oc_scrapper):
    payload, data = oc_scrapper.get_wspayload(symbol, exch)
    col =['Symbol', 'StrikePrice', 'OptionType', 'OI', 'LTP', 'datetime']
    client = oc_scrapper.client_login()
    get_websocket(oc_scrapper=oc_scrapper, wsPayload=payload, df=data, client=client)
    payload1, data1 = oc_scrapper.get_wspayload(symbol, exch, market='mf')
    get_websocket(oc_scrapper=oc_scrapper, wsPayload=payload1, df=data1, client=client, OI=False)
    col1 = ['datetime', 'Symbol', 'StrikePrice', 'OptionType', 'OI', 'OI_CHANGE', 'LTP', 'LTP_CHANGE']
    for i in os.listdir(f'dataset/{expiry}/{symbol}/OI'):
        oi_df = pd.read_csv(f'dataset/{expiry}/{symbol}/OI/{i}', names=col)
        ltp_df = pd.read_csv(f'dataset/{expiry}/{symbol}/LTP/{i}', names=col)
        oi_df['LTP'] = ltp_df['LTP']
        oi_df['OI_CHANGE'], oi_df['LTP_CHANGE'] = get_per_change(oi_df)
        oi_df = oi_df[col1]
        oi_df.to_csv(f'dataset/{expiry}/{symbol}/OC/{i}', index=False, mode='a', header=False)
    ltp = get_index(client, symbol)
    oc = get_option_chain(expiry, symbol, ltp)

    return oc


def get_option_chain(expiry, symbol, ltp):
    col1 = ['datetime', 'Symbol', 'StrikePrice', 'OptionType', 'OI', 'OI_CHANGE', 'LTP', 'LTP_CHANGE']
    l1 = []
    for i in os.listdir(f'dataset/{expiry}/{symbol}/OC'):
        if i.__contains__('CE'):
            b = i.replace('CE', 'PE')
            df = pd.read_csv(f'dataset/{expiry}/{symbol}/OC/{i}', names=col1).reset_index()
            df1 = pd.read_csv(f'dataset/{expiry}/{symbol}/OC/{b}', names=col1).reset_index()
            values = [df['datetime'].iloc[-1], df['OI'].iloc[-1], df['OI_CHANGE'].iloc[-1],
                      df['LTP'].iloc[-1], df['LTP_CHANGE'].iloc[-1], df['StrikePrice'].iloc[-1],
                      df1['OI'].iloc[-1], df1['OI_CHANGE'].iloc[-1], df1['LTP'].iloc[-1],
                      df1['LTP_CHANGE'].iloc[-1]]
            l1.append(values)
    oc = pd.DataFrame(l1, columns=['datetime','Call OI', '% Call OI', 'Call LTP', '% Call LTP', 'STRIKE',
                                   'Put LTP', '% Put LTP', 'Put OI', '% Put OI'])
    oc['datetime'] = datetime.datetime.now()
    oc.loc[:, 'ltp'] = ltp
    dates = datetime.datetime.now().strftime('%y-%m-%d %H-%M')
    oc.to_csv(f'dataset/{expiry}/{symbol}/{dates}.csv', index=False)
    return oc


def get_index(client,name):
    req_list_ = [{"Exch": "N", "ExchType": "C", "Symbol": name}]
    a = client.fetch_market_feed(req_list_)
    ltp = a['Data'][0]['LastRate']
    ltp = pd.DataFrame([ltp], columns=['ltp'])
    return ltp


