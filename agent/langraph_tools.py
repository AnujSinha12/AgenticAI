from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import requests
from datetime import datetime

from langchain.tools import tool
from langchain_core.tools import StructuredTool

@tool
def fetch_exchange_rate(base_curency: str, target_currency: str, start_date: str, end_date: str) -> list:
    """
    Fetch BaseCountry and TargetCountry exchange rates
    e.g USA and UK currencies USD/GBP exchange rates trend for year 2025
    """
    # api url and results are changing frequently
    url = f"https://frankfurter.dev{start_date}..{end_date}?base={base_curency}&symbols={target_currency}"
    data = requests.get(url, verify=False).json()

    exchange_rates = []
    for key_date, val_rate in data['rates'].items():
        exchange_rates.append({
            'date': datetime.strptime(key_date, '%Y-%m-%d'),
            'rate': val_rate[target_currency]
        })

    df = pd.DataFrame(exchange_rates)
    df['month'] = df['date'].dt.month
    df = df.groupby('month', as_index=False).median()
    df = df.drop(columns=['month'])

    df['date'] = [row.date() for row in df['date']]

    return {
        'type': 'line_chart',
        'data': df.to_dict(orient='records'),
        'x': 'date',
        'y': 'rate',
        'title': 'Exchange Rate',
        'base_currency': base_curency,
        'target_currency': target_currency
    }

@tool
def fetch_inflation_rate(base_country: str, target_country: str):
    """
    Fetch BaseCountry and TargetCountry inflation rates
    e.g USA and UK inflation rates
    """

    df_inflation_rate = pd.read_excel(r'E:\work\GenAIApp\data\economic_data_top10.xlsx', sheet_name='inflation_rates')

    schema_dtypes = {
        'USA': 'float64',
        'China': 'float64',
        'Japan': 'float64',
        'Germany': 'float64',
        'India': 'float64',
        'UK': 'float64',
        'France': 'float64',
        'Italy': 'float64',
        'Brazil': 'float64',
        'Canada': 'float64'
    }

    df_inflation_rate['Date'] = pd.to_datetime(df_inflation_rate['Date'], format='%d/%m/%Y')
    df_inflation_rate['Date'] = df_inflation_rate['Date'].dt.strftime('%Y=%m-%d')
    df_inflation_rate = df_inflation_rate.astype(schema_dtypes)
    df_inflation_rate = df_inflation_rate[['Date', base_country, target_country]]

    return {
        'type': 'line_chart',
        'data': df_inflation_rate.to_dict(orient='records'),
        'x': 'Date',
        'y': [base_country, target_country],
        'title': 'Inflation Rate'
    }

@tool
def fetch_funds_rate(base_country: str, target_country: str):
    """
    Fetch BaseCountry and TargetCountry central bank interest rates
    e.g USA and UK central bank interest rates
    """

    df_funds_rate = pd.read_excel(r'E:\work\GenAIApp\data\economic_data_top10.xlsx', sheet_name='bank_fund_rates')

    schema_dtypes = {
        'USA': 'float64',
        'China': 'float64',
        'Japan': 'float64',
        'Germany': 'float64',
        'India': 'float64',
        'UK': 'float64',
        'France': 'float64',
        'Italy': 'float64',
        'Brazil': 'float64',
        'Canada': 'float64'
    }

    df_funds_rate['Date'] = pd.to_datetime(df_funds_rate['Date'], format='%d/%m/%Y')
    df_funds_rate['Date'] = df_funds_rate['Date'].dt.strftime('%Y=%m-%d')
    df_funds_rate = df_funds_rate.astype(schema_dtypes)
    df_funds_rate = df_funds_rate[['Date', base_country, target_country]]

    return {
        'type': 'line_chart',
        'data': df_funds_rate.to_dict(orient='records'),
        'x': 'Date',
        'y': [base_country, target_country],
        'title': 'Funds Rate'
    }