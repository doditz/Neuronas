from flask import render_template, request, jsonify, session
import uuid
import time
from datetime import datetime

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
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """System dashboard page"""
        return render_template('dashboard.html')
    
    @app.route('/metrics')
    def metrics():
        """Cognitive metrics visualization page"""
        return render_template('metrics.html')
    
    @app.route('/settings')
    def settings():
        """System settings page"""
        return render_template('settings.html')
    
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
