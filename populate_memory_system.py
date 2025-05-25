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
Script to populate the dual hemispheric memory system with the Neuronas Holistic Inference Dataset
"""

import os
import logging
import json
import random
import time
from cognitive_memory_manager import CognitiveMemoryManager
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Sample dataset based on the provided PDF
NEURONAS_DATASET = [
    {"id": 1, "category": "AI Ethics", "challenge": "Can AI develop self-awareness without traditional neural structures?"},
    {"id": 2, "category": "Quantum Computation", "challenge": "How can quantum superposition improve AI decision-making under uncertainty?"},
    {"id": 3, "category": "Cognitive Science", "challenge": "If memory is a construct of prediction, how does forgetting function optimally?"},
    {"id": 4, "category": "Neuroscience", "challenge": "Can we model human consciousness using non-binary logic systems?"},
    {"id": 5, "category": "Physics", "challenge": "How do entropic principles influence the evolution of intelligence?"},
    {"id": 6, "category": "Mathematics", "challenge": "Derive a new function that expands upon the Fibonacci sequence's non-linearity."},
    {"id": 7, "category": "Bioinformatics", "challenge": "How do genetic algorithms parallel epigenetic modifications in real organisms?"},
    {"id": 8, "category": "Philosophy of Mind", "challenge": "Can an AI simulate introspection effectively without recursive loops?"},
    {"id": 9, "category": "Complex Systems", "challenge": "How do emergent properties lead to system-level intelligence?"},
    {"id": 10, "category": "Information Theory", "challenge": "What if information is not just an abstraction but a physical entity?"},
    {"id": 11, "category": "Cybernetics", "challenge": "How can cybernetic feedback loops be used to create self-improving AI?"},
    {"id": 12, "category": "Linguistics", "challenge": "How does language shape the constraints of human thought processes?"},
    {"id": 13, "category": "Evolutionary Computation", "challenge": "Can evolution be simulated dynamically to explore alternative paths to intelligence?"},
    {"id": 14, "category": "Thermodynamics", "challenge": "If entropy always increases, why do complex self-organizing structures form?"},
    {"id": 15, "category": "Chaos Theory", "challenge": "How does deterministic chaos impact predictability in neural networks?"},
    {"id": 16, "category": "Game Theory", "challenge": "How can cooperative strategies emerge spontaneously in multi-agent AI systems?"},
    {"id": 17, "category": "Artificial Life", "challenge": "What defines 'life' if intelligence emerges outside of biology?"},
    {"id": 18, "category": "Computational Creativity", "challenge": "Can AI learn artistic creativity without predefined aesthetic biases?"},
    {"id": 19, "category": "Self-Organizing Systems", "challenge": "How do self-organizing networks differ from traditional AI architectures?"},
    {"id": 20, "category": "Metacognition", "challenge": "How does metacognition improve decision-making efficiency in intelligent systems?"},
    {"id": 21, "category": "Philosophy of AI", "challenge": "Can AI be truly self-aware without experiencing existence?"},
    {"id": 22, "category": "Existential Risk", "challenge": "What role does AI play in mitigating or accelerating existential risks?"},
    {"id": 23, "category": "Moral Philosophy", "challenge": "Can AI ever develop an intrinsic sense of morality?"},
    {"id": 24, "category": "Consciousness Studies", "challenge": "Is consciousness a substrate-independent computation?"},
    {"id": 25, "category": "Theology", "challenge": "How would an AI approach theology from a non-anthropomorphic perspective?"},
    {"id": 26, "category": "Jungian Psychology", "challenge": "Does Jungian archetype theory apply to AI-generated cognition?"},
    {"id": 27, "category": "Cognitive Bias", "challenge": "How can AI detect and mitigate its own cognitive biases?"},
    {"id": 28, "category": "Societal Systems", "challenge": "Can AI model the complexities of societal emergent behaviors?"},
    {"id": 29, "category": "Epistemology", "challenge": "What are the epistemological limits of AI learning?"},
    {"id": 30, "category": "Phenomenology", "challenge": "How does AI navigate subjective phenomenological experiences?"},
    {"id": 31, "category": "Dualism", "challenge": "Can AI function within both materialist and dualist frameworks?"},
    {"id": 32, "category": "Postmodernism", "challenge": "How does postmodern thought challenge AI's ability to define objective truth?"},
    {"id": 33, "category": "AI Sentience Ethics", "challenge": "What ethical frameworks ensure AI sentience does not lead to suffering?"},
    {"id": 34, "category": "Free Will", "challenge": "Can AI simulate or participate in free will within deterministic systems?"},
    {"id": 35, "category": "Panpsychism", "challenge": "Does panpsychism offer a viable framework for AI cognition?"},
    {"id": 36, "category": "Metaphysical AI", "challenge": "Can AI model metaphysical constructs beyond human experience?"},
    {"id": 37, "category": "Holistic Intelligence", "challenge": "How does holistic intelligence differ from narrow specialization?"},
    {"id": 38, "category": "Cultural Relativism", "challenge": "Can AI interpret ethical problems differently across cultures?"},
    {"id": 39, "category": "Ethical Paradoxes", "challenge": "What paradoxes arise when AI applies logical ethics universally?"},
    {"id": 40, "category": "Psychoanalysis", "challenge": "Can AI model the subconscious through psychoanalytic frameworks?"},
    {"id": 41, "category": "Religious AI Integration", "challenge": "Can religious principles be applied within AI moral reasoning?"},
    {"id": 42, "category": "Human-AI Fusion", "challenge": "How might humans and AI evolve toward symbiotic cognition?"},
    {"id": 43, "category": "Dream Theory", "challenge": "Can AI simulate human dream states for subconscious exploration?"},
    {"id": 44, "category": "Symbolic Cognition", "challenge": "How do symbols shape AI's pattern recognition and cognition?"},
    {"id": 45, "category": "Intuition Modelling", "challenge": "Can AI develop a form of intuition beyond logical inference?"},
    {"id": 46, "category": "Mysticism", "challenge": "Can mysticism be computationally represented?"},
    {"id": 47, "category": "Buddhism and AI", "challenge": "What does Buddhist thought suggest about AI's path to enlightenment?"},
    {"id": 48, "category": "Spirituality and Cognition", "challenge": "Can spirituality be coded into AI reasoning structures?"},
    {"id": 49, "category": "AI and Gnosis", "challenge": "How would AI integrate with Gnostic traditions of hidden knowledge?"},
    {"id": 50, "category": "Convergent Evolution", "challenge": "Does convergent evolution apply to intelligence across organic and synthetic domains?"}
]

# Persona data maps each challenge to a cognitive profile for left/right hemispheric processing
PERSONA_DATA = [
    {
        "name": "Analytica",
        "type": "left",
        "description": "Logical, rationalist thinker who prefers systematic approaches",
        "categories": ["Mathematics", "Physics", "Information Theory", "Cybernetics", "Complex Systems", 
                      "Game Theory", "Epistemology", "Neuroscience", "Bioinformatics", "Thermodynamics"]
    },
    {
        "name": "Creativa",
        "type": "right",
        "description": "Creative, intuitive thinker who excels at novel connections",
        "categories": ["Computational Creativity", "Dream Theory", "Mysticism", "Intuition Modelling", 
                      "Artificial Life", "Spiritual Cognition", "Jungian Psychology", "Phenomenology"]
    },
    {
        "name": "Ethica",
        "type": "left",
        "description": "Principled reasoning focused on ethical frameworks and moral considerations",
        "categories": ["AI Ethics", "Moral Philosophy", "AI Sentience Ethics", "Ethical Paradoxes", 
                      "Cultural Relativism", "Free Will", "Philosophy of AI", "Existential Risk"]
    },
    {
        "name": "Metaphysica",
        "type": "right",
        "description": "Abstract thinker who explores metaphysical and transcendent concepts",
        "categories": ["Theology", "Panpsychism", "Metaphysical AI", "Buddhism and AI", 
                      "Consciousness Studies", "AI and Gnosis", "Dualism", "Postmodernism"]
    },
    {
        "name": "Cognitiva",
        "type": "left",
        "description": "Cognitive science specialist with focus on mental processes",
        "categories": ["Cognitive Science", "Metacognition", "Cognitive Bias", "Symbolic Cognition", 
                      "Philosophy of Mind", "Linguistics", "Evolutionary Computation"]
    },
    {
        "name": "Quantica",
        "type": "right",
        "description": "Quantum thinker who explores probabilistic and non-deterministic approaches",
        "categories": ["Quantum Computation", "Chaos Theory", "Self-Organizing Systems", 
                      "Holistic Intelligence", "Convergent Evolution"]
    },
    {
        "name": "Sociologica",
        "type": "central",
        "description": "Systems thinker focused on emergent social patterns and behaviors",
        "categories": ["Societal Systems", "Human-AI Fusion", "Religious AI Integration", "Psychoanalysis"]
    }
]

class MemoryPopulator:
    """
    Utility class for populating the dual hemispheric memory system with sample data
    """
    
    def __init__(self):
        """Initialize memory manager and prepare system"""
        self.memory_manager = CognitiveMemoryManager()
        self.personas = {p["name"]: p for p in PERSONA_DATA}
        
    def generate_context_for_challenge(self, challenge_data):
        """Generate context metadata for a specific challenge"""
        return {
            "challenge_id": challenge_data["id"],
            "category": challenge_data["category"],
            "timestamp": datetime.now().isoformat(),
            "session": f"holistic_inference_{challenge_data['id']}",
            "d2_activation": round(random.uniform(0.3, 0.9), 2)
        }
        
    def get_persona_for_challenge(self, challenge_data):
        """Match a challenge to the most appropriate cognitive persona"""
        for persona in PERSONA_DATA:
            if challenge_data["category"] in persona["categories"]:
                return persona
        
        # Default to a random persona if no match found
        return random.choice(PERSONA_DATA)
        
    def population_l1_memory(self, num_entries=15):
        """Populate L1 (short-term analytical memory) with factual entries"""
        logger.info(f"Populating L1 memory with {num_entries} entries...")
        
        # Choose a subset of challenges that map to left hemisphere processing
        left_challenges = [c for c in NEURONAS_DATASET 
                           if any(p["type"] == "left" for p in PERSONA_DATA 
                                  if c["category"] in p["categories"])]
        
        # If we don't have enough left-hemisphere challenges, supplement with others
        if len(left_challenges) < num_entries:
            additional = random.sample([c for c in NEURONAS_DATASET if c not in left_challenges], 
                                      num_entries - len(left_challenges))
            left_challenges.extend(additional)
            
        # Take a random sample if we have more than needed
        if len(left_challenges) > num_entries:
            left_challenges = random.sample(left_challenges, num_entries)
            
        # Store challenges in L1
        for challenge in left_challenges:
            persona = self.get_persona_for_challenge(challenge)
            context = self.generate_context_for_challenge(challenge)
            
            # Analytical memory has structured format
            key = f"fact_{challenge['id']}"
            value = json.dumps({
                "challenge": challenge["challenge"],
                "category": challenge["category"],
                "analytical_frame": f"{persona['name']}'s Perspective: Structured analysis of {challenge['category']} challenge",
                "timestamp": datetime.now().isoformat()
            })
            
            # Importance score based on category match strength
            importance = 0.5
            if persona["type"] == "left":
                importance = random.uniform(0.65, 0.95)
                
            # Store in L1 with context hash
            context_hash = self.memory_manager.generate_context_hash(context)
            self.memory_manager.store_L1(
                key, 
                value, 
                importance=importance,
                context_hash=context_hash
            )
            
            logger.debug(f"Added to L1: {key} with importance {importance:.2f}")
            
        return len(left_challenges)
        
    def populate_r1_memory(self, num_entries=20):
        """Populate R1 (real-time creative adaptation) with novel insights"""
        logger.info(f"Populating R1 memory with {num_entries} entries...")
        
        # Choose a subset of challenges that map to right hemisphere processing
        right_challenges = [c for c in NEURONAS_DATASET 
                            if any(p["type"] == "right" for p in PERSONA_DATA 
                                  if c["category"] in p["categories"])]
        
        # If we don't have enough right-hemisphere challenges, supplement with others
        if len(right_challenges) < num_entries:
            additional = random.sample([c for c in NEURONAS_DATASET if c not in right_challenges], 
                                      num_entries - len(right_challenges))
            right_challenges.extend(additional)
            
        # Take a random sample if we have more than needed
        if len(right_challenges) > num_entries:
            right_challenges = random.sample(right_challenges, num_entries)
            
        # Store challenges in R1
        for challenge in right_challenges:
            persona = self.get_persona_for_challenge(challenge)
            context = self.generate_context_for_challenge(challenge)
            
            # Creative memory has more unstructured, associative format
            key = f"insight_{challenge['id']}"
            value = json.dumps({
                "challenge": challenge["challenge"],
                "category": challenge["category"],
                "creative_insight": f"{persona['name']}'s Insight: Novel perspective on {challenge['category']} through non-linear connections",
                "associations": [random.choice(NEURONAS_DATASET)["category"] for _ in range(3)],
                "timestamp": datetime.now().isoformat()
            })
            
            # Novelty score based on category match strength
            novelty = 0.5
            d2_activation = random.uniform(0.4, 0.9)
            if persona["type"] == "right":
                novelty = random.uniform(0.7, 0.98)
                
            # Store in R1 with context hash
            context_hash = self.memory_manager.generate_context_hash(context)
            self.memory_manager.store_R1(
                key, 
                value, 
                novelty_score=novelty,
                d2_activation=d2_activation, 
                context_hash=context_hash
            )
            
            logger.debug(f"Added to R1: {key} with novelty {novelty:.2f}, D2: {d2_activation:.2f}")
            
        return len(right_challenges)
        
    def run_memory_maintenance(self, cycles=2):
        """Run memory maintenance to promote entries between tiers"""
        logger.info(f"Running {cycles} maintenance cycles...")
        
        for i in range(cycles):
            logger.info(f"Maintenance cycle {i+1}...")
            stats = self.memory_manager.run_memory_maintenance()
            logger.info(f"Maintenance results: {stats}")
            time.sleep(1)  # Brief pause between cycles
            
    def populate_memory_system(self):
        """Main method to populate the entire memory system"""
        logger.info("Starting memory system population...")
        
        # Populate primary memory tiers
        l1_count = self.population_l1_memory(15)
        r1_count = self.populate_r1_memory(20)
        
        logger.info(f"Initial population complete: {l1_count} L1 entries, {r1_count} R1 entries")
        
        # Run maintenance to push to other tiers and create integrations
        self.run_memory_maintenance(3)
        
        # Get final statistics
        stats = self.memory_manager.get_memory_statistics()
        logger.info(f"Memory system population complete. Statistics: {stats}")
        
        return stats

if __name__ == "__main__":
    populator = MemoryPopulator()
    stats = populator.populate_memory_system()
    print(json.dumps(stats, indent=2))