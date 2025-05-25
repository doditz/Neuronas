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
 * Neuronas Visualization Library
 * Provides visualization functions for neural pathways, memory structures,
 * and cognitive processes.
 */

class NeuronasVisualizer {
    constructor() {
        // Initialize visualization settings
        this.settings = {
            colors: {
                left: '#3498db',  // Blue for left hemisphere
                right: '#9b59b6', // Purple for right hemisphere
                central: '#2ecc71', // Green for central integration
                inactive: '#bdc3c7', // Light gray for inactive elements
                active: '#f39c12',  // Orange for active elements
                highlight: '#e74c3c' // Red for highlights
            },
            animation: {
                duration: 500,
                easing: d3.easeCubicInOut
            }
        };
    }

    /**
     * Create a neural pathway visualization
     * @param {string} containerId - ID of the container element
     * @param {object} data - Neural pathway data
     */
    createNeuralPathways(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Set dimensions
        const width = container.offsetWidth;
        const height = container.offsetHeight || 400;
        const margin = { top: 20, right: 20, bottom: 20, left: 20 };

        // Create SVG container
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height);

        // Process data if needed
        const nodes = data.nodes || this._generateDefaultNodes(width, height);
        const links = data.links || this._generateDefaultLinks(nodes);

        // Create force simulation
        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links).id(d => d.id).distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collision', d3.forceCollide().radius(d => d.radius + 5));

        // Create links
        const link = svg.append('g')
            .attr('class', 'links')
            .selectAll('line')
            .data(links)
            .enter()
            .append('line')
            .attr('stroke-width', d => d.weight || 1)
            .attr('stroke', d => {
                if (d.source.hemisphere === 'left' && d.target.hemisphere === 'left') {
                    return this.settings.colors.left;
                } else if (d.source.hemisphere === 'right' && d.target.hemisphere === 'right') {
                    return this.settings.colors.right;
                } else {
                    return this.settings.colors.central;
                }
            });

        // Create nodes
        const node = svg.append('g')
            .attr('class', 'nodes')
            .selectAll('circle')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('r', d => d.radius || 10)
            .attr('fill', d => {
                if (d.hemisphere === 'left') {
                    return this.settings.colors.left;
                } else if (d.hemisphere === 'right') {
                    return this.settings.colors.right;
                } else {
                    return this.settings.colors.central;
                }
            })
            .call(d3.drag()
                .on('start', this._dragstarted.bind(this, simulation))
                .on('drag', this._dragged.bind(this))
                .on('end', this._dragended.bind(this, simulation)));

        // Add labels
        const label = svg.append('g')
            .attr('class', 'labels')
            .selectAll('text')
            .data(nodes)
            .enter()
            .append('text')
            .text(d => d.name)
            .attr('font-size', 12)
            .attr('dx', 15)
            .attr('dy', 4)
            .attr('fill', 'white');

        // Update positions
        simulation.on('tick', () => {
            link
                .attr('x1', d => d.source.x)
                .attr('y1', d => d.source.y)
                .attr('x2', d => d.target.x)
                .attr('y2', d => d.target.y);

            node
                .attr('cx', d => d.x = Math.max(d.radius, Math.min(width - d.radius, d.x)))
                .attr('cy', d => d.y = Math.max(d.radius, Math.min(height - d.radius, d.y)));

            label
                .attr('x', d => d.x)
                .attr('y', d => d.y);
        });

        // Store the simulation for later use
        container.simulation = simulation;
    }

    /**
     * Create a hemispheric architecture visualization
     * @param {string} containerId - ID of the container element
     * @param {object} data - Hemispheric data
     */
    createHemisphericVisualization(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Set dimensions
        const width = container.offsetWidth;
        const height = container.offsetHeight || 400;
        const margin = { top: 20, right: 20, bottom: 50, left: 20 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Create SVG container
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Default data if none provided
        const memoryTiers = data && data.memoryTiers ? data.memoryTiers : {
            L1: { count: 0, capacity: 20 },
            L2: { count: 0, capacity: 50 },
            L3: { count: 0, capacity: 100 },
            R1: { count: 0, capacity: 20 },
            R2: { count: 0, capacity: 50 },
            R3: { count: 0, capacity: 100 }
        };

        // Create hemispheres
        this._createBrainVisualization(svg, innerWidth, innerHeight, memoryTiers);

        // Add title
        svg.append('text')
            .attr('x', innerWidth / 2)
            .attr('y', -5)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .style('font-size', '16px')
            .text('Hemispheric Architecture');
    }

    /**
     * Create a memory heatmap visualization
     * @param {string} containerId - ID of the container element
     * @param {object} data - Memory data
     */
    createMemoryHeatmap(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Set dimensions
        const width = container.offsetWidth;
        const height = container.offsetHeight || 300;
        const margin = { top: 40, right: 50, bottom: 40, left: 50 };
        const innerWidth = width - margin.left - margin.right;
        const innerHeight = height - margin.top - margin.bottom;

        // Create SVG container
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Default data if none provided
        const memoryData = data || this._generateMemoryHeatmapData();

        // Process data to extract tiers and keys
        const tiers = [...new Set(memoryData.map(d => d.tier))];
        const keys = [...new Set(memoryData.map(d => d.key))];

        // Create scales
        const xScale = d3.scaleBand()
            .domain(keys)
            .range([0, innerWidth])
            .padding(0.1);

        const yScale = d3.scaleBand()
            .domain(tiers)
            .range([0, innerHeight])
            .padding(0.1);

        const colorScale = d3.scaleSequential()
            .interpolator(d3.interpolateInferno)
            .domain([0, 1]);

        // Create cells
        svg.selectAll('rect')
            .data(memoryData)
            .enter()
            .append('rect')
            .attr('x', d => xScale(d.key))
            .attr('y', d => yScale(d.tier))
            .attr('width', xScale.bandwidth())
            .attr('height', yScale.bandwidth())
            .attr('fill', d => colorScale(d.importance))
            .attr('stroke', '#1e1e2f')
            .attr('stroke-width', 1)
            .append('title')
            .text(d => `Key: ${d.key}\nTier: ${d.tier}\nImportance: ${d.importance.toFixed(2)}`);

        // Add X axis
        svg.append('g')
            .attr('transform', `translate(0,${innerHeight})`)
            .call(d3.axisBottom(xScale))
            .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end');

        // Add Y axis
        svg.append('g')
            .call(d3.axisLeft(yScale));

        // Add title
        svg.append('text')
            .attr('x', innerWidth / 2)
            .attr('y', -20)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .style('font-size', '16px')
            .text('Memory Importance Heatmap');
    }

    /**
     * Create a cognitive metrics visualization
     * @param {string} containerId - ID of the container element
     * @param {object} data - Metrics data
     */
    createCognitiveMetricsVisualization(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Set dimensions
        const width = container.offsetWidth;
        const height = container.offsetHeight || 300;
        const radius = Math.min(width, height) / 2 - 40;

        // Create SVG container
        const svg = d3.select(container)
            .append('svg')
            .attr('width', width)
            .attr('height', height)
            .append('g')
            .attr('transform', `translate(${width / 2},${height / 2})`);

        // Default data if none provided
        const metricsData = data || {
            focus: 0.7,
            entropy: 0.3,
            d2_activation: 0.5,
            attention: 0.6,
            working_memory: 0.4,
            learning: 0.8
        };

        // Convert data to array format for radar chart
        const metrics = Object.keys(metricsData);
        const dataValues = metrics.map(metric => ({
            metric: metric,
            value: metricsData[metric]
        }));

        // Create radar chart scales
        const angleScale = d3.scalePoint()
            .domain(metrics)
            .range([0, 2 * Math.PI]);

        const radiusScale = d3.scaleLinear()
            .domain([0, 1])
            .range([0, radius]);

        // Create radar grid
        const levels = 5;
        const gridCircles = svg.selectAll('.grid-circle')
            .data(d3.range(1, levels + 1).map(i => i / levels))
            .enter()
            .append('circle')
            .attr('class', 'grid-circle')
            .attr('r', d => radiusScale(d))
            .attr('fill', 'none')
            .attr('stroke', 'rgba(255, 255, 255, 0.2)')
            .attr('stroke-dasharray', '4,4');

        // Create grid lines
        const gridLines = svg.selectAll('.grid-line')
            .data(metrics)
            .enter()
            .append('line')
            .attr('class', 'grid-line')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', (d, i) => radiusScale(1) * Math.cos(angleScale(d) - Math.PI / 2))
            .attr('y2', (d, i) => radiusScale(1) * Math.sin(angleScale(d) - Math.PI / 2))
            .attr('stroke', 'rgba(255, 255, 255, 0.2)');

        // Create radar path
        const radarLine = d3.lineRadial()
            .angle(d => angleScale(d.metric) - Math.PI / 2)
            .radius(d => radiusScale(d.value))
            .curve(d3.curveLinearClosed);

        const radarPath = svg.append('path')
            .datum(dataValues)
            .attr('class', 'radar-path')
            .attr('d', radarLine)
            .attr('fill', 'rgba(52, 152, 219, 0.5)')
            .attr('stroke', '#3498db')
            .attr('stroke-width', 2);

        // Add axis labels
        const axisLabels = svg.selectAll('.axis-label')
            .data(metrics)
            .enter()
            .append('text')
            .attr('class', 'axis-label')
            .attr('x', d => (radiusScale(1.1)) * Math.cos(angleScale(d) - Math.PI / 2))
            .attr('y', d => (radiusScale(1.1)) * Math.sin(angleScale(d) - Math.PI / 2))
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .attr('fill', 'white')
            .style('font-size', '12px')
            .text(d => d.replace('_', ' '));

        // Add data points
        const dataPoints = svg.selectAll('.data-point')
            .data(dataValues)
            .enter()
            .append('circle')
            .attr('class', 'data-point')
            .attr('cx', d => radiusScale(d.value) * Math.cos(angleScale(d.metric) - Math.PI / 2))
            .attr('cy', d => radiusScale(d.value) * Math.sin(angleScale(d.metric) - Math.PI / 2))
            .attr('r', 4)
            .attr('fill', '#e74c3c');

        // Add title
        svg.append('text')
            .attr('x', 0)
            .attr('y', -radius - 20)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .style('font-size', '16px')
            .text('Cognitive Metrics Radar');
    }

    /**
     * Update neural pathway activity
     * @param {string} containerId - ID of the container element
     * @param {object} data - Activity data
     */
    updatePathwayActivity(containerId, data) {
        const container = document.getElementById(containerId);
        if (!container || !container.querySelector('svg')) return;

        const svg = d3.select(container).select('svg');
        
        // Update node colors based on activity
        if (data && data.activeNodes) {
            svg.selectAll('circle')
                .transition()
                .duration(this.settings.animation.duration)
                .attr('fill', d => {
                    // If node is active, highlight it
                    if (data.activeNodes.includes(d.id)) {
                        return this.settings.colors.active;
                    }
                    
                    // Otherwise use default hemisphere color
                    if (d.hemisphere === 'left') {
                        return this.settings.colors.left;
                    } else if (d.hemisphere === 'right') {
                        return this.settings.colors.right;
                    } else {
                        return this.settings.colors.central;
                    }
                });
        }
        
        // Update link colors based on activity
        if (data && data.activeLinks) {
            svg.selectAll('line')
                .transition()
                .duration(this.settings.animation.duration)
                .attr('stroke', d => {
                    // Check if link is active
                    const linkId = `${d.source.id}-${d.target.id}`;
                    if (data.activeLinks.includes(linkId)) {
                        return this.settings.colors.active;
                    }
                    
                    // Otherwise use default hemisphere color
                    if (d.source.hemisphere === 'left' && d.target.hemisphere === 'left') {
                        return this.settings.colors.left;
                    } else if (d.source.hemisphere === 'right' && d.target.hemisphere === 'right') {
                        return this.settings.colors.right;
                    } else {
                        return this.settings.colors.central;
                    }
                })
                .attr('stroke-width', d => {
                    const linkId = `${d.source.id}-${d.target.id}`;
                    return data.activeLinks.includes(linkId) ? (d.weight || 1) * 2 : (d.weight || 1);
                });
        }
    }

    /**
     * Private: Create brain hemisphere visualization
     */
    _createBrainVisualization(svg, width, height, memoryTiers) {
        // Brain dimensions
        const brainWidth = width * 0.8;
        const brainHeight = height * 0.7;
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Draw dividing line
        svg.append('line')
            .attr('x1', centerX)
            .attr('y1', centerY - brainHeight/2)
            .attr('x2', centerX)
            .attr('y2', centerY + brainHeight/2)
            .attr('stroke', 'rgba(255, 255, 255, 0.5)')
            .attr('stroke-width', 1)
            .attr('stroke-dasharray', '4,4');
        
        // Create left hemisphere
        const leftHemisphere = svg.append('ellipse')
            .attr('cx', centerX - brainWidth/4)
            .attr('cy', centerY)
            .attr('rx', brainWidth/4)
            .attr('ry', brainHeight/2)
            .attr('fill', 'rgba(52, 152, 219, 0.2)')
            .attr('stroke', '#3498db')
            .attr('stroke-width', 2);
        
        // Create right hemisphere
        const rightHemisphere = svg.append('ellipse')
            .attr('cx', centerX + brainWidth/4)
            .attr('cy', centerY)
            .attr('rx', brainWidth/4)
            .attr('ry', brainHeight/2)
            .attr('fill', 'rgba(155, 89, 182, 0.2)')
            .attr('stroke', '#9b59b6')
            .attr('stroke-width', 2);
        
        // Add hemisphere labels
        svg.append('text')
            .attr('x', centerX - brainWidth/4)
            .attr('y', centerY - brainHeight/2 - 10)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .text('Left Hemisphere');
        
        svg.append('text')
            .attr('x', centerX + brainWidth/4)
            .attr('y', centerY - brainHeight/2 - 10)
            .attr('text-anchor', 'middle')
            .attr('fill', 'white')
            .text('Right Hemisphere');
        
        // Add memory tiers
        this._addMemoryTiers(svg, centerX, centerY, brainWidth, brainHeight, memoryTiers);
    }
    
    /**
     * Private: Add memory tiers to brain visualization
     */
    _addMemoryTiers(svg, centerX, centerY, brainWidth, brainHeight, memoryTiers) {
        // Left hemisphere tiers
        const leftTiers = ['L3', 'L2', 'L1'];
        const leftColors = ['#1f618d', '#2980b9', '#3498db'];
        
        leftTiers.forEach((tier, i) => {
            const tierData = memoryTiers[tier];
            const fillRatio = tierData.count / tierData.capacity;
            
            // Tier circle
            svg.append('circle')
                .attr('cx', centerX - brainWidth/4)
                .attr('cy', centerY - brainHeight/4 + (i * brainHeight/4))
                .attr('r', 20)
                .attr('fill', leftColors[i])
                .attr('stroke', 'white')
                .attr('stroke-width', 1);
            
            // Fill indicator
            svg.append('circle')
                .attr('cx', centerX - brainWidth/4)
                .attr('cy', centerY - brainHeight/4 + (i * brainHeight/4))
                .attr('r', 20 * fillRatio)
                .attr('fill', 'rgba(255, 255, 255, 0.3)');
            
            // Label
            svg.append('text')
                .attr('x', centerX - brainWidth/4)
                .attr('y', centerY - brainHeight/4 + (i * brainHeight/4))
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('fill', 'white')
                .text(tier);
        });
        
        // Right hemisphere tiers
        const rightTiers = ['R3', 'R2', 'R1'];
        const rightColors = ['#6c3483', '#8e44ad', '#9b59b6'];
        
        rightTiers.forEach((tier, i) => {
            const tierData = memoryTiers[tier];
            const fillRatio = tierData.count / tierData.capacity;
            
            // Tier circle
            svg.append('circle')
                .attr('cx', centerX + brainWidth/4)
                .attr('cy', centerY - brainHeight/4 + (i * brainHeight/4))
                .attr('r', 20)
                .attr('fill', rightColors[i])
                .attr('stroke', 'white')
                .attr('stroke-width', 1);
            
            // Fill indicator
            svg.append('circle')
                .attr('cx', centerX + brainWidth/4)
                .attr('cy', centerY - brainHeight/4 + (i * brainHeight/4))
                .attr('r', 20 * fillRatio)
                .attr('fill', 'rgba(255, 255, 255, 0.3)');
            
            // Label
            svg.append('text')
                .attr('x', centerX + brainWidth/4)
                .attr('y', centerY - brainHeight/4 + (i * brainHeight/4))
                .attr('text-anchor', 'middle')
                .attr('dominant-baseline', 'middle')
                .attr('fill', 'white')
                .text(tier);
        });
        
        // Add legend
        const legend = svg.append('g')
            .attr('transform', `translate(${centerX - 100},${centerY + brainHeight/2 + 30})`);
        
        legend.append('text')
            .attr('x', 0)
            .attr('y', 0)
            .attr('fill', 'white')
            .text('Memory Tiers:');
        
        legend.append('circle')
            .attr('cx', 10)
            .attr('cy', 20)
            .attr('r', 5)
            .attr('fill', '#3498db');
        
        legend.append('text')
            .attr('x', 20)
            .attr('y', 23)
            .attr('fill', 'white')
            .text('L1/R1: Short-term (20)');
        
        legend.append('circle')
            .attr('cx', 10)
            .attr('cy', 40)
            .attr('r', 5)
            .attr('fill', '#2980b9');
        
        legend.append('text')
            .attr('x', 20)
            .attr('y', 43)
            .attr('fill', 'white')
            .text('L2/R2: Medium-term (50)');
        
        legend.append('circle')
            .attr('cx', 10)
            .attr('cy', 60)
            .attr('r', 5)
            .attr('fill', '#1f618d');
        
        legend.append('text')
            .attr('x', 20)
            .attr('y', 63)
            .attr('fill', 'white')
            .text('L3/R3: Long-term (100)');
    }

    /**
     * Private: Generate default nodes for neural pathway visualization
     */
    _generateDefaultNodes(width, height) {
        return [
            // Input and classification
            { id: 'input', name: 'Input', hemisphere: 'central', radius: 15 },
            { id: 'classify', name: 'Classify', hemisphere: 'central', radius: 12 },
            
            // Left hemisphere nodes (analytical)
            { id: 'l1', name: 'L1', hemisphere: 'left', radius: 10 },
            { id: 'l2', name: 'L2', hemisphere: 'left', radius: 10 },
            { id: 'l3', name: 'L3', hemisphere: 'left', radius: 10 },
            { id: 'd2pin', name: 'D2Pin', hemisphere: 'left', radius: 8 },
            { id: 'analysis', name: 'Analysis', hemisphere: 'left', radius: 10 },
            
            // Right hemisphere nodes (creative)
            { id: 'r1', name: 'R1', hemisphere: 'right', radius: 10 },
            { id: 'r2', name: 'R2', hemisphere: 'right', radius: 10 },
            { id: 'r3', name: 'R3', hemisphere: 'right', radius: 10 },
            { id: 'd2stim', name: 'D2Stim', hemisphere: 'right', radius: 8 },
            { id: 'creative', name: 'Creative', hemisphere: 'right', radius: 10 },
            
            // Integration and output
            { id: 'integrate', name: 'Integration', hemisphere: 'central', radius: 12 },
            { id: 'output', name: 'Output', hemisphere: 'central', radius: 15 }
        ];
    }

    /**
     * Private: Generate default links for neural pathway visualization
     */
    _generateDefaultLinks(nodes) {
        return [
            // Input flow
            { source: 'input', target: 'classify', weight: 3 },
            
            // Classification routes
            { source: 'classify', target: 'l1', weight: 2 },
            { source: 'classify', target: 'r1', weight: 2 },
            
            // Left hemisphere internal
            { source: 'l1', target: 'd2pin', weight: 1 },
            { source: 'l1', target: 'l2', weight: 2 },
            { source: 'l2', target: 'l3', weight: 2 },
            { source: 'l3', target: 'analysis', weight: 2 },
            
            // Right hemisphere internal
            { source: 'r1', target: 'd2stim', weight: 1 },
            { source: 'r1', target: 'r2', weight: 2 },
            { source: 'r2', target: 'r3', weight: 2 },
            { source: 'r3', target: 'creative', weight: 2 },
            
            // Integration
            { source: 'analysis', target: 'integrate', weight: 2 },
            { source: 'creative', target: 'integrate', weight: 2 },
            { source: 'integrate', target: 'output', weight: 3 }
        ];
    }

    /**
     * Private: Generate sample memory heatmap data
     */
    _generateMemoryHeatmapData() {
        const tiers = ['L1', 'L2', 'L3', 'R1', 'R2', 'R3'];
        const keys = ['A', 'B', 'C', 'D', 'E'];
        const data = [];
        
        tiers.forEach(tier => {
            keys.forEach(key => {
                data.push({
                    tier: tier,
                    key: key,
                    importance: Math.random()
                });
            });
        });
        
        return data;
    }

    /**
     * Private: D3 drag start handler
     */
    _dragstarted(simulation, event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    /**
     * Private: D3 drag handler
     */
    _dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    /**
     * Private: D3 drag end handler
     */
    _dragended(simulation, event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }
}

// Create global instance
const neuronasVisualizer = new NeuronasVisualizer();
