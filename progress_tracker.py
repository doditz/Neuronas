"""
Progress Tracker for NeuronasX

This module implements a comprehensive logging and progress tracking system
for NeuronasX, providing detailed records of changes, development milestones,
and a visual roadmap workflow.
"""

import logging
import json
import uuid
import time
from datetime import datetime, timedelta
import os
import threading
from enum import Enum
from sqlalchemy import func, desc
from models import db

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ChangeType(Enum):
    """Types of changes that can be tracked"""
    FEATURE_ADDED = "feature_added"
    BUG_FIXED = "bug_fixed"
    ENHANCEMENT = "enhancement"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    CONFIGURATION = "configuration"
    INTEGRATION = "integration"
    SECURITY = "security"
    DATABASE = "database"
    UI_UX = "ui_ux"
    OTHER = "other"

class MilestoneStatus(Enum):
    """Status of development milestones"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"

class SystemComponent(Enum):
    """Main system components"""
    CORE = "core"
    UI = "ui"
    DATABASE = "database"
    API = "api"
    INTEGRATION = "integration"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    DEPLOYMENT = "deployment"
    TESTING = "testing"
    MEMORY = "memory"
    LEFT_HEMISPHERE = "left_hemisphere"
    RIGHT_HEMISPHERE = "right_hemisphere"
    BRONAS = "bronas"
    QRONAS = "qronas"
    SMAS = "smas"
    D2_MECHANISM = "d2_mechanism"
    GEOLOCATION = "geolocation"
    OTHER = "other"

class ProgressTracker:
    """
    Tracks development progress, logs changes, and visualizes the roadmap
    for the NeuronasX project.
    """
    
    def __init__(self, db_instance=None, log_file=None):
        """
        Initialize the progress tracker
        
        Args:
            db_instance: Database instance
            log_file (str, optional): Path to log file
        """
        self.db = db_instance if db_instance else db
        
        # Set up log file
        self.log_file = log_file if log_file else "neuronas_development.log"
        
        # Internal tracking
        self.changes = []
        self.milestones = []
        self.roadmap = {}
        
        # Load existing data
        self._load_data()
        
    def _load_data(self):
        """Load existing progress data"""
        try:
            # Try to load from database first
            # (Placeholder for database implementation)
            
            # If not in database, try to load from file
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    self.changes = data.get('changes', [])
                    self.milestones = data.get('milestones', [])
                    self.roadmap = data.get('roadmap', {})
            else:
                # Initialize with default roadmap
                self._initialize_default_roadmap()
        except Exception as e:
            logger.error(f"Error loading progress data: {e}")
            # Initialize with default roadmap
            self._initialize_default_roadmap()
            
    def _initialize_default_roadmap(self):
        """Initialize default roadmap for NeuronasX"""
        self.roadmap = {
            "name": "NeuronasX Development Roadmap",
            "description": "Bio-inspired dual-hemisphere cognitive system",
            "version": "3.0",
            "phases": [
                {
                    "id": "phase1",
                    "name": "Foundation",
                    "status": MilestoneStatus.COMPLETED.value,
                    "start_date": "2025-04-01",
                    "end_date": "2025-04-15",
                    "milestones": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Core architecture design",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.CORE.value,
                            "date_completed": "2025-04-10",
                            "description": "Design the core architecture for the dual-hemisphere system"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Database schema design",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.DATABASE.value,
                            "date_completed": "2025-04-12",
                            "description": "Design the database schema for the system"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Initial deployment setup",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.DEPLOYMENT.value,
                            "date_completed": "2025-04-15",
                            "description": "Set up initial deployment environment"
                        }
                    ]
                },
                {
                    "id": "phase2",
                    "name": "Core Components",
                    "status": MilestoneStatus.COMPLETED.value,
                    "start_date": "2025-04-16",
                    "end_date": "2025-05-10",
                    "milestones": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Left hemisphere implementation",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.LEFT_HEMISPHERE.value,
                            "date_completed": "2025-04-25",
                            "description": "Implement analytical left hemisphere processing"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Right hemisphere implementation",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.RIGHT_HEMISPHERE.value,
                            "date_completed": "2025-04-30",
                            "description": "Implement creative right hemisphere processing"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "D2 mechanism integration",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.D2_MECHANISM.value,
                            "date_completed": "2025-05-05",
                            "description": "Implement D2 receptor mechanism for hemisphere balance"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Tiered memory system",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.MEMORY.value,
                            "date_completed": "2025-05-10",
                            "description": "Implement three-tiered memory system for both hemispheres"
                        }
                    ]
                },
                {
                    "id": "phase3",
                    "name": "Advanced Features",
                    "status": MilestoneStatus.IN_PROGRESS.value,
                    "start_date": "2025-05-11",
                    "end_date": "2025-06-15",
                    "milestones": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "BRONAS ethics repository",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.BRONAS.value,
                            "date_completed": "2025-05-20",
                            "description": "Implement ethical rules repository"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "SMAS dispatcher",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.SMAS.value,
                            "date_completed": "2025-05-23",
                            "description": "Implement system management and synchronization"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Agent positioning system",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.CORE.value,
                            "date_completed": "2025-05-24",
                            "description": "Implement agent positioning within hemispheres"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Geolocation adaptation",
                            "status": MilestoneStatus.COMPLETED.value,
                            "component": SystemComponent.GEOLOCATION.value,
                            "date_completed": "2025-05-25",
                            "description": "Implement cultural adaptation based on location"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Session transparency",
                            "status": MilestoneStatus.IN_PROGRESS.value,
                            "component": SystemComponent.SECURITY.value,
                            "date_completed": None,
                            "description": "Implement transparent session tracking with hashes"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Progress tracking system",
                            "status": MilestoneStatus.IN_PROGRESS.value,
                            "component": SystemComponent.DOCUMENTATION.value,
                            "date_completed": None,
                            "description": "Implement development progress tracking"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "QRONAS quantum reasoning",
                            "status": MilestoneStatus.PLANNED.value,
                            "component": SystemComponent.QRONAS.value,
                            "date_completed": None,
                            "description": "Implement quantum-inspired reasoning capabilities"
                        }
                    ]
                },
                {
                    "id": "phase4",
                    "name": "Optimization & Scaling",
                    "status": MilestoneStatus.PLANNED.value,
                    "start_date": "2025-06-16",
                    "end_date": "2025-07-15",
                    "milestones": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Performance optimization",
                            "status": MilestoneStatus.PLANNED.value,
                            "component": SystemComponent.OPTIMIZATION.value,
                            "date_completed": None,
                            "description": "Optimize system performance"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Scaling improvements",
                            "status": MilestoneStatus.PLANNED.value,
                            "component": SystemComponent.DEPLOYMENT.value,
                            "date_completed": None,
                            "description": "Improve system scaling capabilities"
                        },
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Advanced UI/UX",
                            "status": MilestoneStatus.PLANNED.value,
                            "component": SystemComponent.UI.value,
                            "date_completed": None,
                            "description": "Enhance user interface and experience"
                        }
                    ]
                }
            ]
        }
        
    def _save_data(self):
        """Save progress data"""
        try:
            # Save to file
            with open(self.log_file, 'w') as f:
                json.dump({
                    'changes': self.changes,
                    'milestones': self.milestones,
                    'roadmap': self.roadmap
                }, f, indent=2)
                
            # Also log to database if available
            # (Placeholder for database implementation)
            
        except Exception as e:
            logger.error(f"Error saving progress data: {e}")
            
    def log_change(self, description, change_type, component, user=None, details=None):
        """
        Log a change to the system
        
        Args:
            description (str): Description of the change
            change_type (ChangeType): Type of change
            component (SystemComponent): System component changed
            user (str, optional): User who made the change
            details (dict, optional): Additional details
            
        Returns:
            dict: The logged change
        """
        # Convert enum values if needed
        if isinstance(change_type, ChangeType):
            change_type = change_type.value
            
        if isinstance(component, SystemComponent):
            component = component.value
            
        # Create change record
        change = {
            'id': str(uuid.uuid4()),
            'description': description,
            'change_type': change_type,
            'component': component,
            'timestamp': datetime.utcnow().isoformat(),
            'user': user
        }
        
        # Add details if provided
        if details:
            change['details'] = details
            
        # Add to changes list
        self.changes.append(change)
        
        # Save data
        self._save_data()
        
        # Log to standard logger
        logger.info(f"[{component.upper()}] {change_type}: {description}")
        
        return change
        
    def update_milestone(self, milestone_id, status=None, progress=None, notes=None):
        """
        Update a milestone's status
        
        Args:
            milestone_id (str): ID of the milestone
            status (MilestoneStatus, optional): New status
            progress (float, optional): Progress percentage (0-100)
            notes (str, optional): Additional notes
            
        Returns:
            dict: The updated milestone
        """
        # Convert status enum if needed
        if isinstance(status, MilestoneStatus):
            status = status.value
            
        # Find the milestone in the roadmap
        for phase in self.roadmap.get('phases', []):
            for milestone in phase.get('milestones', []):
                if milestone.get('id') == milestone_id:
                    # Update fields
                    if status:
                        milestone['status'] = status
                        
                        # Set completion date if completed
                        if status == MilestoneStatus.COMPLETED.value:
                            milestone['date_completed'] = datetime.utcnow().isoformat()
                        
                    if progress is not None:
                        milestone['progress'] = progress
                        
                    if notes:
                        milestone['notes'] = notes
                        
                    # Update phase status based on milestones
                    self._update_phase_status(phase)
                    
                    # Save data
                    self._save_data()
                    
                    # Log the update
                    logger.info(f"Milestone '{milestone.get('name')}' updated: {status}")
                    
                    return milestone
                    
        logger.warning(f"Milestone with ID {milestone_id} not found")
        return None
        
    def _update_phase_status(self, phase):
        """Update a phase's status based on its milestones"""
        milestones = phase.get('milestones', [])
        
        if not milestones:
            return
            
        # Count milestones by status
        status_counts = {}
        for milestone in milestones:
            status = milestone.get('status')
            status_counts[status] = status_counts.get(status, 0) + 1
            
        total = len(milestones)
        completed = status_counts.get(MilestoneStatus.COMPLETED.value, 0)
        in_progress = status_counts.get(MilestoneStatus.IN_PROGRESS.value, 0)
        blocked = status_counts.get(MilestoneStatus.BLOCKED.value, 0)
        
        # Determine phase status
        if completed == total:
            phase['status'] = MilestoneStatus.COMPLETED.value
        elif blocked > 0:
            phase['status'] = MilestoneStatus.BLOCKED.value
        elif in_progress > 0:
            phase['status'] = MilestoneStatus.IN_PROGRESS.value
        else:
            phase['status'] = MilestoneStatus.PLANNED.value
            
    def add_milestone(self, name, phase_id, component, description=None, status=None):
        """
        Add a new milestone
        
        Args:
            name (str): Milestone name
            phase_id (str): ID of the phase
            component (SystemComponent): System component
            description (str, optional): Description
            status (MilestoneStatus, optional): Status
            
        Returns:
            dict: The new milestone
        """
        # Convert enum values if needed
        if isinstance(component, SystemComponent):
            component = component.value
            
        if isinstance(status, MilestoneStatus):
            status = status.value
        elif not status:
            status = MilestoneStatus.PLANNED.value
            
        # Create milestone
        milestone = {
            'id': str(uuid.uuid4()),
            'name': name,
            'status': status,
            'component': component,
            'description': description or "",
            'date_created': datetime.utcnow().isoformat(),
            'date_completed': None
        }
        
        # Find the phase
        for phase in self.roadmap.get('phases', []):
            if phase.get('id') == phase_id:
                # Add milestone to phase
                if 'milestones' not in phase:
                    phase['milestones'] = []
                    
                phase['milestones'].append(milestone)
                
                # Update phase status
                self._update_phase_status(phase)
                
                # Save data
                self._save_data()
                
                # Log the addition
                logger.info(f"Added milestone '{name}' to phase '{phase.get('name')}'")
                
                return milestone
                
        logger.warning(f"Phase with ID {phase_id} not found")
        return None
        
    def add_phase(self, name, start_date=None, end_date=None, description=None):
        """
        Add a new phase to the roadmap
        
        Args:
            name (str): Phase name
            start_date (str, optional): Start date (YYYY-MM-DD)
            end_date (str, optional): End date (YYYY-MM-DD)
            description (str, optional): Description
            
        Returns:
            dict: The new phase
        """
        # Set default dates if not provided
        if not start_date:
            start_date = datetime.utcnow().strftime('%Y-%m-%d')
            
        if not end_date:
            # Default to 30 days after start
            end_date = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')
            
        # Create phase
        phase = {
            'id': str(uuid.uuid4()),
            'name': name,
            'status': MilestoneStatus.PLANNED.value,
            'start_date': start_date,
            'end_date': end_date,
            'description': description or "",
            'milestones': []
        }
        
        # Add to roadmap
        if 'phases' not in self.roadmap:
            self.roadmap['phases'] = []
            
        self.roadmap['phases'].append(phase)
        
        # Save data
        self._save_data()
        
        # Log the addition
        logger.info(f"Added phase '{name}' to roadmap")
        
        return phase
        
    def get_roadmap(self):
        """
        Get the current roadmap
        
        Returns:
            dict: The roadmap
        """
        return self.roadmap
        
    def get_milestone(self, milestone_id):
        """
        Get a milestone by ID
        
        Args:
            milestone_id (str): Milestone ID
            
        Returns:
            dict: The milestone
        """
        for phase in self.roadmap.get('phases', []):
            for milestone in phase.get('milestones', []):
                if milestone.get('id') == milestone_id:
                    return milestone
                    
        return None
        
    def get_changes(self, component=None, change_type=None, limit=50):
        """
        Get logged changes
        
        Args:
            component (SystemComponent, optional): Filter by component
            change_type (ChangeType, optional): Filter by change type
            limit (int): Maximum number of changes to return
            
        Returns:
            list: Filtered changes
        """
        # Convert enum values if needed
        if isinstance(component, SystemComponent):
            component = component.value
            
        if isinstance(change_type, ChangeType):
            change_type = change_type.value
            
        # Filter changes
        filtered = self.changes
        
        if component:
            filtered = [c for c in filtered if c.get('component') == component]
            
        if change_type:
            filtered = [c for c in filtered if c.get('change_type') == change_type]
            
        # Sort by timestamp (newest first)
        filtered.sort(key=lambda c: c.get('timestamp', ''), reverse=True)
        
        # Limit results
        return filtered[:limit]
        
    def get_progress_summary(self):
        """
        Get a summary of project progress
        
        Returns:
            dict: Progress summary
        """
        phases = self.roadmap.get('phases', [])
        
        # Count milestones by status
        milestone_stats = {
            'total': 0,
            'completed': 0,
            'in_progress': 0,
            'planned': 0,
            'blocked': 0,
            'delayed': 0,
            'cancelled': 0
        }
        
        # Count changes by type
        change_stats = {}
        for change in self.changes:
            change_type = change.get('change_type')
            change_stats[change_type] = change_stats.get(change_type, 0) + 1
            
        # Count components changed
        component_stats = {}
        for change in self.changes:
            component = change.get('component')
            component_stats[component] = component_stats.get(component, 0) + 1
            
        # Process milestones
        for phase in phases:
            for milestone in phase.get('milestones', []):
                status = milestone.get('status')
                milestone_stats['total'] += 1
                
                if status == MilestoneStatus.COMPLETED.value:
                    milestone_stats['completed'] += 1
                elif status == MilestoneStatus.IN_PROGRESS.value:
                    milestone_stats['in_progress'] += 1
                elif status == MilestoneStatus.PLANNED.value:
                    milestone_stats['planned'] += 1
                elif status == MilestoneStatus.BLOCKED.value:
                    milestone_stats['blocked'] += 1
                elif status == MilestoneStatus.DELAYED.value:
                    milestone_stats['delayed'] += 1
                elif status == MilestoneStatus.CANCELLED.value:
                    milestone_stats['cancelled'] += 1
                    
        # Calculate overall progress
        if milestone_stats['total'] > 0:
            overall_progress = (milestone_stats['completed'] / milestone_stats['total']) * 100
        else:
            overall_progress = 0
            
        # Calculate recent activity
        now = datetime.utcnow()
        recent_changes = [c for c in self.changes if now - datetime.fromisoformat(c.get('timestamp', now.isoformat())) < timedelta(days=7)]
        
        return {
            'overall_progress': overall_progress,
            'milestone_stats': milestone_stats,
            'change_stats': change_stats,
            'component_stats': component_stats,
            'recent_activity_count': len(recent_changes),
            'phase_count': len(phases),
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def generate_html_report(self, output_file="neuronas_progress.html"):
        """
        Generate an HTML report of the project progress
        
        Args:
            output_file (str): Path to output HTML file
            
        Returns:
            str: Path to the generated file
        """
        # Get data for the report
        roadmap = self.get_roadmap()
        summary = self.get_progress_summary()
        recent_changes = self.get_changes(limit=10)
        
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NeuronasX Project Progress Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #2c3e50;
                }}
                .header {{
                    background-color: #3498db;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .summary-box {{
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-left: 5px solid #3498db;
                }}
                .progress-bar {{
                    background-color: #ecf0f1;
                    border-radius: 5px;
                    height: 25px;
                    margin-bottom: 15px;
                    overflow: hidden;
                }}
                .progress-bar-fill {{
                    background-color: #2ecc71;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                }}
                .phase {{
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .phase-header {{
                    display: flex;
                    justify-content: space-between;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                    margin-bottom: 10px;
                }}
                .milestone {{
                    margin-bottom: 10px;
                    padding: 10px;
                    border-radius: 5px;
                }}
                .milestone.completed {{
                    background-color: rgba(46, 204, 113, 0.1);
                    border-left: 3px solid #2ecc71;
                }}
                .milestone.in-progress {{
                    background-color: rgba(52, 152, 219, 0.1);
                    border-left: 3px solid #3498db;
                }}
                .milestone.planned {{
                    background-color: rgba(149, 165, 166, 0.1);
                    border-left: 3px solid #95a5a6;
                }}
                .milestone.blocked {{
                    background-color: rgba(231, 76, 60, 0.1);
                    border-left: 3px solid #e74c3c;
                }}
                .change-log {{
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .change-item {{
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .badge {{
                    display: inline-block;
                    padding: 3px 8px;
                    border-radius: 12px;
                    font-size: 0.8em;
                    font-weight: bold;
                }}
                .badge.feature {{
                    background-color: #3498db;
                    color: white;
                }}
                .badge.bug {{
                    background-color: #e74c3c;
                    color: white;
                }}
                .badge.enhancement {{
                    background-color: #2ecc71;
                    color: white;
                }}
                .badge.refactoring {{
                    background-color: #9b59b6;
                    color: white;
                }}
                .badge.other {{
                    background-color: #95a5a6;
                    color: white;
                }}
                footer {{
                    margin-top: 40px;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                    text-align: center;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NeuronasX Project Progress Report</h1>
                <p>Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="summary-box">
                <h2>Project Summary</h2>
                <div class="progress-bar">
                    <div class="progress-bar-fill" style="width: {summary['overall_progress']}%">
                        {summary['overall_progress']:.1f}% Complete
                    </div>
                </div>
                <p><strong>Milestones:</strong> {summary['milestone_stats']['completed']} completed of {summary['milestone_stats']['total']} total
                ({summary['milestone_stats']['in_progress']} in progress, {summary['milestone_stats']['planned']} planned)</p>
                <p><strong>Recent Activity:</strong> {summary['recent_activity_count']} changes in the last 7 days</p>
            </div>
            
            <h2>Roadmap</h2>
        """
        
        # Add phases and milestones
        for phase in roadmap.get('phases', []):
            phase_name = phase.get('name', 'Unnamed Phase')
            phase_status = phase.get('status', 'planned')
            start_date = phase.get('start_date', 'N/A')
            end_date = phase.get('end_date', 'N/A')
            
            html += f"""
            <div class="phase">
                <div class="phase-header">
                    <h3>{phase_name}</h3>
                    <div>
                        <span class="badge {phase_status}">{phase_status}</span>
                        <span>{start_date} to {end_date}</span>
                    </div>
                </div>
            """
            
            # Add milestones for this phase
            for milestone in phase.get('milestones', []):
                milestone_name = milestone.get('name', 'Unnamed Milestone')
                milestone_status = milestone.get('status', 'planned')
                milestone_component = milestone.get('component', 'other')
                milestone_desc = milestone.get('description', '')
                completion_date = milestone.get('date_completed', 'Not completed')
                
                html += f"""
                <div class="milestone {milestone_status}">
                    <h4>{milestone_name}</h4>
                    <p>{milestone_desc}</p>
                    <div>
                        <span class="badge {milestone_status}">{milestone_status}</span>
                        <span class="badge {milestone_component}">{milestone_component}</span>
                        <span>{completion_date if milestone_status == 'completed' else ''}</span>
                    </div>
                </div>
                """
                
            html += "</div>"
            
        # Add recent changes
        html += """
            <h2>Recent Changes</h2>
            <div class="change-log">
        """
        
        for change in recent_changes:
            change_desc = change.get('description', 'No description')
            change_type = change.get('change_type', 'other')
            change_component = change.get('component', 'other')
            change_time = change.get('timestamp', '')
            change_user = change.get('user', 'Unknown')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(change_time)
                change_time = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
                
            html += f"""
            <div class="change-item">
                <p><strong>{change_desc}</strong></p>
                <div>
                    <span class="badge {change_type}">{change_type}</span>
                    <span class="badge {change_component}">{change_component}</span>
                    <span>{change_time} by {change_user}</span>
                </div>
            </div>
            """
            
        html += """
            </div>
            
            <footer>
                <p>NeuronasX Project Progress Tracker | Generated by the Progress Tracking System</p>
            </footer>
        </body>
        </html>
        """
        
        # Write to file
        try:
            with open(output_file, 'w') as f:
                f.write(html)
                
            logger.info(f"Generated HTML report at {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return None