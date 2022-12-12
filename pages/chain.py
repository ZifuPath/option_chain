import streamlit as st
import time
import numpy as np
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt
st.set_page_config(page_title="Option Chain", page_icon='random', layout='wide')

st.markdown("# Option Chain")
st.sidebar.header("Option Chain")
symbol = 'BANKNIFTY'
with st.sidebar:
    symbol = st.selectbox(f'Select symbol',
                          ('BANKNIFTY', 'NIFTY'))



st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a option chain!"""
)
import datetime
l1 = []
expiry = [file for file in os.listdir(fr'dataset') if not file.__contains__('.csv')]
expiry_date = st.selectbox('Expiry Date', expiry)
#expiry = [file for file in os.listdir(fr'dataset') if not file.__contains__('.csv')]

def get_time_slots():
    b = []
    h = 9
    m = 12
    for i in range(123):
        if m == 60:
            h = h + 1
            m = 0
        a = datetime.time(h, m)
        m = m + 3
        b.append(a)
    return b


sequence = np.array(get_time_slots())
tt = datetime.datetime.now()
mo, day, hr, mm = tt.month, tt.day, tt.hour, tt.minute
df = pd.read_csv(f'dataset/2022-12-15/BANKNIFTY/22-12-12 12-21.csv')
df['datetime'] = pd.to_datetime(df.datetime)
time_of_day = df.datetime.iloc[0]
ltp_price = df.ltp.iloc[0]
strike = int(round(ltp_price/100,0)*100)
step = 100
strikes =[i for i in range(strike-10*step, strike+10*step, step)]
with st.sidebar:
    st.markdown(f'''### Time - {time_of_day.strftime('%b %d %H-%M')}\n
                LTP - {ltp_price}''')


df.STRIKE = df.STRIKE.astype(int)
df = df[df.STRIKE.isin(strikes)]
df['Call OI'] = df['Call OI']/25
df['Put OI'] = df['Put OI']/25
df.reset_index(inplace=True)
df = df.drop(columns=['datetime','ltp','index'])
th_props = [('font-size', '18px'), ('text-align', 'center'), ('font-weight', 'bold'), ('color', '#ffffff'),
            ('background-color', '#000000')]

td_props = [('font-size', '14px')]

styles = [dict(selector="th", props=th_props), dict(selector="td", props=td_props)]
df = (df.style.set_properties(**{'text-align': 'left'}).set_table_styles(styles)
      .background_gradient(axis=0, cmap='RdYlGn', subset=['% Call OI'])
      .background_gradient(axis=0, cmap='RdYlGn', subset=['% Put OI']))

st.table(df)
