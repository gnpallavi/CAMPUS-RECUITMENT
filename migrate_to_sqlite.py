import mysql.connector
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Job, Application, InterviewExperience, MCQTest, MCQQuestion, Course
import os

# MySQL connection details (update as needed)
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Pavank%405214',
    'database': 'placement_db'
}

# Create Flask app for SQLite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/placement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_data():
    # Connect to MySQL
    mysql_conn = mysql.connector.connect(**MYSQL_CONFIG)
    mysql_cursor = mysql_conn.cursor(dictionary=True)

    with app.app_context():
        # Create SQLite tables
        db.create_all()

        # Migrate Users
        mysql_cursor.execute("SELECT * FROM user")
        users = mysql_cursor.fetchall()
        for user in users:
            new_user = User(
                id=user['id'],
                password=user['password'],
                first_name=user['first_name'],
                last_name=user['last_name'],
                role=user['role'],
                is_verified=user['is_verified'],
                rollno=user['rollno'],
                cgpa=user['cgpa'],
                branch=user['branch'],
                semester=user['semester'],
                resume_filename=user['resume_filename'],
                photo_filename=user['photo_filename'],
                phone_number=user['phone_number'],
                address=user['address'],
                linkedin_profile=user['linkedin_profile'],
                github_profile=user['github_profile'],
                skills=user['skills'],
                projects=user['projects'],
                certificates=user['certificates'],
                achievements=user['achievements'],
                employer_id=user['employer_id'],
                company_name=user['company_name'],
                email=user['email'],
                website=user['website'],
                company_description=user['company_description']
            )
            db.session.add(new_user)

        # Migrate Jobs
        mysql_cursor.execute("SELECT * FROM job")
        jobs = mysql_cursor.fetchall()
        for job in jobs:
            new_job = Job(
                id=job['id'],
                title=job['title'],
                company=job['company'],
                salary=job['salary'],
                min_cgpa=job['min_cgpa'],
                branches=job['branches'],
                posted_by_id=job['posted_by_id'],
                created_at=job['created_at']
            )
            db.session.add(new_job)

        # Migrate Applications
        mysql_cursor.execute("SELECT * FROM application")
        applications = mysql_cursor.fetchall()
        for app in applications:
            new_app = Application(
                id=app['id'],
                status=app['status'],
                marks=app['marks'],
                applied_at=app['applied_at'],
                student_id=app['student_id'],
                job_id=app['job_id']
            )
            db.session.add(new_app)

        # Migrate InterviewExperiences
        mysql_cursor.execute("SELECT * FROM interview_experience")
        experiences = mysql_cursor.fetchall()
        for exp in experiences:
            new_exp = InterviewExperience(
                id=exp['id'],
                company=exp['company'],
                rounds=exp['rounds'],
                verdict=exp['verdict'],
                experience=exp['experience'],
                upvotes=exp['upvotes'],
                downvotes=exp['downvotes'],
                created_at=exp['created_at'],
                student_id=exp['student_id']
            )
            db.session.add(new_exp)

        # Migrate MCQTests
        mysql_cursor.execute("SELECT * FROM mcq_test")
        tests = mysql_cursor.fetchall()
        for test in tests:
            new_test = MCQTest(
                id=test['id'],
                job_id=test['job_id'],
                created_at=test['created_at']
            )
            db.session.add(new_test)

        # Migrate MCQQuestions
        mysql_cursor.execute("SELECT * FROM mcq_question")
        questions = mysql_cursor.fetchall()
        for q in questions:
            new_q = MCQQuestion(
                id=q['id'],
                test_id=q['test_id'],
                question_text=q['question_text'],
                option_a=q['option_a'],
                option_b=q['option_b'],
                option_c=q['option_c'],
                option_d=q['option_d'],
                correct_option=q['correct_option']
            )
            db.session.add(new_q)

        # Migrate Courses
        mysql_cursor.execute("SELECT * FROM course")
        courses = mysql_cursor.fetchall()
        for course in courses:
            new_course = Course(
                id=course['id'],
                semester=course['semester'],
                title=course['title'],
                description=course['description'],
                link=course['link'],
                created_at=course['created_at'],
                completed=course['completed'],
                notes=course['notes']
            )
            db.session.add(new_course)

        # Commit all changes
        db.session.commit()
        print("Migration completed successfully!")

    mysql_cursor.close()
    mysql_conn.close()

if __name__ == '__main__':
    migrate_data()
