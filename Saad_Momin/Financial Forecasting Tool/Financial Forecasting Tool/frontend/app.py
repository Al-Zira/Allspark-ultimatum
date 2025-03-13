import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime
import json

# Constants
API_BASE_URL = "http://localhost:8000"  # FastAPI backend URL

def load_financial_data(symbol: str, period: str = "2y"):
    response = requests.get(f"{API_BASE_URL}/financial-data/{symbol}", params={"period": period})
    if response.status_code == 200:
        data = response.json()
        # Convert ISO format dates back to datetime
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        return df
    else:
        st.error(f"Error loading data: {response.text}")
        return None

def get_risk_metrics(symbol: str, period: str = "2y"):
    response = requests.get(f"{API_BASE_URL}/risk-metrics/{symbol}", params={"period": period})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error getting risk metrics: {response.text}")
        return None

def get_ml_prediction(symbol: str, period: str = "2y"):
    response = requests.get(f"{API_BASE_URL}/ml-prediction/{symbol}", params={"period": period})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error getting ML prediction: {response.text}")
        return None

def get_ai_prediction(symbol: str, context: str, asset_type: str, period: str = "2y"):
    response = requests.get(
        f"{API_BASE_URL}/ai-prediction/{symbol}",
        params={"period": period, "context": context, "asset_type": asset_type}
    )
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error getting AI prediction: {response.text}")
        return None

def plot_financial_data(df, title):
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='OHLC'
    ))
    fig.update_layout(
        title=title,
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark'
    )
    return fig

def plot_risk_metrics(chart_data):
    if not chart_data:
        return None
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=chart_data['labels'],
        y=chart_data['values'],
        text=[f"{v:.2f}" for v in chart_data['values']],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=chart_data['title'],
        xaxis_title=chart_data['x_label'],
        yaxis_title=chart_data['y_label'],
        template='plotly_dark',
        showlegend=False
    )
    return fig

def plot_ml_prediction(chart_data):
    if not chart_data:
        return None
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=chart_data['data']['forecast'],
        mode='lines',
        name='Forecast',
        line=dict(color='cyan')
    ))
    fig.update_layout(
        title=chart_data['title'],
        xaxis_title=chart_data['x_label'],
        yaxis_title=chart_data['y_label'],
        template='plotly_dark'
    )
    return fig

def plot_price_forecast(chart_data):
    if not chart_data:
        return None
        
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=chart_data['labels'],
        y=chart_data['data']['forecast'],
        text=[f"{v:.1f}%" for v in chart_data['data']['forecast']],
        textposition='auto',
    ))
    
    fig.update_layout(
        title=chart_data['title'],
        xaxis_title=chart_data['x_label'],
        yaxis_title=chart_data['y_label'],
        template='plotly_dark',
        showlegend=False
    )
    return fig

def main():
    st.set_page_config(page_title="Financial Forecast", layout="wide")
    st.title("Financial Forecast Dashboard")
    
    # Sidebar inputs
    st.sidebar.header("Settings")
    symbol = st.sidebar.text_input("Enter Stock Symbol", value="AAPL").upper()
    period = st.sidebar.selectbox("Select Time Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    asset_type = st.sidebar.selectbox("Asset Type", ["Stock", "Cryptocurrency", "ETF", "Index"])
    
    if st.sidebar.button("Analyze"):
        with st.spinner('Loading data...'):
            # Load financial data
            df = load_financial_data(symbol, period)
            if df is not None:
                # Display stock chart
                st.subheader(f"{symbol} Price Chart")
                st.plotly_chart(plot_financial_data(df, f"{symbol} Stock Price"), use_container_width=True)
                
                # Get and display risk metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Risk Analysis")
                    risk_data = get_risk_metrics(symbol, period)
                    if risk_data:
                        st.plotly_chart(plot_risk_metrics(risk_data['chart_data']), use_container_width=True)
                
                # Get and display ML prediction
                with col2:
                    st.subheader("ML Prediction")
                    ml_data = get_ml_prediction(symbol, period)
                    if ml_data:
                        st.plotly_chart(plot_ml_prediction(ml_data['chart_data']), use_container_width=True)
                        st.write("Feature Importance:")
                        st.json(ml_data['prediction']['feature_importance'])
                
                # Get and display AI prediction
                st.subheader("AI Analysis")
                context = f"Analyze {symbol} stock performance over the past {period}"
                ai_data = get_ai_prediction(symbol, context, asset_type, period)
                if ai_data:
                    prediction = ai_data['prediction']
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("Trend")
                        st.info(prediction['trend'])
                    
                    with col2:
                        st.write("Risks")
                        for risk in prediction['risks']:
                            st.warning(risk)
                    
                    with col3:
                        st.write("Opportunities")
                        for opp in prediction['opportunities']:
                            st.success(opp)
                    
                    st.write("Price Forecast")
                    st.plotly_chart(plot_price_forecast(ai_data['chart_data']), use_container_width=True)

if __name__ == "__main__":
    main() 