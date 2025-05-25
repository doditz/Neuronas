"""
Geolocation Service for NeuronasX

This module provides geolocation capabilities for NeuronasX to adapt responses
based on the user's cultural context and location, respecting differences
between users from different regions around the world.
"""

import logging
import json
import os
import requests
from datetime import datetime
from flask import request
from sqlalchemy import func
from models import db, User, QueryLog

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class GeolocationService:
    """
    Service for determining user location and providing cultural context
    for personalized responses that respect regional differences.
    """
    
    def __init__(self, db_instance=None):
        """Initialize the geolocation service"""
        self.db = db_instance if db_instance else db
        self._load_cultural_context_data()
        
    def _load_cultural_context_data(self):
        """Load cultural context data for different regions"""
        # Cultural context profiles for different regions
        self.cultural_contexts = {
            # East Asian contexts
            "JP": {  # Japan
                "name": "Japan",
                "language_preference": "ja",
                "formality_level": 0.85,  # High formality
                "collectivism_index": 0.85,  # Group-oriented
                "context_communication": 0.90,  # High-context communication
                "honorifics_important": True,
                "key_values": ["harmony", "respect", "hierarchy", "indirect communication", "group consensus"],
                "communication_style": "indirect, modest, emphasizes harmony",
                "time_orientation": "long-term",
                "response_adaptation": {
                    "tone": "respectful, formal",
                    "directness": "less direct, more nuanced",
                    "examples": "use culturally relevant examples (e.g., seasons, nature references)",
                    "language": "consider using appropriate levels of formality and honorifics"
                }
            },
            "CN": {  # China
                "name": "China",
                "language_preference": "zh",
                "formality_level": 0.80,
                "collectivism_index": 0.90,
                "context_communication": 0.85,
                "honorifics_important": True,
                "key_values": ["family", "respect for authority", "harmony", "face", "hierarchy"],
                "communication_style": "indirect, contextual, relationship-focused",
                "time_orientation": "long-term",
                "response_adaptation": {
                    "tone": "respectful, acknowledging hierarchy",
                    "directness": "less direct, contextual",
                    "examples": "use culturally relevant examples",
                    "language": "consider appropriate formality"
                }
            },
            "KR": {  # South Korea
                "name": "South Korea",
                "language_preference": "ko",
                "formality_level": 0.85,
                "collectivism_index": 0.85,
                "context_communication": 0.85,
                "honorifics_important": True,
                "key_values": ["harmony", "respect", "age hierarchy", "group identity", "education"],
                "communication_style": "indirect, contextual, hierarchical",
                "time_orientation": "long-term",
                "response_adaptation": {
                    "tone": "respectful, age-appropriate",
                    "directness": "contextual, relationship-aware",
                    "examples": "use culturally relevant examples",
                    "language": "consider appropriate honorifics"
                }
            },
            
            # Western contexts
            "US": {  # United States
                "name": "United States",
                "language_preference": "en",
                "formality_level": 0.40,  # Less formal
                "collectivism_index": 0.20,  # Individualistic
                "context_communication": 0.30,  # Low-context communication
                "honorifics_important": False,
                "key_values": ["individualism", "directness", "equality", "efficiency", "innovation"],
                "communication_style": "direct, explicit, task-oriented",
                "time_orientation": "short-term",
                "response_adaptation": {
                    "tone": "friendly, casual, direct",
                    "directness": "straightforward, explicit",
                    "examples": "use practical, efficiency-focused examples",
                    "language": "casual, concise, straightforward"
                }
            },
            "GB": {  # United Kingdom
                "name": "United Kingdom",
                "language_preference": "en",
                "formality_level": 0.60,
                "collectivism_index": 0.35,
                "context_communication": 0.50,
                "honorifics_important": False,
                "key_values": ["politeness", "privacy", "fairness", "moderation", "tradition"],
                "communication_style": "polite, indirect, understated",
                "time_orientation": "balanced",
                "response_adaptation": {
                    "tone": "polite, measured, sometimes understated",
                    "directness": "moderately indirect, uses understatement",
                    "examples": "consider tradition and history in examples",
                    "language": "polite, may use dry humor"
                }
            },
            "DE": {  # Germany
                "name": "Germany",
                "language_preference": "de",
                "formality_level": 0.75,
                "collectivism_index": 0.40,
                "context_communication": 0.40,
                "honorifics_important": True,
                "key_values": ["order", "precision", "directness", "privacy", "punctuality"],
                "communication_style": "direct, detailed, fact-oriented",
                "time_orientation": "long-term",
                "response_adaptation": {
                    "tone": "factual, structured",
                    "directness": "very direct, fact-focused",
                    "examples": "use precise, detailed examples",
                    "language": "formal, structured, thorough"
                }
            },
            
            # Latin American contexts
            "MX": {  # Mexico
                "name": "Mexico",
                "language_preference": "es",
                "formality_level": 0.65,
                "collectivism_index": 0.75,
                "context_communication": 0.70,
                "honorifics_important": True,
                "key_values": ["family", "respect", "relationships", "warmth", "hierarchy"],
                "communication_style": "warm, relationship-oriented, indirect",
                "time_orientation": "present-focused",
                "response_adaptation": {
                    "tone": "warm, personal, expressive",
                    "directness": "relationship-focused, warm",
                    "examples": "include family or community themes",
                    "language": "warm, personable, expressive"
                }
            },
            "BR": {  # Brazil
                "name": "Brazil",
                "language_preference": "pt",
                "formality_level": 0.60,
                "collectivism_index": 0.70,
                "context_communication": 0.65,
                "honorifics_important": True,
                "key_values": ["relationships", "flexibility", "joy", "creativity", "warmth"],
                "communication_style": "warm, relationship-oriented, expressive",
                "time_orientation": "present-focused",
                "response_adaptation": {
                    "tone": "warm, optimistic, expressive",
                    "directness": "flexible, relationship-focused",
                    "examples": "creative, socially relevant examples",
                    "language": "warm, vibrant, adaptable"
                }
            },
            
            # Middle Eastern contexts
            "AE": {  # United Arab Emirates
                "name": "United Arab Emirates",
                "language_preference": "ar",
                "formality_level": 0.80,
                "collectivism_index": 0.85,
                "context_communication": 0.75,
                "honorifics_important": True,
                "key_values": ["respect", "hospitality", "honor", "relationships", "family"],
                "communication_style": "formal, relationship-oriented, contextual",
                "time_orientation": "flexible",
                "response_adaptation": {
                    "tone": "respectful, formal",
                    "directness": "contextual, relationship-focused",
                    "examples": "respect cultural sensitivities",
                    "language": "formal, respectful"
                }
            },
            
            # African contexts
            "NG": {  # Nigeria
                "name": "Nigeria",
                "language_preference": "en",
                "formality_level": 0.70,
                "collectivism_index": 0.80,
                "context_communication": 0.70,
                "honorifics_important": True,
                "key_values": ["respect for elders", "community", "family", "spirituality", "resilience"],
                "communication_style": "respectful, storytelling, relationship-oriented",
                "time_orientation": "flexible",
                "response_adaptation": {
                    "tone": "respectful, community-oriented",
                    "directness": "narrative, contextual",
                    "examples": "include community or family themes",
                    "language": "respectful, expressive"
                }
            },
            
            # South Asian contexts
            "IN": {  # India
                "name": "India",
                "language_preference": "en",  # Many languages, but often uses English
                "formality_level": 0.75,
                "collectivism_index": 0.80,
                "context_communication": 0.75,
                "honorifics_important": True,
                "key_values": ["family", "respect", "spirituality", "hierarchy", "pluralism"],
                "communication_style": "indirect, contextual, relationship-oriented",
                "time_orientation": "cyclical",
                "response_adaptation": {
                    "tone": "respectful, contextual",
                    "directness": "moderate, relationship-aware",
                    "examples": "diverse, context-sensitive examples",
                    "language": "respectful, acknowledging diversity"
                }
            },
            
            # Default context (used when location is unknown)
            "DEFAULT": {
                "name": "Global",
                "language_preference": "en",
                "formality_level": 0.60,
                "collectivism_index": 0.50,
                "context_communication": 0.50,
                "honorifics_important": False,
                "key_values": ["respect", "clarity", "adaptability", "inclusivity", "balance"],
                "communication_style": "balanced, adaptable, inclusive",
                "time_orientation": "balanced",
                "response_adaptation": {
                    "tone": "balanced, adaptable",
                    "directness": "moderately direct, clear",
                    "examples": "globally relevant examples",
                    "language": "clear, inclusive, adaptable"
                }
            }
        }
        
    def get_location_from_ip(self, ip_address=None):
        """
        Get location information from IP address
        
        Args:
            ip_address (str, optional): IP address to geolocate
            
        Returns:
            dict: Location information
        """
        # Get IP address from request if not provided
        if not ip_address:
            ip_address = self._get_client_ip()
            
        # Don't try to geolocate private IPs
        if self._is_private_ip(ip_address):
            logger.info(f"Not attempting to geolocate private IP: {ip_address}")
            return {
                "success": False,
                "country_code": "DEFAULT",
                "country_name": "Unknown",
                "region": "Unknown",
                "city": "Unknown",
                "latitude": 0,
                "longitude": 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        try:
            # For the free and open-source approach, we'll use the ipapi.co service
            # This has generous free limits and doesn't require an API key
            response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" in data:
                    logger.warning(f"Error in IP geolocation: {data['error']}")
                    return {
                        "success": False,
                        "country_code": "DEFAULT",
                        "country_name": "Unknown",
                        "region": "Unknown",
                        "city": "Unknown",
                        "latitude": 0,
                        "longitude": 0,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                return {
                    "success": True,
                    "country_code": data.get("country_code", "DEFAULT"),
                    "country_name": data.get("country_name", "Unknown"),
                    "region": data.get("region", "Unknown"),
                    "city": data.get("city", "Unknown"),
                    "latitude": data.get("latitude", 0),
                    "longitude": data.get("longitude", 0),
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                logger.warning(f"Failed to get location for IP {ip_address}: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error getting location from IP: {e}")
            
        # Return default if geolocation fails
        return {
            "success": False,
            "country_code": "DEFAULT",
            "country_name": "Unknown",
            "region": "Unknown",
            "city": "Unknown",
            "latitude": 0,
            "longitude": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def _get_client_ip(self):
        """Get client IP address from request"""
        # Check various headers for forwarded IP
        if request:
            headers_to_check = [
                'X-Forwarded-For', 
                'X-Real-IP', 
                'CF-Connecting-IP',  # Cloudflare
                'True-Client-IP'
            ]
            
            for header in headers_to_check:
                if header in request.headers:
                    # X-Forwarded-For can contain multiple IPs; get the first one
                    ip = request.headers[header].split(',')[0].strip()
                    if ip:
                        return ip
                        
            # Fall back to remote_addr
            return request.remote_addr or "127.0.0.1"
        
        return "127.0.0.1"
        
    def _is_private_ip(self, ip):
        """Check if IP address is private"""
        # Simple check for common private IP ranges
        if not ip or ip == "127.0.0.1":
            return True
            
        private_prefixes = [
            "10.", "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
            "172.21.", "172.22.", "172.23.", "172.24.", "172.25.", "172.26.",
            "172.27.", "172.28.", "172.29.", "172.30.", "172.31.", "192.168.",
            "127.", "0.", "localhost"
        ]
        
        return any(ip.startswith(prefix) for prefix in private_prefixes)
        
    def get_cultural_context(self, country_code=None, default_code="DEFAULT"):
        """
        Get cultural context for a country
        
        Args:
            country_code (str, optional): ISO country code
            default_code (str): Default country code if not found
            
        Returns:
            dict: Cultural context information
        """
        if not country_code:
            # Get location from IP
            location = self.get_location_from_ip()
            country_code = location.get("country_code", default_code)
            
        # Normalize country code
        if country_code:
            country_code = country_code.upper()
            
        # Get cultural context
        context = self.cultural_contexts.get(country_code)
        
        # Fall back to default if not found
        if not context:
            context = self.cultural_contexts.get(default_code)
            
        return {
            "country_code": country_code,
            "context": context
        }
        
    def adapt_response(self, response, country_code=None):
        """
        Adapt a response based on cultural context
        
        Args:
            response (str): Original response
            country_code (str, optional): ISO country code
            
        Returns:
            dict: Adapted response with cultural context
        """
        # Get cultural context
        cultural_data = self.get_cultural_context(country_code)
        context = cultural_data["context"]
        country_code = cultural_data["country_code"]
        
        # For now, we'll just return the original response with the cultural context
        # In a production system, you would implement actual response adaptation
        # based on the cultural context
        
        return {
            "original_response": response,
            "adapted_response": response,  # In future versions, this would be adapted
            "country_code": country_code,
            "cultural_context": {
                "name": context.get("name"),
                "language_preference": context.get("language_preference"),
                "formality_level": context.get("formality_level"),
                "communication_style": context.get("communication_style")
            },
            "adaptation_applied": False,  # True when adaptation is implemented
            "timestamp": datetime.utcnow().isoformat()
        }
        
    def get_statistics(self):
        """Get statistics about geolocation usage"""
        try:
            # This would track geolocation statistics in a production system
            # For now, we'll return placeholder statistics
            return {
                "total_geolocations": 0,
                "countries_served": {},
                "adaptation_rate": 0
            }
        except Exception as e:
            logger.error(f"Error getting geolocation statistics: {e}")
            return {
                "total_geolocations": 0,
                "countries_served": {},
                "adaptation_rate": 0
            }