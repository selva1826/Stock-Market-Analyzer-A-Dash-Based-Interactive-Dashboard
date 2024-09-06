import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import yfinance as yf
import pandas as pd
from datetime import datetime

app = dash.Dash(__name__)

app.layout = html.Div(
    style={'background-image': 'url(https://cdn.pixabay.com/photo/2024/01/06/02/44/ai-generated-8490532_640.png)',
           'background-size': 'cover',
           'background-position': 'center',
           'height': '100vh',
           'width': '100vw',
           'background-repeat': 'no-repeat',  # Add this line
           'background-attachment': 'fixed'},  # Add this line
    children=[
        html.H1('Stock Market Analysis', style={'color': 'white','font-family': 'Roboto','font-size': '42px','font-weight': 'bold'}),
        
        # For stock ticker input
        html.H3('Enter Stock Ticker Name:', style={'color': 'white','font-family': 'Roboto','font-size': '28px','font-weight': 'bold'}),
        dcc.Input(id='stock-input', value='', type='text'),
        
        # Stock screener (for simplicity, filter stocks by price range)
        html.H3('Enter Price Range for Stock Screener:', style={'color': 'White','font-family':'Roboto','font-size':'28px','font-family': 'Roboto','font-size': '30px','font-weight': 'bold'}),
        dcc.Input(id='price-min', value='0', type='number', placeholder="Min Price"),
        dcc.Input(id='price-max', value='1000', type='number', placeholder="Max Price"),
        html.Button('Apply Filter', id='filter-button', n_clicks=0),
        
        html.Div(id='filtered-stocks', style={'color': 'white'}),
        
        # Graph for stock candlestick chart
        dcc.Graph(id='stock-graph'),
        
        # Display prices
        html.Div(id='stock-prices', style={'color': 'white'}),
        
        # Time slider for period selection
        dcc.Slider(
            id='time-slider',
            min=1,
            max=365,
            value=30,
            marks={i: str(i) for i in range(1, 366, 30)}
        ),
        
        # Display current stock price and time
        html.Div(id='current-stock-info', style={'position': 'absolute', 'top': '0', 'right': '0', 'padding': '10px', 'background-color': 'lightgray', 'text-align': 'right',})
    ]
)

@app.callback(
    [Output('stock-graph', 'figure'),
     Output('stock-prices', 'children'),
     Output('current-stock-info', 'children')],
    [Input('stock-input', 'value'),
     Input('time-slider', 'value')]
)
    
def update_graph(selected_stock, time_period):
    supported_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    period_map = {1: '1d', 5: '5d', 30: '1mo', 60: '3mo', 120: '6mo', 365: '1y'}
    period = period_map.get(time_period, '1y')  # default to 1y if not found
    
    if not selected_stock:
        return {}, '', ''
    
    try:
        # Download stock data
        stock_data = yf.download(selected_stock, period=period)

        # Get the current stock price
        ticker = yf.Ticker(selected_stock)
        current_price = ticker.history(period='1d')['Close'][0]
        
        # Create candlestick figure
        fig = go.Figure(data=[go.Candlestick(x=stock_data.index,
                                             open=stock_data['Open'],
                                             high=stock_data['High'],
                                             low=stock_data['Low'],
                                             close=stock_data['Close'])])
        
        fig.update_layout(title=f'{selected_stock} Stock Price',
                          yaxis_title='Price (USD)',
                          xaxis_title='Date',
                          plot_bgcolor='rgba(255, 255, 255, 0.5)',  # Change graph background color
                          paper_bgcolor='rgba(255, 255, 255, 0.5)'
                          )
        
        # Calculate and format prices
        open_price = stock_data['Open'].iloc[-1]
        close_price = stock_data['Close'].iloc[-1]
        high_price = stock_data['High'].max()
        low_price = stock_data['Low'].min()
        
        prices_html = [
    html.Div(style={'display': 'flex', 'margin-bottom': '10px'}, children=[
        html.Span(style={'margin-right': '20px'}, children=[
            html.P(f'Open: ${open_price:.2f}', style={'color': 'white','font-family': 'Roboto','font-size': '25px','font-weight': 'bold'}),
        ]),
        html.Span(children=[
            html.P(f'Close: ${close_price:.2f}', style={'color': 'white','font-family': 'Roboto','font-size': '25px','font-weight': 'bold'}),
        ]),
    ]),
    html.Div(style={'display': 'flex'}, children=[
        html.Span(style={'margin-right': '20px'}, children=[
            html.P(f'Low: ${low_price:.2f}', style={'color': 'white','font-family': 'Roboto','font-size': '25px','font-weight': 'bold'}),
        ]),
        html.Span(children=[
            html.P(f'High: ${high_price:.2f}', style={'color': 'white','font-family': 'Roboto','font-size': '25px','font-weight': 'bold'}),
        ]),
    ]),
]
        
        # Get current stock price and time
        ticker = yf.Ticker(selected_stock)
        current_price = ticker.history(period='1d')['Close'][0]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        current_stock_info = [
            html.P(f'Current Price: {current_price:.2f}', style={'font-size': '20px'}),
                        html.P(f'Time: {current_time}', style={'font-size': '14px'})
        ]
        
        return fig, prices_html, current_stock_info
    except Exception as e:
        print(f"Error updating graph: {e}")
        return {
            'data': [],
            'layout': {
                'title': 'No data found',
                'xaxis': {'title': ''},
                'yaxis': {'title': ''}
            }
        }, [html.P('No data found')], ''

@app.callback(
    Output('filtered-stocks', 'children'),
    [Input('filter-button', 'n_clicks')],
    [Input('price-min', 'value'),
     Input('price-max', 'value')]
)
def stock_screener(n_clicks, price_min, price_max):
    if n_clicks > 0:
        # Example stock symbols for filtering (in real-world, we would pull a larger set)
        stock_list = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']
        screened_stocks = []
        
        for stock in stock_list:
            stock_data = yf.Ticker(stock).history(period='1d')
            close_price = stock_data['Close'][0]
            
            if price_min <= close_price <= price_max:
                screened_stocks.append(f'{stock}: {close_price:.2f}')
        
        if screened_stocks:
            return html.Div([html.P(stock) for stock in screened_stocks])
        else:
            return html.P("No stocks found in the given range.")
    
    return ''

if __name__ == '__main__':
    app.run_server()
