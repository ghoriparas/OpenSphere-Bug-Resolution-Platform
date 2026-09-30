import os
import csv
import io
from functools import wraps
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response
from models import db, User, Project, Issue, Comment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-987654'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///opensphere.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'Admin':
            flash('Admin privilege required for this action.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# Helper to pass logged in user to all templates
@app.context_processor
def inject_user():
    current_user = None
    if 'user_id' in session:
        current_user = User.query.get(session['user_id'])
    return dict(current_user=current_user)

# --- Authentication Routes ---


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        role = request.form.get('role', 'Developer')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Choose another.', 'danger')
            return render_template('register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
            
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

# ----------------- DASHBOARD & ANALYTICS -----------------

@app.route('/dashboard')
@login_required
def dashboard():
    total_projects = Project.query.count()
    total_issues = Issue.query.count()
    open_issues = Issue.query.filter_by(status='Open').count()
    in_progress = Issue.query.filter_by(status='In Progress').count()
    resolved_issues = Issue.query.filter_by(status='Resolved').count()
    critical_issues = Issue.query.filter_by(priority='Critical').count()
    
    recent_issues = Issue.query.order_by(Issue.created_at.desc()).limit(5).all()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    
    # Priority counts for analytics
    low_count = Issue.query.filter_by(priority='Low').count()
    med_count = Issue.query.filter_by(priority='Medium').count()
    high_count = Issue.query.filter_by(priority='High').count()
    crit_count = Issue.query.filter_by(priority='Critical').count()

    analytics_data = {
        'status': [open_issues, in_progress, resolved_issues, Issue.query.filter_by(status='Closed').count()],
        'priority': [low_count, med_count, high_count, crit_count]
    }
    
    return render_template(
        'dashboard.html',
        total_projects=total_projects,
        total_issues=total_issues,
        open_issues=open_issues,
        in_progress=in_progress,
        resolved_issues=resolved_issues,
        critical_issues=critical_issues,
        recent_issues=recent_issues,
        projects=projects,
        analytics=analytics_data
    )

# --- Projects Management ---

@app.route('/projects')
@login_required
def projects():
    all_projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=all_projects)

@app.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        title = request.form.get('title').strip()
        description = request.form.get('description').strip()
        technology_stack = request.form.get('technology_stack').strip()
        repository_url = request.form.get('repository_url').strip()
        status = request.form.get('status', 'Active')
        
        project = Project(
            title=title,
            description=description,
            technology_stack=technology_stack,
            repository_url=repository_url,
            status=status
        )
        db.session.add(project)
        db.session.commit()
        flash(f'Project "{title}" created successfully!', 'success')
        return redirect(url_for('projects'))
        
    return render_template('project_form.html', action='Create', project=None)

@app.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    issues = Issue.query.filter_by(project_id=project.id).order_by(Issue.created_at.desc()).all()
    return render_template('project_detail.html', project=project, issues=issues)

@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.title = request.form.get('title').strip()
        project.description = request.form.get('description').strip()
        project.technology_stack = request.form.get('technology_stack').strip()
        project.repository_url = request.form.get('repository_url').strip()
        project.status = request.form.get('status')
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('project_detail', project_id=project.id))
    return render_template('project_form.html', action='Edit', project=project)

@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully.', 'info')
    return redirect(url_for('projects'))

# --- Issues & Bug Tracking ---

@app.route('/issues')
@login_required
def issues():
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    project_filter = request.args.get('project_id')
    search_query = request.args.get('search')
    
    query = Issue.query
    if status_filter:
        query = query.filter_by(status=status_filter)
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    if project_filter:
        query = query.filter_by(project_id=int(project_filter))
    if search_query:
        query = query.filter(Issue.title.ilike(f'%{search_query}%'))
        
    all_issues = query.order_by(Issue.created_at.desc()).all()
    projects = Project.query.all()
    
    return render_template('issues.html', issues=all_issues, projects=projects)

@app.route('/issues/create', methods=['GET', 'POST'])
@login_required
def create_issue():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        issue_type = request.form.get('issue_type', 'Bug')
        priority = request.form.get('priority', 'Medium')
        status = request.form.get('status', 'Open')
        project_id_val = request.form.get('project_id')
        assigned_to_id = request.form.get('assigned_to_id')
        
        if not title or not project_id_val:
            flash('Issue title and project selection are required.', 'danger')
            return redirect(url_for('create_issue'))
            
        try:
            project_id = int(project_id_val)
        except ValueError:
            flash('Invalid project selected.', 'danger')
            return redirect(url_for('create_issue'))
            
        assigned_to = int(assigned_to_id) if (assigned_to_id and assigned_to_id.isdigit()) else None
        
        issue = Issue(
            title=title,
            description=description,
            issue_type=issue_type,
            priority=priority,
            status=status,
            project_id=project_id,
            assigned_to_id=assigned_to,
            reported_by_id=session['user_id']
        )
        db.session.add(issue)
        db.session.commit()
        flash('Issue reported successfully!', 'success')
        return redirect(url_for('issues'))
        
    projects = Project.query.all()
    users = User.query.all()
    return render_template('issue_form.html', action='Create', issue=None, projects=projects, users=users)


@app.route('/issues/<int:issue_id>')
@login_required
def issue_detail(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    users = User.query.all()
    return render_template('issue_detail.html', issue=issue, users=users)

@app.route('/issues/<int:issue_id>/update-status', methods=['POST'])
@login_required
def update_issue_status(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    new_status = request.form.get('status')
    assigned_to_id = request.form.get('assigned_to_id')
    
    if new_status in ['Open', 'In Progress', 'Resolved', 'Closed']:
        issue.status = new_status
    if assigned_to_id:
        issue.assigned_to_id = int(assigned_to_id) if (assigned_to_id != 'none' and assigned_to_id.isdigit()) else None
        
    issue.updated_at = datetime.utcnow()
    db.session.commit()
    flash(f'Issue #{issue.id} status updated to {issue.status}.', 'success')
    return redirect(url_for('issue_detail', issue_id=issue.id))

@app.route('/issues/<int:issue_id>/comment', methods=['POST'])
@login_required
def add_comment(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    content = request.form.get('content', '').strip()
    if content:
        comment = Comment(
            content=content,
            issue_id=issue.id,
            user_id=session['user_id']
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment added.', 'success')
    return redirect(url_for('issue_detail', issue_id=issue.id))

# --- Kanban Board ---

@app.route('/kanban')
@login_required
def kanban():
    open_issues = Issue.query.filter_by(status='Open').all()
    in_progress_issues = Issue.query.filter_by(status='In Progress').all()
    resolved_issues = Issue.query.filter_by(status='Resolved').all()
    closed_issues = Issue.query.filter_by(status='Closed').all()
    
    return render_template(
        'kanban.html',
        open_issues=open_issues,
        in_progress_issues=in_progress_issues,
        resolved_issues=resolved_issues,
        closed_issues=closed_issues
    )

@app.route('/api/issues/update-status', methods=['POST'])
@login_required
def api_update_issue_status():
    data = request.get_json(silent=True) or {}
    issue_id = data.get('issue_id')
    new_status = data.get('status')
    
    if not issue_id or not new_status:
        return jsonify({'success': False, 'error': 'Missing issue_id or status'}), 400
        
    issue = Issue.query.get(issue_id)
    if issue and new_status in ['Open', 'In Progress', 'Resolved', 'Closed']:
        issue.status = new_status
        issue.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'message': 'Status updated'})
    return jsonify({'success': False, 'error': 'Invalid issue or status'}), 400


# --- CSV Report Export ---

@app.route('/export/csv')
@login_required
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Project', 'Type', 'Priority', 'Status', 'Reporter', 'Assignee', 'Created At'])
    
    issues = Issue.query.all()
    for issue in issues:
        writer.writerow([
            issue.id,
            issue.title,
            issue.project.title if issue.project else 'N/A',
            issue.issue_type,
            issue.priority,
            issue.status,
            issue.reporter.username if issue.reporter else 'N/A',
            issue.assignee.username if issue.assignee else 'Unassigned',
            issue.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=OpenSphere_Issues_Report.csv"}
    )

# Create tables if not present
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)


