import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models import db, Employee, Partner, Engagement, Assignment, TimeOff, Observation
from datetime import datetime, timedelta
import random
from faker import Faker

# Generate a new database file in the script's directory
db_file = 'stress_test_database.db'
db_path = os.path.join(os.path.dirname(__file__), db_file)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

fake = Faker()

def generate_employees(num_employees):
    employees = []
    for _ in range(num_employees):
        employee = Employee(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            hire_date=fake.date_between(start_date='-5y', end_date='today'),
            active_status=random.choice([True, True, True, False])  # 75% chance of being active
        )
        employees.append(employee)
    db.session.add_all(employees)
    db.session.commit()
    return employees

def generate_partners(num_partners):
    partners = []
    for _ in range(num_partners):
        first_name = fake.first_name()
        last_name = fake.last_name()
        partner = Partner(
            first_name=first_name,
            last_name=last_name,
            initials=f"{first_name[0]}{last_name[0]}"
        )
        partners.append(partner)
    db.session.add_all(partners)
    db.session.commit()
    return partners

def generate_engagements(num_engagements, partners):
    engagements = []
    for _ in range(num_engagements):
        engagement = Engagement(
            engagement_title=fake.company(),
            engagement_type=random.choice(['Audit', 'Tax', 'Consulting', 'Advisory']),
            fiscal_year=str(fake.year())
        )
        engagements.append(engagement)
    
    db.session.add_all(engagements)
    db.session.flush()

    # Now update the engagements with partner_id and deadline
    for engagement in engagements:
        engagement.partner_id = random.choice(partners).id
        engagement.deadline = fake.date_between(start_date='today', end_date='+2y')

    db.session.commit()
    return engagements

def generate_assignments(num_assignments, employees, engagements):
    assignments = []
    for _ in range(num_assignments):
        start_date = fake.date_between(start_date='today', end_date='+1y')
        end_date = start_date + timedelta(days=random.randint(1, 90))
        assignment = Assignment(
            employee_id=random.choice(employees).id,
            engagement_id=random.choice(engagements).id,
            start_date=start_date,
            end_date=end_date
        )
        assignments.append(assignment)
    db.session.add_all(assignments)
    db.session.commit()
    return assignments

def generate_time_off(num_time_off, employees):
    time_offs = []
    for _ in range(num_time_off):
        start_date = fake.date_between(start_date='today', end_date='+1y')
        end_date = start_date + timedelta(days=random.randint(1, 14))
        time_off = TimeOff(
            employee_id=random.choice(employees).id,
            start_date=start_date,
            end_date=end_date,
            description=fake.sentence()
        )
        time_offs.append(time_off)
    db.session.add_all(time_offs)
    db.session.commit()
    return time_offs

def generate_observations(num_observations, engagements, employees, partners):
    observations = []
    for _ in range(num_observations):
        observation = Observation(
            engagement_id=random.choice(engagements).id,
            scheduler_id=random.choice(employees).id if random.choice([True, False]) else None,
            scheduler_partner_id=random.choice(partners).id if random.choice([True, False]) else None,
            observer_id=random.choice(employees).id if random.choice([True, False]) else None,
            observer_partner_id=random.choice(partners).id if random.choice([True, False]) else None,
            outside_observer=fake.name() if random.choice([True, False]) else None,
            scheduled_observation_date=fake.date_between(start_date='today', end_date='+1y')
        )
        observations.append(observation)
    db.session.add_all(observations)
    db.session.commit()
    return observations

def generate_stress_test_data():
    with app.app_context():
        db.create_all()
        print(f"Created new database at {db_path}")
        
        print("Generating employees...")
        employees = generate_employees(100)
        print("Generating partners...")
        partners = generate_partners(15)
        print("Generating engagements...")
        engagements = generate_engagements(800, partners)
        print("Generating assignments...")
        generate_assignments_for_engagements(engagements, employees)
        print("Generating observations...")
        generate_observations(200, engagements, employees, partners)
        print("Data generation complete!")

def generate_assignments_for_engagements(engagements, employees):
    assignments = []
    for engagement in engagements:
        num_assignments = random.randint(2, 4)
        for _ in range(num_assignments):
            start_date = fake.date_between(start_date='today', end_date='+1y')
            end_date = start_date + timedelta(days=random.randint(1, 90))
            assignment = Assignment(
                employee_id=random.choice(employees).id,
                engagement_id=engagement.id,
                start_date=start_date,
                end_date=end_date
            )
            assignments.append(assignment)
    db.session.add_all(assignments)
    db.session.commit()
    return assignments




if __name__ == "__main__":
    generate_stress_test_data()