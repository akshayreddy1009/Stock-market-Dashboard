import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

st.set_page_config(layout="wide", page_title="Akshay's Stock Portfolio Dashboard")

st.title("📈 Stock Portfolio Dashboard")

my_password = st.text_input("Enter your Password", value='Password', type= 'password')
if st.button("Submit") and my_password == 'Ipl20sunrh!':
    df = pd.read_excel("excel_attachments\Master_Portfolio_Tracker.xlsx")
    st.subheader("📊 Portfolio Summary")
    df['Date'] = pd.to_datetime(df['Date'])
    max_date = df['Date'].max()

    final_df = df[df['Date']==max_date]   
    total_invested = final_df['Invested Value'].sum()
    total_current = final_df['Current Value'].sum()
    total_gain = total_current - total_invested
    total_gain_pct = (total_gain / total_invested) * 100

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invested", f"₹{total_invested:,.2f}")
    col2.metric("Current Value", f"₹{total_current:,.2f}")
    col3.metric("Total Gain/Loss", f"₹{total_gain:,.2f}", delta=f"{total_gain_pct:.2f}%")
    col4.metric("Return %", f"{total_gain_pct:.2f}%")

    # Charts
    st.subheader("📈 Performance by Stock")
    fig = px.bar(final_df, x='Script Name', y='Unrealized P&L', color='Unrealized P&L',
                    color_continuous_scale=['red', 'green'], title="Gain/Loss by Stock")
    st.plotly_chart(fig, use_container_width=True)

    pie = px.pie(final_df, names='Script Name', values='Current Value', title='Portfolio Allocation')
    st.plotly_chart(pie, use_container_width=True)













    tickers = df['ISIN'].unique().tolist()
    cleaned_tickers = [item.strip() for item in tickers]
    stock_dict = {}
    new_tickers = []

    for i in cleaned_tickers:

        stock = yf.Ticker(i)
        info = stock.info.get('shortName')
        stock_dict[i]=info
        new_tickers.append(info)


    data = yf.download(cleaned_tickers, period='1mo', interval='1d', group_by='ISIN')
    top_level = data.columns.get_level_values(0)
    top_labels = list(pd.unique(top_level))
    new_columns = data.columns.map(lambda x: (stock_dict.get(x[0], x[0]), x[1]))
    data.columns = pd.MultiIndex.from_tuples(new_columns)
    #st.dataframe(data)

    st.subheader("Portfolio Performance")
    for ticker in new_tickers:
        if ticker in data:
            price_data = data[ticker]['Close']
            fig = px.line(price_data, title=f"{ticker} Price")
            st.plotly_chart(fig)

else:

    st.write('### Entered Password is incorrect')            