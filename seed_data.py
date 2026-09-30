from app import app, db
from models import User, Project, Issue, Comment
from datetime import datetime

def seed():
    with app.app_context():
        # Recreate DB schema
        db.drop_all()
        db.create_all()
        
        print("Creating initial users...")
        admin = User(username='admin', email='admin@opensphere.org', role='Admin')
        admin.set_password('admin123')
        
        dev1 = User(username='paras', email='paras@opensphere.org', role='Developer')
        dev1.set_password('paras123')
        
        dev2 = User(username='rahul', email='rahul@opensphere.org', role='Developer')
        dev2.set_password('rahul123')
        
        db.session.add_all([admin, dev1, dev2])
        db.session.commit()
        
        print("Creating sample open source projects...")
        p1 = Project(
            title="OpenSphere Dashboard Engine",
            description="Core Flask-based real-time analytics and workload tracking dashboard engine for open source projects.",
            technology_stack="Python, Flask, SQLite, Chart.js, HTML5/CSS3",
            repository_url="https://github.com/opensource/opensphere-engine",
            status="Active"
        )
        
        p2 = Project(
            title="Smart Cloud Asset Scanner",
            description="Automated Python microservice for scanning cloud assets, auditing IAM policies, and discovering security vulnerabilities.",
            technology_stack="Python, Flask, Docker, REST API",
            repository_url="https://github.com/opensource/cloud-scanner",
            status="Active"
        )

        p3 = Project(
            title="AI Text Summarizer CLI",
            description="Command-line utility and Web API for summarizing technical project documentation using NLP and transformers.",
            technology_stack="Python, HuggingFace, FastAPI, PyTorch",
            repository_url="https://github.com/opensource/ai-summarizer",
            status="Completed"
        )
        
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        print("Creating sample issues and bugs...")
        i1 = Issue(
            title="Database Connection Pool Exhaustion under Heavy Load",
            description="Under concurrent API calls, SQLite lock errors occur when multiple worker threads write simultaneously.",
            issue_type="Bug",
            priority="Critical",
            status="In Progress",
            project_id=p1.id,
            reported_by_id=dev1.id,
            assigned_to_id=dev2.id
        )

        i2 = Issue(
            title="Implement Chart.js Dark Mode Toggle on Dashboard",
            description="Add support for dynamic theme switching (Dark/Light mode) across all analytical chart widgets.",
            issue_type="Feature",
            priority="Medium",
            status="Open",
            project_id=p1.id,
            reported_by_id=admin.id,
            assigned_to_id=dev1.id
        )

        i3 = Issue(
            title="Fix CORS Headers for REST API Endpoint `/api/analytics`",
            description="Frontend requests from separate origin receive 403 Forbidden due to missing Access-Control-Allow-Origin response header.",
            issue_type="Bug",
            priority="High",
            status="Resolved",
            project_id=p2.id,
            reported_by_id=dev2.id,
            assigned_to_id=admin.id
        )

        i4 = Issue(
            title="Export Reports to PDF and CSV Format",
            description="Users need ability to download issue metrics report directly as PDF and CSV files from the dashboard header.",
            issue_type="Enhancement",
            priority="Medium",
            status="Open",
            project_id=p1.id,
            reported_by_id=dev1.id,
            assigned_to_id=dev1.id
        )

        db.session.add_all([i1, i2, i3, i4])
        db.session.commit()

        print("Creating sample discussion comments...")
        c1 = Comment(
            content="I am inspecting `models.py` and configuring scoped session pool settings to prevent SQLite file lock concurrency issues.",
            issue_id=i1.id,
            user_id=dev2.id
        )
        c2 = Comment(
            content="Fixed CORS middleware header in `app.py`. Unit tests passing cleanly.",
            issue_id=i3.id,
            user_id=admin.id
        )
        
        db.session.add_all([c1, c2])
        db.session.commit()
        print("Seed data successfully created! Run `python app.py` to start application.")

if __name__ == '__main__':
    seed()
