/**
 * This work is licensed under CC BY-NC 4.0 International.
 * Commercial use requires prior written consent and compensation.
 * Contact: sebastienbrulotte@gmail.com
 * Attribution: Sebastien Brulotte aka [ Doditz ]
 *
 * This document is part of the NEURONAS cognitive system.
 * Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
 * All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
 */

/**
 * Neuronas Dashboard Visualization
 * Manages real-time cognitive metrics visualization and monitoring
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initHemisphereChart();
    initQueryDistribution();
    initMemoryChart();
    initNeuralPathways();
    initQueryLog();
    
    // Set up refresh button
    document.getElementById('refresh-dashboard').addEventListener('click', function() {
        updateAllCharts();
        updateQueryLog();
        updateSystemStats();
        showAlert('Dashboard refreshed', 'info');
    });
    
    // Set up filter buttons
    setupFilterButtons();
    
    // Initialize all data
    updateAllCharts();
    updateQueryLog();
    updateSystemStats();
    
    // Set up periodic refresh
    setInterval(function() {
        updateSystemStats();
    }, 5000);
    
    setInterval(function() {
        updateAllCharts();
        updateQueryLog();
    }, 30000);
});

// Chart objects
let hemisphereChart, queryDistChart, memoryChart, pathwaysChart;

/**
 * Initialize the hemispheric activity chart
 */
function initHemisphereChart() {
    const ctx = document.getElementById('hemisphere-chart');
    
    hemisphereChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: generateTimeLabels(12),
            datasets: [
                {
                    label: 'Left Hemisphere',
                    data: Array(12).fill(0.5),
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Right Hemisphere',
                    data: Array(12).fill(0.5),
                    borderColor: '#9b59b6',
                    backgroundColor: 'rgba(155, 89, 182, 0.2)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Central Integration',
                    data: Array(12).fill(0.3),
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.2)',
                    tension: 0.4,
                    fill: true,
                    borderDash: [5, 5]
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1.0,
                    title: {
                        display: true,
                        text: 'Activation Level'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Hemispheric Activation Levels'
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
 * Initialize the query distribution chart
 */
function initQueryDistribution() {
    const ctx = document.getElementById('query-distribution');
    
    queryDistChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Analytical', 'Creative', 'Factual'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#3498db', '#9b59b6', '#2ecc71'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Query Types'
                },
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Initialize the memory distribution chart
 */
function initMemoryChart() {
    const ctx = document.getElementById('memory-chart');
    
    memoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['L1', 'L2', 'L3', 'R1', 'R2', 'R3'],
            datasets: [{
                label: 'Memory Entries',
                data: [0, 0, 0, 0, 0, 0],
                backgroundColor: [
                    'rgba(52, 152, 219, 0.7)',
                    'rgba(52, 152, 219, 0.5)',
                    'rgba(52, 152, 219, 0.3)',
                    'rgba(155, 89, 182, 0.7)',
                    'rgba(155, 89, 182, 0.5)',
                    'rgba(155, 89, 182, 0.3)'
                ],
                borderColor: [
                    '#3498db',
                    '#3498db',
                    '#3498db',
                    '#9b59b6',
                    '#9b59b6',
                    '#9b59b6'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Memory Tier'
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Memory Distribution'
                }
            }
        }
    });
}

/**
 * Initialize the neural pathways visualization
 */
function initNeuralPathways() {
    const container = document.getElementById('neural-pathways');
    
    // Create SVG container using D3.js
    const width = container.offsetWidth;
    const height = container.offsetHeight;
    
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    // Add groups for different elements
    svg.append('g').attr('class', 'links');
    svg.append('g').attr('class', 'nodes');
    
    // Initialize with empty data - will be populated in updateNeuralPathways
    updateNeuralPathways();
}

/**
 * Initialize the query log display
 */
function initQueryLog() {
    const container = document.getElementById('query-log');
    container.innerHTML = '<p class="text-center text-muted">Loading query history...</p>';
    updateQueryLog();
}

/**
 * Update all charts with fresh data
 */
function updateAllCharts() {
    // Fetch system status for chart data
    fetch('/api/system/status')
        .then(response => response.json())
        .then(data => {
            updateHemisphereChart(data);
            updateMemoryChart(data.memory_stats);
            updateSystemStats(data);
        })
        .catch(error => {
            console.error('Error fetching system data:', error);
        });
    
    // Fetch metrics for query distribution
    fetch('/api/metrics')
        .then(response => response.json())
        .then(data => {
            updateQueryDistribution(data.metrics);
            updateNeuralPathways();
        })
        .catch(error => {
            console.error('Error fetching metrics:', error);
        });
}

/**
 * Update the hemispheric activity chart with new data
 */
function updateHemisphereChart(data) {
    // Add new data point and remove oldest
    const leftActivation = data.state.activation.left_hemisphere;
    const rightActivation = data.state.activation.right_hemisphere;
    const centralActivation = data.state.activation.central_integration;
    
    hemisphereChart.data.datasets[0].data.push(leftActivation);
    hemisphereChart.data.datasets[0].data.shift();
    
    hemisphereChart.data.datasets[1].data.push(rightActivation);
    hemisphereChart.data.datasets[1].data.shift();
    
    hemisphereChart.data.datasets[2].data.push(centralActivation);
    hemisphereChart.data.datasets[2].data.shift();
    
    // Update time labels
    hemisphereChart.data.labels.push(formatTime(new Date()));
    hemisphereChart.data.labels.shift();
    
    hemisphereChart.update();
}

/**
 * Update the query distribution chart
 */
function updateQueryDistribution(metrics) {
    // Count different query types
    let analytical = 0;
    let creative = 0;
    let factual = 0;
    
    metrics.forEach(metric => {
        if (metric.metric_name === 'analytical_query' && metric.value > 0) {
            analytical++;
        } else if (metric.metric_name === 'creative_query' && metric.value > 0) {
            creative++;
        } else if (metric.metric_name === 'factual_query' && metric.value > 0) {
            factual++;
        }
    });
    
    // Update chart data
    queryDistChart.data.datasets[0].data = [analytical, creative, factual];
    queryDistChart.update();
}

/**
 * Update the memory distribution chart
 */
function updateMemoryChart(memoryStats) {
    // Update chart data
    memoryChart.data.datasets[0].data = [
        memoryStats.L1,
        memoryStats.L2,
        memoryStats.L3,
        memoryStats.R1,
        memoryStats.R2,
        memoryStats.R3
    ];
    
    memoryChart.update();
}

/**
 * Update the neural pathways visualization
 */
function updateNeuralPathways() {
    const container = d3.select('#neural-pathways');
    const svg = container.select('svg');
    const width = container.node().offsetWidth;
    const height = container.node().offsetHeight;
    
    // Neural pathway data (nodes and connections)
    const nodes = [
        { id: 'input', name: 'Input', x: width * 0.1, y: height * 0.5, radius: 20, color: '#3498db' },
        { id: 'classify', name: 'Classify', x: width * 0.25, y: height * 0.5, radius: 15, color: '#3498db' },
        
        // Left hemisphere nodes
        { id: 'l1', name: 'L1', x: width * 0.4, y: height * 0.3, radius: 15, color: '#2980b9' },
        { id: 'l2', name: 'L2', x: width * 0.55, y: height * 0.3, radius: 15, color: '#2980b9' },
        { id: 'l3', name: 'L3', x: width * 0.7, y: height * 0.3, radius: 15, color: '#2980b9' },
        
        // Right hemisphere nodes
        { id: 'r1', name: 'R1', x: width * 0.4, y: height * 0.7, radius: 15, color: '#8e44ad' },
        { id: 'r2', name: 'R2', x: width * 0.55, y: height * 0.7, radius: 15, color: '#8e44ad' },
        { id: 'r3', name: 'R3', x: width * 0.7, y: height * 0.7, radius: 15, color: '#8e44ad' },
        
        // Integration node
        { id: 'integration', name: 'Integration', x: width * 0.85, y: height * 0.5, radius: 20, color: '#2ecc71' }
    ];
    
    const links = [
        { source: 'input', target: 'classify', value: 1, color: '#bdc3c7' },
        { source: 'classify', target: 'l1', value: 0.6, color: '#3498db' },
        { source: 'classify', target: 'r1', value: 0.6, color: '#9b59b6' },
        { source: 'l1', target: 'l2', value: 0.5, color: '#3498db' },
        { source: 'l2', target: 'l3', value: 0.4, color: '#3498db' },
        { source: 'r1', target: 'r2', value: 0.5, color: '#9b59b6' },
        { source: 'r2', target: 'r3', value: 0.4, color: '#9b59b6' },
        { source: 'l3', target: 'integration', value: 0.7, color: '#2ecc71' },
        { source: 'r3', target: 'integration', value: 0.7, color: '#2ecc71' }
    ];
    
    // Process links for D3
    const processedLinks = links.map(link => {
        const sourceNode = nodes.find(node => node.id === link.source);
        const targetNode = nodes.find(node => node.id === link.target);
        
        return {
            ...link,
            source: sourceNode,
            target: targetNode
        };
    });
    
    // Draw links
    const linkElements = svg.select('.links')
        .selectAll('line')
        .data(processedLinks);
    
    linkElements.enter()
        .append('line')
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y)
        .attr('stroke', d => d.color)
        .attr('stroke-width', d => d.value * 3)
        .merge(linkElements)
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);
    
    linkElements.exit().remove();
    
    // Draw nodes
    const nodeElements = svg.select('.nodes')
        .selectAll('g')
        .data(nodes);
    
    const nodeEnter = nodeElements.enter()
        .append('g');
    
    nodeEnter.append('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', d => d.radius)
        .attr('fill', d => d.color);
    
    nodeEnter.append('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .attr('dy', 4)
        .attr('text-anchor', 'middle')
        .attr('fill', 'white')
        .text(d => d.name);
    
    const nodeUpdate = nodeEnter.merge(nodeElements);
    
    nodeUpdate.select('circle')
        .attr('cx', d => d.x)
        .attr('cy', d => d.y)
        .attr('r', d => d.radius)
        .attr('fill', d => d.color);
    
    nodeUpdate.select('text')
        .attr('x', d => d.x)
        .attr('y', d => d.y)
        .text(d => d.name);
    
    nodeElements.exit().remove();
    
    // Simulate some activity by pulsing
    svg.selectAll('circle')
        .each(function(d) {
            const circle = d3.select(this);
            
            // Pulse effect
            function pulse() {
                circle.transition()
                    .duration(1000)
                    .attr('r', d.radius * 1.2)
                    .transition()
                    .duration(1000)
                    .attr('r', d.radius)
                    .on('end', pulse);
            }
            
            // Start pulsing on random delay
            setTimeout(pulse, Math.random() * 2000);
        });
}

/**
 * Update the query log display
 */
function updateQueryLog() {
    fetch('/api/query')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            displayQueryLog(data.queries || []);
        })
        .catch(error => {
            // For demo purposes, show sample queries since the endpoint may not exist
            console.warn('Could not fetch query log:', error);
            
            // Create empty log message
            const container = document.getElementById('query-log');
            container.innerHTML = '<p class="text-center text-muted">No queries recorded yet.</p>';
        });
}

/**
 * Display query log entries
 */
function displayQueryLog(queries) {
    const container = document.getElementById('query-log');
    
    if (!queries || queries.length === 0) {
        container.innerHTML = '<p class="text-center text-muted">No queries recorded yet.</p>';
        return;
    }
    
    // Clear container
    container.innerHTML = '';
    
    // Add each query
    queries.forEach(query => {
        const queryItem = document.createElement('div');
        queryItem.className = `query-item ${query.query_type || 'unknown'}`;
        queryItem.setAttribute('data-type', query.query_type || 'unknown');
        
        const timestamp = new Date(query.created_at);
        const formattedTime = formatTime(timestamp);
        
        // Create elements instead of using innerHTML to prevent XSS
        const itemContainer = document.createElement('div');
        itemContainer.className = 'd-flex justify-content-between';
        
        const queryTextSpan = document.createElement('span');
        queryTextSpan.className = 'query-text';
        queryTextSpan.textContent = query.query; // Using textContent for safe insertion
        
        const timeSpan = document.createElement('span');
        timeSpan.className = 'badge bg-secondary';
        timeSpan.textContent = formattedTime;
        
        itemContainer.appendChild(queryTextSpan);
        itemContainer.appendChild(timeSpan);
        
        const metadataDiv = document.createElement('div');
        metadataDiv.className = 'small text-muted mt-1';
        
        // Type span with badge
        const typeSpanOuter = document.createElement('span');
        typeSpanOuter.textContent = 'Type: ';
        
        const typeSpanInner = document.createElement('span');
        typeSpanInner.className = 'badge bg-info';
        typeSpanInner.textContent = query.query_type || 'unknown';
        
        typeSpanOuter.appendChild(typeSpanInner);
        
        // Separator spans
        const separator1 = document.createElement('span');
        separator1.className = 'mx-2';
        separator1.textContent = '|';
        
        const separator2 = document.createElement('span');
        separator2.className = 'mx-2';
        separator2.textContent = '|';
        
        // Hemisphere span
        const hemisphereSpan = document.createElement('span');
        hemisphereSpan.textContent = `Hemisphere: ${query.hemisphere_used || 'N/A'}`;
        
        // D2 activation span
        const d2Span = document.createElement('span');
        d2Span.textContent = `D2: ${query.d2_activation ? query.d2_activation.toFixed(2) : 'N/A'}`;
        
        // Append all metadata elements
        metadataDiv.appendChild(typeSpanOuter);
        metadataDiv.appendChild(separator1);
        metadataDiv.appendChild(hemisphereSpan);
        metadataDiv.appendChild(separator2);
        metadataDiv.appendChild(d2Span);
        
        // Append everything to the query item
        queryItem.appendChild(itemContainer);
        queryItem.appendChild(metadataDiv);
        
        container.appendChild(queryItem);
    });
}

/**
 * Set up filter buttons for query log
 */
function setupFilterButtons() {
    document.getElementById('filter-all').addEventListener('click', function() {
        setActiveFilterButton(this);
        filterQueries('all');
    });
    
    document.getElementById('filter-analytical').addEventListener('click', function() {
        setActiveFilterButton(this);
        filterQueries('analytical');
    });
    
    document.getElementById('filter-creative').addEventListener('click', function() {
        setActiveFilterButton(this);
        filterQueries('creative');
    });
    
    document.getElementById('filter-factual').addEventListener('click', function() {
        setActiveFilterButton(this);
        filterQueries('factual');
    });
}

/**
 * Set active filter button
 */
function setActiveFilterButton(button) {
    // Remove active class from all buttons
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
        btn.classList.remove('btn-info');
        btn.classList.add('btn-outline-info');
    });
    
    // Add active class to selected button
    button.classList.add('active');
    button.classList.remove('btn-outline-info');
    button.classList.add('btn-info');
}

/**
 * Filter queries by type
 */
function filterQueries(type) {
    const queryItems = document.querySelectorAll('.query-item');
    
    queryItems.forEach(item => {
        if (type === 'all' || item.getAttribute('data-type') === type) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Update system stats
 */
function updateSystemStats(data) {
    // If no data provided, fetch it
    if (!data) {
        fetch('/api/system/status')
            .then(response => response.json())
            .then(data => {
                updateSystemStatsDisplay(data);
            })
            .catch(error => {
                console.error('Error fetching system stats:', error);
            });
    } else {
        updateSystemStatsDisplay(data);
    }
}

/**
 * Update system stats display
 */
function updateSystemStatsDisplay(data) {
    // Update focus stat
    document.getElementById('focus-stat').textContent = data.state.focus.toFixed(2);
    
    // Update entropy stat
    document.getElementById('entropy-stat').textContent = data.state.entropy.toFixed(2);
    
    // Determine active hemisphere
    let activeHemi = 'C';
    if (data.state.activation.left_hemisphere > data.state.activation.right_hemisphere) {
        activeHemi = 'L';
    } else if (data.state.activation.right_hemisphere > data.state.activation.left_hemisphere) {
        activeHemi = 'R';
    }
    document.getElementById('hemisphere-stat').textContent = activeHemi;
    
    // Calculate total memory entries
    const totalMemory = Object.values(data.memory_stats).reduce((sum, val) => sum + val, 0);
    document.getElementById('memory-stat').textContent = totalMemory;
    
    // Query count (placeholder since we don't have this in the API)
    // In a real implementation, this would come from the API
    const queryCount = document.querySelectorAll('.query-item').length;
    document.getElementById('queries-stat').textContent = queryCount;
}

/**
 * Generate time labels for charts
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
