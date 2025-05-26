"""
This work is licensed under CC BY-NC 4.0 International.
Commercial use requires prior written consent and compensation.
Contact: sebastienbrulotte@gmail.com
Attribution: Sebastien Brulotte aka [ Doditz ]

This document is part of the NEURONAS cognitive system.
Core modules referenced: BRONAS (Ethical Reflex Filter) and QRONAS (Probabilistic Symbolic Vector Engine).
All outputs are subject to integrity validation and ethical compliance enforced by BRONAS.
"""


# Add import at the top of the file
from core_modules.cognitive_processing import CognitiveProcessor

# Initialize the cognitive processor
cognitive_processor = CognitiveProcessor()

from flask import render_template, request, jsonify, session, redirect, url_for, flash
from flask_login import login_required, current_user
import uuid
import time
from datetime import datetime
from models import User, UserSetting, QueryLog, CognitiveMemory, CognitiveMetrics, db

def register_routes(app):
    """Register all application routes"""

    # Check if routes are already registered to prevent duplicates
    if hasattr(app, '_routes_registered'):
        return

    # Import SMS service
    from sms_service import send_sms
    from models import SMSNotification

    # Ensure session is created for each user
    @app.before_request
    def create_session():
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())

    @app.route('/')
    def index():
        """Main application page with intelligent device detection"""
        # Show landing page for non-authenticated users
        if not current_user.is_authenticated:
            return render_template('landing.html')

        # Enhanced mobile device detection
        user_agent = request.headers.get('User-Agent', '').lower()

        # Comprehensive mobile detection patterns
        mobile_patterns = [
            'mobile', 'android', 'iphone', 'ipod', 'blackberry', 'windows phone',
            'samsung', 'lg', 'htc', 'sony', 'nokia', 'motorola', 'huawei', 'xiaomi',
            'webos', 'opera mini', 'opera mobi', 'fennec', 'iemobile', 'silk',
            'kindle', 'phone', 'tablet', 'pad'
        ]

        # Check for mobile indicators
        is_mobile = any(pattern in user_agent for pattern in mobile_patterns)

        # Also check screen width via JavaScript if available (for responsive design)
        # Force mobile version if explicitly requested
        force_mobile = request.args.get('mobile', '').lower() == 'true'
        force_desktop = request.args.get('desktop', '').lower() == 'true'

        if force_mobile or (is_mobile and not force_desktop):
            return render_template('responsive_mobile.html')
        else:
            return render_template('index.html')

    @app.route('/login')
    def login_page():
        """Login page with authentication options"""
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        # Redirect to Replit auth
        return redirect(url_for('replit_auth.login'))

    @app.route('/mobile')
    def mobile():
        """Interface mobile duplex"""
        return render_template('mobile.html')

    @app.route('/thinking')
    def thinking_process():
        return render_template('thinking_process.html')

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

    @app.route('/tiered-memory')
    @login_required
    def tiered_memory_page():
        """Tiered memory system visualization and management"""
        return render_template('tiered_memory.html')

    @app.route('/personas')
    @login_required
    def personas_page():
        """Cognitive personas visualization page"""
        return render_template('persona_display.html')

    @app.route('/dual-llm')
    @login_required
    def dual_llm_page():
        """Dual hemispheric LLM system page"""
        return render_template('dual_llm.html')

    @app.route('/agent-positioning')
    def agent_positioning_page():
        """Agent positioning system interface"""
        return render_template('agent_positioning.html')

    @app.route('/profile/update', methods=['POST'])
    @login_required
    def update_profile():
        """Mettre à jour le profil utilisateur et les préférences Neuronas"""
        # Mise à jour des paramètres Neuronas
        def safe_float(value, default=0.5):
            """Convert input to float safely, preventing NaN injection"""
            if isinstance(value, str) and value.lower() == 'nan':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        current_user.d2_temperature = safe_float(request.form.get('d2_temperature', 0.5))
        current_user.hemisphere_balance = safe_float(request.form.get('hemisphere_balance', 0.5))
        current_user.creativity_weight = safe_float(request.form.get('creativity_weight', 0.5))
        current_user.analytical_weight = safe_float(request.form.get('analytical_weight', 0.5))

        # Mise à jour des modules spéciaux
        modules = ['QRONAS', 'BRONAS', 'D2Stim', 'D2Pin', 'D2Spin']

        for module in modules:
            module_enabled = request.form.get(f'{module}_enabled') == 'on'
            module_weight = safe_float(request.form.get(f'{module}_weight', 0.5))

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

    # Add these routes to the existing routes.py file
    @app.route('/api/cognitive/process', methods=['POST'])
    def process_cognitive():
        """
        Process a query through the 5-lobe cognitive model
        """
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query parameter'}), 400

        query = data['query']
        context = data.get('context', {})

        try:
            result = cognitive_processor.process_query(query, context)
            return jsonify({
                'success': True,
                'result': result,
                'processing_time': result['processing_time']
            })
        except Exception as e:
            app.logger.error(f"Error in cognitive processing: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    @app.route('/api/cognitive/history', methods=['GET'])
    def get_cognitive_history():
        """
        Get cognitive processing history
        """
        try:
            return jsonify({
                'success': True,
                'history': cognitive_processor.processing_history
            })
        except Exception as e:
            app.logger.error(f"Error fetching cognitive history: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    # Add the route for the cognitive processing page
    @app.route('/cognitive')
    def cognitive_page():
        """
        Render cognitive processing visualization page
        """
        return render_template('cognitive_processing.html')

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
        try:
            # Get current state from cognitive engine
            state = app.cognitive_engine.get_state()

            # Get memory stats from tiered memory system
            try:
                # Try to get stats from the new tiered memory system
                if hasattr(app, 'tiered_memory'):
                    memory_stats = app.tiered_memory.get_statistics()
                    memory_stats = {
                        'L1': memory_stats['left']['1'],
                        'L2': memory_stats['left']['2'],
                        'L3': memory_stats['left']['3'],
                        'R1': memory_stats['right']['1'],
                        'R2': memory_stats['right']['2'],
                        'R3': memory_stats['right']['3']
                    }
                else:
                    # Fallback to old memory stats
                    from models import CognitiveMemory
                    memory_stats = {
                        'L1': CognitiveMemory.query.filter_by(hemisphere='L', tier=1).count(),
                        'L2': CognitiveMemory.query.filter_by(hemisphere='L', tier=2).count(),
                        'L3': CognitiveMemory.query.filter_by(hemisphere='L', tier=3).count(),
                        'R1': CognitiveMemory.query.filter_by(hemisphere='R', tier=1).count(),
                        'R2': CognitiveMemory.query.filter_by(hemisphere='R', tier=2).count(),
                        'R3': CognitiveMemory.query.filter_by(hemisphere='R', tier=3).count()
                    }
            except Exception as e:
                app.logger.error(f"Error getting memory stats: {e}")
                memory_stats = {
                    'L1': 0, 'L2': 0, 'L3': 0,
                    'R1': 0, 'R2': 0, 'R3': 0
                }

            return jsonify({
                'state': state,
                'memory_stats': memory_stats,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Error in system status: {e}")
            # Return a safe default state
            return jsonify({
                'state': {
                    'focus': 0.5,
                    'activation': {'left_hemisphere': 0.5, 'right_hemisphere': 0.5},
                    'mode': 'balanced'
                },
                'memory_stats': {'L1': 0, 'L2': 0, 'L3': 0, 'R1': 0, 'R2': 0, 'R3': 0},
                'timestamp': datetime.utcnow().isoformat()
            })

    @app.route('/api/sms/send', methods=['POST'])
    @login_required
    def send_sms_message():
        """Send SMS notification"""
        data = request.json
        phone_number = data.get('phone_number')
        message = data.get('message')

        # Validate input
        if not phone_number:
            return jsonify({'success': False, 'error': 'Phone number is required'}), 400
        if not message:
            return jsonify({'success': False, 'error': 'Message content is required'}), 400

        # Validate phone number format (basic E.164 format validation)
        if not phone_number.startswith('+') or not phone_number[1:].isdigit():
            return jsonify({'success': False, 'error': 'Phone number must be in E.164 format (e.g., +15551234567)'}), 400

        # Send SMS via Twilio
        result = send_sms(phone_number, message)

        # Store notification in database
        notification = SMSNotification(
            phone_number=phone_number,
            message=message,
            status='sent' if result.get('success') else 'failed',
            message_sid=result.get('message_sid'),
            error_message=result.get('error'),
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(notification)
        db.session.commit()

        if not result.get('success'):
            return jsonify({'success': False, 'error': result.get('error')}), 500

        return jsonify({'success': True, 'message_sid': result.get('message_sid')})

    @app.route('/api/sms/history', methods=['GET'])
    @login_required
    def get_sms_history():
        """Get SMS notification history for the current user"""
        # Get history for current user
        notifications = SMSNotification.query.filter_by(user_id=current_user.id).order_by(
            SMSNotification.created_at.desc()
        ).limit(50).all()

        return jsonify({
            'notifications': [notification.to_dict() for notification in notifications]
        })

    @app.route('/notifications', methods=['GET'])
    @login_required
    def notifications_page():
        """SMS Notifications management page"""
        return render_template('notifications.html')

    # Mark routes as registered to prevent duplicates
    app._routes_registered = True

    return app