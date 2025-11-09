// Get backend URL from environment or default to localhost
const BACKEND_URL = window.BACKEND_URL || 'http://localhost:5001';

let stockChart = null;

// Helper function to make API requests
async function fetchFromBackend(endpoint) {
    try {
        const response = await fetch(`${BACKEND_URL}${endpoint}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        return { success: true, data };
    } catch (error) {
        return { success: false, error: error.message };
    }
}

// Helper function to display data in a pretty format
function displayData(elementId, data, isError = false) {
    const element = document.getElementById(elementId);
    element.innerHTML = '';
    
    if (isError) {
        element.className = 'display-box error';
        element.innerHTML = `<pre>❌ Error: ${data}</pre>`;
    } else {
        element.className = 'display-box success';
        element.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }
}

// Load available stocks
async function loadStocks() {
    const result = await fetchFromBackend('/api/stocks');
    const select = document.getElementById('stock-select');
    
    if (result.success) {
        select.innerHTML = '<option value="">-- Select a stock --</option>';
        result.data.stocks.forEach(stock => {
            const option = document.createElement('option');
            option.value = stock.symbol;
            option.textContent = `${stock.symbol} - ${stock.name}`;
            select.appendChild(option);
        });
    } else {
        select.innerHTML = '<option value="">Error loading stocks</option>';
    }
}

// Load and display stock chart
async function loadStockChart(symbol) {
    const button = document.getElementById('load-stock-btn');
    button.disabled = true;
    button.classList.add('loading');
    const originalText = button.textContent;
    button.textContent = 'Loading...';
    
    const result = await fetchFromBackend(`/api/stock/${symbol}`);
    
    if (result.success) {
        const data = result.data;
        
        // Update stock info
        document.getElementById('stock-info').style.display = 'block';
        document.getElementById('current-price').textContent = `$${data.current_price.toFixed(2)}`;
        
        const changeElement = document.getElementById('price-change');
        const changeText = `${data.price_change >= 0 ? '+' : ''}$${data.price_change.toFixed(2)} (${data.price_change_percent.toFixed(2)}%)`;
        changeElement.textContent = changeText;
        changeElement.className = `info-value ${data.price_change >= 0 ? 'price-positive' : 'price-negative'}`;
        
        document.getElementById('high-price').textContent = `$${data.high_price.toFixed(2)}`;
        document.getElementById('low-price').textContent = `$${data.low_price.toFixed(2)}`;
        
        // Create or update chart
        const ctx = document.getElementById('stockChart').getContext('2d');
        
        if (stockChart) {
            stockChart.destroy();
        }
        
        stockChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timestamps,
                datasets: [{
                    label: `${data.symbol} - ${data.name}`,
                    data: data.prices,
                    borderColor: data.price_change >= 0 ? '#4ade80' : '#f87171',
                    backgroundColor: data.price_change >= 0 ? 'rgba(74, 222, 128, 0.1)' : 'rgba(248, 113, 113, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return `Price: $${context.parsed.y.toFixed(2)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        ticks: {
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    },
                    x: {
                        ticks: {
                            maxTicksLimit: 10
                        }
                    }
                }
            }
        });
    } else {
        alert(`Error loading stock data: ${result.error}`);
        document.getElementById('stock-info').style.display = 'none';
    }
    
    button.disabled = false;
    button.classList.remove('loading');
    button.textContent = originalText;
}

// Stock chart button
document.getElementById('load-stock-btn').addEventListener('click', async function() {
    const symbol = document.getElementById('stock-select').value;
    if (!symbol) {
        alert('Please select a stock first!');
        return;
    }
    await loadStockChart(symbol);
});

// Fetch message from backend
document.getElementById('fetch-message-btn').addEventListener('click', async function() {
    const button = this;
    button.disabled = true;
    button.textContent = 'Loading...';
    
    const result = await fetchFromBackend('/api/message');
    
    if (result.success) {
        displayData('message-display', result.data);
    } else {
        displayData('message-display', result.error, true);
    }
    
    button.disabled = false;
    button.textContent = 'Fetch Message';
});

// Health check
document.getElementById('health-check-btn').addEventListener('click', async function() {
    const button = this;
    button.disabled = true;
    button.textContent = 'Checking...';
    
    const result = await fetchFromBackend('/api/health');
    
    if (result.success) {
        displayData('health-display', result.data);
    } else {
        displayData('health-display', result.error, true);
    }
    
    button.disabled = false;
    button.textContent = 'Check Health';
});

// Load stocks on page load
window.addEventListener('DOMContentLoaded', () => {
    console.log('Frontend loaded. Backend URL:', BACKEND_URL);
    loadStocks();
});


