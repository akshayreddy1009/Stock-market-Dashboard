import yfinance as yf
import pandas as pd

# my_list =['INE602W01027   ', 'INE067A01029   ', 'INE202E01016   ', 'INE532F01054   ', 'INE292B01021   ', 'INE002A01018   ', 'INE763I01026   ', 'INE071N01016   ', 'INE935B01025   ', 'INE217L01019   ', 'INE542W01025   ', 'INE484J01027   ', 'INE170V01027   ', 'INE415G01027   ', 'INE299N01021   ']
# cleaned_tickers = [item.strip() for item in my_list]
# stock_dict = {}
stock = yf.Ticker('AMD')

hist = stock.history(period ='max')
print(hist['Volume'].head(1))
