import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👨🏽‍💻",
)

st.write("# Welcome to FINMAN Stock App! 📈")

st.sidebar.success("Select a page above.")

st.markdown(
    """
    This app uses open interest data of option strikes
    ### FNO stock
    ### chartink Investment scanners
    - Investment stocks
    - Pivot Intraday Stock
    - Special Stock
"""
)

# import plotly.express as px
# import pandas as pd
# from websocket_option import OptionChain,get_expiry_date
# from datetime import datetime,timedelta
# df = pd.read_csv('oc/option_chain_2022-12-07 21-03.csv')
# # print(df.head())
#
#
# symbol = 'BANKNIFTY'
# expiry = get_expiry_date(symbol)
#
#
# oc = OptionChain(expiry, symbol)
# client = oc.client_login()
# t1 = datetime.today().strftime('%Y-%m-%d')
# t2 = (datetime.today() - timedelta(days=0)).strftime('%Y-%m-%d')
# df = client.historical_data(Exch='N', ExchangeSegment='C', ScripCode=999920005, time='5m',From=t2, To= t1)
# print(df.head())
# import plotly.graph_objects as go
#
#
# candlestick = go.Candlestick(x=df.Datetime,
#                      open=df['Open'],
#                      high=df['High'],
#                      low=df['Low'],
#                      close=df['Close'],
#                      showlegend=False
#                             )
# fig = go.Figure(data=[candlestick])
# fig.update(layout_xaxis_rangeslider_visible=True)
# fig.update_layout(
#     width=800, height=600,
#     title="BNF",
#     yaxis_title='BANKNIFTY Stock',
# )
#
# fig.show()