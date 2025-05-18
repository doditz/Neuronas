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