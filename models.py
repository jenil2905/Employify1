from datetime import datetime
from flask_login import UserMixin
from mongoengine import Document, StringField, DateTimeField, ReferenceField, IntField, FloatField, BooleanField, ListField, EmbeddedDocument, EmbeddedDocumentField
from werkzeug.security import generate_password_hash, check_password_hash

def get_utc_now():
    """Get current time in UTC."""
    return datetime.utcnow()

class User(UserMixin, Document):
    username = StringField(unique=True, required=True)
    email = StringField(unique=True, required=True)
    password_hash = StringField(required=True)
    registration_date = DateTimeField(default=get_utc_now)
    points = IntField(default=0)
    last_login_date = DateTimeField(default=get_utc_now)
    profile_photo = StringField()
    full_name = StringField()
    course = StringField()
    university = StringField()
    marks_10th = FloatField()
    marks_12th = FloatField()
    current_cgpa = FloatField()
    address = StringField()
    contact_number = StringField()
    whatsapp_number = StringField()
    parents_contact = StringField()
    profile_completed = BooleanField(default=False)
    skills = StringField()
    experience = FloatField(default=0.0)
    preferred_job_type = StringField()
    preferred_location = StringField()
    resume_url = StringField()
    job_applications = ListField(ReferenceField('JobApplication'))

    def get_id(self):
        return str(self.id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def add_points(self, points):
        self.points += points
        self.save()

    def add_daily_points(self):
        today = datetime.utcnow().date()
        if self.last_login_date.date() < today:
            self.add_points(10)
            self.last_login_date = datetime.utcnow()
            self.save()

    def get_skills(self):
        return [skill.strip() for skill in self.skills.split(',')] if self.skills else []

class Job(Document):
    title = StringField(required=True)
    company = StringField(required=True)
    description = StringField(required=True)
    requirements = StringField(required=True)
    location = StringField(required=True)
    salary = StringField()
    posted_date = DateTimeField(default=get_utc_now)
    employer = ReferenceField('User', required=True)
    required_skills = StringField()
    job_type = StringField()
    experience_required = FloatField(default=0.0)
    education_required = StringField()
    application_deadline = DateTimeField()
    is_active = BooleanField(default=True)
    applications = ListField(ReferenceField('JobApplication'))

    def get_required_skills(self):
        return [skill.strip() for skill in self.required_skills.split(',')] if self.required_skills else []

class JobApplication(Document):
    job = ReferenceField('Job', required=True)
    applicant = ReferenceField('User', required=True)
    status = StringField(default='pending')
    applied_date = DateTimeField(default=get_utc_now)
    cover_letter = StringField()
    resume_url = StringField()
    last_updated = DateTimeField(default=get_utc_now)

class CodeChallenge(Document):
    title = StringField(required=True)
    description = StringField(required=True)
    difficulty = StringField(required=True)
    points = IntField(default=0)
    test_cases = StringField()
    solution = StringField()
    created_at = DateTimeField(default=get_utc_now)

class ChallengeSubmission(Document):
    user = ReferenceField('User', required=True)
    challenge = ReferenceField('CodeChallenge', required=True)
    code = StringField(required=True)
    status = StringField(required=True)
    score = IntField(default=0)
    submitted_at = DateTimeField(default=get_utc_now)

class Education(EmbeddedDocument):
    level = StringField()
    institution_name = StringField()
    percentage = FloatField()
    year = IntField()
    marksheet_path = StringField()
    degree = StringField()

class Certificate(Document):
    user_id = StringField(required=True)
    organization = StringField(required=True)
    certificate_name = StringField(required=True)
    date = DateTimeField(required=True)
    description = StringField(required=True)
    certificate_file = StringField(required=True)  # Path to the stored certificate file
    created_at = DateTimeField(default=get_utc_now)
    updated_at = DateTimeField(default=get_utc_now)

    meta = {
        'collection': 'certificates',
        'indexes': [
            'user_id',
            'organization',
            'certificate_name',
            'date'
        ]
    }

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = get_utc_now()
        self.updated_at = get_utc_now()
        return super(Certificate, self).save(*args, **kwargs)

class Resume(Document):
    user_id = IntField(required=True)
    name = StringField(required=True)
    contact = StringField(required=True)
    email = StringField(required=True)
    linkedin = StringField()
    photo_path = StringField()
    skills = StringField()
    interests = StringField()
    about = StringField()
    summary = StringField()
    created_at = DateTimeField(default=get_utc_now)
    education = ListField(EmbeddedDocumentField(Education))
    certificates = ListField(EmbeddedDocumentField(Certificate))
