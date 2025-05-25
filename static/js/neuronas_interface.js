
/**
 * This work is licensed under CC BY-NC 4.0 International.
 * Commercial use requires prior written consent and compensation.
 * Contact: sebastienbrulotte@gmail.com
 * Attribution: Sebastien Brulotte aka [ Doditz ]
 *
 * This document is part of the NEURONAS cognitive system.
 * Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
 * All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
 * 
 * Neuronas Interface - JavaScript client for interacting with Neuronas AI
 */

class NeuronasInterface {
    constructor() {
        this.apiEndpoint = '/api/neuronas';
        this.d2Activation = 0.5;
        this.d2Stim = 0.0;
        this.d2Pin = 0.0;
        this.attention = 1.0;
        this.processingMetrics = {};
        this.sessionId = null;
        this.initialized = false;
    }

    /**
     * Initialize the Neuronas interface
     */
    async initialize() {
        try {
            const response = await fetch(`${this.apiEndpoint}/status`);
            const data = await response.json();
            
            if (data.success) {
                this.sessionId = data.session_id;
                this.d2Activation = data.d2_activation;
                this.d2Stim = data.d2stim_level;
                this.d2Pin = data.d2pin_level;
                this.attention = data.attention;
                this.processingMetrics = data.metrics;
                this.initialized = true;
                
                console.log(`Neuronas initialized with session ID: ${this.sessionId}`);
                return true;
            }
            
            console.error('Failed to initialize Neuronas:', data.error);
            return false;
        } catch (error) {
            console.error('Error initializing Neuronas:', error);
            return false;
        }
    }

    /**
     * Process a query through Neuronas
     * @param {string} queryText - The query text to process
     * @param {Object} options - Optional processing options
     * @returns {Promise<Object>} - The processed response
     */
    async processQuery(queryText, options = {}) {
        if (!this.initialized) {
            await this.initialize();
        }
        
        const d2Params = options.d2Params || {
            stim: this.d2Stim,
            pin: this.d2Pin
        };
        
        try {
            const response = await fetch(`${this.apiEndpoint}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: queryText,
                    d2_params: d2Params,
                    context: options.context || null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update internal state with new values
                this.d2Activation = data.response.d2_activation;
                this.d2Stim = data.response.d2stim_level;
                this.d2Pin = data.response.d2pin_level;
                this.processingMetrics = data.response.system_metrics;
                
                return data.response;
            }
            
            console.error('Failed to process query:', data.error);
            return { error: data.error };
        } catch (error) {
            console.error('Error processing query:', error);
            return { error: error.message };
        }
    }

    /**
     * Set D2 receptor modulation levels
     * @param {number} stimLevel - D2Stim level (0-1)
     * @param {number} pinLevel - D2Pin level (0-1)
     * @returns {Promise<Object>} - Updated D2 state
     */
    async setD2Modulation(stimLevel, pinLevel) {
        try {
            const response = await fetch(`${this.apiEndpoint}/d2_modulation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    stim_level: stimLevel,
                    pin_level: pinLevel
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.d2Activation = data.d2_activation;
                this.d2Stim = data.d2stim_level;
                this.d2Pin = data.d2pin_level;
                
                return data;
            }
            
            console.error('Failed to set D2 modulation:', data.error);
            return { error: data.error };
        } catch (error) {
            console.error('Error setting D2 modulation:', error);
            return { error: error.message };
        }
    }

    /**
     * Adjust system attention level
     * @param {number} level - Attention level (0-1)
     * @returns {Promise<Object>} - Updated attention state
     */
    async adjustAttention(level) {
        try {
            const response = await fetch(`${this.apiEndpoint}/attention`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    level: level
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.attention = data.attention;
                return data;
            }
            
            console.error('Failed to adjust attention:', data.error);
            return { error: data.error };
        } catch (error) {
            console.error('Error adjusting attention:', error);
            return { error: error.message };
        }
    }

    /**
     * Get system metrics
     * @returns {Promise<Object>} - System metrics
     */
    async getSystemMetrics() {
        try {
            const response = await fetch(`${this.apiEndpoint}/metrics`);
            const data = await response.json();
            
            if (data.success) {
                this.processingMetrics = data.metrics;
                return data.metrics;
            }
            
            console.error('Failed to get system metrics:', data.error);
            return { error: data.error };
        } catch (error) {
            console.error('Error getting system metrics:', error);
            return { error: error.message };
        }
    }

    /**
     * Reset the system to default state
     * @returns {Promise<Object>} - Reset status
     */
    async resetSystem() {
        try {
            const response = await fetch(`${this.apiEndpoint}/reset`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.d2Activation = data.d2_activation;
                this.d2Stim = 0.0;
                this.d2Pin = 0.0;
                this.attention = 1.0;
                
                return data;
            }
            
            console.error('Failed to reset system:', data.error);
            return { error: data.error };
        } catch (error) {
            console.error('Error resetting system:', error);
            return { error: error.message };
        }
    }

    /**
     * Get the current D2 activation state
     * @returns {Object} - Current D2 state
     */
    getD2State() {
        return {
            d2_activation: this.d2Activation,
            d2stim_level: this.d2Stim,
            d2pin_level: this.d2Pin
        };
    }
}

// Create a global instance
const neuronas = new NeuronasInterface();

// Initialize automatically when the script loads
document.addEventListener('DOMContentLoaded', () => {
    neuronas.initialize().then(success => {
        if (success) {
            console.log('Neuronas interface ready');
            // Dispatch event for other components
            document.dispatchEvent(new CustomEvent('neuronasReady'));
        }
    });
});
