import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from utils import gmail_extract,excel_load
import gspread
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(layout="wide", page_title="Akshay's Stock Portfolio Dashboard")

st.title("📈 Stock Portfolio Dashboard")

my_password = st.text_input("Enter your Password", type= 'password')

secret_pass = st.secrets["sec_pass"]

if st.button('Refresh Gmail') and my_password == secret_pass:

    msg_mail = gmail_extract()
    msg_excel = excel_load()

    if msg_mail =='Done' and msg_excel == 'Done':
        st.write('Excel created')
    

if st.button("Submit") and my_password == secret_pass:

    # Step 1: Authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
    client = gspread.authorize(creds)

    # Step 2: Open the Google Sheet and read data
    sheet = client.open("Master_Portfolio_Tracker").worksheet("Sheet1")
    data = sheet.get_all_records()  # Gets all data as list of dicts

    # Step 3: Load into DataFrame
    df = pd.DataFrame(data)
    main_df = df
    # df = pd.read_excel("excel_attachments/Master_Portfolio_Tracker.xlsx")
    # main_df = df

    st.subheader("📊 Portfolio Summary")
    df['Date'] = pd.to_datetime(df['Date'])
    df['Total Gain']=df['Current Value']-df['Invested Value']
    max_date = df['Date'].max()
    df["Month"] = df["Date"].dt.to_period("M")
    print(df)

    final_df = df[df['Date']==max_date]   
    total_invested = final_df['Invested Value'].sum()
    total_current = final_df['Current Value'].sum()
    total_gain = total_current - total_invested
    total_gain_pct = (total_gain / total_invested) * 100
    todat_pl = final_df['''Today's P&L'''].sum()

    col1, col2, col3, col4,col5 = st.columns(5)
    col1.metric("Total Invested", f"₹{total_invested:,.2f}")
    col2.metric("Current Value", f"₹{total_current:,.2f}")
    col3.metric("Total Gain/Loss", f"₹{total_gain:,.2f}", delta=f"{total_gain_pct:.2f}%")
    col4.metric("Return %", f"{total_gain_pct:.2f}%")
    col5.metric("Today's P&L", f"₹{todat_pl:,.2f}")

    portfolio_value = df.groupby('Date')['Current Value'].sum().reset_index()
    profit_value = df.groupby('Date')['Total Gain'].sum().reset_index()
    month_value = df.groupby('Month')['''Today's P&L'''].sum().reset_index()
    month_value["Month_Name"] = month_value["Month"].dt.strftime("%b")
    month_value=month_value.sort_values(by='Month')
    month_value = month_value[['Month_Name','''Today's P&L''']]
    #print(month_value)

    month_value["MoM_Change"] = month_value['''Today's P&L'''].diff()

    # Optional: percentage change
    month_value["MoM_%"] = month_value['''Today's P&L'''].pct_change() * 100


    stock_value = final_df.groupby('Script Name')[['Invested Value','Unrealized P&L','Current Value']].sum().reset_index()
    stock_value['Current Value']=stock_value['Current Value'].astype(float)
    stock_value.sort_values(by='Current Value', ascending=False, inplace = True)
    attrs = ['Invested Value','Unrealized P&L','Current Value']
    for i in attrs:
         stock_value[i]=stock_value[i].apply(lambda x: f"₹ {round(x):,}")

    # Charts

    st.subheader('📈 Daily P&L trend')
    last_90_days = df[df['Date'] >= pd.Timestamp.today() - pd.Timedelta(days=90)]
    grouped_df = last_90_days.groupby('Date').agg({'''Today's P&L''':'sum'}).reset_index()

    line_graph = px.line(grouped_df, x="Date", y='''Today's P&L''', title='Daily P&L Statement')
    st.plotly_chart(line_graph, use_container_width=True)
    st.subheader('📈 Stock Details')
    st.dataframe(stock_value, hide_index =1)

    # st.subheader("📈 Performance by Stock")
    # fig = px.bar(final_df, x='Script Name', y='Unrealized P&L', color='Unrealized P&L',
    #                 color_continuous_scale=['red', 'green'], title="Gain/Loss by Stock")
    # st.plotly_chart(fig, use_container_width=True)

    # c1, c2 = st.columns(2)
    
    # with c1:
    #     st.subheader("Performance by Stock")
    #     fig3 = px.bar(final_df, x='Script Name', y='Unrealized P&L', color='Unrealized P&L',
    #                 color_continuous_scale=['red', 'green'], title="Gain/Loss by Stock")
    #     st.plotly_chart(fig3, use_container_width=True)

    # with c2:
    #     st.subheader("Individual Stock Performance over time")
    #     fig4 = px.line(df, x='Date', y='Current Value', color='Script Name')
    #     st.plotly_chart(fig4, use_container_width=True)

    fig3 = px.treemap(final_df, path=[px.Constant("Akshay's Portfolio"), 'Script Name'], values='Current Value',
                  color='Current Value', hover_data=['Unrealized P&L'],
                  color_continuous_scale='tealgrn',
                  color_continuous_midpoint=np.average(df['Current Value'], weights=df['Current Value']),title = '''Portfolio Heatmap''')
    fig3.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    st.plotly_chart(fig3, use_container_width=True)

    # pie = px.pie(final_df, names='Script Name', values='Current Value', title='Portfolio Allocation', hole=0.4)
    # st.plotly_chart(pie, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
            st.subheader("Total Profit Value Over Time")
            fig5 = px.line(profit_value, x='Date', y='Total Gain')
            st.plotly_chart(fig5, use_container_width=True)
       

    with col2:
        st.subheader("Total Portfolio Value Over Time")
        fig2 = px.line(portfolio_value, x='Date', y='Current Value')
        st.plotly_chart(fig2, use_container_width=True)



    st.subheader("Portfolio Allocation")
    fig1 = px.pie(final_df, names='Script Name', values='Current Value', hole=0.4)
    st.plotly_chart(fig1, use_container_width=True)

    c10, c11 = st.columns(2)

    c10.subheader("📈 Monthly Profit Trend")
    fig_bar = px.bar(month_value,x='Month_Name',y='''Today's P&L''')
    c10.plotly_chart(fig_bar, use_container_width=True)

    c11.subheader("📊 Month-over-Month Change")
    fig_bar_2 = px.bar(month_value,x='Month_Name',y='''MoM_Change''')
    c11.plotly_chart(fig_bar_2, use_container_width=True)


    tickers = final_df['ISIN'].unique().tolist()
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
