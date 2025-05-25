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
Update routes.py to add the persona display page
"""
from flask import render_template

def add_persona_routes(app):
    """Add persona display routes to the app"""
    
    @app.route('/personas')
    def persona_display():
        """Display cognitive personas visualization page"""
        return render_template('persona_display.html')
        
    return app