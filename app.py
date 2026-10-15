# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Job, Application, InterviewExperience, Notification
import pandas as pd
from werkzeug.utils import secure_filename
import os
import re



# --- Create the app FIRST ---
app = Flask(__name__)

# --- Configurations ---
app.config['SECRET_KEY'] = 'campus_placement_2025'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.getcwd(), "instance", "placement.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS_RESUME = {'pdf', 'doc', 'docx'}
ALLOWED_EXTENSIONS_PHOTO = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- Initialize Extensions ---
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "You must be logged in to access this page."
login_manager.login_message_category = "error"

# --- Helper Functions ---
def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

def create_upload_dirs():
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create DB + Sample Data
def create_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(first_name="Placement").first():
            print("Creating default users and jobs...")

            # TPO User
            tpo = User(
                password=generate_password_hash("tpo123"),
                role="tpo",
                first_name="Placement",
                last_name="Officer",
                is_verified=True
            )

            # Students (10, all CSE branch)
            students = [
                User(password=generate_password_hash("12345"), role="student", first_name="Rahul", last_name="Sharma", rollno="21CSE001", cgpa=8.9, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Priya", last_name="Gupta", rollno="21CSE002", cgpa=7.8, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Amit", last_name="Verma", rollno="21CSE003", cgpa=8.1, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Sneha", last_name="Kumar", rollno="21CSE004", cgpa=7.3, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Rohan", last_name="Singh", rollno="21CSE005", cgpa=8.5, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Anjali", last_name="Patel", rollno="21CSE006", cgpa=7.9, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Karan", last_name="Jain", rollno="21CSE007", cgpa=6.8, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Divya", last_name="Malhotra", rollno="21CSE008", cgpa=8.3, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Saurabh", last_name="Mehta", rollno="21CSE009", cgpa=7.5, branch="CSE", is_verified=True),
                User(password=generate_password_hash("12345"), role="student", first_name="Meera", last_name="Nair", rollno="21CSE010", cgpa=8.0, branch="CSE", is_verified=True),
            ]

            # HRs (4 companies)
            hrs = [
                User(password=generate_password_hash("emp123"), role="HR", first_name="HR", last_name="Manager", company_name="Microsoft", hr_id="hr1", is_verified=True),
                User(password=generate_password_hash("emp123"), role="HR", first_name="HR", last_name="Lead", company_name="Google", hr_id="hr2", is_verified=True),
                User(password=generate_password_hash("emp123"), role="HR", first_name="HR", last_name="Coordinator", company_name="Amazon", hr_id="hr3", is_verified=True),
                User(password=generate_password_hash("emp123"), role="HR", first_name="HR", last_name="Representative", company_name="Deloitte", hr_id="hr4", is_verified=True)
            ]

            db.session.add(tpo)
            db.session.add_all(students)
            db.session.add_all(hrs)
            db.session.commit()

            # Jobs for each HR
            jobs = [
                Job(title="SDE", company="Microsoft", salary="25 LPA", min_cgpa=8.0, branches="CSE", posted_by_id=hrs[0].id),
                Job(title="Software Engineer", company="Google", salary="30 LPA", min_cgpa=8.5, branches="CSE", posted_by_id=hrs[1].id),
                Job(title="Cloud Engineer", company="Amazon", salary="28 LPA", min_cgpa=8.0, branches="CSE", posted_by_id=hrs[2].id),
                Job(title="Consultant", company="Deloitte", salary="14 LPA", min_cgpa=7.0, branches="CSE", posted_by_id=hrs[3].id)
            ]
            db.session.add_all(jobs)
            db.session.commit()

            # Applications with varied statuses for students and jobs
            applications = [
                # Rahul: Selected for Microsoft SDE
                Application(status="Selected", student_id=students[0].id, job_id=jobs[0].id),
                # Priya: Rejected for Google Software Engineer
                Application(status="Rejected", student_id=students[1].id, job_id=jobs[1].id),
                # Amit: Shortlisted for Amazon Cloud Engineer
                Application(status="Shortlisted", student_id=students[2].id, job_id=jobs[2].id),
                # Sneha: Applied for Deloitte Consultant
                Application(status="Applied", student_id=students[3].id, job_id=jobs[3].id),
                # Rohan: Selected for Google Software Engineer
                Application(status="Selected", student_id=students[4].id, job_id=jobs[1].id),
                # Anjali: Rejected for Microsoft SDE
                Application(status="Rejected", student_id=students[5].id, job_id=jobs[0].id),
                # Karan: Shortlisted for Deloitte Consultant
                Application(status="Shortlisted", student_id=students[6].id, job_id=jobs[3].id),
                # Divya: Applied for Amazon Cloud Engineer
                Application(status="Applied", student_id=students[7].id, job_id=jobs[2].id),
                # Saurabh: Selected for Microsoft SDE
                Application(status="Selected", student_id=students[8].id, job_id=jobs[0].id),
                # Meera: Rejected for Google Software Engineer
                Application(status="Rejected", student_id=students[9].id, job_id=jobs[1].id)
            ]
            db.session.add_all(applications)
            db.session.commit()

            # Interview Experiences associated with some students
            experiences = [
                InterviewExperience(company="Microsoft", rounds="Online Test, Technical Rounds, HR Round", verdict="Selected", experience="Challenging process with focus on algorithms.", student_id=students[0].id),
                InterviewExperience(company="Google", rounds="Aptitude, Technical, HR", verdict="Rejected", experience="Very tough technical rounds, prepared but not selected.", student_id=students[1].id),
                InterviewExperience(company="Amazon", rounds="Technical and HR", verdict="Shortlisted", experience="Good experience but waiting for final results.", student_id=students[2].id)
            ]
            db.session.add_all(experiences)
            db.session.commit()

        else:
            print("Database already populated.")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        login_identifier = request.form['login_identifier'].strip()
        password = request.form['password']

        # Determine if it's a student (rollno) or HR (hr_id) or TPO
        user = None
        if login_identifier == 'tpo':
            user = User.query.filter_by(role='tpo').first()
        else:
            # Try student first
            user = User.query.filter_by(rollno=login_identifier).first()
            if not user:
                # Try HR
                user = User.query.filter_by(hr_id=login_identifier).first()

        if user and check_password_hash(user.password, password):
            if not user.is_verified:
                flash('Your account is pending approval. Please contact TPO.', 'error')
                return render_template('login.html')
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid login identifier or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        role = request.form['role']
        hashed_password = generate_password_hash(request.form['password'])

        full_name = request.form['name'].strip()
        first_name, last_name = full_name.split(' ', 1) if ' ' in full_name else (full_name, '')
        new_user = User(password=hashed_password, first_name=first_name, last_name=last_name, role=role, is_verified=(role == 'tpo'))
        try:
            if role == 'student':
                if User.query.filter_by(rollno=request.form['rollno']).first():
                    flash('Roll number already registered.', 'error')
                    return render_template('register.html')
                new_user.rollno = request.form['rollno']
                new_user.cgpa = float(request.form['cgpa'])
                new_user.branch = request.form['branch']
                semester_str = request.form.get('semester')
                if not semester_str:
                    flash('Please select a semester.', 'error')
                    return render_template('register.html')
                new_user.semester = int(semester_str)
        except ValueError:
            flash('Invalid CGPA or semester.', 'error')
            return render_template('register.html')

        if role == 'HR':
            company_name = request.form.get('company_name', '').strip()
            hr_id = request.form.get('hr_id', '').strip()
            email = request.form.get('email', '').strip()
            website = request.form.get('website', '').strip()
            company_description = request.form.get('company_description', '').strip()

            if not company_name or not hr_id or not email or not website or not company_description:
                flash('All company details are required for HR registration.', 'error')
                return render_template('register.html')

            if User.query.filter_by(hr_id=hr_id).first():
                flash('HR ID already registered.', 'error')
                return render_template('register.html')

            new_user.company_name = company_name
            new_user.hr_id = hr_id
            new_user.email = email
            new_user.website = website
            new_user.company_description = company_description

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please wait for TPO approval before logging in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'tpo':
        return redirect(url_for('tpo_dashboard'))
    elif current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.role == 'HR':
        return redirect(url_for('hr_dashboard'))
    return redirect(url_for('logout'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

# ==========================================
# STUDENT FILE UPLOADS
# ==========================================
@app.route('/upload_resume', methods=['POST'])
@login_required
def upload_resume():
    if current_user.role != 'student': return redirect(url_for('dashboard'))
    if 'resume' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('student_dashboard'))
    file = request.files['resume']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_EXTENSIONS_RESUME):
        flash('Invalid resume file. Allowed: pdf, doc, docx', 'error')
        return redirect(url_for('student_dashboard'))

    filename = secure_filename(file.filename)
    unique_filename = f"{current_user.rollno}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'resumes', unique_filename))
    current_user.resume_filename = unique_filename
    db.session.commit()
    flash('Resume uploaded!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))

    current_user.phone_number = request.form.get('phone_number', '').strip()
    current_user.address = request.form.get('address', '').strip()
    current_user.linkedin_profile = request.form.get('linkedin_profile', '').strip()
    current_user.github_profile = request.form.get('github_profile', '').strip()
    current_user.skills = request.form.get('skills', '').strip()
    current_user.projects = request.form.get('projects', '').strip()
    current_user.certificates = request.form.get('certificates', '').strip()
    current_user.achievements = request.form.get('achievements', '').strip()

    db.session.commit()
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/upload_photo', methods=['POST'])
@login_required
def upload_photo():
    if current_user.role != 'student': return redirect(url_for('dashboard'))
    if 'photo' not in request.files:
        flash('No photo selected', 'error')
        return redirect(url_for('student_dashboard'))
    file = request.files['photo']
    if file.filename == '' or not allowed_file(file.filename, ALLOWED_EXTENSIONS_PHOTO):
        flash('Invalid photo. Allowed: png, jpg, jpeg', 'error')
        return redirect(url_for('student_dashboard'))
    
    filename = secure_filename(file.filename)
    unique_filename = f"{current_user.rollno}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'photos', unique_filename))
    current_user.photo_filename = unique_filename
    db.session.commit()
    flash('Photo uploaded!', 'success')
    return redirect(url_for('student_dashboard'))

# ==========================================
# TPO DASHBOARD + COURSES
# ==========================================

# Helper to extract numbers from "25 LPA" or "14.5"
def extract_salary_float(salary_str):
    if not salary_str:
        return 0.0
    numbers = re.findall(r"[\d\.]+", salary_str)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return 0.0
    return 0.0

@app.route('/tpo')
@login_required
def tpo_dashboard():
    if current_user.role != 'tpo':
        return redirect(url_for('dashboard'))

    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()

    # --- Applications with pagination and search ---
    apps_query = Application.query.options(db.joinedload(Application.student), db.joinedload(Application.job))
    if search:
        apps_query = apps_query.filter(
            db.or_(
                Application.student.has(User.name.contains(search)),
                Application.job.has(Job.company.contains(search)),
                Application.job.has(Job.title.contains(search))
            )
        )
    apps_pagination = apps_query.paginate(page=page, per_page=10, error_out=False)
    apps = apps_pagination.items

    # --- Jobs ---
    jobs = Job.query.options(db.joinedload(Job.hr)).all()

    # --- Students ---
    students = User.query.filter_by(role='student').all()

    # --- HRs ---
    hrs = User.query.filter_by(role='HR').all()

    # --- Pending Users ---
    pending_students = User.query.filter_by(role='student', is_verified=False).all()
    pending_hrs = User.query.filter_by(role='HR', is_verified=False).all()

    # --- Statistics Pre-Calculation ---
    all_apps = Application.query.all()  # For stats, get all
    placed_apps = [a for a in all_apps if a.status == 'Selected']
    placed_count = len(placed_apps)
    student_count = len(students)

    placement_rate = 0.0
    if student_count > 0:
        placement_rate = (placed_count / student_count) * 100

    max_package = 0.0
    avg_package = 0.0

    if placed_count > 0:
        salaries = [extract_salary_float(a.job.salary) for a in placed_apps if a.job.salary]
        if salaries:
            max_package = max(salaries)
            avg_package = sum(salaries) / len(salaries)

    bar_chart_labels = [job.company for job in jobs if job.salary]
    bar_chart_data = [extract_salary_float(job.salary) for job in jobs if job.salary]

    return render_template(
        'tpo_dashboard.html',
        apps=apps,
        apps_pagination=apps_pagination,
        search=search,
        jobs=jobs,
        students=students,
        hrs=hrs,
        pending_students=pending_students,
        pending_hrs=pending_hrs,
        # --- Pass all stats to template ---
        placement_rate=placement_rate,
        placed_count=placed_count,
        unplaced_count=student_count - placed_count,
        max_package=max_package,
        avg_package=avg_package,
        bar_chart_labels=bar_chart_labels,
        bar_chart_data=bar_chart_data
    )



# ==========================================
# STUDENT DASHBOARD
# ==========================================
@app.route('/student')
@login_required
def student_dashboard():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))

    jobs = Job.query.all()
    applications = Application.query.filter_by(student_id=current_user.id).all()
    applied_job_ids = {app.job_id for app in applications}
    experiences = InterviewExperience.query.order_by(InterviewExperience.upvotes.desc()).all()

    return render_template('student_dashboard.html',
                           jobs=jobs, applications=applications,
                           applied_job_ids=applied_job_ids,
                           experiences=experiences)

# ==========================================
# HR DASHBOARD
# ==========================================
@app.route('/hr')
@login_required
def hr_dashboard():
    if current_user.role != 'HR':
        return redirect(url_for('dashboard'))
    my_jobs = Job.query.filter_by(posted_by_id=current_user.id).all()
    my_job_ids = [j.id for j in my_jobs]
    apps = Application.query.filter(Application.job_id.in_(my_job_ids))\
                            .options(db.selectinload(Application.student), db.selectinload(Application.job)).all()
    return render_template('hr_dashboard.html', jobs=my_jobs, apps=apps)

@app.route('/export')
@login_required
def export():
    if current_user.role != 'tpo':
        flash('Not authorized.', 'error')
        return redirect(url_for('dashboard'))
    data = []
    for a in Application.query.options(db.joinedload(Application.student), db.joinedload(Application.job)).all():
        data.append({
            'Name': a.student.name, 'Roll': a.student.rollno, 'CGPA': a.student.cgpa,
            'Branch': a.student.branch, 'Company': a.job.company, 
            'Job Title': a.job.title, 'Status': a.status
        })
    df = pd.DataFrame(data)
    filepath = 'placement_report.xlsx'
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True, download_name='placement_report.xlsx')

# ==========================================
# == SHARED ROUTES
# ==========================================
@app.route('/apply/<int:job_id>')
@login_required
def apply(job_id):
    if current_user.role != 'student':
        flash('Only students can apply.', 'error')
        return redirect(url_for('dashboard'))
    job = Job.query.get_or_404(job_id)
    is_eligible_cgpa = current_user.cgpa >= job.min_cgpa
    is_eligible_branch = current_user.branch in [b.strip() for b in job.branches.split(',')]
    
    if not is_eligible_cgpa:
        flash(f'CGPA too low for {job.title}', 'error')
    elif not is_eligible_branch:
        flash(f'Branch not eligible for {job.title}', 'error')
    elif Application.query.filter_by(student_id=current_user.id, job_id=job_id).first():
        flash('Already applied', 'info')
    else:
        new_app = Application(student_id=current_user.id, job_id=job_id)
        db.session.add(new_app)
        db.session.commit()
        # Create notification
        notification = Notification(
            user_id=current_user.id,
            message=f'You have successfully applied for {job.title} at {job.company}.'
        )
        db.session.add(notification)
        db.session.commit()
        flash(f'Applied to {job.title}!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/update_status/<int:app_id>/<status>')
@login_required
def update_status(app_id, status):
    app_to_update = Application.query.get_or_404(app_id)
    job = app_to_update.job
    
    if current_user.role == 'tpo' or (current_user.role == 'HR' and job.posted_by_id == current_user.id):
        if status in ['Shortlisted', 'Selected', 'Rejected', 'Applied', 'Test Sent']:
            app_to_update.status = status
            db.session.commit()
            # Create notification for the student
            notification = Notification(
                user_id=app_to_update.student_id,
                message=f'Your application for {job.title} at {job.company} has been updated to: {status}.'
            )
            db.session.add(notification)
            db.session.commit()
            flash(f'Application status updated to {status}', 'success')
        else:
            flash('Invalid status.', 'error')
    else:
        flash('Not authorized.', 'error')

    if current_user.role == 'tpo':
        return redirect(url_for('tpo_dashboard'))
    elif current_user.role == 'HR':
        return redirect(url_for('hr_dashboard'))
    else:
        return redirect(url_for('dashboard'))

@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    if current_user.role not in ['tpo', 'HR']:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        company_name = current_user.company_name if current_user.role == 'HR' else request.form['company']
        try:
            new_job = Job(
                title=request.form['title'],
                company=company_name,
                salary=request.form['salary'],
                min_cgpa=float(request.form['min_cgpa']),
                branches=request.form['branches'],
                posted_by_id=current_user.id
            )
            db.session.add(new_job)
            db.session.commit()
            flash('New job added successfully.', 'success')
        except ValueError:
             flash('Invalid input for Min. CGPA.', 'error')
             return render_template('add_job.html', job=None)

        if current_user.role == 'tpo':
            return redirect(url_for('tpo_dashboard'))
        else:
            return redirect(url_for('hr_dashboard'))
    return render_template('add_job.html', job=None)

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    job_to_edit = Job.query.get_or_404(job_id)
    
    if not (current_user.role == 'tpo' or (current_user.role == 'HR' and job_to_edit.posted_by_id == current_user.id)):
        flash('Not authorized to edit this job.', 'error')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        try:
            job_to_edit.title = request.form['title']
            if current_user.role == 'tpo':
                job_to_edit.company = request.form['company']
            job_to_edit.salary = request.form['salary']
            job_to_edit.min_cgpa = float(request.form['min_cgpa'])
            job_to_edit.branches = request.form['branches']
            job_to_edit.test_link = request.form.get('test_link')
            db.session.commit()
            flash('Job updated successfully.', 'success')
        except ValueError:
            flash('Invalid input for Min. CGPA.', 'error')
            return render_template('add_job.html', job=job_to_edit)
        
        if current_user.role == 'tpo':
            return redirect(url_for('tpo_dashboard')) # <-- FIXED TYPO
        else:
            return redirect(url_for('hr_dashboard'))
    
    return render_template('add_job.html', job=job_to_edit)

@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    job_to_delete = Job.query.get_or_404(job_id)
    if not (current_user.role == 'tpo' or (current_user.role == 'HR' and job_to_delete.posted_by_id == current_user.id)):
        flash('Not authorized to delete this job.', 'error')
        return redirect(url_for('dashboard'))

    Application.query.filter_by(job_id=job_id).delete()
    db.session.delete(job_to_delete)
    db.session.commit()
    flash('Job and all associated applications have been deleted.', 'success')
    
    if current_user.role == 'tpo':
        return redirect(url_for('tpo_dashboard'))
    else:
        return redirect(url_for('hr_dashboard'))

# ==========================================
# == INTERVIEW EXPERIENCE ROUTES (NEW)
# ==========================================
@app.route('/add_experience', methods=['GET', 'POST'])
@login_required
def add_experience():
    if current_user.role != 'student':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        exp = InterviewExperience(
            company=request.form['company'],
            rounds=request.form['rounds'],
            verdict=request.form['verdict'],
            experience=request.form['experience'],
            student_id=current_user.id
        )
        db.session.add(exp)
        db.session.commit()
        flash('Interview experience shared!', 'success')
        return redirect(url_for('student_dashboard'))
    return render_template('add_experience.html')

@app.route('/upvote/<int:exp_id>')
@login_required
def upvote(exp_id):
    exp = InterviewExperience.query.get_or_404(exp_id)
    exp.upvotes += 1
    db.session.commit()
    return redirect(request.referrer or url_for('student_dashboard'))

@app.route('/downvote/<int:exp_id>')
@login_required
def downvote(exp_id):
    exp = InterviewExperience.query.get_or_404(exp_id)
    exp.downvotes += 1
    db.session.commit()
    return redirect(request.referrer or url_for('student_dashboard'))

@app.route('/send_test/<int:app_id>')
@login_required
def send_test(app_id):
    return redirect(url_for('update_status', app_id=app_id, status='Test Sent'))



@app.route('/get_student/<int:student_id>')
@login_required
def get_student(student_id):
    if current_user.role not in ['tpo', 'HR']:
        return {'error': 'Unauthorized'}, 403
    student = User.query.get_or_404(student_id)
    if student.role != 'student':
        return {'error': 'Not a student'}, 404
    return {
        'id': student.id,
        'name': student.name,
        'rollno': student.rollno,
        'cgpa': student.cgpa,
        'branch': student.branch,
        'semester': student.semester,
        'phone_number': student.phone_number,
        'address': student.address,
        'linkedin_profile': student.linkedin_profile,
        'github_profile': student.github_profile,
        'skills': student.skills,
        'projects': student.projects,
        'certificates': student.certificates,
        'achievements': student.achievements,
        'resume_filename': student.resume_filename,
        'photo_filename': student.photo_filename
    }



# ==========================================
# == VERIFICATION ROUTES (NEW)
# ==========================================
@app.route('/approve_user/<int:user_id>')
@login_required
def approve_user(user_id):
    if current_user.role != 'tpo':
        flash('Not authorized.', 'error')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    if user.role not in ['student', 'HR']:
        flash('Invalid user type.', 'error')
        return redirect(url_for('tpo_dashboard'))
    user.is_verified = True
    db.session.commit()
    flash(f'{user.name} ({user.role}) has been approved.', 'success')
    return redirect(url_for('tpo_dashboard'))

@app.route('/reject_user/<int:user_id>')
@login_required
def reject_user(user_id):
    if current_user.role != 'tpo':
        flash('Not authorized.', 'error')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    if user.role not in ['student', 'HR']:
        flash('Invalid user type.', 'error')
        return redirect(url_for('tpo_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash(f'{user.name} ({user.role}) registration has been rejected and removed.', 'success')
    return redirect(url_for('tpo_dashboard'))

# ==========================================
# == NOTIFICATION ROUTES
# ==========================================
@app.route('/notifications')
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return {
        'notifications': [
            {
                'id': n.id,
                'message': n.message,
                'is_read': n.is_read,
                'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for n in notifications
        ]
    }

@app.route('/mark_notification_read/<int:notif_id>')
@login_required
def mark_notification_read(notif_id):
    notification = Notification.query.get_or_404(notif_id)
    if notification.user_id != current_user.id:
        return {'error': 'Unauthorized'}, 403
    notification.is_read = True
    db.session.commit()
    return {'success': True}



# ==========================================
# == MAIN RUN
# ==========================================
if __name__ == '__main__':
    with app.app_context():
        create_db()
        create_upload_dirs()
    app.run(debug=True)