from flask import render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
import uuid
import time
from datetime import datetime
from models import User, UserSetting, QueryLog, CognitiveMemory, CognitiveMetrics, db

def register_routes(app):
    """Register all application routes"""
    
    # Ensure session is created for each user
    @app.before_request
    def create_session():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
    
    @app.route('/')
    def index():
        """Main application page"""
        # Détecter les appareils mobiles
        user_agent = request.headers.get('User-Agent', '').lower()
        mobile_agents = ['iphone', 'android', 'mobile', 'samsung', 'lg', 'sony', 'nokia']
        
        # Rediriger vers l'interface mobile si c'est un appareil mobile
        is_mobile = any(agent in user_agent for agent in mobile_agents)
        
        if is_mobile:
            return render_template('mobile.html')
        else:
            return render_template('index.html')
            
    @app.route('/mobile')
    def mobile():
        """Interface mobile duplex"""
        return render_template('mobile.html')
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """System dashboard page"""
        section = request.args.get('section', 'overview')
        
        if section == 'profile':
            # Récupération des paramètres utilisateur
            user_settings = UserSetting.query.filter_by(user_id=current_user.id).all()
            return render_template('dashboard.html', section=section, 
                                  user=current_user, 
                                  user_settings=user_settings)
        
        return render_template('dashboard.html', section=section)
    
    @app.route('/metrics')
    @login_required
    def metrics():
        """Cognitive metrics visualization page"""
        return render_template('metrics.html')
    
    @app.route('/settings')
    @login_required
    def settings():
        """System settings page"""
        return render_template('settings.html')
        
    @app.route('/profile/update', methods=['POST'])
    @login_required
    def update_profile():
        """Mettre à jour le profil utilisateur et les préférences Neuronas"""
        # Mise à jour des paramètres Neuronas
        current_user.d2_temperature = float(request.form.get('d2_temperature', 0.5))
        current_user.hemisphere_balance = float(request.form.get('hemisphere_balance', 0.5))
        current_user.creativity_weight = float(request.form.get('creativity_weight', 0.5))
        current_user.analytical_weight = float(request.form.get('analytical_weight', 0.5))
        
        # Mise à jour des modules spéciaux
        modules = ['QRONAS', 'BRONAS', 'D2Stim', 'D2Pin', 'D2Spin']
        
        for module in modules:
            module_enabled = request.form.get(f'{module}_enabled') == 'on'
            module_weight = float(request.form.get(f'{module}_weight', 0.5))
            
            # Recherche des paramètres existants
            setting_enabled = UserSetting.query.filter_by(
                user_id=current_user.id, 
                module_name=module, 
                setting_key='enabled'
            ).first()
            
            setting_weight = UserSetting.query.filter_by(
                user_id=current_user.id, 
                module_name=module, 
                setting_key='weight'
            ).first()
            
            # Création ou mise à jour des paramètres
            if setting_enabled:
                setting_enabled.setting_value = str(module_enabled)
            else:
                setting_enabled = UserSetting(
                    user_id=current_user.id,
                    module_name=module,
                    setting_key='enabled',
                    setting_value=str(module_enabled)
                )
                db.session.add(setting_enabled)
            
            if setting_weight:
                setting_weight.setting_value = str(module_weight)
            else:
                setting_weight = UserSetting(
                    user_id=current_user.id,
                    module_name=module,
                    setting_key='weight',
                    setting_value=str(module_weight)
                )
                db.session.add(setting_weight)
        
        # Enregistrer les modifications
        db.session.commit()
        
        flash("Vos préférences ont été mises à jour avec succès", "success")
        return redirect(url_for('dashboard', section='profile'))
    
    @app.route('/api/query', methods=['POST'])
    def process_query():
        """Process a cognitive query"""
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Get the session ID
        session_id = session.get('session_id')
        
        # Record start time for performance tracking
        start_time = time.time()
        
        # Process query through gateway interface
        response = app.gateway.process_query(query, session_id)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Log the query
        from models import QueryLog, db
        query_log = QueryLog(
            query=query,
            response=response['response'],
            query_type=response['query_type'],
            hemisphere_used=response['hemisphere_used'],
            processing_time=processing_time,
            d2_activation=response['d2_activation'],
            session_id=session_id
        )
        db.session.add(query_log)
        db.session.commit()
        
        return jsonify(response)
    
    @app.route('/api/metrics', methods=['GET'])
    def get_metrics():
        """Get cognitive metrics data"""
        from models import CognitiveMetrics
        
        # Get session ID
        session_id = session.get('session_id')
        
        # Query metrics for this session
        metrics = CognitiveMetrics.query.filter_by(session_id=session_id).all()
        
        return jsonify({
            'metrics': [metric.to_dict() for metric in metrics]
        })
    
    @app.route('/api/memory', methods=['GET'])
    def get_memory():
        """Get memory data for visualization"""
        hemisphere = request.args.get('hemisphere', 'L')
        tier = request.args.get('tier', 1, type=int)
        
        from models import CognitiveMemory
        
        # Query memory entries
        memories = CognitiveMemory.query.filter_by(
            hemisphere=hemisphere,
            tier=tier
        ).order_by(CognitiveMemory.updated_at.desc()).limit(50).all()
        
        return jsonify({
            'memories': [memory.to_dict() for memory in memories]
        })
    
    @app.route('/api/feedback', methods=['POST'])
    def process_feedback():
        """Process user feedback for reinforcement learning"""
        data = request.json
        hypothesis = data.get('hypothesis')
        feedback = data.get('feedback', 0.0)
        
        if not hypothesis:
            return jsonify({'error': 'Hypothesis is required'}), 400
        
        # Update reinforced hypotheses
        app.cognitive_engine.process_feedback(hypothesis, feedback)
        
        return jsonify({'status': 'success'})
    
    @app.route('/api/system/status', methods=['GET'])
    def system_status():
        """Get current system status"""
        
        # Get current state from cognitive engine
        state = app.cognitive_engine.get_state()
        
        # Get memory stats
        from models import CognitiveMemory
        memory_stats = {
            'L1': CognitiveMemory.query.filter_by(hemisphere='L', tier=1).count(),
            'L2': CognitiveMemory.query.filter_by(hemisphere='L', tier=2).count(),
            'L3': CognitiveMemory.query.filter_by(hemisphere='L', tier=3).count(),
            'R1': CognitiveMemory.query.filter_by(hemisphere='R', tier=1).count(),
            'R2': CognitiveMemory.query.filter_by(hemisphere='R', tier=2).count(),
            'R3': CognitiveMemory.query.filter_by(hemisphere='R', tier=3).count()
        }
        
        return jsonify({
            'state': state,
            'memory_stats': memory_stats,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    return app
