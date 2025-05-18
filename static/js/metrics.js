/**
 * Neuronas Cognitive Metrics Visualization
 * Provides detailed visualization of all cognitive metrics and memory structures
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all charts
    initPerformanceChart();
    initProcessingTimeChart();
    initD2ModulationChart();
    initMemoryCharts();
    initActivityHeatmap();
    
    // Update metrics display
    updateMetricsDisplay();
    
    // Set up time filtering
    setupTimeFilters();
    
    // Set up periodic refresh
    setInterval(updateMetricsDisplay, 30000); // 30 seconds
});

// Chart objects
let performanceChart, processingTimeChart, d2ModulationChart;
let leftMemoryChart, rightMemoryChart, activityHeatmap;

// Current time filter
let currentTimePeriod = 'hour';

/**
 * Initialize the cognitive performance chart
 */
function initPerformanceChart() {
    const ctx = document.getElementById('performance-chart');
    
    performanceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Focus',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Attention',
                    data: [],
                    borderColor: '#f39c12',
                    backgroundColor: 'rgba(243, 156, 18, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Working Memory',
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'D2 Activation',
                    data: [],
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    min: 0,
                    max: 2,
                    title: {
                        display: true,
                        text: 'Value'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Cognitive Performance Metrics'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    });
}

/**
 * Initialize the processing time chart
 */
function initProcessingTimeChart() {
    const ctx = document.getElementById('processing-time-chart');
    
    processingTimeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Processing Time (s)',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Query'
                    }
                },
                y: {
                    min: 0,
                    title: {
                        display: true,
                        text: 'Time (seconds)'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Query Processing Time'
                }
            }
        }
    });
}

/**
 * Initialize the D2 modulation chart
 */
function initD2ModulationChart() {
    const ctx = document.getElementById('d2-modulation-chart');
    
    d2ModulationChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'D2 Activation',
                data: [],
                borderColor: '#9b59b6',
                backgroundColor: 'rgba(155, 89, 182, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    min: 0,
                    max: 1,
                    title: {
                        display: true,
                        text: 'Activation Level'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'D2 Dopaminergic Modulation'
                }
            }
        }
    });
}

/**
 * Initialize memory charts for both hemispheres
 */
function initMemoryCharts() {
    const leftCtx = document.getElementById('left-memory-chart');
    const rightCtx = document.getElementById('right-memory-chart');
    
    // Left hemisphere memory chart
    leftMemoryChart = new Chart(leftCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'L1',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.7)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'L2',
                    data: [],
                    borderColor: '#2980b9',
                    backgroundColor: 'rgba(41, 128, 185, 0.5)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'L3',
                    data: [],
                    borderColor: '#1f618d',
                    backgroundColor: 'rgba(31, 97, 141, 0.3)',
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Memory Entries'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Left Hemisphere Memory'
                }
            }
        }
    });
    
    // Right hemisphere memory chart
    rightMemoryChart = new Chart(rightCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'R1',
                    data: [],
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.7)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'R2',
                    data: [],
                    borderColor: '#8e44ad',
                    backgroundColor: 'rgba(142, 68, 173, 0.5)',
                    borderWidth: 2,
                    fill: true
                },
                {
                    label: 'R3',
                    data: [],
                    borderColor: '#6c3483',
                    backgroundColor: 'rgba(108, 52, 131, 0.3)',
                    borderWidth: 2,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Memory Entries'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Right Hemisphere Memory'
                }
            }
        }
    });
}

/**
 * Initialize activity heatmap
 */
function initActivityHeatmap() {
    const container = document.getElementById('activity-heatmap');
    
    // Set up D3.js heatmap
    const margin = { top: 50, right: 50, bottom: 70, left: 80 };
    const width = container.offsetWidth - margin.left - margin.right;
    const height = container.offsetHeight - margin.top - margin.bottom;
    
    // Create SVG element
    const svg = d3.select(container)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);
    
    // Create initial empty heatmap
    createHeatmap(svg, width, height, []);
}

/**
 * Create or update heatmap with provided data
 */
function createHeatmap(svg, width, height, data) {
    // If no data, use empty dataset with structure
    if (!data || data.length === 0) {
        // Create placeholder data
        const hours = Array.from({length: 24}, (_, i) => i);
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        
        data = [];
        days.forEach(day => {
            hours.forEach(hour => {
                data.push({
                    day: day,
                    hour: hour,
                    value: 0
                });
            });
        });
    }
    
    // Get unique days and hours
    const days = [...new Set(data.map(d => d.day))];
    const hours = [...new Set(data.map(d => d.hour))];
    
    // Create scales
    const xScale = d3.scaleBand()
        .domain(hours)
        .range([0, width])
        .padding(0.05);
    
    const yScale = d3.scaleBand()
        .domain(days)
        .range([0, height])
        .padding(0.05);
    
    // Color scale
    const colorScale = d3.scaleSequential()
        .interpolator(d3.interpolateInferno)
        .domain([0, d3.max(data, d => d.value) || 1]);
    
    // Clear previous content
    svg.selectAll("*").remove();
    
    // Add X axis
    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(xScale)
            .tickFormat(h => `${h}:00`))
        .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");
    
    // Add X axis label
    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", height + 60)
        .text("Hour of Day")
        .attr("fill", "white");
    
    // Add Y axis
    svg.append("g")
        .call(d3.axisLeft(yScale));
    
    // Add Y axis label
    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("transform", "rotate(-90)")
        .attr("y", -60)
        .attr("x", -height / 2)
        .text("Day of Week")
        .attr("fill", "white");
    
    // Create tooltip
    const tooltip = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0)
        .style("position", "absolute")
        .style("background-color", "rgba(0, 0, 0, 0.8)")
        .style("color", "white")
        .style("padding", "10px")
        .style("border-radius", "5px")
        .style("pointer-events", "none");
    
    // Create heatmap cells
    svg.selectAll("rect")
        .data(data)
        .enter()
        .append("rect")
        .attr("x", d => xScale(d.hour))
        .attr("y", d => yScale(d.day))
        .attr("width", xScale.bandwidth())
        .attr("height", yScale.bandwidth())
        .style("fill", d => d.value === 0 ? "#1e1e2f" : colorScale(d.value))
        .style("stroke", "#1e1e2f")
        .style("stroke-width", 1)
        .on("mouseover", function(event, d) {
            d3.select(this)
                .style("stroke", "white")
                .style("stroke-width", 2);
            
            tooltip.transition()
                .duration(200)
                .style("opacity", .9);
            
            tooltip.html(`Day: ${d.day}<br>Hour: ${d.hour}:00<br>Value: ${d.value}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this)
                .style("stroke", "#1e1e2f")
                .style("stroke-width", 1);
            
            tooltip.transition()
                .duration(500)
                .style("opacity", 0);
        });
    
    // Add title
    svg.append("text")
        .attr("x", width / 2)
        .attr("y", -20)
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .style("fill", "white")
        .text("Cognitive Activity Heatmap");
    
    // Add legend
    const legendWidth = 20;
    const legendHeight = height / 2;
    
    const legendScale = d3.scaleSequential()
        .interpolator(d3.interpolateInferno)
        .domain([0, 1]);
    
    const legendAxisScale = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.value) || 1])
        .range([legendHeight, 0]);
    
    const legend = svg.append("g")
        .attr("transform", `translate(${width + 20}, ${height/4})`);
    
    // Create gradient for legend
    const defs = svg.append("defs");
    const gradient = defs.append("linearGradient")
        .attr("id", "legend-gradient")
        .attr("x1", "0%")
        .attr("y1", "100%")
        .attr("x2", "0%")
        .attr("y2", "0%");
    
    // Add gradient stops
    const stops = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0];
    stops.forEach(stop => {
        gradient.append("stop")
            .attr("offset", `${stop * 100}%`)
            .attr("stop-color", legendScale(stop));
    });
    
    // Draw legend rectangle
    legend.append("rect")
        .attr("width", legendWidth)
        .attr("height", legendHeight)
        .style("fill", "url(#legend-gradient)");
    
    // Add legend axis
    legend.append("g")
        .attr("transform", `translate(${legendWidth}, 0)`)
        .call(d3.axisRight(legendAxisScale)
            .ticks(5));
    
    // Add legend label
    legend.append("text")
        .attr("x", legendWidth / 2)
        .attr("y", -10)
        .attr("text-anchor", "middle")
        .style("fill", "white")
        .text("Activity");
}

/**
 * Set up time filter buttons
 */
function setupTimeFilters() {
    document.querySelectorAll('.time-filter-btn').forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            document.querySelectorAll('.time-filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Update time period and refresh data
            currentTimePeriod = this.getAttribute('data-period');
            updateMetricsDisplay();
        });
    });
}

/**
 * Update all metrics displays
 */
function updateMetricsDisplay() {
    // Fetch metrics data
    fetch('/api/metrics')
        .then(response => response.json())
        .then(data => {
            updateCognitiveMetricsDisplay(data.metrics);
            updatePerformanceChart(data.metrics);
            updateProcessingTimeChart(data.metrics);
            updateD2ModulationChart(data.metrics);
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
        });
    
    // Fetch system status for memory stats
    fetch('/api/system/status')
        .then(response => response.json())
        .then(data => {
            updateMemoryStats(data.memory_stats);
            updateMemoryCharts(data.memory_stats);
            updateActivityHeatmap();
        })
        .catch(error => {
            console.error('Error fetching system status:', error);
        });
}

/**
 * Update the cognitive metrics summary display
 */
function updateCognitiveMetricsDisplay(metrics) {
    // Find the latest metrics
    let focusValue = 1.0;
    let attentionValue = 0.5;
    let memoryValue = 0.5;
    let d2Value = 0.5;
    
    // Extract latest metrics values
    if (metrics && metrics.length > 0) {
        // Process metrics to find the latest values
        const latestMetrics = metrics.reduce((acc, metric) => {
            if (!acc[metric.metric_name] || new Date(metric.timestamp) > new Date(acc[metric.metric_name].timestamp)) {
                acc[metric.metric_name] = metric;
            }
            return acc;
        }, {});
        
        // Update with latest values if available
        if (latestMetrics.focus) {
            focusValue = latestMetrics.focus.value;
        }
        
        if (latestMetrics.attention) {
            attentionValue = latestMetrics.attention.value;
        }
        
        if (latestMetrics.working_memory) {
            memoryValue = latestMetrics.working_memory.value;
        }
        
        if (latestMetrics.d2_activation) {
            d2Value = latestMetrics.d2_activation.value;
        }
    }
    
    // Update the display
    document.getElementById('focus-metric').textContent = focusValue.toFixed(2);
    document.getElementById('attention-metric').textContent = attentionValue.toFixed(2);
    document.getElementById('memory-metric').textContent = memoryValue.toFixed(2);
    document.getElementById('d2-metric').textContent = d2Value.toFixed(2);
}

/**
 * Update the performance chart with latest metrics
 */
function updatePerformanceChart(metrics) {
    // Filter metrics by time period
    const filteredMetrics = filterMetricsByTimePeriod(metrics, currentTimePeriod);
    
    // Extract time series data
    const timeLabels = [];
    const focusData = [];
    const attentionData = [];
    const memoryData = [];
    const d2Data = [];
    
    // Get all unique timestamps and sort them
    const timestamps = [...new Set(filteredMetrics.map(metric => metric.timestamp))];
    timestamps.sort((a, b) => new Date(a) - new Date(b));
    
    // For each timestamp, find the relevant metrics
    timestamps.forEach(timestamp => {
        const time = new Date(timestamp);
        timeLabels.push(formatTime(time));
        
        // Find metrics for this timestamp
        const metricsAtTime = filteredMetrics.filter(m => m.timestamp === timestamp);
        
        // Extract values or use defaults
        const focus = metricsAtTime.find(m => m.metric_name === 'focus');
        focusData.push(focus ? focus.value : null);
        
        const attention = metricsAtTime.find(m => m.metric_name === 'attention');
        attentionData.push(attention ? attention.value : null);
        
        const memory = metricsAtTime.find(m => m.metric_name === 'working_memory');
        memoryData.push(memory ? memory.value : null);
        
        const d2 = metricsAtTime.find(m => m.metric_name === 'd2_activation');
        d2Data.push(d2 ? d2.value : null);
    });
    
    // Update chart data
    performanceChart.data.labels = timeLabels;
    performanceChart.data.datasets[0].data = focusData;
    performanceChart.data.datasets[1].data = attentionData;
    performanceChart.data.datasets[2].data = memoryData;
    performanceChart.data.datasets[3].data = d2Data;
    
    // Update chart
    performanceChart.update();
}

/**
 * Update the processing time chart
 */
function updateProcessingTimeChart(metrics) {
    // Filter to processing_time metrics only
    const processingTimes = metrics.filter(m => m.metric_name === 'processing_time');
    
    // Filter by time period
    const filteredTimes = filterMetricsByTimePeriod(processingTimes, currentTimePeriod);
    
    // Sort by timestamp
    filteredTimes.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Extract data
    const labels = [];
    const times = [];
    
    filteredTimes.forEach((metric, index) => {
        labels.push(`Q${index + 1}`);
        times.push(metric.value);
    });
    
    // Update chart data
    processingTimeChart.data.labels = labels;
    processingTimeChart.data.datasets[0].data = times;
    
    // Update chart
    processingTimeChart.update();
}

/**
 * Update the D2 modulation chart
 */
function updateD2ModulationChart(metrics) {
    // Filter to d2_activation metrics only
    const d2Metrics = metrics.filter(m => m.metric_name === 'd2_activation');
    
    // Filter by time period
    const filteredD2 = filterMetricsByTimePeriod(d2Metrics, currentTimePeriod);
    
    // Sort by timestamp
    filteredD2.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    // Extract data
    const labels = [];
    const values = [];
    
    filteredD2.forEach(metric => {
        labels.push(formatTime(new Date(metric.timestamp)));
        values.push(metric.value);
    });
    
    // Update chart data
    d2ModulationChart.data.labels = labels;
    d2ModulationChart.data.datasets[0].data = values;
    
    // Update chart
    d2ModulationChart.update();
}

/**
 * Update memory stats display
 */
function updateMemoryStats(memoryStats) {
    // Update memory tier counters
    document.getElementById('l1-count').textContent = memoryStats.L1;
    document.getElementById('l2-count').textContent = memoryStats.L2;
    document.getElementById('l3-count').textContent = memoryStats.L3;
    document.getElementById('r1-count').textContent = memoryStats.R1;
    document.getElementById('r2-count').textContent = memoryStats.R2;
    document.getElementById('r3-count').textContent = memoryStats.R3;
}

/**
 * Update memory charts
 */
function updateMemoryCharts(memoryStats) {
    // Simulate time series data for memory
    // In a real implementation, this would come from an API endpoint that returns historical data
    const timeLabels = generateTimeLabels(12);
    
    // Generate sample memory data
    // This would be replaced with actual historical data from an API
    const l1Data = generateMemorySeries(12, memoryStats.L1);
    const l2Data = generateMemorySeries(12, memoryStats.L2);
    const l3Data = generateMemorySeries(12, memoryStats.L3);
    
    const r1Data = generateMemorySeries(12, memoryStats.R1);
    const r2Data = generateMemorySeries(12, memoryStats.R2);
    const r3Data = generateMemorySeries(12, memoryStats.R3);
    
    // Update left hemisphere chart
    leftMemoryChart.data.labels = timeLabels;
    leftMemoryChart.data.datasets[0].data = l1Data;
    leftMemoryChart.data.datasets[1].data = l2Data;
    leftMemoryChart.data.datasets[2].data = l3Data;
    leftMemoryChart.update();
    
    // Update right hemisphere chart
    rightMemoryChart.data.labels = timeLabels;
    rightMemoryChart.data.datasets[0].data = r1Data;
    rightMemoryChart.data.datasets[1].data = r2Data;
    rightMemoryChart.data.datasets[2].data = r3Data;
    rightMemoryChart.update();
}

/**
 * Update activity heatmap
 */
function updateActivityHeatmap() {
    // In a real implementation, this would fetch data from an API endpoint
    // For now, generate sample data
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const hours = Array.from({length: 24}, (_, i) => i);
    
    const data = [];
    days.forEach(day => {
        hours.forEach(hour => {
            // Generate random activity level, with higher activity during work hours
            let value = 0;
            if (hour >= 8 && hour <= 18) {
                // Higher activity during work hours
                value = Math.random() * 0.8 + 0.2;
            } else {
                // Lower activity outside work hours
                value = Math.random() * 0.3;
            }
            
            // Weekend adjustment
            if (day === 'Sat' || day === 'Sun') {
                value *= 0.6;
            }
            
            data.push({
                day: day,
                hour: hour,
                value: value
            });
        });
    });
    
    // Get the SVG element
    const svg = d3.select('#activity-heatmap svg g');
    const width = document.getElementById('activity-heatmap').offsetWidth - 130;
    const height = document.getElementById('activity-heatmap').offsetHeight - 120;
    
    // Update heatmap
    createHeatmap(svg, width, height, data);
}

/**
 * Filter metrics by time period
 */
function filterMetricsByTimePeriod(metrics, period) {
    const now = new Date();
    let cutoff;
    
    // Calculate cutoff time based on period
    switch (period) {
        case 'hour':
            cutoff = new Date(now - 60 * 60 * 1000); // 1 hour ago
            break;
        case 'day':
            cutoff = new Date(now - 24 * 60 * 60 * 1000); // 1 day ago
            break;
        case 'week':
            cutoff = new Date(now - 7 * 24 * 60 * 60 * 1000); // 1 week ago
            break;
        case 'all':
        default:
            return metrics;
    }
    
    // Filter metrics
    return metrics.filter(metric => new Date(metric.timestamp) >= cutoff);
}

/**
 * Generate memory time series data
 * This is a placeholder for actual historical data that would come from an API
 */
function generateMemorySeries(count, currentValue) {
    const series = [];
    const baseValue = Math.max(0, currentValue - Math.random() * 10);
    
    for (let i = 0; i < count; i++) {
        // Generate values that trend toward the current value
        const progress = i / (count - 1);
        const randomVariation = Math.random() * 5 - 2.5;
        const value = baseValue + (currentValue - baseValue) * progress + randomVariation;
        series.push(Math.max(0, Math.round(value)));
    }
    
    return series;
}

/**
 * Generate time labels
 */
function generateTimeLabels(count) {
    const labels = [];
    const now = new Date();
    
    for (let i = count - 1; i >= 0; i--) {
        const time = new Date(now - i * 5 * 60 * 1000); // 5-minute intervals
        labels.push(formatTime(time));
    }
    
    return labels;
}

/**
 * Format time as HH:MM
 */
function formatTime(date) {
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}
