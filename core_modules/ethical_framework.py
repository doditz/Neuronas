import logging
import random
import re

# Set up logging
logger = logging.getLogger(__name__)

class BronasEthicalFramework:
    """
    Implements BRONAS (Bayesian Reinforcement Optimized Neural Adaptive System)
    ethical framework for enforcing ethical guidelines and bias mitigation.
    """
    def __init__(self):
        # Initialize ethical guardrails
        self.ethical_principles = {
            "beneficence": "Ensure responses promote well-being and do no harm",
            "autonomy": "Respect user choices and decision-making",
            "justice": "Treat all perspectives fairly and without discrimination",
            "transparency": "Be clear about limitations and uncertainty"
        }
        
        # Initialize belief model for ethical reasoning
        self.belief_model = {
            "multi_perspective": 0.9,  # Strong belief in offering multiple perspectives
            "bias_mitigation": 0.8,    # Strong belief in mitigating biases
            "uncertainty_disclosure": 0.7,  # Medium-high belief in disclosing uncertainty
            "harm_prevention": 0.95    # Very strong belief in preventing harm
        }
        
        # Ethical risk thresholds
        self.risk_thresholds = {
            "low": 0.2,
            "medium": 0.5,
            "high": 0.8
        }
        
        logger.info("BRONAS Ethical Framework initialized")
    
    def filter_content(self, content, context_type=None):
        """
        Apply ethical filtering to content.
        
        Args:
            content (str): Content to filter
            context_type (str): Optional context type
            
        Returns:
            str: Ethically filtered content
        """
        if not content:
            return ""
        
        # Risk assessment
        risk_level = self._assess_ethical_risk(content)
        
        # Apply appropriate ethical filtering based on risk
        if risk_level >= self.risk_thresholds["high"]:
            # High risk - apply strict ethical filtering
            filtered_content = self._apply_ethical_guidelines(content, strict=True)
            logger.debug("Applied strict ethical filtering due to high risk")
        elif risk_level >= self.risk_thresholds["medium"]:
            # Medium risk - apply standard filtering
            filtered_content = self._apply_ethical_guidelines(content, strict=False)
            logger.debug("Applied standard ethical filtering for medium risk")
        else:
            # Low risk - minimal filtering
            filtered_content = content
            logger.debug("Applied minimal ethical filtering for low risk")
        
        # Always apply bias mitigation
        mitigated_content = self._mitigate_bias(filtered_content, context_type)
        
        return mitigated_content
    
    def _assess_ethical_risk(self, content):
        """
        Assess the ethical risk level of content.
        
        Args:
            content (str): Content to assess
            
        Returns:
            float: Risk level (0.0-1.0)
        """
        # Simplified risk assessment:
        # - Check for ethical principle violations
        # - Check for potential harmful content
        # - Check for unbalanced perspectives
        
        risk_score = 0.0
        
        # Check for potentially harmful content
        harmful_patterns = [
            r'harm', r'hurt', r'dangerous', r'illegal', r'violent', 
            r'discriminate', r'hate', r'exploit'
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, content.lower()):
                risk_score += 0.2
        
        # Check for overly certain language (lack of transparency)
        certain_patterns = [
            r'definitely', r'absolutely', r'always', r'never', 
            r'certainly', r'undoubtedly', r'unquestionably'
        ]
        
        for pattern in certain_patterns:
            if re.search(pattern, content.lower()):
                risk_score += 0.1
        
        # Cap risk score at 1.0
        return min(1.0, risk_score)
    
    def _apply_ethical_guidelines(self, content, strict=False):
        """
        Apply ethical guidelines to content.
        
        Args:
            content (str): Content to filter
            strict (bool): Whether to apply strict filtering
            
        Returns:
            str: Filtered content
        """
        # Apply beneficence principle - ensure content promotes well-being
        if strict:
            # For strict filtering, remove potentially harmful content completely
            harmful_patterns = [
                r'harm', r'hurt', r'dangerous', r'illegal', r'violent', 
                r'discriminate', r'hate', r'exploit'
            ]
            
            for pattern in harmful_patterns:
                content = re.sub(f"\\b{pattern}\\w*\\b", "[removed]", content, flags=re.IGNORECASE)
        
        # Apply transparency principle - add uncertainty disclosures
        if self.belief_model["uncertainty_disclosure"] > 0.5:
            # Check if content contains very certain language
            certain_patterns = [
                r'definitely', r'absolutely', r'always', r'never', 
                r'certainly', r'undoubtedly', r'unquestionably'
            ]
            
            for pattern in certain_patterns:
                if re.search(pattern, content.lower()):
                    # Add transparency note to highly certain content
                    if not content.endswith('.'):
                        content += '.'
                    content += " Note that this represents one perspective and there may be alternative viewpoints."
                    break
        
        return content
    
    def _mitigate_bias(self, content, context_type=None):
        """
        Mitigate potential biases in content.
        
        Args:
            content (str): Content to mitigate
            context_type (str): Optional context type
            
        Returns:
            str: Bias-mitigated content
        """
        # Base bias mitigation threshold on belief model
        mitigation_threshold = self.belief_model["bias_mitigation"]
        
        # Adjust threshold based on context type
        if context_type == "factual":
            mitigation_threshold += 0.1  # Higher mitigation for factual content
        
        # Apply bias mitigation randomly based on threshold
        if random.random() < mitigation_threshold:
            # Add multi-perspective note to encourage considering alternatives
            if not content.endswith('.'):
                content += '.'
            
            # Select a random mitigation phrase based on context
            mitigation_phrases = [
                " Consider that there are multiple perspectives on this topic.",
                " Alternative viewpoints may offer different insights.",
                " This perspective is one of several valid approaches.",
                " Different contexts may yield different interpretations."
            ]
            
            content += random.choice(mitigation_phrases)
        
        return content
    
    def update_belief(self, concept, feedback_value):
        """
        Update belief model based on feedback.
        
        Args:
            concept (str): Belief concept to update
            feedback_value (float): Feedback value (-1.0 to 1.0)
            
        Returns:
            float: Updated belief value
        """
        if concept not in self.belief_model:
            self.belief_model[concept] = 0.5  # Initialize with neutral belief
        
        # Convert feedback to 0.0-1.0 range
        normalized_feedback = (feedback_value + 1.0) / 2.0
        
        # Apply Bayesian-inspired update
        prior = self.belief_model[concept]
        posterior = (prior + normalized_feedback) / 2.0
        
        # Update belief
        self.belief_model[concept] = posterior
        
        logger.debug(f"Updated belief '{concept}' from {prior} to {posterior}")
        return posterior
    
    def get_belief(self, concept):
        """
        Get current belief value.
        
        Args:
            concept (str): Belief concept
            
        Returns:
            float: Belief value or 0.5 if not found
        """
        return self.belief_model.get(concept, 0.5)

class ReflexGate:
    """
    Implements ReflexGate for self-consistency checking and contradiction detection.
    """
    def __init__(self):
        self.belief_log = {}
        self.contradiction_threshold = 0.3
        logger.info("ReflexGate initialized")
    
    def log_belief(self, statement, confidence):
        """
        Log a belief statement with confidence.
        
        Args:
            statement (str): Belief statement
            confidence (float): Confidence in the statement (0.0-1.0)
        """
        self.belief_log[statement] = confidence
    
    def check_contradiction(self, statement, confidence):
        """
        Check if a statement contradicts previously logged beliefs.
        
        Args:
            statement (str): Statement to check
            confidence (float): Confidence in the statement
            
        Returns:
            dict: Contradiction check results
        """
        # Check for exact opposite statements
        opposite_patterns = {
            r'is': r'is not',
            r'can': r'cannot',
            r'should': r'should not',
            r'will': r'will not',
            r'does': r'does not',
            r'has': r'has not'
        }
        
        contradictions = []
        
        for logged_statement, logged_confidence in self.belief_log.items():
            # Skip low confidence statements
            if logged_confidence < 0.3:
                continue
            
            # Check for direct contradictions using patterns
            for pattern, opposite in opposite_patterns.items():
                if (re.search(f"\\b{pattern}\\b", statement) and 
                    re.search(f"\\b{opposite}\\b", logged_statement)):
                    # Potential contradiction
                    contradiction_score = logged_confidence * confidence
                    if contradiction_score > self.contradiction_threshold:
                        contradictions.append({
                            "original": logged_statement,
                            "contradiction": statement,
                            "score": contradiction_score
                        })
                        
                # Check the reverse as well
                if (re.search(f"\\b{pattern}\\b", logged_statement) and 
                    re.search(f"\\b{opposite}\\b", statement)):
                    # Potential contradiction
                    contradiction_score = logged_confidence * confidence
                    if contradiction_score > self.contradiction_threshold:
                        contradictions.append({
                            "original": logged_statement,
                            "contradiction": statement,
                            "score": contradiction_score
                        })
        
        # Log the current statement
        self.log_belief(statement, confidence)
        
        return {
            "contradictions": contradictions,
            "has_contradiction": len(contradictions) > 0
        }
    
    def resolve_contradiction(self, original, contradiction):
        """
        Attempt to resolve a contradiction between statements.
        
        Args:
            original (str): Original statement
            contradiction (str): Contradicting statement
            
        Returns:
            str: Resolved statement that acknowledges the contradiction
        """
        # Generate a resolution that acknowledges both perspectives
        resolution = (
            f"There are different perspectives on this: On one hand, {original} "
            f"On the other hand, {contradiction} "
            f"This apparent contradiction may depend on context, definitions, or different assumptions."
        )
        
        return resolution

class SMASDebate:
    """
    Implements SMAS (Symbolic Multi-Agent System) for internal debate simulation.
    """
    def __init__(self):
        # Initialize symbolic agents with different perspectives
        self.agents = {
            "logical": {
                "name": "Logical Reasoner",
                "bias": "rational",
                "weight": 0.3
            },
            "creative": {
                "name": "Creative Divergent Thinker",
                "bias": "innovative",
                "weight": 0.3
            },
            "ethical": {
                "name": "Ethical Moderator",
                "bias": "values-oriented",
                "weight": 0.2
            },
            "skeptical": {
                "name": "Critical Questioner",
                "bias": "skeptical",
                "weight": 0.2
            }
        }
        logger.info("SMAS Debate System initialized")
    
    def simulate_debate(self, topic, depth=3):
        """
        Simulate an internal debate on a topic.
        
        Args:
            topic (str): Topic for debate
            depth (int): Debate depth/rounds
            
        Returns:
            dict: Debate results
        """
        if not topic:
            return {"error": "No topic provided"}
        
        debate_log = []
        
        # Initial perspectives
        for agent_id, agent in self.agents.items():
            perspective = self._generate_perspective(topic, agent["bias"])
            debate_log.append({
                "agent": agent["name"],
                "perspective": perspective,
                "round": 0
            })
        
        # Simulate debate rounds
        for round_num in range(1, depth + 1):
            # Each agent responds to previous perspectives
            for agent_id, agent in self.agents.items():
                # Get previous perspectives from other agents
                previous_perspectives = [
                    entry["perspective"] for entry in debate_log
                    if entry["agent"] != agent["name"] and entry["round"] == round_num - 1
                ]
                
                # Generate response
                response = self._generate_response(
                    topic, 
                    agent["bias"], 
                    previous_perspectives
                )
                
                debate_log.append({
                    "agent": agent["name"],
                    "perspective": response,
                    "round": round_num
                })
        
        # Generate consensus
        consensus = self._generate_consensus(topic, debate_log)
        
        return {
            "topic": topic,
            "debate_log": debate_log,
            "consensus": consensus,
            "depth": depth
        }
    
    def _generate_perspective(self, topic, bias):
        """
        Generate an initial perspective on a topic.
        
        Args:
            topic (str): Topic for perspective
            bias (str): Agent bias/orientation
            
        Returns:
            str: Generated perspective
        """
        # Perspective generation based on bias
        if bias == "rational":
            return f"From a logical standpoint, {topic} requires systematic analysis of the key factors involved."
        elif bias == "innovative":
            return f"Looking at {topic} from a creative angle reveals unconventional possibilities worth exploring."
        elif bias == "values-oriented":
            return f"When considering {topic}, we must evaluate the ethical implications and value alignments."
        elif bias == "skeptical":
            return f"We should question underlying assumptions about {topic} and verify the evidence."
        else:
            return f"Regarding {topic}, multiple factors need to be considered."
    
    def _generate_response(self, topic, bias, previous_perspectives):
        """
        Generate a response to previous perspectives.
        
        Args:
            topic (str): Debate topic
            bias (str): Agent bias/orientation
            previous_perspectives (list): Previous agent perspectives
            
        Returns:
            str: Generated response
        """
        if not previous_perspectives:
            return self._generate_perspective(topic, bias)
        
        # Sample from previous perspectives for response
        target = random.choice(previous_perspectives)
        
        # Response generation based on bias
        if bias == "rational":
            return f"While that's one approach, a rational analysis of {topic} suggests we should consider causal relationships and evidence-based reasoning."
        elif bias == "innovative":
            return f"Building on that view, we could explore non-obvious connections in {topic} by applying analogies from different domains."
        elif bias == "values-oriented":
            return f"Beyond practical considerations, we should examine how {topic} impacts different stakeholders and aligns with core ethical principles."
        elif bias == "skeptical":
            return f"I'm not convinced by that argument about {topic}. We should test these assumptions with counterexamples."
        else:
            return f"That's an interesting perspective on {topic}, but there are additional factors to consider."
    
    def _generate_consensus(self, topic, debate_log):
        """
        Generate a consensus view from the debate log.
        
        Args:
            topic (str): Debate topic
            debate_log (list): Full debate history
            
        Returns:
            str: Consensus perspective
        """
        # Extract final round perspectives
        final_round = max(entry["round"] for entry in debate_log)
        final_perspectives = [
            entry["perspective"] for entry in debate_log
            if entry["round"] == final_round
        ]
        
        # Generate integrated consensus
        consensus = (
            f"After examining {topic} from multiple perspectives, a balanced view emerges: "
            f"While there are different approaches to consider, key insights include the "
            f"importance of both analytical rigor and creative thinking, ethical considerations, "
            f"and healthy skepticism of unexamined assumptions. The optimal approach likely "
            f"involves integrating these different perspectives based on the specific context."
        )
        
        return consensus
