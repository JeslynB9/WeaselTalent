# entry point
from db import engine
from models import Base
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from users import router as users_router
from cors_config import add_cors_middleware
import auth, recruiter, assessment
from datetime import datetime


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register signup for candidate routes
app.include_router(candidate_router)

# create all tables defined on `Base`
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import sessionmaker
from models import Base, TechnicalDomain, Course, Assessment, Level, Task
from db import engine

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Clear all data from relevant tables before inserting new data
from models import User, UserProfile, Company, Recruiter, JobRole, JobRoleRequirement, CandidateJobMatch, Interview, InterviewNote, Notification, CandidateAssessment
db.query(Notification).delete()
db.query(InterviewNote).delete()
db.query(Interview).delete()
db.query(CandidateJobMatch).delete()
db.query(JobRoleRequirement).delete()
db.query(JobRole).delete()
db.query(Recruiter).delete()
db.query(Company).delete()
db.query(CandidateAssessment).delete()
db.query(Task).delete()
db.query(Level).delete()
db.query(Assessment).delete()
db.query(Course).delete()
db.query(TechnicalDomain).delete()
db.query(UserProfile).delete()
db.query(User).delete()
db.commit()

db.commit()  # Commit the deletion

# Now insert new data (following the existing logic)

# Create domains
python_domain = TechnicalDomain(name="Python Development", description="Python programming assessments")
js_domain = TechnicalDomain(name="JavaScript Development", description="JavaScript programming assessments")
db.add(python_domain)
db.add(js_domain)
db.commit()

# Create courses
python_course = Course(domain_id=python_domain.domain_id, difficulty_level=1, description="Intro to Python - 4 levels covering basic syntax, control flow, functions, and data structures")
js_course = Course(domain_id=js_domain.domain_id, difficulty_level=1, description="Intro to JavaScript - 4 levels covering basic syntax, functions, arrays/objects, and DOM manipulation")
ds_course = Course(domain_id=python_domain.domain_id, difficulty_level=2, description="Data Structures and Algorithms - 4 levels covering algorithms, sorting, data structures, and advanced topics")
db.add(python_course)
db.add(js_course)
db.add(ds_course)
db.commit()

# Create assessments
assessment1 = Assessment(course_id=python_course.course_id, time_limit_minutes=60)
assessment2 = Assessment(course_id=js_course.course_id, time_limit_minutes=90)
assessment3 = Assessment(course_id=ds_course.course_id, time_limit_minutes=60)
db.add(assessment1)
db.add(assessment2)
db.add(assessment3)
db.commit()

# Assessment 1: Python Basics - 4 Levels
# Level 1
level1 = Level(course_id=python_course.course_id, name="Level 1: Basic Syntax", order=1)
db.add(level1)
db.commit()

task1_1 = Task(level_id=level1.level_id, type="content", title="Introduction to Python", content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms and has a vast ecosystem of libraries.", order=1)
task1_2 = Task(level_id=level1.level_id, type="content", title="Variables and Data Types", content="Variables store data values. Python has several built-in data types: integers, floats, strings, booleans, lists, tuples, and dictionaries.", order=2)
task1_3 = Task(level_id=level1.level_id, type="assessment", title="Basic Print Statement", content="Write a Python program that prints 'Hello, World!' to the console.", order=3)
task1_4 = Task(level_id=level1.level_id, type="assessment", title="Variable Assignment", content="Create variables for your name (string), age (integer), and height (float), then print them.", order=4)
db.add(task1_1)
db.add(task1_2)
db.add(task1_3)
db.add(task1_4)
db.commit()

# Level 2
level2 = Level(course_id=python_course.course_id, name="Level 2: Control Flow", order=2)
db.add(level2)
db.commit()

task2_1 = Task(level_id=level2.level_id, type="content", title="Conditional Statements", content="if, elif, and else statements allow you to execute different code based on conditions.", order=1)
task2_2 = Task(level_id=level2.level_id, type="content", title="Loops", content="for loops iterate over sequences, while loops repeat while a condition is true.", order=2)
task2_3 = Task(level_id=level2.level_id, type="assessment", title="If-Else Logic", content="Write a program that checks if a number is positive, negative, or zero and prints the result.", order=3)
task2_4 = Task(level_id=level2.level_id, type="assessment", title="For Loop Practice", content="Write a for loop that prints numbers from 1 to 10.", order=4)
db.add(task2_1)
db.add(task2_2)
db.add(task2_3)
db.add(task2_4)
db.commit()

# Level 3
level3 = Level(course_id=python_course.course_id, name="Level 3: Functions", order=3)
db.add(level3)
db.commit()

task3_1 = Task(level_id=level3.level_id, type="content", title="Defining Functions", content="Functions are reusable blocks of code. Use 'def' to define them, and 'return' to send back values.", order=1)
task3_2 = Task(level_id=level3.level_id, type="content", title="Function Parameters", content="Functions can accept parameters to make them more flexible.", order=2)
task3_3 = Task(level_id=level3.level_id, type="assessment", title="Simple Function", content="Write a function called 'greet' that takes a name parameter and returns 'Hello, [name]!'.", order=3)
task3_4 = Task(level_id=level3.level_id, type="assessment", title="Function with Math", content="Write a function that calculates the area of a rectangle given width and height.", order=4)
db.add(task3_1)
db.add(task3_2)
db.add(task3_3)
db.add(task3_4)
db.commit()

# Level 4
level4 = Level(course_id=python_course.course_id, name="Level 4: Data Structures", order=4)
db.add(level4)
db.commit()

task4_1 = Task(level_id=level4.level_id, type="content", title="Lists", content="Lists are ordered, mutable collections. You can add, remove, and modify elements.", order=1)
task4_2 = Task(level_id=level4.level_id, type="content", title="Dictionaries", content="Dictionaries store key-value pairs. Keys must be immutable, values can be anything.", order=2)
task4_3 = Task(level_id=level4.level_id, type="assessment", title="List Operations", content="Create a list of 5 numbers, then write code to find the sum and average.", order=3)
task4_4 = Task(level_id=level4.level_id, type="assessment", title="Dictionary Practice", content="Create a dictionary with student names as keys and grades as values, then print all students with grades above 80.", order=4)
db.add(task4_1)
db.add(task4_2)
db.add(task4_3)
db.add(task4_4)
db.commit()

# Assessment 2: JavaScript Fundamentals - 4 Levels
# Level 1
level2_1 = Level(course_id=js_course.course_id, name="Level 1: Basic Syntax", order=1)
db.add(level2_1)
db.commit()

task2_1_1 = Task(level_id=level2_1.level_id, type="content", title="Introduction to JavaScript", content="JavaScript is a versatile programming language primarily used for web development. It can run in browsers and on servers.", order=1)
task2_1_2 = Task(level_id=level2_1.level_id, type="content", title="Variables and Data Types", content="JavaScript has dynamic typing. Common data types include strings, numbers, booleans, arrays, and objects.", order=2)
task2_1_3 = Task(level_id=level2_1.level_id, type="assessment", title="Console Output", content="Write JavaScript code that logs 'Hello, World!' to the console.", order=3)
task2_1_4 = Task(level_id=level2_1.level_id, type="assessment", title="Variable Declaration", content="Declare variables for your name, age, and city, then log them to the console.", order=4)
db.add(task2_1_1)
db.add(task2_1_2)
db.add(task2_1_3)
db.add(task2_1_4)
db.commit()

# Level 2
level2_2 = Level(course_id=js_course.course_id, name="Level 2: Functions", order=2)
db.add(level2_2)
db.commit()

task2_2_1 = Task(level_id=level2_2.level_id, type="content", title="Function Declaration", content="Functions are reusable blocks of code. Use 'function' keyword or arrow syntax to define them.", order=1)
task2_2_2 = Task(level_id=level2_2.level_id, type="content", title="Parameters and Return", content="Functions can accept parameters and return values to make them flexible and useful.", order=2)
task2_2_3 = Task(level_id=level2_2.level_id, type="assessment", title="Simple Function", content="Write a function called 'greet' that takes a name parameter and returns 'Hello, [name]!'.", order=3)
task2_2_4 = Task(level_id=level2_2.level_id, type="assessment", title="Math Function", content="Write a function that calculates the area of a circle given the radius.", order=4)
db.add(task2_2_1)
db.add(task2_2_2)
db.add(task2_2_3)
db.add(task2_2_4)
db.commit()

# Level 3
level2_3 = Level(course_id=js_course.course_id, name="Level 3: Arrays and Objects", order=3)
db.add(level2_3)
db.commit()

task2_3_1 = Task(level_id=level2_3.level_id, type="content", title="Arrays", content="Arrays are ordered collections of values. They have methods like push, pop, map, filter, and reduce.", order=1)
task2_3_2 = Task(level_id=level2_3.level_id, type="content", title="Objects", content="Objects store key-value pairs. They are the foundation of JavaScript's object-oriented features.", order=2)
task2_3_3 = Task(level_id=level2_3.level_id, type="assessment", title="Array Methods", content="Create an array of numbers and use map() to double each value, then filter() to keep only even numbers.", order=3)
task2_3_4 = Task(level_id=level2_3.level_id, type="assessment", title="Object Manipulation", content="Create an object representing a person with name, age, and city properties, then add a method to greet.", order=4)
db.add(task2_3_1)
db.add(task2_3_2)
db.add(task2_3_3)
db.add(task2_3_4)
db.commit()

# Level 4
level2_4 = Level(course_id=js_course.course_id, name="Level 4: DOM Manipulation", order=4)
db.add(level2_4)
db.commit()

task2_4_1 = Task(level_id=level2_4.level_id, type="content", title="DOM Basics", content="The Document Object Model (DOM) represents the structure of HTML documents. JavaScript can manipulate it.", order=1)
task2_4_2 = Task(level_id=level2_4.level_id, type="content", title="Event Handling", content="Events allow JavaScript to respond to user interactions like clicks, hovers, and form submissions.", order=2)
task2_4_3 = Task(level_id=level2_4.level_id, type="assessment", title="Element Selection", content="Write code to select an element with id 'myDiv' and change its text content.", order=3)
task2_4_4 = Task(level_id=level2_4.level_id, type="assessment", title="Event Listener", content="Add a click event listener to a button that changes the background color of the page.", order=4)
db.add(task2_4_1)
db.add(task2_4_2)
db.add(task2_4_3)
db.add(task2_4_4)
db.commit()

# Assessment 3: Data Structures and Algorithms - 4 Levels
# Level 1
level3_1 = Level(course_id=ds_course.course_id, name="Level 1: Basic Algorithms", order=1)
db.add(level3_1)
db.commit()

task3_1_1 = Task(level_id=level3_1.level_id, type="content", title="Algorithm Complexity", content="Understanding Big O notation helps analyze algorithm efficiency in terms of time and space complexity.", order=1)
task3_1_2 = Task(level_id=level3_1.level_id, type="content", title="Linear Search", content="Linear search checks each element in a list sequentially until finding the target value.", order=2)
task3_1_3 = Task(level_id=level3_1.level_id, type="assessment", title="Linear Search Implementation", content="Implement a linear search function that returns the index of a target value in an array, or -1 if not found.", order=3)
task3_1_4 = Task(level_id=level3_1.level_id, type="assessment", title="Find Maximum", content="Write a function that finds the maximum value in an array of numbers.", order=4)
db.add(task3_1_1)
db.add(task3_1_2)
db.add(task3_1_3)
db.add(task3_1_4)
db.commit()

# Level 2
level3_2 = Level(course_id=ds_course.course_id, name="Level 2: Sorting Algorithms", order=2)
db.add(level3_2)
db.commit()

task3_2_1 = Task(level_id=level3_2.level_id, type="content", title="Bubble Sort", content="Bubble sort repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.", order=1)
task3_2_2 = Task(level_id=level3_2.level_id, type="content", title="Selection Sort", content="Selection sort divides the input list into sorted and unsorted portions, repeatedly finding the minimum element.", order=2)
task3_2_3 = Task(level_id=level3_2.level_id, type="assessment", title="Bubble Sort", content="Implement bubble sort algorithm to sort an array of numbers in ascending order.", order=3)
task3_2_4 = Task(level_id=level3_2.level_id, type="assessment", title="Selection Sort", content="Implement selection sort algorithm to sort an array of numbers in ascending order.", order=4)
db.add(task3_2_1)
db.add(task3_2_2)
db.add(task3_2_3)
db.add(task3_2_4)
db.commit()

# Level 3
level3_3 = Level(course_id=ds_course.course_id, name="Level 3: Data Structures", order=3)
db.add(level3_3)
db.commit()

task3_3_1 = Task(level_id=level3_3.level_id, type="content", title="Stacks and Queues", content="Stacks follow LIFO (Last In, First Out), queues follow FIFO (First In, First Out) principles.", order=1)
task3_3_2 = Task(level_id=level3_3.level_id, type="content", title="Linked Lists", content="Linked lists consist of nodes where each node contains data and a reference to the next node.", order=2)
task3_3_3 = Task(level_id=level3_3.level_id, type="assessment", title="Stack Implementation", content="Implement a stack class with push, pop, and peek methods.", order=3)
task3_3_4 = Task(level_id=level3_3.level_id, type="assessment", title="Queue Implementation", content="Implement a queue class with enqueue, dequeue, and front methods.", order=4)
db.add(task3_3_1)
db.add(task3_3_2)
db.add(task3_3_3)
db.add(task3_3_4)
db.commit()

# Level 4
level3_4 = Level(course_id=ds_course.course_id, name="Level 4: Advanced Topics", order=4)
db.add(level3_4)
db.commit()

task3_4_1 = Task(level_id=level3_4.level_id, type="content", title="Binary Trees", content="Binary trees are hierarchical data structures where each node has at most two children.", order=1)
task3_4_2 = Task(level_id=level3_4.level_id, type="content", title="Hash Tables", content="Hash tables provide fast lookups by mapping keys to array indices using hash functions.", order=2)
task3_4_3 = Task(level_id=level3_4.level_id, type="assessment", title="Binary Tree Traversal", content="Implement inorder traversal of a binary tree.", order=3)
task3_4_4 = Task(level_id=level3_4.level_id, type="assessment", title="Hash Table Implementation", content="Implement a simple hash table with set and get methods.", order=4)
db.add(task3_4_1)
db.add(task3_4_2)
db.add(task3_4_3)
db.add(task3_4_4)
db.commit()

# Seed users
from models import User, UserProfile
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Candidates
candidate1 = User(email="candidate1@example.com", password_hash=hash_password("pass123"), role="candidate")
candidate2 = User(email="candidate2@example.com", password_hash=hash_password("pass123"), role="candidate")
db.add(candidate1)
db.add(candidate2)
db.commit()

profile1 = UserProfile(user_id=candidate1.user_id, name="John Doe")
profile2 = UserProfile(user_id=candidate2.user_id, name="Jane Smith")
db.add(profile1)
db.add(profile2)
db.commit()

# Recruiters
recruiter_user1 = User(email="recruiter1@example.com", password_hash=hash_password("pass123"), role="recruiter")
recruiter_user2 = User(email="recruiter2@example.com", password_hash=hash_password("pass123"), role="recruiter")
db.add(recruiter_user1)
db.add(recruiter_user2)
db.commit()

# Companies
from models import Company, Recruiter, JobRole, JobRoleRequirement
company1 = Company(name="TechCorp", description="Leading tech company")
company2 = Company(name="InnovateInc", description="Innovation-driven startup")
db.add(company1)
db.add(company2)
db.commit()

recruiter1 = Recruiter(user_id=recruiter_user1.user_id, company_id=company1.company_id, job_title="Senior Recruiter")
recruiter2 = Recruiter(user_id=recruiter_user2.user_id, company_id=company2.company_id, job_title="HR Manager")
db.add(recruiter1)
db.add(recruiter2)
db.commit()

# Job Roles
job1 = JobRole(company_id=company1.company_id, title="Python Developer", description="Develop Python applications")
job2 = JobRole(company_id=company1.company_id, title="JavaScript Developer", description="Build web applications")
job3 = JobRole(company_id=company2.company_id, title="Data Analyst", description="Analyze data and create reports")
db.add(job1)
db.add(job2)
db.add(job3)
db.commit()

# Job Requirements
req1 = JobRoleRequirement(role_id=job1.role_id, domain_id=python_domain.domain_id, minimum_level=1)
req2 = JobRoleRequirement(role_id=job2.role_id, domain_id=js_domain.domain_id, minimum_level=1)
req3 = JobRoleRequirement(role_id=job3.role_id, domain_id=python_domain.domain_id, minimum_level=2)
db.add(req1)
db.add(req2)
db.add(req3)
db.commit()

# Candidate Assessments (some completed)
from models import CandidateAssessment
ca1 = CandidateAssessment(candidate_id=candidate1.user_id, assessment_id=assessment1.assessment_id, total_score=85, completed_at=datetime.utcnow())
ca2 = CandidateAssessment(candidate_id=candidate1.user_id, assessment_id=assessment2.assessment_id, total_score=78, completed_at=datetime.utcnow())
db.add(ca1)
db.add(ca2)
db.commit()

# Interviews
from models import Interview, InterviewNote
interview1 = Interview(candidate_id=candidate1.user_id, recruiter_id=recruiter1.recruiter_id, role_id=job1.role_id, scheduled_time=datetime.utcnow(), status="scheduled")
db.add(interview1)
db.commit()

notes1 = InterviewNote(interview_id=interview1.interview_id, recruiter_id=recruiter1.recruiter_id, notes="Good candidate", fit_score=8, decision="advance")
db.add(notes1)
db.commit()

# Notifications
from models import Notification
notif1 = Notification(user_id=candidate1.user_id, type="interview", message="You have an upcoming interview", is_read=False, created_at=datetime.utcnow())
notif2 = Notification(user_id=recruiter1.user_id, type="application", message="New application received", is_read=False, created_at=datetime.utcnow())
# Candidate Job Matches
from models import CandidateJobMatch
match1 = CandidateJobMatch(candidate_id=candidate1.user_id, role_id=job1.role_id, match_score=85, last_updated=datetime.utcnow())
match2 = CandidateJobMatch(candidate_id=candidate2.user_id, role_id=job2.role_id, match_score=72, last_updated=datetime.utcnow())
db.add(match1)
db.add(match2)
db.commit()

# register user routes
app.include_router(users_router)
app.include_router(auth.router)
# app.include_router(recruiter.router)
app.include_router(assessment.router)

# to start server: uvicorn main:app --reload