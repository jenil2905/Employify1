import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from datetime import datetime, timedelta, timezone
import pytz
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.urls import url_parse
import logging
import random
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Regexp

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employify.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Certificate upload configuration
CERTIFICATE_UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'certificates')
CERTIFICATE_ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

app.config['CERTIFICATE_UPLOAD_FOLDER'] = CERTIFICATE_UPLOAD_FOLDER

# Create upload folder if it doesn't exist
os.makedirs(CERTIFICATE_UPLOAD_FOLDER, exist_ok=True)

def allowed_certificate_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in CERTIFICATE_ALLOWED_EXTENSIONS

# User Model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    points = db.Column(db.Integer, default=0)
    last_login_date = db.Column(db.DateTime, default=datetime.utcnow)
    profile_photo = db.Column(db.String(200))
    full_name = db.Column(db.String(100))
    course = db.Column(db.String(100))
    university = db.Column(db.String(100))
    marks_10th = db.Column(db.Float)
    marks_12th = db.Column(db.Float)
    current_cgpa = db.Column(db.Float)
    address = db.Column(db.Text)
    contact_number = db.Column(db.String(15))
    whatsapp_number = db.Column(db.String(15))
    parents_contact = db.Column(db.String(15))
    profile_completed = db.Column(db.Boolean, default=False)
    skills = db.Column(db.Text)
    experience = db.Column(db.Float, default=0.0)
    preferred_job_type = db.Column(db.String(50))
    preferred_location = db.Column(db.String(100))
    resume_url = db.Column(db.String(200))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

# Certificate Model
class Certificate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organization = db.Column(db.String(100), nullable=False)
    certificate_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    certificate_file = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except ValueError:
        # If we can't convert the user_id to int, the user doesn't exist
        return None

# Create all database tables
with app.app_context():
    db.create_all()

# File upload configuration
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Job Model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(100))
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    employer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    required_skills = db.Column(db.Text)
    job_type = db.Column(db.String(50))
    experience_required = db.Column(db.Float, default=0.0)
    education_required = db.Column(db.String(100))
    application_deadline = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

# Job Application Model
class JobApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), default='pending')
    applied_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_letter = db.Column(db.Text)
    resume_url = db.Column(db.String(200))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Code Challenge Model
class CodeChallenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(50), nullable=False)
    points = db.Column(db.Integer, default=0)
    test_cases = db.Column(db.Text)
    solution = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Challenge Submission Model
class ChallengeSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('code_challenge.id'), nullable=False)
    code = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

# Resume Builder Models
class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resume.id'), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    institution_name = db.Column(db.String(100), nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    marksheet_path = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(100))

class Resume(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    linkedin = db.Column(db.String(100))
    photo_path = db.Column(db.String(200))
    skills = db.Column(db.Text)
    interests = db.Column(db.Text)
    about = db.Column(db.Text)
    summary = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    education = db.relationship('Education', backref='resume', lazy=True)

# Interview questions for different levels
INTERVIEW_QUESTIONS = {
    'basic': [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Why do you want to work in this field?",
        "Where do you see yourself in 5 years?",
        "What is your greatest achievement?",
    ],
    'intermediate': [
        "Describe a challenging project you worked on.",
        "How do you handle conflicts in a team?",
        "Explain your problem-solving approach.",
        "What's your experience with agile methodologies?",
        "How do you stay updated with industry trends?",
    ],
    'tough': [
        "Describe a time you had to make a difficult technical decision.",
        "How would you improve our current product?",
        "How do you handle tight deadlines and pressure?",
        "What's your approach to system design and scalability?",
        "How do you ensure code quality and maintainability?",
    ]
}

# Required perks for each level
INTERVIEW_PERKS = {
    'basic': 100,
    'intermediate': 200,
    'tough': 350
}

# Interview session management
class InterviewSession:
    def __init__(self, level):
        self.level = level
        self.questions = INTERVIEW_QUESTIONS[level].copy()
        self.current_question_index = 0
        self.responses = []
        self.score = 0
        random.shuffle(self.questions)

    def get_current_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def add_response(self, response):
        self.responses.append(response)
        self.current_question_index += 1
        # Simple scoring based on response length and keywords
        score = min(len(response.split()) / 10, 5)  # Up to 5 points for length
        keywords = ['experience', 'project', 'team', 'learn', 'improve', 'success', 'challenge']
        score += sum(2 for keyword in keywords if keyword.lower() in response.lower())  # 2 points per keyword
        self.score += min(score, 10)  # Cap score at 10 points per answer

    def is_complete(self):
        return self.current_question_index >= len(self.questions)

    def get_final_score(self):
        return int(self.score)

# Profile Form
class ProfileForm(FlaskForm):
    profile_photo = FileField('Profile Photo')
    full_name = StringField('Full Name', validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()])
    university = StringField('University', validators=[DataRequired()])
    marks_10th = DecimalField('10th Marks', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message='10th marks must be between 0 and 100')
    ])
    marks_12th = DecimalField('12th Marks', validators=[
        DataRequired(),
        NumberRange(min=0, max=100, message='12th marks must be between 0 and 100')
    ])
    current_cgpa = DecimalField('Current CGPA', validators=[
        DataRequired(),
        NumberRange(min=0, max=10, message='CGPA must be between 0 and 10')
    ])
    address = TextAreaField('Address', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='Contact number must be 10 digits')
    ])
    whatsapp_number = StringField('WhatsApp Number', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='WhatsApp number must be 10 digits')
    ])
    parents_contact = StringField('Parents Contact', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='Parents contact must be 10 digits')
    ])

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.last_login_date = datetime.utcnow()
            db.session.commit()
            
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        logger.debug(f"Registration attempt for username: {username}, email: {email}")
        
        if User.query.filter_by(username=username).first():
            logger.debug("Username already exists")
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            logger.debug("Email already registered")
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            logger.debug("User registered successfully")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/jobs')
def jobs():
    search_query = request.args.get('q', '')
    location = request.args.get('location', '')
    job_type = request.args.get('type', '')
    
    query = Job.query.filter_by(is_active=True)
    
    if search_query:
        query = query.filter(
            db.or_(
                Job.title.like(f'%{search_query}%'),
                Job.description.like(f'%{search_query}%'),
                Job.required_skills.like(f'%{search_query}%')
            )
        )
    
    if location:
        query = query.filter(Job.location.like(f'%{location}%'))
    
    if job_type:
        query = query.filter_by(job_type=job_type)
    
    jobs = query.order_by(Job.posted_date.desc())
    return render_template('jobs.html', jobs=jobs)

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        new_job = Job(
            title=request.form.get('title'),
            company=request.form.get('company'),
            description=request.form.get('description'),
            requirements=request.form.get('requirements'),
            location=request.form.get('location'),
            salary=request.form.get('salary'),
            employer_id=current_user.id
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('jobs'))
    return render_template('post_job.html')

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('job_detail.html', job=job)

@app.route('/perks')
@login_required
def perks():
    # Calculate points from completed challenges
    base_points = current_user.points  # Get points earned from challenges
    profile_points = 30 if current_user.profile_completed else 0
    total_points = base_points + profile_points

    # Define interview levels
    interview_levels = [
        {
            'name': 'Basic',
            'required_points': 100,
            'available': total_points >= 100,
            'points_needed': max(0, 100 - total_points),
            'stars': 1,
            'color': '#FFD700'  # Gold color
        },
        {
            'name': 'Intermediate',
            'required_points': 200,
            'available': total_points >= 200,
            'points_needed': max(0, 200 - total_points),
            'stars': 2,
            'color': '#C0C0C0'  # Silver color
        },
        {
            'name': 'Hard',
            'required_points': 350,
            'available': total_points >= 350,
            'points_needed': max(0, 350 - total_points),
            'stars': 3,
            'color': '#CD7F32'  # Bronze color
        }
    ]
    
    return render_template('perks.html',
                         total_points=total_points,
                         base_points=base_points,
                         profile_points=profile_points,
                         interview_levels=interview_levels)

@app.route('/interview/<level>')
@login_required
def interview(level):
    if level not in INTERVIEW_QUESTIONS:
        flash('Invalid interview level', 'error')
        return redirect(url_for('perks'))
    
    required_perks = INTERVIEW_PERKS[level]
    has_access = current_user.points >= required_perks
    
    if not has_access:
        flash(f'You need {required_perks} perks to access this interview level', 'warning')
        return render_template('interview.html', 
                             level=level,
                             has_access=False,
                             current_perks=current_user.points,
                             required_perks=required_perks)
    
    # Initialize or get existing interview session
    if 'interview_session' not in session:
        session['interview_session'] = InterviewSession(level).__dict__
    
    interview_session = InterviewSession(level)
    interview_session.__dict__ = session['interview_session']
    
    messages = []
    if not interview_session.is_complete():
        current_question = interview_session.get_current_question()
        messages.append({
            'sender': 'ai',
            'content': current_question,
            'time': datetime.utcnow().strftime('%H:%M')
        })
    
    return render_template('interview.html',
                         level=level,
                         has_access=True,
                         current_perks=current_user.points,
                         required_perks=required_perks,
                         messages=messages)

@app.route('/interview/respond', methods=['POST'])
@login_required
def interview_respond():
    data = request.get_json()
    if not data or 'message' not in data or 'level' not in data:
        return jsonify({'error': 'Invalid request'}), 400
    
    if 'interview_session' not in session:
        return jsonify({'error': 'No active interview session'}), 400
    
    interview_session = InterviewSession(data['level'])
    interview_session.__dict__ = session['interview_session']
    
    # Process the response
    interview_session.add_response(data['message'])
    session['interview_session'] = interview_session.__dict__
    
    if interview_session.is_complete():
        # Interview complete - award points
        final_score = interview_session.get_final_score()
        points_earned = final_score * 2  # 2 points per score point
        current_user.points += points_earned
        db.session.commit()
        session.pop('interview_session', None)
        return jsonify({
            'response': f'Interview complete! You earned {points_earned} points based on your performance.',
            'complete': True
        })
    
    # Get next question
    next_question = interview_session.get_current_question()
    
    # Generate AI feedback based on the previous response
    feedback = generate_interview_feedback(data['message'])
    response = f"{feedback}\n\nNext question: {next_question}"
    
    return jsonify({'response': response})

def generate_interview_feedback(response):
    """Generate simple feedback based on the response."""
    feedback = []
    
    # Length-based feedback
    words = len(response.split())
    if words < 20:
        feedback.append("Try to provide more detailed responses.")
    elif words > 100:
        feedback.append("Good detailed response!")
    
    # Content-based feedback
    keywords = ['experience', 'project', 'team', 'learn', 'improve', 'success', 'challenge']
    used_keywords = [k for k in keywords if k.lower() in response.lower()]
    
    if used_keywords:
        feedback.append(f"Good use of key terms: {', '.join(used_keywords)}!")
    
    if not feedback:
        feedback.append("Thank you for your response.")
    
    return ' '.join(feedback)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if form.validate_on_submit():
        try:
            # Handle profile photo upload
            if form.profile_photo.data:
                file = form.profile_photo.data
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    # Delete old profile photo if it exists
                    if current_user.profile_photo:
                        old_photo_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.profile_photo)
                        if os.path.exists(old_photo_path):
                            os.remove(old_photo_path)
                    current_user.profile_photo = filename

            # Update user profile
            current_user.full_name = form.full_name.data
            current_user.course = form.course.data
            current_user.university = form.university.data
            current_user.marks_10th = float(form.marks_10th.data)
            current_user.marks_12th = float(form.marks_12th.data)
            current_user.current_cgpa = float(form.current_cgpa.data)
            current_user.address = form.address.data
            current_user.contact_number = form.contact_number.data
            current_user.whatsapp_number = form.whatsapp_number.data
            current_user.parents_contact = form.parents_contact.data
            current_user.profile_completed = True

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))

        except Exception as e:
            flash(f'Error updating profile: {str(e)}', 'error')
            app.logger.error(f"Profile update error: {str(e)}")
            return render_template('profile.html', form=form)

    # For both GET requests and failed form submissions
    if request.method == 'GET' and current_user.profile_completed:
        # Pre-fill form with existing data
        form.full_name.data = current_user.full_name
        form.course.data = current_user.course
        form.university.data = current_user.university
        form.marks_10th.data = current_user.marks_10th
        form.marks_12th.data = current_user.marks_12th
        form.current_cgpa.data = current_user.current_cgpa
        form.address.data = current_user.address
        form.contact_number.data = current_user.contact_number
        form.whatsapp_number.data = current_user.whatsapp_number
        form.parents_contact.data = current_user.parents_contact

    return render_template('profile.html', form=form)

# Add profile link check to navbar
@app.context_processor
def inject_profile_status():
    if current_user.is_authenticated:
        return {'profile_completed': current_user.profile_completed}
    return {'profile_completed': False}

@app.route('/challenges')
@app.route('/challenges/<level>')
@login_required
def challenges(level=None):
    if level:
        if level not in ['basic', 'intermediate', 'tough']:
            flash('Invalid difficulty level', 'danger')
            return redirect(url_for('challenges'))
            
        challenges = CodeChallenge.query.filter_by(difficulty=level).order_by(CodeChallenge.created_at.desc()).all()
        return render_template('challenge_list.html', challenges=challenges, level=level)
    
    return render_template('challenges.html')

@app.route('/challenge/<int:challenge_id>')
@login_required
def challenge_detail(challenge_id):
    challenge = CodeChallenge.query.get(challenge_id)
    user_submission = ChallengeSubmission.query.filter_by(
        user_id=current_user.id,
        challenge_id=challenge_id
    ).order_by(ChallengeSubmission.submitted_at.desc()).first()
    
    return render_template('challenge_detail.html', challenge=challenge, submission=user_submission)

@app.route('/challenge/<int:challenge_id>/submit', methods=['POST'])
@login_required
def submit_challenge(challenge_id):
    challenge = CodeChallenge.query.get(challenge_id)
    code = request.form.get('code')
    
    if not code:
        flash('Please provide your solution', 'danger')
        return redirect(url_for('challenge_detail', challenge_id=challenge_id))
    
    # Here you would typically:
    # 1. Run the code against test cases
    # 2. Calculate the score
    # 3. Update user points if passed
    
    submission = ChallengeSubmission(
        user_id=current_user.id,
        challenge_id=challenge_id,
        code=code,
        status='pending',  # You would update this based on test results
        score=0  # You would calculate this based on test results
    )
    
    db.session.add(submission)
    db.session.commit()
    
    flash('Your solution has been submitted!', 'success')
    return redirect(url_for('challenge_detail', challenge_id=challenge_id))

@app.route('/jobs/matched')
@login_required
def matched_jobs():
    user_skills = current_user.skills.split(',')
    user_location = current_user.preferred_location
    user_job_type = current_user.preferred_job_type
    
    # Get all active jobs
    query = Job.query.filter_by(is_active=True)
    
    # Filter by location if user has preference
    if user_location:
        query = query.filter(Job.location.like(f'%{user_location}%'))
    
    # Filter by job type if user has preference
    if user_job_type:
        query = query.filter_by(job_type=user_job_type)
    
    jobs = query.all()
    
    # Calculate match score for each job
    matched_jobs = []
    for job in jobs:
        required_skills = job.required_skills.split(',')
        matching_skills = set(user_skills) & set(required_skills)
        match_score = len(matching_skills) / len(required_skills) if required_skills else 0
        
        if match_score > 0:  # Only include jobs with at least one matching skill
            matched_jobs.append({
                'job': job,
                'match_score': match_score,
                'matching_skills': list(matching_skills)
            })
    
    # Sort by match score
    matched_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return render_template('matched_jobs.html', matched_jobs=matched_jobs)

@app.route('/jobs/<int:job_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_job(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if user has already applied
    existing_application = JobApplication.query.filter_by(
        job_id=job_id,
        applicant_id=current_user.id
    ).first()
    
    if existing_application:
        flash('You have already applied for this job!', 'info')
        return redirect(url_for('job_detail', job_id=job_id))
    
    if request.method == 'POST':
        application = JobApplication(
            job_id=job_id,
            applicant_id=current_user.id,
            cover_letter=request.form.get('cover_letter'),
            resume_url=current_user.resume_url
        )
        
        db.session.add(application)
        db.session.commit()
        
        flash('Your application has been submitted successfully!', 'success')
        return redirect(url_for('job_detail', job_id=job_id))
    
    return render_template('apply_job.html', job=job)

@app.route('/applications')
@login_required
def my_applications():
    applications = JobApplication.query.filter_by(applicant_id=current_user.id)\
        .order_by(JobApplication.applied_date.desc())
    return render_template('my_applications.html', applications=applications)

@app.route('/jobs/<job_id>/applications')
@login_required
def job_applications(job_id):
    job = Job.query.get_or_404(job_id)
    
    # Check if current user is the employer
    if job.employer_id != current_user.id:
        flash('You are not authorized to view these applications.', 'error')
        return redirect(url_for('jobs'))
    
    applications = JobApplication.query.filter_by(job_id=job_id)\
        .order_by(JobApplication.applied_date.desc())
    return render_template('job_applications.html', job=job, applications=applications)

@app.route('/applications/<int:application_id>/update-status', methods=['POST'])
@login_required
def update_application_status(application_id):
    application = JobApplication.query.get_or_404(application_id)
    job = application.job
    
    # Check if current user is the employer
    if job.employer_id != current_user.id:
        flash('You are not authorized to update this application.', 'error')
        return redirect(url_for('jobs'))
    
    new_status = request.form.get('status')
    if new_status in ['pending', 'accepted', 'rejected']:
        application.status = new_status
        db.session.commit()
        flash('Application status updated successfully!', 'success')
    
    return redirect(url_for('job_applications', job_id=job.id))

@app.route('/resume-builder', methods=['GET', 'POST'])
@login_required
def resume_builder():
    if request.method == 'POST':
        try:
            # Create resume entry
            resume = Resume(
                user_id=current_user.id,
                name=request.form['name'],
                contact=request.form['contact'],
                email=request.form['email'],
                linkedin=request.form['linkedin'],
                skills=request.form['skills'],
                interests=request.form['interests'],
                about=request.form['about'],
                summary=request.form['summary']
            )

            # Handle photo upload
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo.filename:
                    filename = secure_filename(f"{current_user.id}_photo_{int(datetime.utcnow().timestamp())}{os.path.splitext(photo.filename)[1]}")
                    photo_path = os.path.join('static', 'uploads', 'photos', filename)
                    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
                    photo.save(photo_path)
                    resume.photo_path = photo_path

            db.session.add(resume)
            db.session.commit()

            # Handle 10th education
            tenth_marksheet = request.files['tenth_marksheet']
            if tenth_marksheet.filename:
                filename = secure_filename(f"{current_user.id}_10th_{int(datetime.utcnow().timestamp())}{os.path.splitext(tenth_marksheet.filename)[1]}")
                marksheet_path = os.path.join('static', 'uploads', 'marksheets', filename)
                os.makedirs(os.path.dirname(marksheet_path), exist_ok=True)
                tenth_marksheet.save(marksheet_path)
                
                education_10th = Education(
                    user_id=current_user.id,
                    resume_id=resume.id,
                    level='10th',
                    institution_name=request.form['tenth_school'],
                    percentage=float(request.form['tenth_percentage']),
                    year=int(request.form['tenth_year']),
                    marksheet_path=marksheet_path
                )
                db.session.add(education_10th)

            # Handle 12th education
            twelfth_marksheet = request.files['twelfth_marksheet']
            if twelfth_marksheet.filename:
                filename = secure_filename(f"{current_user.id}_12th_{int(datetime.utcnow().timestamp())}{os.path.splitext(twelfth_marksheet.filename)[1]}")
                marksheet_path = os.path.join('static', 'uploads', 'marksheets', filename)
                os.makedirs(os.path.dirname(marksheet_path), exist_ok=True)
                twelfth_marksheet.save(marksheet_path)
                
                education_12th = Education(
                    user_id=current_user.id,
                    resume_id=resume.id,
                    level='12th',
                    institution_name=request.form['twelfth_school'],
                    percentage=float(request.form['twelfth_percentage']),
                    year=int(request.form['twelfth_year']),
                    marksheet_path=marksheet_path
                )
                db.session.add(education_12th)

            # Handle college education (multiple entries possible)
            college_names = request.form.getlist('college_name[]')
            college_degrees = request.form.getlist('college_degree[]')
            college_cgpas = request.form.getlist('college_cgpa[]')
            college_years = request.form.getlist('college_year[]')
            college_marksheets = request.files.getlist('college_marksheet[]')

            for i in range(len(college_names)):
                if college_marksheets[i].filename:
                    filename = secure_filename(f"{current_user.id}_college_{i}_{int(datetime.utcnow().timestamp())}{os.path.splitext(college_marksheets[i].filename)[1]}")
                    marksheet_path = os.path.join('static', 'uploads', 'marksheets', filename)
                    os.makedirs(os.path.dirname(marksheet_path), exist_ok=True)
                    college_marksheets[i].save(marksheet_path)
                    
                    college_edu = Education(
                        user_id=current_user.id,
                        resume_id=resume.id,
                        level='college',
                        institution_name=college_names[i],
                        degree=college_degrees[i],
                        percentage=float(college_cgpas[i]),
                        year=int(college_years[i]),
                        marksheet_path=marksheet_path
                    )
                    db.session.add(college_edu)

            db.session.commit()
            flash('Resume created successfully!', 'success')
            return redirect(url_for('dashboard'))

        except Exception as e:
            flash(f'Error creating resume: {str(e)}', 'danger')
            return redirect(url_for('resume_builder'))

    return render_template('resume_builder.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent activities (you can customize this based on your needs)
    activities = []  # You can populate this with actual user activities
    return render_template('dashboard.html', activities=activities)

@app.route('/certificates', methods=['GET', 'POST'])
@login_required
def certificates():
    if request.method == 'POST':
        # Check if all required fields are present
        if not all(field in request.form for field in ['organization', 'certificate_name', 'date', 'description']):
            flash('Please fill all required fields', 'danger')
            return redirect(url_for('certificates'))

        # Check if file was uploaded
        if 'certificate_file' not in request.files:
            flash('No file uploaded', 'danger')
            return redirect(url_for('certificates'))

        file = request.files['certificate_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('certificates'))

        if file and allowed_certificate_file(file.filename):
            try:
                # Secure the filename and save the file
                filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                file_path = os.path.join(app.config['CERTIFICATE_UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Create certificate entry in database
                new_certificate = Certificate(
                    user_id=current_user.id,
                    organization=request.form['organization'],
                    certificate_name=request.form['certificate_name'],
                    date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                    description=request.form['description'],
                    certificate_file=f"certificates/{filename}"
                )
                db.session.add(new_certificate)
                db.session.commit()

                flash('Certificate added successfully!', 'success')
                return redirect(url_for('certificates'))
            except Exception as e:
                flash(f'Error saving certificate: {str(e)}', 'danger')
                return redirect(url_for('certificates'))
        else:
            flash('Invalid file type. Please upload PDF, JPG, or PNG files only.', 'danger')
            return redirect(url_for('certificates'))

    # GET request - display certificates
    try:
        user_certificates = Certificate.query.filter_by(user_id=current_user.id).order_by(Certificate.date.desc()).all()
        return render_template('certificates.html', certificates=user_certificates)
    except Exception as e:
        flash(f'Error loading certificates: {str(e)}', 'danger')
        return render_template('certificates.html', certificates=[])

if __name__ == '__main__':
    # Use environment variables for host and port
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
