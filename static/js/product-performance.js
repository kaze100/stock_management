// Product Performance Chart
function initProductPerformanceChart(chartData) {
    var ctx = document.getElementById('productPerformanceChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: chartData.revenueLabel,
                    data: chartData.revenueData,
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    order: 2
                },
                {
                    label: chartData.profitLabel,
                    data: chartData.profitData,
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1,
                    order: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: chartData.yAxisLabel
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' RWF';
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: chartData.xAxisLabel
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toLocaleString() + ' RWF';
                        }
                    }
                }
            }
        }
    });
}

// Product Quantity Chart
function initProductQuantityChart(chartData) {
    var ctx = document.getElementById('productQuantityChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [
                {
                    label: chartData.quantityLabel,
                    data: chartData.quantityData,
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',  // Horizontal bar chart for better readability
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: chartData.quantityAxisLabel
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: chartData.xAxisLabel
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.raw.toLocaleString() + ' ' + chartData.quantityUnit;
                        }
                    }
                }
            }
        }
    });
}

// Initialize all charts when document is ready
document.addEventListener('DOMContentLoaded', function() {
    try {
        console.log('Initializing product performance charts...');
        
        // Check if the elements exist
        if (!document.getElementById('productPerformanceChart') || 
            !document.getElementById('productQuantityChart')) {
            console.error('Chart canvas elements not found');
            return;
        }
        
        if (!document.getElementById('product-data')) {
            console.error('Product data element not found');
            return;
        }
        
        // Parse data from hidden element
        var dataElement = document.getElementById('product-data');
        var productData;
        
        try {
            productData = JSON.parse(dataElement.textContent);
            console.log('Parsed product data:', productData);
        } catch (e) {
            console.error('Error parsing product data JSON:', e);
            return;
        }
        
        // Check if we have data to display
        if (!productData.labels || productData.labels.length === 0) {
            console.warn('No product labels available for charts');
            return;
        }
        
        // Initialize charts
        initProductPerformanceChart(productData);
        initProductQuantityChart(productData);
        console.log('Charts initialized successfully');
        
    } catch (error) {
        console.error('Error initializing charts:', error);
    }
});
