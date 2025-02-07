    // Create and switch to employify database
use('employify');

// Drop existing collections if they exist
db.users.drop();
db.jobs.drop();
db.jobApplications.drop();
db.codeChallenges.drop();
db.challengeSubmissions.drop();

// Create users collection with validation
db.createCollection('users', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['username', 'email', 'password_hash'],
            properties: {
                username: {
                    bsonType: 'string',
                    description: 'Username must be a string and is required'
                },
                email: {
                    bsonType: 'string',
                    pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$',
                    description: 'Email must be a valid email address and is required'
                },
                password_hash: {
                    bsonType: 'string',
                    description: 'Password hash must be a string and is required'
                },
                registration_date: {
                    bsonType: 'date',
                    description: 'Registration date must be a date'
                },
                points: {
                    bsonType: 'int',
                    minimum: 0,
                    description: 'Points must be a non-negative integer'
                },
                profile_completed: {
                    bsonType: 'bool',
                    description: 'Profile completed status must be a boolean'
                }
            }
        }
    }
});

// Create jobs collection with validation
db.createCollection('jobs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['title', 'company', 'description', 'requirements', 'location'],
            properties: {
                title: {
                    bsonType: 'string',
                    description: 'Job title must be a string and is required'
                },
                company: {
                    bsonType: 'string',
                    description: 'Company name must be a string and is required'
                },
                description: {
                    bsonType: 'string',
                    description: 'Job description must be a string and is required'
                },
                requirements: {
                    bsonType: 'string',
                    description: 'Job requirements must be a string and is required'
                },
                location: {
                    bsonType: 'string',
                    description: 'Job location must be a string and is required'
                },
                salary: {
                    bsonType: 'string',
                    description: 'Salary must be a string'
                },
                posted_date: {
                    bsonType: 'date',
                    description: 'Posted date must be a date'
                },
                is_active: {
                    bsonType: 'bool',
                    description: 'Active status must be a boolean'
                }
            }
        }
    }
});

// Create job applications collection with validation
db.createCollection('jobApplications', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['job_id', 'applicant_id', 'status', 'applied_date'],
            properties: {
                job_id: {
                    bsonType: 'objectId',
                    description: 'Job ID must be an ObjectId and is required'
                },
                applicant_id: {
                    bsonType: 'objectId',
                    description: 'Applicant ID must be an ObjectId and is required'
                },
                status: {
                    bsonType: 'string',
                    enum: ['pending', 'accepted', 'rejected'],
                    description: 'Status must be one of: pending, accepted, rejected'
                },
                applied_date: {
                    bsonType: 'date',
                    description: 'Applied date must be a date'
                }
            }
        }
    }
});

// Create code challenges collection with validation
db.createCollection('codeChallenges', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['title', 'description', 'difficulty', 'points'],
            properties: {
                title: {
                    bsonType: 'string',
                    description: 'Challenge title must be a string and is required'
                },
                description: {
                    bsonType: 'string',
                    description: 'Challenge description must be a string and is required'
                },
                difficulty: {
                    bsonType: 'string',
                    enum: ['easy', 'medium', 'hard'],
                    description: 'Difficulty must be one of: easy, medium, hard'
                },
                points: {
                    bsonType: 'int',
                    minimum: 0,
                    description: 'Points must be a non-negative integer'
                }
            }
        }
    }
});

// Create challenge submissions collection with validation
db.createCollection('challengeSubmissions', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['user_id', 'challenge_id', 'code', 'status', 'submitted_at'],
            properties: {
                user_id: {
                    bsonType: 'objectId',
                    description: 'User ID must be an ObjectId and is required'
                },
                challenge_id: {
                    bsonType: 'objectId',
                    description: 'Challenge ID must be an ObjectId and is required'
                },
                code: {
                    bsonType: 'string',
                    description: 'Submitted code must be a string and is required'
                },
                status: {
                    bsonType: 'string',
                    enum: ['pending', 'passed', 'failed'],
                    description: 'Status must be one of: pending, passed, failed'
                },
                submitted_at: {
                    bsonType: 'date',
                    description: 'Submission date must be a date'
                }
            }
        }
    }
});

// Create indexes for better query performance
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });
db.jobs.createIndex({ "posted_date": -1 });
db.jobs.createIndex({ "company": 1 });
db.jobApplications.createIndex({ "job_id": 1 });
db.jobApplications.createIndex({ "applicant_id": 1 });
db.codeChallenges.createIndex({ "difficulty": 1 });
db.challengeSubmissions.createIndex({ "user_id": 1 });
db.challengeSubmissions.createIndex({ "challenge_id": 1 });

// Insert a sample user
db.users.insertOne({
    username: "test_user",
    email: "test@example.com",
    password_hash: "hashed_password",
    registration_date: new Date(),
    points: 0,
    profile_completed: false
});

print("Database setup completed successfully!");
