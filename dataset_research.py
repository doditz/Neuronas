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
Dataset Research and Collection for Neuronas Cognitive System

This module identifies and gathers free datasets suitable for cognitive reasoning,
dual-hemisphere processing, and self-validating workflows.
"""

import requests
import json
import os
from typing import Dict, List, Any
import logging

class DatasetCollector:
    """Collects and validates datasets for Neuronas cognitive processing"""
    
    def __init__(self):
        self.datasets = []
        self.cognitive_categories = {
            'logical_reasoning': [],
            'creative_reasoning': [],
            'ethical_scenarios': [],
            'pattern_recognition': [],
            'language_understanding': [],
            'mathematical_reasoning': [],
            'causal_inference': [],
            'common_sense': []
        }
        
    def search_huggingface_datasets(self):
        """Search Hugging Face for cognitive reasoning datasets"""
        base_url = "https://huggingface.co/api/datasets"
        
        # Search terms for cognitive reasoning datasets
        search_terms = [
            "reasoning", "logic", "cognitive", "inference", "causal",
            "commonsense", "ethical", "moral", "pattern", "mathematical"
        ]
        
        datasets_found = []
        
        for term in search_terms:
            try:
                response = requests.get(f"{base_url}?search={term}&filter=dataset&sort=downloads&direction=-1")
                if response.status_code == 200:
                    data = response.json()
                    for dataset in data[:10]:  # Top 10 for each term
                        datasets_found.append({
                            'name': dataset.get('id', ''),
                            'downloads': dataset.get('downloads', 0),
                            'likes': dataset.get('likes', 0),
                            'description': dataset.get('description', ''),
                            'tags': dataset.get('tags', []),
                            'source': 'huggingface',
                            'url': f"https://huggingface.co/datasets/{dataset.get('id', '')}"
                        })
            except Exception as e:
                logging.warning(f"Error searching for {term}: {e}")
        
        return datasets_found
    
    def get_recommended_datasets(self):
        """Get curated list of recommended datasets for cognitive reasoning"""
        return [
            {
                'name': 'CommonsenseQA',
                'description': 'Multiple-choice question answering dataset requiring commonsense reasoning',
                'category': 'common_sense',
                'url': 'https://huggingface.co/datasets/commonsense_qa',
                'size': '12K questions',
                'license': 'MIT',
                'format': 'JSON',
                'suitable_for': ['right_hemisphere', 'pattern_recognition', 'intuitive_reasoning']
            },
            {
                'name': 'LogiQA',
                'description': 'Logical reasoning dataset with reading comprehension',
                'category': 'logical_reasoning',
                'url': 'https://huggingface.co/datasets/logiqa',
                'size': '8K questions',
                'license': 'Apache 2.0',
                'format': 'JSON',
                'suitable_for': ['left_hemisphere', 'analytical_processing', 'structured_reasoning']
            },
            {
                'name': 'ETHICS',
                'description': 'Dataset for training models to predict human ethical judgments',
                'category': 'ethical_scenarios',
                'url': 'https://huggingface.co/datasets/hendrycks/ethics',
                'size': '130K scenarios',
                'license': 'MIT',
                'format': 'JSON',
                'suitable_for': ['bronas_training', 'ethical_validation', 'dual_hemisphere']
            },
            {
                'name': 'GSM8K',
                'description': 'Grade school math word problems requiring multi-step reasoning',
                'category': 'mathematical_reasoning',
                'url': 'https://huggingface.co/datasets/gsm8k',
                'size': '8.5K problems',
                'license': 'MIT',
                'format': 'JSON',
                'suitable_for': ['left_hemisphere', 'step_by_step_reasoning', 'validation']
            },
            {
                'name': 'ARC-Challenge',
                'description': 'AI2 Reasoning Challenge with science questions',
                'category': 'logical_reasoning',
                'url': 'https://huggingface.co/datasets/ai2_arc',
                'size': '7K questions',
                'license': 'Apache 2.0',
                'format': 'JSON',
                'suitable_for': ['dual_hemisphere', 'scientific_reasoning', 'fact_validation']
            },
            {
                'name': 'StrategyQA',
                'description': 'Strategy questions requiring implicit multi-step reasoning',
                'category': 'causal_inference',
                'url': 'https://huggingface.co/datasets/strategy_qa',
                'size': '2.7K questions',
                'license': 'Apache 2.0',
                'format': 'JSON',
                'suitable_for': ['right_hemisphere', 'creative_reasoning', 'strategy_planning']
            },
            {
                'name': 'COPA',
                'description': 'Choice of Plausible Alternatives for causal reasoning',
                'category': 'causal_inference',
                'url': 'https://huggingface.co/datasets/super_glue',
                'size': '1K questions',
                'license': 'BSD',
                'format': 'JSON',
                'suitable_for': ['dual_hemisphere', 'causal_reasoning', 'plausibility_assessment']
            },
            {
                'name': 'WinoGrande',
                'description': 'Commonsense reasoning benchmark with pronoun resolution',
                'category': 'common_sense',
                'url': 'https://huggingface.co/datasets/winogrande',
                'size': '44K questions',
                'license': 'Apache 2.0',
                'format': 'JSON',
                'suitable_for': ['right_hemisphere', 'contextual_understanding', 'ambiguity_resolution']
            },
            {
                'name': 'QuALITY',
                'description': 'Question Answering with Long Input Texts for reading comprehension',
                'category': 'language_understanding',
                'url': 'https://huggingface.co/datasets/quality',
                'size': '6K questions',
                'license': 'Apache 2.0',
                'format': 'JSON',
                'suitable_for': ['left_hemisphere', 'analytical_reading', 'long_context_processing']
            },
            {
                'name': 'Social IQa',
                'description': 'Social interaction reasoning with emotional intelligence',
                'category': 'common_sense',
                'url': 'https://huggingface.co/datasets/social_i_qa',
                'size': '38K questions',
                'license': 'Apache 2.0',
                'format': 'JSON',
                'suitable_for': ['right_hemisphere', 'social_reasoning', 'emotional_processing']
            }
        ]
    
    def download_dataset_sample(self, dataset_name: str, sample_size: int = 100):
        """Download a sample of a dataset for testing"""
        try:
            from datasets import load_dataset
            
            # Load dataset
            dataset = load_dataset(dataset_name, split='train')
            
            # Get sample
            sample = dataset.select(range(min(sample_size, len(dataset))))
            
            # Save sample
            sample_path = f"dataset_samples/{dataset_name.replace('/', '_')}_sample.json"
            os.makedirs('dataset_samples', exist_ok=True)
            
            sample.to_json(sample_path)
            return sample_path
            
        except Exception as e:
            logging.error(f"Error downloading {dataset_name}: {e}")
            return None
    
    def validate_dataset_for_neuronas(self, dataset_info: Dict) -> Dict:
        """Validate if a dataset is suitable for Neuronas processing"""
        validation_score = 0
        validation_details = {
            'hemisphere_compatibility': [],
            'processing_type': [],
            'memory_tier_suitability': [],
            'ethical_considerations': [],
            'overall_score': 0
        }
        
        # Check hemisphere compatibility
        if 'logical' in dataset_info.get('category', '').lower() or 'mathematical' in dataset_info.get('category', '').lower():
            validation_details['hemisphere_compatibility'].append('left_hemisphere')
            validation_score += 2
            
        if 'creative' in dataset_info.get('category', '').lower() or 'common_sense' in dataset_info.get('category', '').lower():
            validation_details['hemisphere_compatibility'].append('right_hemisphere')
            validation_score += 2
            
        # Check for dual-hemisphere suitability
        if 'ethical' in dataset_info.get('category', '').lower():
            validation_details['hemisphere_compatibility'].append('dual_hemisphere')
            validation_score += 3
            
        # Memory tier suitability
        size = dataset_info.get('size', '')
        if 'K' in size:
            try:
                num_str = size.split('K')[0]
                num = float(num_str)  # Use float to handle decimals like 8.5K
                if num < 10:
                    validation_details['memory_tier_suitability'].append('L1_R1')
                    validation_score += 1
                elif num < 50:
                    validation_details['memory_tier_suitability'].append('L2_R2')
                    validation_score += 1
                else:
                    validation_details['memory_tier_suitability'].append('L3_R3')
                    validation_score += 1
            except ValueError:
                # If parsing fails, default to L2_R2
                validation_details['memory_tier_suitability'].append('L2_R2')
                validation_score += 1
                
        # Ethical considerations
        if dataset_info.get('license') in ['MIT', 'Apache 2.0', 'BSD']:
            validation_details['ethical_considerations'].append('open_license')
            validation_score += 1
            
        validation_details['overall_score'] = validation_score
        return validation_details
    
    def generate_integration_plan(self, datasets: List[Dict]) -> Dict:
        """Generate integration plan for datasets into Neuronas system"""
        plan = {
            'left_hemisphere_datasets': [],
            'right_hemisphere_datasets': [],
            'dual_hemisphere_datasets': [],
            'bronas_training_datasets': [],
            'memory_tier_allocation': {},
            'processing_workflow': []
        }
        
        for dataset in datasets:
            validation = self.validate_dataset_for_neuronas(dataset)
            
            if 'left_hemisphere' in validation['hemisphere_compatibility']:
                plan['left_hemisphere_datasets'].append(dataset['name'])
                
            if 'right_hemisphere' in validation['hemisphere_compatibility']:
                plan['right_hemisphere_datasets'].append(dataset['name'])
                
            if 'dual_hemisphere' in validation['hemisphere_compatibility']:
                plan['dual_hemisphere_datasets'].append(dataset['name'])
                
            if dataset.get('category') == 'ethical_scenarios':
                plan['bronas_training_datasets'].append(dataset['name'])
                
            # Memory allocation
            for tier in validation['memory_tier_suitability']:
                if tier not in plan['memory_tier_allocation']:
                    plan['memory_tier_allocation'][tier] = []
                plan['memory_tier_allocation'][tier].append(dataset['name'])
        
        # Generate processing workflow
        plan['processing_workflow'] = [
            "1. Load datasets into appropriate memory tiers",
            "2. Preprocess for hemisphere-specific formats",
            "3. Initialize BRONAS ethical validation",
            "4. Begin dual-hemisphere training/validation",
            "5. Implement self-validation workflows",
            "6. Monitor cognitive memory integration"
        ]
        
        return plan
    
    def save_dataset_catalog(self, filepath: str = 'neuronas_dataset_catalog.json'):
        """Save complete dataset catalog with analysis"""
        recommended_datasets = self.get_recommended_datasets()
        
        catalog = {
            'metadata': {
                'created_date': '2025-06-30',
                'total_datasets': len(recommended_datasets),
                'categories': list(self.cognitive_categories.keys()),
                'neuronas_version': '4.3'
            },
            'datasets': recommended_datasets,
            'integration_plan': self.generate_integration_plan(recommended_datasets),
            'validation_summary': {}
        }
        
        # Add validation for each dataset
        for dataset in recommended_datasets:
            validation = self.validate_dataset_for_neuronas(dataset)
            catalog['validation_summary'][dataset['name']] = validation
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(catalog, f, indent=2, ensure_ascii=False)
        
        return filepath

if __name__ == "__main__":
    collector = DatasetCollector()
    catalog_path = collector.save_dataset_catalog()
    print(f"Dataset catalog saved to: {catalog_path}")