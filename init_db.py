from flask import Flask
from flask_mongoengine import MongoEngine
from config import Config
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)
db = MongoEngine(app)

# Import models after db initialization
from app import User, Job, JobApplication, CodeChallenge, ChallengeSubmission

def init_db():
    with app.app_context():
        # Clear existing data
        User.objects.delete()
        Job.objects.delete()
        JobApplication.objects.delete()
        CodeChallenge.objects.delete()
        ChallengeSubmission.objects.delete()

        print("Creating sample users...")
        # Create sample user
        user = User(
            username="test_user",
            email="test@example.com",
            points=0,
            profile_completed=False
        )
        user.set_password("password123")
        user.save()

        # Create sample employer
        employer = User(
            username="employer",
            email="employer@company.com",
            points=0,
            profile_completed=True
        )
        employer.set_password("password123")
        employer.save()

        print("Creating sample job...")
        # Create sample job
        job = Job(
            title="Software Developer",
            company="Tech Corp",
            description="Looking for a talented software developer",
            requirements="Python, JavaScript, MongoDB experience required",
            location="Remote",
            salary="$80,000 - $100,000",
            employer=employer,
            required_skills="Python,JavaScript,MongoDB",
            job_type="Full-time",
            experience_required=2.0,
            education_required="Bachelor's in Computer Science",
            application_deadline=datetime.utcnow() + timedelta(days=30),
            is_active=True
        )
        job.save()

        print("Creating sample code challenge...")
        # Create sample code challenge
        challenge = CodeChallenge(
            title="Basic Python Challenge",
            description="Write a function to reverse a string",
            difficulty="basic",
            points=10,
            test_cases='{"test1": {"input": "hello", "output": "olleh"}}',
            solution="def reverse_string(s):\n    return s[::-1]"
        )
        challenge.save()

        print("Creating sample job application...")
        # Create sample job application
        application = JobApplication(
            job=job,
            applicant=user,
            status="pending",
            cover_letter="I am very interested in this position.",
            resume_url="/static/uploads/sample_resume.pdf"
        )
        application.save()

        print("Creating sample challenge submission...")
        # Create sample challenge submission
        submission = ChallengeSubmission(
            user=user,
            challenge=challenge,
            code="def reverse_string(s):\n    return s[::-1]",
            status="passed",
            score=10
        )
        submission.save()

        print("Database initialized with sample data!")

if __name__ == '__main__':
    init_db()
