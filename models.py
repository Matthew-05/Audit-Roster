from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey, Column, String, Integer
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(10), nullable=False)  # 'login' or 'logout'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))

    def __repr__(self):
        return f'<UserLog {self.user.username} {self.action} at {self.timestamp}>'

class VersionInfo(db.Model):
    __tablename__ = 'version_info'
    id = Column(Integer, primary_key=True)
    version = Column(String(10), nullable=False)

class Observation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    engagement_id = db.Column(db.Integer, db.ForeignKey('engagement.id'), nullable=False)
    scheduler_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    scheduler_partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    observer_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    observer_partner_id = db.Column(db.Integer, db.ForeignKey('partner.id'))
    previous_observation_id = db.Column(db.Integer, db.ForeignKey('observation.id'))
    scheduled_observation_date = db.Column(db.Date)
    outside_observer = db.Column(db.String(200))
    hidden = db.Column(db.Boolean, default=False)


    engagement = relationship('Engagement', back_populates='observations')
    scheduler_employee = relationship('Employee', foreign_keys=[scheduler_id])
    scheduler_partner = relationship('Partner', foreign_keys=[scheduler_partner_id])
    observer_employee = relationship('Employee', foreign_keys=[observer_id])
    observer_partner = relationship('Partner', foreign_keys=[observer_partner_id])
    previous_observation = relationship('Observation', remote_side=[id])

    def to_dict(self):
        return {
            'id': self.id,
            'engagement_id': self.engagement_id,
            'engagement_title': self.engagement.engagement_title,
            'engagement_type': self.engagement.engagement_type,
            'scheduler_id': self.scheduler_id,
            'scheduler_partner_id': self.scheduler_partner_id,
            'scheduler_name': self.get_person_name(self.scheduler_employee, self.scheduler_partner),
            'observer_id': self.observer_id,
            'observer_partner_id': self.observer_partner_id,
            'observer_name': self.get_person_name(self.observer_employee, self.observer_partner) or self.outside_observer,
            'outside_observer': self.outside_observer,
            'scheduled_observation_date': self.scheduled_observation_date.isoformat() if self.scheduled_observation_date else None,
            'previous_observation_id': self.previous_observation_id,
            'hidden': self.hidden,
        }

    @staticmethod
    def get_person_name(employee, partner):
        if employee:
            return f"{employee.first_name} {employee.last_name}"
        elif partner:
            return f"{partner.first_name} {partner.last_name}"
        return None

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)
    active_status = db.Column(db.Boolean, default=True)
    
    assignments = db.relationship('Assignment', back_populates='employee')
    time_off = db.relationship('TimeOff', back_populates='employee')

    def __repr__(self):
        return f'<Employee {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'active_status': self.active_status
        }


class Partner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    initials = db.Column(db.String(10), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'initials': self.initials
        }


class Engagement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    engagement_title = db.Column(db.String(200), nullable=False)
    engagement_type = db.Column(db.String(100), nullable=False)
    fiscal_year = db.Column(db.String(10))  

    assignments = db.relationship('Assignment', back_populates='engagement')
    partner_id = db.Column(db.Integer, db.ForeignKey('partner.id', name='fk_engagement_partner'))
    deadline = db.Column(db.Date)
    partner = db.relationship('Partner', backref='engagements')
    observations = relationship('Observation', back_populates='engagement')


    def __repr__(self):
        return f'<Engagement {self.engagement_title}>'

    def to_dict(self):
        return {
            'id': self.id,
            'engagement_title': self.engagement_title,
            'engagement_type': self.engagement_type,
            'partner_id': self.partner_id,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'fiscal_year': self.fiscal_year,
            'partner_name': f"{self.partner.first_name} {self.partner.last_name}" if self.partner else None,
            'partner_initials': self.partner.initials if self.partner else None
        }

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    engagement_id = db.Column(db.Integer, db.ForeignKey('engagement.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    
    employee = db.relationship('Employee', back_populates='assignments')
    engagement = db.relationship('Engagement', back_populates='assignments')

    def __repr__(self):
        return f'<Assignment {self.employee_id} - {self.engagement_id} - {self.start_date} to {self.end_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'engagement_id': self.engagement_id,
            'employee_id': self.employee_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat()
        }

class TimeOff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255))
    
    employee = db.relationship('Employee', back_populates='time_off')

    def __repr__(self):
        return f'<TimeOff {self.employee_id} - {self.start_date} to {self.end_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'description': self.description
        }

