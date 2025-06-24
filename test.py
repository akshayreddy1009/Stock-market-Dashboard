import yfinance as yf

a= 'TCS.NE'

data = yf.Ticker(a)

print(data.info.get('ISIN'))