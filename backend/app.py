from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import random
import math

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Popular stocks list with realistic base prices
AVAILABLE_STOCKS = {
    'AAPL': {'name': 'Apple Inc.', 'base_price': 178.50, 'volatility': 0.015},
    'GOOGL': {'name': 'Alphabet Inc.', 'base_price': 141.80, 'volatility': 0.018},
    'MSFT': {'name': 'Microsoft Corporation', 'base_price': 378.91, 'volatility': 0.014},
    'AMZN': {'name': 'Amazon.com Inc.', 'base_price': 148.28, 'volatility': 0.020},
    'TSLA': {'name': 'Tesla Inc.', 'base_price': 242.84, 'volatility': 0.030},
    'META': {'name': 'Meta Platforms Inc.', 'base_price': 486.36, 'volatility': 0.022},
    'NVDA': {'name': 'NVIDIA Corporation', 'base_price': 483.09, 'volatility': 0.025},
    'JPM': {'name': 'JPMorgan Chase & Co.', 'base_price': 188.75, 'volatility': 0.012},
    'V': {'name': 'Visa Inc.', 'base_price': 269.42, 'volatility': 0.011},
    'WMT': {'name': 'Walmart Inc.', 'base_price': 69.58, 'volatility': 0.009}
}

def generate_realistic_stock_data(symbol, base_price, volatility, num_points=78):
    """Generate realistic intraday stock data using random walk"""
    # Market hours: 9:30 AM - 4:00 PM = 390 minutes = 78 5-minute intervals
    market_open = datetime.now().replace(hour=9, minute=30, second=0, microsecond=0)
    
    timestamps = []
    prices = []
    volumes = []
    
    # Random opening gap
    open_gap = random.uniform(-0.01, 0.01)
    current_price = base_price * (1 + open_gap)
    
    # Trend for the day (-1 to 1)
    daily_trend = random.uniform(-0.015, 0.015)
    
    for i in range(num_points):
        # Generate timestamp
        timestamp = market_open + timedelta(minutes=i * 5)
        timestamps.append(timestamp.strftime('%H:%M'))
        
        # Generate price using geometric Brownian motion
        dt = 5 / (6.5 * 60)  # 5 minutes as fraction of trading day
        drift = daily_trend
        shock = random.gauss(0, volatility) * math.sqrt(dt)
        
        price_change = current_price * (drift * dt + shock)
        current_price += price_change
        
        # Add mean reversion to keep prices reasonable
        if current_price > base_price * 1.05:
            current_price -= (current_price - base_price * 1.05) * 0.1
        elif current_price < base_price * 0.95:
            current_price += (base_price * 0.95 - current_price) * 0.1
        
        prices.append(round(current_price, 2))
        
        # Generate volume (higher at open/close)
        time_factor = 1.0
        if i < 10 or i > num_points - 10:  # First/last 50 minutes
            time_factor = 1.5
        volumes.append(int(random.randint(100000, 500000) * time_factor))
    
    return timestamps, prices, volumes

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/message', methods=['GET'])
def get_message():
    """Main endpoint that returns a message"""
    return jsonify({
        'message': 'Hello from the backend! 🚀',
        'timestamp': datetime.now().isoformat(),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'note': 'Stock data is simulated for demonstration purposes'
    })

@app.route('/api/about', methods=['GET'])
def about():
    """About endpoint with application information"""
    return jsonify({
        'name': 'Stock Price Tracker',
        'version': '1.0.0',
        'description': 'A web application demonstrating frontend-backend communication',
        'backend': 'Python Flask',
        'frontend': 'HTML/CSS/JavaScript',
        'features': [
            'Real-time stock price visualization',
            'Interactive charts with Chart.js',
            'Dockerized microservices',
            'RESTful API design'
        ]
    })

@app.route('/api/stocks', methods=['GET'])
def get_stocks():
    """Get list of available stocks"""
    try:
        stocks = [
            {
                'symbol': k,
                'name': v['name'],
                'price': v['base_price']
            }
            for k, v in AVAILABLE_STOCKS.items()
        ]
        return jsonify({
            'stocks': stocks,
            'count': len(stocks)
        })
    except Exception as e:
        print(f"Error in /api/stocks: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """Get simulated stock price data"""
    try:
        symbol = symbol.upper()
        print(f"Generating stock data for {symbol}")
        
        if symbol not in AVAILABLE_STOCKS:
            return jsonify({'error': f'Stock symbol {symbol} not found'}), 404
        
        stock_info = AVAILABLE_STOCKS[symbol]
        
        # Generate realistic data
        timestamps, prices, volumes = generate_realistic_stock_data(
            symbol,
            stock_info['base_price'],
            stock_info['volatility']
        )
        
        # Calculate statistics
        open_price = prices[0]
        current_price = prices[-1]
        high_price = max(prices)
        low_price = min(prices)
        avg_volume = sum(volumes) // len(volumes)
        
        # Format response
        chart_data = {
            'symbol': symbol,
            'name': stock_info['name'],
            'timestamps': timestamps,
            'prices': prices,
            'volumes': volumes,
            'current_price': current_price,
            'open_price': open_price,
            'high_price': high_price,
            'low_price': low_price,
            'avg_volume': avg_volume,
            'total_volume': sum(volumes),
        }
        
        # Calculate changes
        chart_data['price_change'] = round(current_price - open_price, 2)
        chart_data['price_change_percent'] = round(
            (chart_data['price_change'] / open_price) * 100, 2
        )
        
        print(f"Generated data for {symbol}: ${current_price} ({chart_data['price_change_percent']:+.2f}%)")
        return jsonify(chart_data)
    
    except Exception as e:
        print(f"Error generating stock data for {symbol}: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
