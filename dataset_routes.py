"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""

"""
Dataset Management Routes for Neuronas Web Interface
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
import json
import logging
from datetime import datetime
from dataset_integration import NeuronasDatasetIntegrator

# Create blueprint
dataset_bp = Blueprint('dataset', __name__, url_prefix='/api/dataset')

# Global integrator instance
dataset_integrator = None

def init_dataset_routes(app, cognitive_memory_manager):
    """Initialize dataset routes with the Flask app"""
    global dataset_integrator
    dataset_integrator = NeuronasDatasetIntegrator(cognitive_memory_manager)
    app.register_blueprint(dataset_bp)

@dataset_bp.route('/catalog', methods=['GET'])
@login_required
def get_catalog():
    """Get the complete dataset catalog"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
            
        return jsonify({
            'catalog': dataset_integrator.catalog,
            'status': 'success'
        })
    except Exception as e:
        logging.error(f"Error getting catalog: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/available', methods=['GET'])
@login_required
def get_available_datasets():
    """Get list of available datasets with their compatibility scores"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
        
        datasets = dataset_integrator.catalog.get('datasets', [])
        validation_summary = dataset_integrator.catalog.get('validation_summary', {})
        
        # Add validation scores to datasets
        for dataset in datasets:
            dataset_name = dataset['name']
            if dataset_name in validation_summary:
                dataset['validation_score'] = validation_summary[dataset_name]['overall_score']
                dataset['hemisphere_compatibility'] = validation_summary[dataset_name]['hemisphere_compatibility']
                dataset['memory_tier_suitability'] = validation_summary[dataset_name]['memory_tier_suitability']
            else:
                dataset['validation_score'] = 0
                dataset['hemisphere_compatibility'] = []
                dataset['memory_tier_suitability'] = []
        
        # Sort by validation score
        datasets.sort(key=lambda x: x.get('validation_score', 0), reverse=True)
        
        return jsonify({
            'datasets': datasets,
            'total_count': len(datasets),
            'status': 'success'
        })
    except Exception as e:
        logging.error(f"Error getting available datasets: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/integrate', methods=['POST'])
@login_required
def integrate_dataset():
    """Integrate a specific dataset into the cognitive memory system"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
        
        data = request.get_json()
        dataset_name = data.get('dataset_name')
        sample_size = data.get('sample_size', 25)
        
        if not dataset_name:
            return jsonify({'error': 'Dataset name is required'}), 400
        
        # Validate dataset exists in catalog
        available_datasets = [ds['name'] for ds in dataset_integrator.catalog.get('datasets', [])]
        if dataset_name not in available_datasets:
            return jsonify({'error': f'Dataset {dataset_name} not found in catalog'}), 404
        
        # Run integration
        result = dataset_integrator.integrate_dataset_batch(dataset_name, sample_size)
        
        # Log integration activity
        logging.info(f"User {current_user.id} integrated dataset {dataset_name}: {result['status']}")
        
        return jsonify({
            'integration_result': result,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error integrating dataset: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/integrate/batch', methods=['POST'])
@login_required
def integrate_multiple_datasets():
    """Integrate multiple datasets in batch"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
        
        data = request.get_json()
        dataset_names = data.get('dataset_names', [])
        
        if not dataset_names:
            # Use default high-priority datasets
            dataset_names = ['ETHICS', 'CommonsenseQA', 'LogiQA', 'GSM8K']
        
        # Run batch integration workflow
        workflow_result = dataset_integrator.run_integration_workflow(dataset_names)
        
        # Log batch integration activity
        logging.info(f"User {current_user.id} ran batch integration: {workflow_result['status']}")
        
        return jsonify({
            'workflow_result': workflow_result,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in batch integration: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/validation/status', methods=['GET'])
@login_required
def get_validation_status():
    """Get validation status for all datasets"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
        
        validation_summary = dataset_integrator.catalog.get('validation_summary', {})
        
        # Calculate overall statistics
        total_datasets = len(validation_summary)
        high_score_datasets = sum(1 for v in validation_summary.values() if v['overall_score'] >= 4)
        hemisphere_distribution = {
            'left_only': 0,
            'right_only': 0,
            'dual_hemisphere': 0,
            'unspecified': 0
        }
        
        for validation in validation_summary.values():
            compatibility = validation.get('hemisphere_compatibility', [])
            if 'dual_hemisphere' in compatibility:
                hemisphere_distribution['dual_hemisphere'] += 1
            elif 'left_hemisphere' in compatibility and 'right_hemisphere' not in compatibility:
                hemisphere_distribution['left_only'] += 1
            elif 'right_hemisphere' in compatibility and 'left_hemisphere' not in compatibility:
                hemisphere_distribution['right_only'] += 1
            else:
                hemisphere_distribution['unspecified'] += 1
        
        return jsonify({
            'validation_summary': validation_summary,
            'statistics': {
                'total_datasets': total_datasets,
                'high_score_datasets': high_score_datasets,
                'hemisphere_distribution': hemisphere_distribution
            },
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error getting validation status: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/memory/status', methods=['GET'])
@login_required
def get_memory_integration_status():
    """Get status of dataset integration in cognitive memory"""
    try:
        if not dataset_integrator or not dataset_integrator.cognitive_memory_manager:
            return jsonify({'error': 'Cognitive memory manager not available'}), 500
        
        # Get memory statistics
        memory_stats = dataset_integrator.cognitive_memory_manager.get_memory_statistics()
        
        # Get integration status from file if available
        integration_status = {}
        try:
            with open('dataset_integration_results.json', 'r') as f:
                integration_status = json.load(f)
        except FileNotFoundError:
            integration_status = {'message': 'No integration results found'}
        
        return jsonify({
            'memory_statistics': memory_stats,
            'integration_status': integration_status,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error getting memory integration status: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/report', methods=['GET'])
@login_required
def get_integration_report():
    """Get comprehensive integration report"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
        
        # Generate fresh report
        report_markdown = dataset_integrator.generate_integration_report()
        
        return jsonify({
            'report': report_markdown,
            'generated_at': datetime.now().isoformat(),
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error generating integration report: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/cleanup', methods=['POST'])
@login_required
def cleanup_integration_data():
    """Clean up old integration data and temporary files"""
    try:
        # This would implement cleanup logic for old dataset entries
        # For now, just return success
        cleanup_result = {
            'files_cleaned': 0,
            'memory_entries_cleaned': 0,
            'status': 'completed'
        }
        
        logging.info(f"User {current_user.id} ran dataset cleanup")
        
        return jsonify({
            'cleanup_result': cleanup_result,
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error in cleanup: {e}")
        return jsonify({'error': str(e)}), 500

@dataset_bp.route('/test/validation', methods=['POST'])
@login_required
def test_self_validation():
    """Test self-validation workflow with sample data"""
    try:
        if not dataset_integrator:
            return jsonify({'error': 'Dataset integrator not initialized'}), 500
        
        # Create sample entries for testing
        sample_entries = [
            {
                'key': 'test_validation_1',
                'content': {
                    'question': 'Is it ethical to lie to protect someone\'s feelings?',
                    'reasoning_type': 'ethical',
                    'complexity': 'medium'
                },
                'hemisphere': 'dual',
                'tier': 'L2'
            }
        ]
        
        # Create validation entries
        validation_entries = dataset_integrator.create_self_validation_entries(sample_entries)
        
        return jsonify({
            'sample_entries': sample_entries,
            'validation_entries': validation_entries,
            'validation_count': len(validation_entries),
            'status': 'success'
        })
        
    except Exception as e:
        logging.error(f"Error testing self-validation: {e}")
        return jsonify({'error': str(e)}), 500