# models.py - UPDATED VERSION (Removed MCQ Tests and Learning Resources)

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# =============================================================================
# 1. USER MODEL (Student, TPO, HR)
# =============================================================================
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'tpo', 'student', 'HR'
    is_verified = db.Column(db.Boolean, default=False)  # Verification status

    # Student-specific fields
    rollno = db.Column(db.String(20), unique=True, nullable=True)  # Register number for login
    cgpa = db.Column(db.Float, nullable=True)
    branch = db.Column(db.String(50), nullable=True)
    semester = db.Column(db.Integer, nullable=False, default=7)
    resume_filename = db.Column(db.String(200), nullable=True)
    photo_filename = db.Column(db.String(200), nullable=True)

    # Additional student profile details
    phone_number = db.Column(db.String(15), nullable=True)
    address = db.Column(db.Text, nullable=True)
    linkedin_profile = db.Column(db.String(200), nullable=True)
    github_profile = db.Column(db.String(200), nullable=True)
    skills = db.Column(db.Text, nullable=True)  # Comma-separated skills
    projects = db.Column(db.Text, nullable=True)  # Description of projects
    certificates = db.Column(db.Text, nullable=True)  # List of certificates
    achievements = db.Column(db.Text, nullable=True)  # Academic/other achievements

    # HR-specific fields
    hr_id = db.Column(db.String(20), unique=True, nullable=True)  # Unique HR ID for login
    company_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)  # Company email for verification
    website = db.Column(db.String(200), nullable=True)  # Company website
    company_description = db.Column(db.Text, nullable=True)  # Additional details for TPO verification

    # Relationships
    applications = db.relationship('Application', backref='student', lazy=True, cascade="all, delete-orphan")
    posted_jobs = db.relationship('Job', backref='hr', lazy=True, cascade="all, delete-orphan")
    experiences = db.relationship('InterviewExperience', backref='student', lazy=True, cascade="all, delete-orphan")

    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<User {self.name} - {self.role.upper()}>'


# =============================================================================
# 2. JOB MODEL
# =============================================================================
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50))  # e.g., "25 LPA"
    min_cgpa = db.Column(db.Float, nullable=False)
    branches = db.Column(db.String(200), nullable=False)  # "CSE,IT,ECE"
    test_link = db.Column(db.String(500), nullable=True)  # External test link

    posted_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='job', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Job {self.title} @ {self.company}>'


# =============================================================================
# 3. APPLICATION MODEL
# =============================================================================
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(50), nullable=False, default='Applied')  # Applied, Shortlisted, Selected, Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)

    def __repr__(self):
        return f'<Application {self.student.name} → {self.job.title} [{self.status}]>'


# =============================================================================
# 4. INTERVIEW EXPERIENCE (with upvote/downvote)
# =============================================================================
class InterviewExperience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(100), nullable=False)
    rounds = db.Column(db.Text, nullable=False)        # Multi-line: "Aptitude → Technical → HR"
    verdict = db.Column(db.String(20), nullable=False) # "Selected" or "Rejected"
    experience = db.Column(db.Text, nullable=False)    # Full detailed experience
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Experience {self.company} - {self.verdict} by {self.student.name}>'


# =============================================================================
# 5. NOTIFICATION MODEL
# =============================================================================
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification for {self.user.name}: {self.message[:50]}...>'


# =============================================================================
# HELPER: Create tables if not exist (for first run)
# =============================================================================
def init_db():
    db.create_all()
    print("Database tables created successfully!")
