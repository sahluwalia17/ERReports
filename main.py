import requests
import pandas as pd
from io import StringIO
import yfinance as yf

def getUpcomingTickers():
    apikey = "23459325c7mshc3b950155a6f61bp1fbe74jsn16a345f127f2"

    url = 'https://www.alphavantage.co/query?function=EARNINGS_CALENDAR&horizon=3month&apikey=' + apikey
    response = requests.get(url)

    if response.status_code != 200:
        print("Error: unable to retrieve data")
        exit()

    raw_data = StringIO(response.text)
    df = pd.read_csv(raw_data)
    filtered_df = df[df['currency'] == 'USD'][["symbol","name","reportDate"]]
    filtered_df["reportDate"] = pd.to_datetime(filtered_df["reportDate"])
    filtered_df = filtered_df.sort_values(by=["reportDate", "name"])

def getHistoricalERsForTicker(ticker):
    print("FETCHING: ", ticker)
    stock = yf.Ticker(ticker)
    earnings_calendar = stock.earnings_dates
    earnings_calendar.index = pd.to_datetime(earnings_calendar.index).tz_convert('America/New_York')
    current_time = pd.Timestamp.now(tz='America/New_York')
    past_earnings = earnings_calendar[earnings_calendar.index < current_time]
    last_12_reports = past_earnings.sort_index(ascending=False).head(12).index.tolist()
    percentChanges = []
    market_close_time = pd.Timestamp("16:00:00").time()
    for timestamp in last_12_reports:
        ER_time = timestamp.time()
        ER_date = timestamp.date()
        if ER_time >= market_close_time:
            #aftermarket report
            closePrice1 = yf.download(ticker, start=ER_date, end=ER_date + pd.Timedelta(days=1))['Close']
            closePrice1 = closePrice1.iloc[0] if not closePrice1.empty else None
            
            closePrice2 = yf.download(ticker, start=ER_date + pd.Timedelta(days=1), end=ER_date + pd.Timedelta(days=2))['Close']
            closePrice2 = closePrice2.iloc[0] if not closePrice2.empty else None
            
            if closePrice1.item() is not None and closePrice1.item() != 0:
                percentChange = (closePrice2 - closePrice1) / closePrice1
                percentChanges.append(f"{round(percentChange.item() * 100, 2)}%")
        else:
            #premarket report
            closePrice1 = yf.download(ticker, start=ER_date - pd.Timedelta(days=1), end=ER_date)['Close']
            closePrice1 = closePrice1.iloc[0] if not closePrice1.empty else None
            
            closePrice2 = yf.download(ticker, start=ER_date, end=ER_date + pd.Timedelta(days=1))['Close']
            closePrice2 = closePrice2.iloc[0] if not closePrice2.empty else None
            
            if closePrice1.item() is not None and closePrice1.item() != 0:
                percentChange = (closePrice2 - closePrice1) / closePrice1
                percentChanges.append(f"{round(percentChange.item() * 100, 2)}%")
    print("FINISHED: ", ticker)
    print(percentChanges)
        


getHistoricalERsForTicker("MSFT")


