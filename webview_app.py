import webview
from flask import Flask, render_template, jsonify, request
from models import db, Employee, Engagement, Assignment,TimeOff, Partner, Observation, User, UserLog
from datetime import datetime, timedelta
import json
import os
import sys
from app_utils.schedule_saver import save_schedule
from app_utils.generate_changelog import generate_changelog_html
from app_utils.migrations import apply_migrations
import configparser
import os
from sqlalchemy import func,  or_
from flask_migrate import Migrate, upgrade
import io

from collections import defaultdict
import random

import tkinter as tk
from tkinter import filedialog, messagebox,simpledialog
import sqlite3

import pandas as pd

import sys

from dateutil.relativedelta import relativedelta

from app_utils.update_utils import check_for_updates, download_and_install_update


PREVIOUS_VERSION = "1.9.1"
VERSION = "2.0.0"

can_migrate = False
need_to_generate_db = False

server = Flask(__name__)
def check_database_accessibility():
    global can_migrate
    global need_to_generate_db
    settings = get_settings()
    db_path = settings['Database']['Path']
    
    if os.path.exists('settings.ini'):
        if not os.path.exists(db_path):
            root = tk.Tk()
            root.withdraw()
            
            choice = messagebox.askyesno("Database Not Found", "The database file specified in settings does not exist. Would you like to select a new database file? \n\n(If you select 'No', a new database file will be generated.)")
            
            if choice:
                new_db_path = filedialog.askopenfilename(title="Select Database File", filetypes=[("SQLite Database", "*.db")])
                if new_db_path:
                    settings['Database']['Path'] = new_db_path
                    with open('settings.ini', 'w') as configfile:
                        settings.write(configfile)
                    return new_db_path
                else:
                    need_to_generate_db = True
                    return generate_new_database_path(settings)
            else:
                need_to_generate_db = True
                return generate_new_database_path(settings)
        else:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if version_info table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='version_info'")
                if cursor.fetchone() is None:
                    # Table doesn't exist, create it with current version
                    cursor.execute("CREATE TABLE version_info (id INTEGER PRIMARY KEY, version TEXT)")
                    cursor.execute("INSERT INTO version_info (version) VALUES (?)", (VERSION,))
                    conn.commit()
                    print(f"Created version_info table with version {VERSION}")
                else:
                    # Check the version
                    cursor.execute("SELECT version FROM version_info LIMIT 1")
                    result = cursor.fetchone()
                    if result is None:
                        # Table exists but no version entry, insert current version
                        cursor.execute("INSERT INTO version_info (version) VALUES (?)", (VERSION,))
                        conn.commit()
                        print(f"Inserted current version {VERSION} into version_info table")
                    else:
                        db_version = result[0]
                        if db_version == VERSION or db_version == PREVIOUS_VERSION:
                            print("Database version is current.")
                            can_migrate = True
                        #elif db_version == PREVIOUS_VERSION:
                        #    print("Database version is previous. Applying migrations...")
                        #    can_migrate = True
                        else:
                            root = tk.Tk()
                            root.withdraw()
                            override = messagebox.askyesno("Version Mismatch", 
                                f"Database version ({db_version}) does not match current ({VERSION}) or previous ({PREVIOUS_VERSION}) version.\n\nDo you want to override and continue?")
                            if not override:
                                sys.exit(1)
                            else:
                                print("User chose to override version mismatch and continue.")
                                # Optionally update the database version to the current version
                                cursor.execute("UPDATE version_info SET version = ?", (VERSION,))
                                conn.commit()
                
                conn.close()
                return db_path
            except sqlite3.Error:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Database Error", "Unable to access the database. A new database will be generated.")
                return generate_new_database_path(settings)
    else:
        return settings['Database']['Path']




def generate_new_database_path(settings):
    new_db_path = os.path.join(os.path.dirname(settings['Database']['Path']), 'employee_scheduler.db')
    settings['Database']['Path'] = new_db_path
    with open('settings.ini', 'w') as configfile:
        settings.write(configfile)
    
    # Update the Flask app's database URI
    #server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{new_db_path}'

    # Re-create the database
    #with server.app_context():
    #    db.create_all()

    return new_db_path





def get_settings():
    config = configparser.ConfigParser()
    settings_file = 'settings.ini'
    
    default_settings = {
        'Database': {
            'Path': 'employee_scheduler.db'
        },
        'General': {
            'Debug': 'False',
            'SaveCount': '0',
            'LastVersion': VERSION,
            'CurrentlyOpen': 'False',
        },
        'UI': {
            'SidebarCollapsed': 'False',
        },
        'Schedule': {
            'ExportInactiveEmployees': 'False',
        }
    }
    
    if not os.path.exists(settings_file):
        config.read_dict(default_settings)
        with open(settings_file, 'w') as configfile:
            config.write(configfile)
    else:
        config.read(settings_file)
        # Ensure 'General' section exists
        if 'General' not in config:
            config['General'] = {}
        if 'UI' not in config:
            config['UI'] = {}
        if 'Schedule' not in config:
            config['Schedule'] = {}

        if 'LastVersion' not in config['General']:
            print("LastVersion not found in settings.ini. Adding it.")
            config['General']['LastVersion'] = "1.0.0"
            with open(settings_file, 'w') as configfile:
                config.write(configfile)
        if 'SaveCount' not in config['General']:
            config['General']['SaveCount'] = '0'
            with open(settings_file, 'w') as configfile:
                config.write(configfile)
        if 'Debug' not in config['General']:
            config['General']['Debug'] = 'False'
            with open(settings_file, 'w') as configfile:
                config.write(configfile)
        if 'SaveDirectory' not in config['General']:
            config['General']['SaveDirectory'] = ''
            with open(settings_file, 'w') as configfile:
                print("SaveDirectory not found in settings.ini. Adding it.")
                config.write(configfile)
        if 'Database' not in config:
            config['Database'] = {}
            config['Database']['Path'] = 'employee_scheduler.db'
            with open(settings_file, 'w') as configfile:
                config.write(configfile)
        if 'SidebarCollapsed' not in config['UI']:
            print("SidebarCollapsed not found in settings.ini. Adding it.")
            config['UI']['SidebarCollapsed'] = 'False'
        if 'ExportInactiveEmployees' not in config['Schedule']:
            print("ExportInactiveEmployees not found in settings.ini. Adding it.")
            config['Schedule']['ExportInactiveEmployees'] = 'False'
            
        if 'CurrentlyOpen' not in config['General']:
            print("CurrentlyOpen not found in settings.ini. Adding it.")
            config['General']['CurrentlyOpen'] = 'False'
            with open(settings_file, 'w') as configfile:
                config.write(configfile)
        
        # Write updated config if changes were made
        if set(config.sections()) != set(default_settings.keys()):
            with open(settings_file, 'w') as configfile:
                config.write(configfile)
    
    # Get the absolute path for the database
    db_path = os.path.abspath(config['Database']['Path'])
    config['Database']['Path'] = db_path

    return config




settings = get_settings()

db_path = check_database_accessibility()
# Determine if the application is running as a script or frozen exe
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.dirname(os.path.abspath(__file__))


server.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
server.config['SECRET_KEY'] = 'your_secret_key_here'




db.init_app(server)
migrate = Migrate(server, db)

if can_migrate == True:
    migrate = Migrate(server, db)
    #server.extensions['migrate'] = migrate
    #apply_migrations(server)


if need_to_generate_db == True:
    print("Generating new database...")
    with server.app_context():
        db.create_all()
        # Stamp the database with the current migration version
        from flask_migrate import stamp
        stamp()


@server.route('/')
def index():
    return render_template('schedule.html', version=VERSION)

@server.route('/employees')
def employees():
    return render_template('employees.html', version=VERSION)

@server.route('/clients')
def clients():
    return render_template('clients.html', version=VERSION)

@server.route('/engagements')
def engagements():
    return render_template('engagements.html', version=VERSION)

@server.route('/time_off')
def time_off():
    return render_template('time_off.html', version=VERSION)

@server.route('/settings')
def settings_page():
    settings = get_settings()
    return render_template('settings.html', settings=settings, version=VERSION)

@server.route('/reports')
def reports():
    return render_template('reports.html',version=VERSION)

@server.route('/observations')
def observations():
    return render_template('observations.html', version=VERSION)

def create_application():
    return server

class Api:
    def __init__(self):
        self.app = server

    def get_current_user_id(self):
        return self.current_user_id

    def get_current_user_id(self):
        return self.current_user_id

    def download_database_to_excel(self):
        with self.app.app_context():
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                default_filename = f"exported_db_{timestamp}.xlsx"
                
                file_path = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename=default_filename, file_types=('Excel Files (*.xlsx)',))
                
                if file_path and len(file_path) > 0:
                    excel_file = file_path
                    
                    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
                        tables = {
                            'Employees': Employee,
                            'Engagements': Engagement,
                            'Assignments': Assignment,
                            'TimeOff': TimeOff,
                            'Partners': Partner,
                            'Observations': Observation
                        }

                        for sheet_name, model in tables.items():
                            df = pd.DataFrame([item.to_dict() for item in model.query.all()])
                            df.to_excel(writer, sheet_name=sheet_name, index=False)

                    return {'success': True, 'message': 'Database exported successfully'}
                else:
                    return {'success': False, 'message': 'File save cancelled'}
            except Exception as e:
                print(f"Error exporting database to Excel: {str(e)}")
                return {'success': False, 'message': str(e)}



    def get_engagements_with_no_assignments(self):
        with self.app.app_context():
            # Get engagements that have no assignments
            engagements = db.session.query(Engagement)\
                .outerjoin(Assignment)\
                .outerjoin(Partner)\
                .filter(Assignment.id == None)\
                .all()
                
            return [{
                'id': eng.id,
                'title': eng.engagement_title,
                'engagement_type': eng.engagement_type or 'No Type',
                'reporting_period': eng.fiscal_year or 'N/A',
                'partner_name': f"{eng.partner.first_name} {eng.partner.last_name}" if eng.partner else 'No Partner Set'
            } for eng in engagements]
            
    def select_database_file(self):
        file_types = ('SQLite Database (*.db;*.sqlite;*.sqlite3)', 'All files (*.*)')
        result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
        return result[0] if result else None


    def select_save_directory(self):
        result = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG, directory='', allow_multiple=False)
        print(f"Folder selection result: {result}")  # Add this line for debugging
        if result and len(result) > 0:
            return result
        return None
    
    def is_save_directory_set(self):
        with self.app.app_context():
            settings = get_settings()
            save_directory = settings['General'].get('SaveDirectory', '')
            return bool(save_directory)
        
    def get_changelog(self):
        with self.app.app_context():
            return generate_changelog_html()
    def prompt_save_directory(self):
        result = self.select_save_directory()
        if result:
            with self.app.app_context():
                settings = get_settings()
                settings['General']['SaveDirectory'] = result
                with open('settings.ini', 'w') as configfile:
                    settings.write(configfile)
            return True
        return False

    def get_settings_for_web(self):
        with self.app.app_context():
            settings = get_settings()
            print(f"Settings: {settings}")  # Add this line for debugging
            print(settings['UI']['SidebarCollapsed'])
            return {
                'database_path': settings['Database']['Path'],
                'debug_mode': settings['General'].getboolean('Debug'),
                'save_directory': settings['General'].get('SaveDirectory', ''),
                'sidebar_collapsed': settings['UI']['SidebarCollapsed'],
                'export_inactive_employees': settings['Schedule'].getboolean('ExportInactiveEmployees', False)
            }
        
    def check_and_update_version(self):
        with self.app.app_context():
            settings = get_settings()
            last_version = settings['General']['LastVersion'] # this is all for the new version notification
            print(f"Last version: {last_version}, Current version: {VERSION}") 
            if last_version != VERSION:
                settings['General']['LastVersion'] = VERSION
                with open('settings.ini', 'w') as configfile:
                    settings.write(configfile)
                return {'new_version': VERSION, 'old_version': last_version}
            return None

    def save_settings(self, data):
        with self.app.app_context():
            print("Saving settings...")
            settings = get_settings()
            if 'database_path' in data:
                settings['Database']['Path'] = data['database_path']
            if 'debug_mode' in data:
                settings['General']['Debug'] = str(data['debug_mode'])
            if 'save_directory' in data:
                settings['General']['SaveDirectory'] = data['save_directory']
            if 'sidebar_collapsed' in data:
                settings['UI']['SidebarCollapsed'] = str(data['sidebar_collapsed'])
            if 'export_inactive_employees' in data:
                settings['Schedule']['ExportInactiveEmployees'] = str(data['export_inactive_employees'])

            with open('settings.ini', 'w') as configfile:
                settings.write(configfile)
            return True


    def get_all_time_off(self, include_inactive=True):
        with self.app.app_context():
            query = TimeOff.query.join(Employee)
            if not include_inactive:
                query = query.filter(Employee.active_status == True)
            time_off_list = query.all()
            return [{
                'id': time_off.id,
                'employee_id': time_off.employee_id,
                'employee_name': f"{time_off.employee.first_name} {time_off.employee.last_name}",
                'start_date': time_off.start_date.isoformat(),
                'end_date': time_off.end_date.isoformat(),
                'description': time_off.description
            } for time_off in time_off_list]



    def get_employees(self, include_inactive=True):
        with self.app.app_context():
            query = Employee.query
            if not include_inactive:
                query = query.filter(Employee.active_status == True)
            employees = query.filter(
                Employee.first_name != "Removed",
                Employee.last_name != "Employee"
            ).all()
            return [employee.to_dict() for employee in employees]
    
    def add_employee(self, data):
        with self.app.app_context():
            try:
                hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
                new_employee = Employee(first_name=data['first_name'], last_name=data['last_name'], 
                                        hire_date=hire_date, active_status=data['active_status'])
                db.session.add(new_employee)
                db.session.commit()
                return {'success': True, 'id': new_employee.id, 'first_name': new_employee.first_name, 'last_name': new_employee.last_name,
                        'hire_date': new_employee.hire_date.isoformat(), 'active_status': new_employee.active_status}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}

    def get_employee(self, id):
        with self.app.app_context():
            employee = Employee.query.get_or_404(id)
            return {
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'hire_date': employee.hire_date.isoformat(),
                'active_status': employee.active_status
            }

    def update_employee(self, id, data):
        with self.app.app_context():
            try:
                employee = Employee.query.get_or_404(id)
                employee.first_name = data['first_name']
                employee.last_name = data['last_name']
                employee.hire_date = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
                employee.active_status = data['active_status']
                db.session.commit()
                return {'success': True, 'id': employee.id, 'name': f'{employee.first_name} {employee.last_name}'}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}
            
    def delete_employee(self, id, option):
        with self.app.app_context():
            employee = Employee.query.get(id)
            if not employee:
                return {'success': False, 'message': 'Employee not found'}

            # Get or create the "Removed Employee"
            removed_employee = Employee.query.filter_by(first_name="Removed", last_name="Employee").first()
            if not removed_employee:
                removed_employee = Employee(first_name="Removed", last_name="Employee", hire_date=datetime.now(), active_status=False)
                db.session.add(removed_employee)
                db.session.commit()

            if option == 'inactive':
                employee.active_status = False
            elif option == 'delete-all':
                # Update assignments
                Assignment.query.filter_by(employee_id=id).update({'employee_id': removed_employee.id})
                
                # Update observations
                observations = Observation.query.filter(or_(
                    Observation.observer_employee.has(Employee.id == id),
                    Observation.scheduler_employee.has(Employee.id == id)
                )).all()

                for obs in observations:
                    if obs.observer_employee and obs.observer_employee.id == id:
                        obs.observer_employee = removed_employee
                    if obs.scheduler_employee and obs.scheduler_employee.id == id:
                        obs.scheduler_employee = removed_employee
                
                # Delete the employee
                db.session.delete(employee)
            
            db.session.commit()
            return {'success': True}



    # Engagement methods
    def add_engagement(self, data):
        with self.app.app_context():
            print("Adding engagement:", data)
            new_engagement = Engagement(
                engagement_title=data['title'],
                engagement_type=data['engagement_type'],
                partner_id=data['partner_id'] if data['partner_id'] else None,
                deadline=datetime.strptime(data['deadline'], '%Y-%m-%d').date() if data['deadline'] else None,
                fiscal_year=data['reporting_period'] if data['reporting_period'] else None,
            )
            db.session.add(new_engagement)
            db.session.commit()
            return {'id': new_engagement.id, 'title': new_engagement.engagement_title}
        
    def get_engagements(self):
        with self.app.app_context():
            engagements = Engagement.query.all()
            result = []
            for e in engagements:
                # Get earliest assignment date for this engagement
                earliest_assignment = Assignment.query.filter_by(engagement_id=e.id)\
                    .order_by(Assignment.start_date.asc())\
                    .first()
                    
                result.append({
                    'id': e.id,
                    'title': e.engagement_title,
                    'engagement_type': e.engagement_type,
                    'partner_initials': f"{e.partner.first_name} {e.partner.last_name}" if e.partner else '',
                    'deadline': e.deadline.isoformat() if e.deadline else None,
                    'reporting_period': e.fiscal_year,
                    'earliest_assignment': earliest_assignment.start_date.isoformat() if earliest_assignment else None
                })
            return result


    def get_engagement(self, id):
        with self.app.app_context():
            engagement = Engagement.query.get_or_404(id)
            return {
                'id': engagement.id,
                'title': engagement.engagement_title,
                'engagement_type': engagement.engagement_type,
                'partner_id': engagement.partner_id,
                'partner_name': f"{engagement.partner.first_name} {engagement.partner.last_name}" if engagement.partner else '',
                'partner_initials': engagement.partner.initials if engagement.partner else '',
                'deadline': engagement.deadline.isoformat() if engagement.deadline else None,
                'fiscal_year': engagement.fiscal_year  
                }


    def update_engagement(self, id, data):
        with self.app.app_context():
            try:
                if not data['reporting_period']:
                    data['reporting_period'] = None
                
                engagement = Engagement.query.get_or_404(id)
                engagement.engagement_title = data['engagement_title']
                engagement.engagement_type = data['engagement_type']
                engagement.partner_id = data['partner_id'] if data['partner_id'] else None
                engagement.fiscal_year = data['reporting_period']
                
                if data['deadline']:
                    try:
                        engagement.deadline = datetime.strptime(data['deadline'], '%Y-%m-%d').date()
                    except ValueError:
                        try:
                            engagement.deadline = datetime.strptime(data['deadline'], '%b %d, %Y').date()
                        except ValueError:
                            engagement.deadline = datetime.strptime(data['deadline'], '%m/%d/%Y').date()
                else:
                    engagement.deadline = None
                
                db.session.commit()
                return {'success': 'Engagement updated successfuly', 'id': engagement.id, 'title': engagement.engagement_title}
            except Exception as e:
                print(f"Error updating engagement: {e}")
                return {'error': 'Error updating engagement'}

    def get_engagement_assignments(self, engagement_id):
        with self.app.app_context():
            assignments = Assignment.query.filter_by(engagement_id=engagement_id).all()
            return [{
                'id': assignment.id,
                'employee_name': f"{assignment.employee.first_name} {assignment.employee.last_name}",
                'start_date': assignment.start_date.isoformat(),
                'end_date': assignment.end_date.isoformat(),
                'employee_id': assignment.employee_id,
                'engagement_id': assignment.engagement_id
            } for assignment in assignments]

    def get_assignment(self, id):
        with self.app.app_context():
            assignment = Assignment.query.get_or_404(id)
            return {
                'id': assignment.id,
                'engagement_id': assignment.engagement_id,
                'employee_id': assignment.employee_id,
                'employee_name': f"{assignment.employee.first_name} {assignment.employee.last_name}",
                'start_date': assignment.start_date.isoformat(),
                'end_date': assignment.end_date.isoformat()
            }



    def delete_engagement(self, id):
        with self.app.app_context():
            engagement = Engagement.query.get_or_404(id)
            db.session.delete(engagement)
            db.session.commit()
            return True

    def save_assignment(self, data):
        with self.app.app_context():
            if 'id' in data and data['id']:
                assignment = Assignment.query.get_or_404(data['id'])
                assignment.employee_id = data['employee_id']
                assignment.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y').date()
                assignment.end_date = datetime.strptime(data['end_date'], '%m/%d/%Y').date()
            else:
                assignment = Assignment(
                    engagement_id=data['engagement_id'],
                    employee_id=data['employee_id'],
                    start_date=datetime.strptime(data['start_date'], '%m/%d/%Y').date(),
                    end_date=datetime.strptime(data['end_date'], '%m/%d/%Y').date()
                )
                db.session.add(assignment)
            db.session.commit()
            
            # Fetch the engagement title for the newly created assignment
            engagement = Engagement.query.get(assignment.engagement_id)
            
            return {
                'id': assignment.id,
                'employee_id': assignment.employee_id,
                'engagement_id': assignment.engagement_id,
                'engagement_title': engagement.engagement_title,
                'start_date': assignment.start_date.isoformat(),
                'end_date': assignment.end_date.isoformat(),
                
            }



    def delete_assignment(self, id):
        with self.app.app_context():
            assignment = Assignment.query.get_or_404(id)
            db.session.delete(assignment)
            db.session.commit()
            return True

    def get_assignments(self, include_inactive=True):
        with self.app.app_context():
            query = Assignment.query.join(Employee)
            if not include_inactive:
                query = query.filter(Employee.active_status == True)
            assignments = query.all()
            return [{
                'id': a.id,
                'employee_id': a.employee_id,
                'employee_name': f"{a.employee.first_name} {a.employee.last_name}",  # Add this line
                'engagement_id': a.engagement_id,
                'engagement_title': a.engagement.engagement_title,
                'engagement_type': a.engagement.engagement_type,
                'start_date': a.start_date.strftime('%Y-%m-%d'),
                'end_date': a.end_date.strftime('%Y-%m-%d'),
                'partner_initials': a.engagement.partner.initials if a.engagement.partner else None,
                'deadline': a.engagement.deadline.strftime('%m/%d/%Y') if a.engagement.deadline else None,
                'fiscal_year': a.engagement.fiscal_year
            } for a in assignments]
        
    def save_schedule(self):
        with self.app.app_context():
            try:
                employees = self.get_employees()
                assignments = self.get_assignments()
                time_off = self.get_time_off()
                observations = self.get_observations()  # Add this line
                settings = get_settings()
                
                save_directory = settings['General'].get('SaveDirectory', '')
                export_inactive_employees = settings['Schedule'].getboolean('ExportInactiveEmployees', False)

                if not export_inactive_employees:
                    active_employee_ids = set(emp['id'] for emp in employees if emp['active_status'])
                    employees = [emp for emp in employees if emp['active_status']]
                    assignments = [asn for asn in assignments if asn['employee_id'] in active_employee_ids]
                    time_off = [to for to in time_off if to['employee_id'] in active_employee_ids]
                
                save_count = int(settings['General'].get('SaveCount', '0')) + 1
                settings['General']['SaveCount'] = str(save_count)
                
                return save_schedule(employees, assignments, time_off, observations, VERSION, save_directory)
            except Exception as e:
                print(f"Error saving schedule: {e}")
                return False



    def update_assignment(self, id, start_date, end_date, new_employee_id):
        with self.app.app_context():
            try:
                assignment = Assignment.query.get_or_404(id)
                assignment.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                assignment.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                assignment.employee_id = new_employee_id
                
                db.session.commit()
                
                return {
                    'id': assignment.id,
                    'employee_id': assignment.employee_id,
                    'start_date': assignment.start_date.isoformat(),
                    'end_date': assignment.end_date.isoformat(),
                    'engagement_title': assignment.engagement.engagement_title
                }
            except Exception as e:
                db.session.rollback()
                print(f"Error updating assignment: {e}")
                return {'error': str(e)}


    def save_multiple_assignments(self, assignments):
        with self.app.app_context():
            for assignment_data in assignments:
                new_assignment = Assignment(
                    engagement_id=assignment_data['engagement_id'],
                    employee_id=assignment_data['employee_id'],
                    start_date=datetime.strptime(assignment_data['start_date'], '%m/%d/%Y').date(),
                    end_date=datetime.strptime(assignment_data['end_date'], '%m/%d/%Y').date()
                )
                db.session.add(new_assignment)
            db.session.commit()
            return True
        
    def add_time_off(self, data):
        with self.app.app_context():
            try:
                new_time_off = TimeOff(
                    employee_id=data['employee_id'],
                    start_date=datetime.strptime(data['start_date'], '%m/%d/%Y').date(),
                    end_date=datetime.strptime(data['end_date'], '%m/%d/%Y').date(),
                    description=data['description']
                )
                db.session.add(new_time_off)
                db.session.commit()
                return {
                    'success': True,
                    'id': new_time_off.id,
                    'employee_id': new_time_off.employee_id,
                    'employee_name': f"{new_time_off.employee.first_name} {new_time_off.employee.last_name}",
                    'start_date': new_time_off.start_date.isoformat(),
                    'end_date': new_time_off.end_date.isoformat(),
                    'description': new_time_off.description
                }
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}
            
    def delete_time_off(self, id):
        with self.app.app_context():
            try:
                time_off = TimeOff.query.get_or_404(id)
                db.session.delete(time_off)
                db.session.commit()
                return {'success': True}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}
        
    def get_time_off(self):
        with self.app.app_context():
            time_off_list = TimeOff.query.all()
            return [{
                'id': time_off.id,
                'employee_id': time_off.employee_id,
                'employee_name': f"{time_off.employee.first_name} {time_off.employee.last_name}",
                'start_date': time_off.start_date.isoformat(),
                'end_date': time_off.end_date.isoformat(),
                'description': time_off.description
            } for time_off in time_off_list]
        
    def get_time_off_for_edit(self, id):
        with self.app.app_context():
            time_off = TimeOff.query.get_or_404(id)
            return {
                'id': time_off.id,
                'employee_id': time_off.employee_id,
                'employee_name': f"{time_off.employee.first_name} {time_off.employee.last_name}",
                'start_date': time_off.start_date.isoformat(),
                'end_date': time_off.end_date.isoformat(),
                'description': time_off.description
            }


    def update_time_off(self, id, data):
        with self.app.app_context():
            try:
                time_off = TimeOff.query.get_or_404(id)
                time_off.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
                time_off.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
                db.session.commit()
                return {
                    'success': True,
                    'id': time_off.id,
                    'employee_id': time_off.employee_id,
                    'employee_name': f"{time_off.employee.first_name} {time_off.employee.last_name}",
                    'start_date': time_off.start_date.isoformat(),
                    'end_date': time_off.end_date.isoformat(),
                    'description': time_off.description
                }
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}
    
    def check_engagement_assignments(self, engagement_id):
        with self.app.app_context():
            assignments = Assignment.query.filter_by(engagement_id=engagement_id).first()
            return assignments is not None

    def delete_engagement(self, id):
        with self.app.app_context():
            engagement = Engagement.query.get_or_404(id)
            # Delete associated assignments first
            Assignment.query.filter_by(engagement_id=id).delete()
            db.session.delete(engagement)
            db.session.commit()
            return True

    def get_partners(self):
        with self.app.app_context():
            partners = Partner.query.all()
            return [partner.to_dict() for partner in partners]

    def add_partner(self, data):
        with self.app.app_context():
            try:
                new_partner = Partner(
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    initials=data['initials']
                )
                db.session.add(new_partner)
                db.session.commit()
                return {'success': True, **new_partner.to_dict()}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}

    def get_partner(self, id):
        with self.app.app_context():
            partner = Partner.query.get_or_404(id)
            return partner.to_dict()


    def update_partner(self, id, data):
        with self.app.app_context():
            try:
                partner = Partner.query.get_or_404(id)
                partner.first_name = data['first_name']
                partner.last_name = data['last_name']
                partner.initials = data['initials']
                db.session.commit()
                return {'success': True, **partner.to_dict()}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}

    def delete_partner(self, id, option):
        with self.app.app_context():
            partner = Partner.query.get(id)
            if not partner:
                return {'success': False, 'message': 'Partner not found'}

            # Get or create the "Removed Partner"
            removed_partner = Partner.query.filter_by(first_name="Removed", last_name="Partner").first()
            if not removed_partner:
                removed_partner = Partner(first_name="Removed", last_name="Partner", initials="-RP-")
                db.session.add(removed_partner)
                db.session.commit()

            if option == 'delete-all':
                # Update observations
                Observation.query.filter_by(observer_partner=id).update({'observer_partner': removed_partner.id})
                Observation.query.filter_by(scheduler_partner=id).update({'scheduler_partner': removed_partner.id})
                
                # Delete the partner
                db.session.delete(partner)
            
            db.session.commit()
            return {'success': True}

    def get_concurrent_engagements_by_partner(self, start_date, end_date):
        with self.app.app_context():
            start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
            
            partners = Partner.query.all()
            weekly_data = defaultdict(lambda: {partner.id: {'count': 0, 'engagements': set()} for partner in partners})
            current_date = start_date
            
            while current_date <= end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                
                for partner in partners:
                    concurrent_engagements = Engagement.query.filter(
                        Engagement.partner_id == partner.id,
                        Engagement.id.in_(
                            Assignment.query.filter(
                                Assignment.start_date <= current_date,
                                Assignment.end_date >= current_date
                            ).with_entities(Assignment.engagement_id)
                        )
                    ).distinct().all()
                    
                    count = len(concurrent_engagements)
                    weekly_data[week_key][partner.id]['count'] = count
                    weekly_data[week_key][partner.id]['engagements'] = {e.engagement_title for e in concurrent_engagements}
                
                current_date += timedelta(days=1)
            
            dates = sorted(weekly_data.keys())
            datasets = []
            
            for partner in partners:
                counts = [weekly_data[date][partner.id]['count'] for date in dates]
                engagements = [list(weekly_data[date][partner.id]['engagements']) for date in dates]
                datasets.append({
                    'label': f"{partner.first_name} {partner.last_name}",
                    'data': counts,
                    'engagements': engagements
                })
            
            return {
                'dates': dates,
                'datasets': datasets
            }

        
    def get_concurrent_engagements(self, start_date, end_date):
        with self.app.app_context():
            start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
            
            weekly_data = defaultdict(lambda: {'count': 0, 'engagements': set()})
            current_date = start_date
            
            while current_date <= end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                
                concurrent_engagements = Engagement.query.join(Assignment).filter(
                    Assignment.start_date <= current_date,
                    Assignment.end_date >= current_date
                ).distinct().all()
                
                count = len(concurrent_engagements)
                if count > weekly_data[week_key]['count']:
                    weekly_data[week_key]['count'] = count
                    weekly_data[week_key]['engagements'] = {e.engagement_title for e in concurrent_engagements}
                
                current_date += timedelta(days=1)
            
            dates = sorted(weekly_data.keys())
            counts = [weekly_data[date]['count'] for date in dates]
            engagements = [list(weekly_data[date]['engagements']) for date in dates]
            
            return {
                'dates': dates,
                'counts': counts,
                'engagements': engagements
            }

    def get_observations(self, show_hidden=False):
        with self.app.app_context():
            query = Observation.query.join(Engagement)
            if not show_hidden:
                query = query.filter(or_(Observation.hidden.is_(False), Observation.hidden.is_(None)))
            observations = query.all()
            return [{
                'id': o.id,
                'engagement_title': o.engagement.engagement_title,
                'engagement_type': o.engagement.engagement_type,
                'partner_name': f"{o.engagement.partner.first_name} {o.engagement.partner.last_name}" if o.engagement.partner else None,
                'scheduler_name': self.get_person_name(o.scheduler_employee, o.scheduler_partner),
                'observer_name': self.get_person_name(o.observer_employee, o.observer_partner) or o.outside_observer,
                'outside_observer': o.outside_observer,
                'scheduled_observation_date': o.scheduled_observation_date.strftime('%m/%d/%Y') if o.scheduled_observation_date else None,
                'reporting_period': o.engagement.fiscal_year,
                'deadline': o.engagement.deadline.strftime('%m/%d/%Y') if o.engagement.deadline else None,
                'previous_observation': self.get_previous_observation_info(o.previous_observation) if o.previous_observation else None,
                'hidden': o.hidden if o.hidden is not None else False
            } for o in observations]
        
    def toggle_observation_visibility(self, id, hidden_state):
        with self.app.app_context():
            try:
                observation = Observation.query.get_or_404(id)
                observation.hidden = hidden_state
                db.session.commit()
                return {'success': True, 'message': f'Observation visibility updated successfully'}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}
        
    def get_previous_observation_info(self, previous_observation):
        if previous_observation:
            return {
                'id': previous_observation.id,
                'scheduled_observation_date': previous_observation.scheduled_observation_date.strftime('%m/%d/%Y') if previous_observation.scheduled_observation_date else None,
                'scheduler_name': self.get_person_name(previous_observation.scheduler_employee, previous_observation.scheduler_partner),
                'observer_name': self.get_person_name(previous_observation.observer_employee, previous_observation.observer_partner),
                'outside_observer': previous_observation.outside_observer
            }
        return None

    def get_person_name(self, employee, partner):
        if employee:
            return f"{employee.first_name} {employee.last_name}"
        elif partner:
            return f"{partner.first_name} {partner.last_name}"
        return None

    def get_observation(self, id):
        with self.app.app_context():
            o = Observation.query.get_or_404(id)
            return {
                'id': o.id,
                'engagement_id': o.engagement_id,
                'engagement_title': o.engagement.engagement_title,
                'scheduler_id': o.scheduler_id,
                'scheduler_partner_id': o.scheduler_partner_id,
                'scheduler_name': self.get_person_name(o.scheduler_employee, o.scheduler_partner),
                'observer_id': o.observer_id,
                'observer_partner_id': o.observer_partner_id,
                'observer_name': self.get_person_name(o.observer_employee, o.observer_partner) or o.outside_observer,
                'outside_observer': o.outside_observer,
                'scheduled_observation_date': o.scheduled_observation_date.strftime('%Y-%m-%d') if o.scheduled_observation_date else None,
                'previous_observation_id': o.previous_observation_id,
                'engagement_type': o.engagement.engagement_type,
            }

    def add_observation(self, data):
        with self.app.app_context():
            new_observation = Observation(
                engagement_id=data['engagement_id'],
                scheduler_id=data.get('scheduler_id'),
                scheduler_partner_id=data.get('scheduler_partner_id'),
                observer_id=data.get('observer_id'),
                observer_partner_id=data.get('observer_partner_id'),
                outside_observer=data.get('outside_observer'),
                previous_observation_id=data.get('previous_observation_id'),
                scheduled_observation_date=datetime.strptime(data['scheduled_observation_date'], '%Y-%m-%d').date() if data.get('scheduled_observation_date') else None
            )
            db.session.add(new_observation)
            db.session.commit()
            return {'id': new_observation.id}

    def update_observation(self, id, data):
        with self.app.app_context():
            observation = Observation.query.get_or_404(id)
            observation.engagement_id = data['engagement_id']
            observation.scheduler_id = data.get('scheduler_id')
            observation.scheduler_partner_id = data.get('scheduler_partner_id')
            observation.observer_id = data.get('observer_id')
            observation.observer_partner_id = data.get('observer_partner_id')
            observation.outside_observer = data.get('outside_observer')
            observation.previous_observation_id = data.get('previous_observation_id')
            observation.scheduled_observation_date = datetime.strptime(data['scheduled_observation_date'], '%Y-%m-%d').date() if data.get('scheduled_observation_date') else None
            db.session.commit()
            return {'id': observation.id}

    def delete_observation(self, id):
        with self.app.app_context():
            observation = Observation.query.get_or_404(id)
            db.session.delete(observation)
            db.session.commit()
            return True

    def get_employee_concurrent_engagements(self, start_date, end_date):
        with self.app.app_context():
            start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
            
            employees = Employee.query.all()
            weekly_data = defaultdict(lambda: {employee.id: {'count': 0, 'engagements': set()} for employee in employees})
            current_date = start_date
            
            while current_date <= end_date:
                week_start = current_date - timedelta(days=current_date.weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                
                for employee in employees:
                    concurrent_engagements = Engagement.query.join(Assignment).filter(
                        Assignment.employee_id == employee.id,
                        Assignment.start_date <= current_date,
                        Assignment.end_date >= current_date
                    ).distinct().all()
                    
                    count = len(concurrent_engagements)
                    if count > weekly_data[week_key][employee.id]['count']:
                        weekly_data[week_key][employee.id]['count'] = count
                        weekly_data[week_key][employee.id]['engagements'] = {e.engagement_title for e in concurrent_engagements}
                
                current_date += timedelta(days=1)
            
            dates = sorted(weekly_data.keys())
            datasets = []
            engagements = []
            
            for employee in employees:
                counts = [weekly_data[date][employee.id]['count'] for date in dates]
                datasets.append({
                    'label': f"{employee.first_name} {employee.last_name}",
                    'data': counts,
                    'borderColor': self.get_random_color(),
                    'tension': 0.1
                })
                engagements.append([list(weekly_data[date][employee.id]['engagements']) for date in dates])
            
            return {
                'dates': dates,
                'datasets': datasets,
                'engagements': engagements
            }
    
    def get_partner_engagements(self, start_date, end_date):
        with self.app.app_context():
            start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
            
            # Find all assignments that fall within/overlap with the provided date range
            relevant_assignments = Assignment.query.filter(
                Assignment.start_date <= end_date,
                Assignment.end_date >= start_date
            ).all()
            
            # Get the list of corresponding engagements
            relevant_engagement_ids = set(assignment.engagement_id for assignment in relevant_assignments)
            
            partners = Partner.query.all()
            result = []
            
            for partner in partners:
                engagements = []
                
                partner_engagements = Engagement.query.filter(
                    Engagement.partner_id == partner.id,
                    Engagement.id.in_(relevant_engagement_ids)
                ).all()
                
                for engagement in partner_engagements:
                    # Get all assignments for this engagement, regardless of date range
                    all_assignments = Assignment.query.filter(
                        Assignment.engagement_id == engagement.id
                    ).all()
                    
                    if all_assignments:
                        assigned_employees = [f"{a.employee.first_name} {a.employee.last_name}" for a in all_assignments]
                        earliest_assignment = min(a.start_date for a in all_assignments)
                        latest_assignment = max(a.end_date for a in all_assignments)
                        
                    engagements.append({
                        'title': engagement.engagement_title,
                        'type': engagement.engagement_type,  # Add this line
                        'fiscal_year': engagement.fiscal_year,
                        'deadline': engagement.deadline.strftime('%m/%d/%Y') if engagement.deadline else None,
                        'assigned_employees': assigned_employees,
                        'earliest_assignment': earliest_assignment.strftime('%m/%d/%Y'),
                        'latest_assignment': latest_assignment.strftime('%m/%d/%Y')
                    })
                
                if engagements:
                    result.append({
                        'name': f"{partner.first_name} {partner.last_name}",
                        'engagements': engagements
                    })
            
            return result
        
    def download_partner_engagements_to_excel(self, start_date, end_date):
        data = self.get_partner_engagements(start_date, end_date)
        
        # Flatten the data structure
        flattened_data = []
        for partner in data:
            for engagement in partner['engagements']:
                flattened_data.append({
                    'Partner Name': partner['name'],
                    'Engagement Title': engagement['title'],
                    'Engagement Type': engagement['type'],  # Add this line
                    'Fiscal Year': engagement['fiscal_year'],
                    'Earliest Assignment': engagement['earliest_assignment'],
                    'Latest Assignment': engagement['latest_assignment'],
                    'Deadline': engagement['deadline'],
                    'Assigned Employees': ', '.join(engagement['assigned_employees']) if engagement['assigned_employees'] else 'None'
                })

        # Convert the flattened data to a DataFrame
        df = pd.DataFrame(flattened_data)

        # Create a Pandas Excel writer using openpyxl as the engine
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Add a sheet with the date range information
            date_range_df = pd.DataFrame({
                'Report Date Range': [f'From {start_date} to {end_date}']
            })
            date_range_df.to_excel(writer, sheet_name='Report Info', index=False)
            
            # Add the main data sheet
            df.to_excel(writer, sheet_name='Partner Engagements', index=False)
        
        output.seek(0)

        # Generate a default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"partner_engagements_{timestamp}.xlsx"

        # Use webview's file dialog
        file_path = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG, save_filename=default_filename, file_types=('Excel Files (*.xlsx)',))

        if file_path and len(file_path) > 0:
            with open(file_path, 'wb') as f:
                f.write(output.getvalue())
                print("File saved to:", file_path)
            return {"success": True, "filename": os.path.basename(file_path)}
        else:
            return {"success": False, "message": "Save operation cancelled"}



    def get_engagement_deadline_heatmap(self, start_date, end_date):
        with self.app.app_context():
            start_date = datetime.strptime(start_date, '%m/%d/%Y').date()
            end_date = datetime.strptime(end_date, '%m/%d/%Y').date()
            
            engagements = Engagement.query.filter(
                Engagement.deadline >= start_date,
                Engagement.deadline <= end_date
            ).all()
            
            heatmap_data = defaultdict(lambda: {'count': 0, 'engagements': []})
            for engagement in engagements:
                deadline_key = engagement.deadline.strftime('%Y-%m-%d')
                heatmap_data[deadline_key]['count'] += 1
                heatmap_data[deadline_key]['engagements'].append(engagement.engagement_title)
            
            return {
                'dates': list(heatmap_data.keys()),
                'counts': [data['count'] for data in heatmap_data.values()],
                'engagements': [data['engagements'] for data in heatmap_data.values()]
            }

    def update_assignment_and_engagement(self, assignment_id, data):
        with self.app.app_context():
            try:
                # Update Assignment
                assignment = Assignment.query.get_or_404(assignment_id)
                assignment.start_date = datetime.strptime(data['start_date'], '%m/%d/%Y').date()
                
                # Update Engagement
                engagement = assignment.engagement
                engagement.engagement_title = data['engagement_title']
                engagement.engagement_type = data['engagement_type']
                engagement.fiscal_year = data['fiscal_year']
                engagement.partner_id = data['partner_id']
                if data['deadline']:
                    engagement.deadline = datetime.strptime(data['deadline'], '%m/%d/%Y').date()
                else:
                    engagement.deadline = None

                # Update all assignments related to this engagement
                related_assignments = Assignment.query.filter_by(engagement_id=engagement.id).all()
                updated_assignments = []
                for related_assignment in related_assignments:
                    updated_assignments.append({
                        'id': related_assignment.id,
                        'employee_id': related_assignment.employee_id,
                        'start_date': related_assignment.start_date.strftime('%Y-%m-%d'),
                        'end_date': related_assignment.end_date.strftime('%Y-%m-%d'),
                        'engagement_title': engagement.engagement_title,
                        'engagement_type': engagement.engagement_type,
                        'fiscal_year': engagement.fiscal_year,
                        'partner_initials': engagement.partner.initials if engagement.partner else 'N/A',
                        'deadline': engagement.deadline.strftime('%m/%d/%Y') if engagement.deadline else 'N/A'
                    })

                db.session.commit()
                return {
                    'success': True, 
                    'message': 'Assignment and engagement updated successfully',
                    'updated_assignments': updated_assignments
                }
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}

    def add_user(self, username, password):
        with self.app.app_context():
            try:
                new_user = User(username=username)
                new_user.set_password(password)
                db.session.add(new_user)
                db.session.commit()
                return {'success': True}
            except Exception as e:
                return {'success': False, 'error': str(e)}

    def get_users(self):
        with self.app.app_context():
            users = User.query.all()
            return [{'id': user.id, 'username': user.username} for user in users]

    def delete_user(self, user_id):
        with self.app.app_context():
            try:
                user = User.query.get(user_id)
                if user:
                    db.session.delete(user)
                    db.session.commit()
                    return {'success': True, 'message': f'User {user.username} deleted successfully'}
                else:
                    return {'success': False, 'error': 'User not found'}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}


    def logout(self):
        with self.app.app_context():
            # Assuming you have a way to get the current user's ID
            current_user_id = self.get_current_user_id()  # You'll need to implement this function
            log_entry = UserLog(user_id=current_user_id, action='logout')
            db.session.add(log_entry)
            db.session.commit()
        return {'success': True, 'message': 'Logged out successfully'}


    def get_random_color(self):
        return f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"

    def compare_schedules(self, saved_schedule_path):
        with self.app.app_context():
            def format_date(date_str):
                if not date_str:
                    return 'N/A'
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    return date_obj.strftime('%m/%d/%Y')
                except ValueError:
                    return date_str
                
            current_assignments = self.get_assignments(include_inactive=False)
            
            with open(saved_schedule_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            assignments_start = html_content.find('const assignments =') + len('const assignments =')
            assignments_end = html_content.find(';', assignments_start)
            saved_assignments_json = html_content[assignments_start:assignments_end].strip()
            saved_assignments = json.loads(saved_assignments_json)
            
            changes = {
                'new_engagements': [],
                'new_assignments': [],
                'removed_engagements': [],
                'removed_assignments': [],
                'modified_engagement_details': [],
                  'modified_assignment_dates': [] 
            }
            
            # Create dictionaries for quick lookup
            current_assignments_by_id = {str(a['id']): a for a in current_assignments}
            saved_assignments_by_id = {str(a['id']): a for a in saved_assignments}
            
            # Group assignments by engagement_id
            current_by_engagement = {}
            saved_by_engagement = {}
            
            for assignment in current_assignments:
                engagement_id = str(assignment['engagement_id'])
                if engagement_id not in current_by_engagement:
                    current_by_engagement[engagement_id] = []
                current_by_engagement[engagement_id].append(assignment)
                
            for assignment in saved_assignments:
                engagement_id = str(assignment['engagement_id'])
                if engagement_id not in saved_by_engagement:
                    saved_by_engagement[engagement_id] = []
                saved_by_engagement[engagement_id].append(assignment)
            
            # Find new and modified engagements
            for engagement_id, curr_assignments in current_by_engagement.items():
                if engagement_id not in saved_by_engagement:
                    # New engagement
                    changes['new_engagements'].append(curr_assignments[0])
                else:
                    # Compare engagement details using first assignment
                    curr_first = curr_assignments[0]
                    saved_first = saved_by_engagement[engagement_id][0]
                    
                    if (curr_first['partner_initials'] != saved_first['partner_initials'] or
                        curr_first['deadline'] != saved_first['deadline']):
                        changes['modified_engagement_details'].append({
                            'engagement_title': curr_first['engagement_title'],
                            'engagement_type': curr_first['engagement_type'],
                            'fiscal_year': curr_first['fiscal_year'],
                            'current_partner': curr_first['partner_initials'],
                            'previous_partner': saved_first['partner_initials'],
                            'current_deadline': curr_first['deadline'],
                            'previous_deadline': saved_first['deadline']
                        })
            
            # Find removed engagements
            for engagement_id, saved_assignments_list in saved_by_engagement.items():
                if engagement_id not in current_by_engagement:
                    changes['removed_engagements'].append(saved_assignments_list[0])
            
            # Find new and removed assignments
            current_assignment_ids = set(current_assignments_by_id.keys())
            saved_assignment_ids = set(saved_assignments_by_id.keys())
            
            # New assignments
            for assignment_id in current_assignment_ids - saved_assignment_ids:
                assignment = current_assignments_by_id[assignment_id]
                changes['new_assignments'].append({
                    'assignment': assignment,
                    'engagement_title': assignment['engagement_title']
                })
            
            # Removed assignments
            for assignment_id in saved_assignment_ids - current_assignment_ids:
                assignment = saved_assignments_by_id[assignment_id]
                # Match employee information using the employee_id
                changes['removed_assignments'].append({
                    'assignment': {
                        **assignment,  # Keep all original assignment data
                        'employee_name': next(
                            (emp['first_name'] + ' ' + emp['last_name'] 
                            for emp in self.get_employees() 
                            if emp['id'] == assignment['employee_id']),
                            'Unknown Employee'
                        )
                    },
                    'engagement_title': assignment['engagement_title']
                })


            common_assignments = current_assignment_ids.intersection(saved_assignment_ids)
            for assignment_id in common_assignments:
                current = current_assignments_by_id[assignment_id]
                saved = saved_assignments_by_id[assignment_id]
                
                if (current['start_date'] != saved['start_date'] or 
                    current['end_date'] != saved['end_date']):
                    changes['modified_assignment_dates'].append({
                        'assignment': current,
                        'previous_start_date': format_date(saved['start_date']),
                        'previous_end_date': format_date(saved['end_date']),
                        'new_start_date': format_date(current['start_date']),
                        'new_end_date': format_date(current['end_date'])
                    })
            
            # Format dates in the changes
            for assignment in changes['new_engagements']:
                assignment['start_date'] = format_date(assignment['start_date'])
                assignment['end_date'] = format_date(assignment['end_date'])
            
            for item in changes['new_assignments']:
                item['assignment']['start_date'] = format_date(item['assignment']['start_date'])
                item['assignment']['end_date'] = format_date(item['assignment']['end_date'])
            
            for item in changes['removed_assignments']:
                item['assignment']['start_date'] = format_date(item['assignment']['start_date'])
                item['assignment']['end_date'] = format_date(item['assignment']['end_date'])
            
            for item in changes['removed_engagements']:
                item['start_date'] = format_date(item['start_date'])
                item['end_date'] = format_date(item['end_date'])
            
            return changes
        
    def select_saved_schedule(self):
        with self.app.app_context():
            file_types = ('HTML Files (*.html)',)
            result = webview.windows[0].create_file_dialog(webview.OPEN_DIALOG, allow_multiple=False, file_types=file_types)
            
            if result and len(result) > 0:
                return self.compare_schedules(result[0])
            return None

    def export_cpe_time_offs(self):
        with self.app.app_context():
            try:
                # Query time offs with CPE description
                time_offs = TimeOff.query.join(Employee).filter(TimeOff.description == "CPE").all()
                
                # Create DataFrame for CPE time offs
                data = []
                for time_off in time_offs:
                    data.append({
                        'Employee': f"{time_off.employee.first_name} {time_off.employee.last_name}",
                        'Start Date': time_off.start_date.strftime('%m/%d/%Y'),
                        'End Date': time_off.end_date.strftime('%m/%d/%Y'),
                        'Description': time_off.description
                    })
                
                df_cpe = pd.DataFrame(data)
                
                # Create export info DataFrame
                export_info = pd.DataFrame([{
                    'Export Date': datetime.now().strftime('%m/%d/%Y'),
                    'Export Time': datetime.now().strftime('%I:%M:%S %p')
                }])
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                default_filename = f"cpe_time_offs_{timestamp}.xlsx"
                
                file_path = webview.windows[0].create_file_dialog(
                    webview.SAVE_DIALOG, 
                    save_filename=default_filename, 
                    file_types=('Excel Files (*.xlsx)',)
                )
                
                if file_path and len(file_path) > 0:
                    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                        df_cpe.to_excel(writer, sheet_name='CPE Time Off', index=False)
                        export_info.to_excel(writer, sheet_name='Export Info', index=False)
                    return {'success': True}
                return {'success': False}
                
            except Exception as e:
                print(f"Error exporting CPE time offs: {str(e)}")
                return {'success': False}
            

    def rollforward_engagements(self, engagement_ids, months_offset, include_assignments):
        with self.app.app_context():
            try:
                inactive_employees = []
                new_engagements = []
                
                for eng_id in engagement_ids:
                    engagement = Engagement.query.get(eng_id)
                    if not engagement:
                        continue
                    
                    # Create new engagement with offset dates
                    new_engagement = Engagement(
                        engagement_title=f"{engagement.engagement_title} (Rolled Forward)",
                        engagement_type=engagement.engagement_type,
                        partner_id=engagement.partner_id,
                        fiscal_year=engagement.fiscal_year
                    )
                    
                    if engagement.deadline:
                        new_deadline = engagement.deadline + relativedelta(months=months_offset)
                        new_engagement.deadline = new_deadline
                    
                    db.session.add(new_engagement)
                    db.session.flush()  # Get new engagement ID
                    
                    if include_assignments:
                        # Check for inactive employees
                        assignments = Assignment.query.filter_by(engagement_id=eng_id).all()
                        for assignment in assignments:
                            if not assignment.employee.active_status:
                                inactive_employees.append({
                                    'assignment_id': assignment.id,
                                    'employee_name': f"{assignment.employee.first_name} {assignment.employee.last_name}",
                                    'engagement_title': engagement.engagement_title
                                })
                                continue
                            
                            # Create new assignment with offset dates
                            new_assignment = Assignment(
                                engagement_id=new_engagement.id,
                                employee_id=assignment.employee_id,
                                start_date=assignment.start_date + relativedelta(months=months_offset),
                                end_date=assignment.end_date + relativedelta(months=months_offset)
                            )
                            db.session.add(new_assignment)
                    
                    new_engagements.append(new_engagement)
                
                if inactive_employees:
                    return {
                        'success': False,
                        'inactive_employees': inactive_employees
                    }
                
                db.session.commit()
                return {'success': True}
                
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}


    def resolve_inactive_employees(self, resolutions):
        with self.app.app_context():
            try:
                for resolution in resolutions:
                    assignment = Assignment.query.get(resolution['assignment_id'])
                    if resolution['action'] == 'delete':
                        db.session.delete(assignment)
                    elif resolution['action'] == 'replace':
                        assignment.employee_id = resolution['new_employee_id']
                
                db.session.commit()
                return {'success': True}
            except Exception as e:
                db.session.rollback()
                return {'success': False, 'error': str(e)}


    def get_inactive_employee_assignments(self, engagement_ids):
        with self.app.app_context():
            assignments = Assignment.query\
                .join(Employee)\
                .join(Engagement)\
                .filter(
                    Assignment.engagement_id.in_(engagement_ids),
                    Employee.active_status == False
                ).all()
                
            return [{
                'id': assignment.id,
                'engagement_id': assignment.engagement_id,
                'engagement_title': assignment.engagement.engagement_title,
                'employee_id': assignment.employee_id,
                'employee_name': f"{assignment.employee.first_name} {assignment.employee.last_name}",
                'start_date': assignment.start_date.isoformat(),
                'end_date': assignment.end_date.isoformat()
            } for assignment in assignments]

    def get_active_employees(self):
        with self.app.app_context():
            employees = Employee.query\
                .filter(
                    Employee.active_status == True,
                    Employee.first_name != "Removed",
                    Employee.last_name != "Employee"
                )\
                .order_by(Employee.first_name, Employee.last_name)\
                .all()
                
            return [{
                'id': employee.id,
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'hire_date': employee.hire_date.isoformat()
            } for employee in employees]
        
    def preview_rollforward(self, engagement_ids, months_offset, pattern_replacements, assignment_resolutions):
        with self.app.app_context():
            preview_data = {
                'engagements': [],
                'assignments': []
            }
            
            for eng_id in engagement_ids:
                engagement = Engagement.query.get(eng_id)
                if not engagement:
                    continue
                
                # Store original values
                original_title = engagement.engagement_title
                original_type = engagement.engagement_type
                original_reporting_period = engagement.fiscal_year
                original_deadline = engagement.deadline.strftime('%m/%d/%Y') if engagement.deadline else None

                # Calculate new values with pattern replacements
                new_title = original_title
                new_type = original_type
                new_reporting_period = original_reporting_period

                # Apply pattern replacements to all fields
                for pattern in pattern_replacements:
                    if pattern['field'] == 'engagement_type' and pattern['find'] in new_type:
                        new_type = new_type.replace(pattern['find'], pattern['replace'])
                    elif pattern['field'] == 'title' and pattern['find'] in new_title:
                        new_title = new_title.replace(pattern['find'], pattern['replace'])
                    elif pattern['field'] == 'reporting_period' and pattern['find'] in str(new_reporting_period):
                        new_reporting_period = str(new_reporting_period).replace(pattern['find'], pattern['replace'])
                
                # Add "(Rolled Forward)" to title if no pattern replacement was done
                if new_title == original_title:
                    new_title = original_title
                
                # Calculate new deadline
                new_deadline = None
                if engagement.deadline:
                    new_deadline = (engagement.deadline + relativedelta(months=months_offset)).strftime('%m/%d/%Y')
                
                preview_data['engagements'].append({
                    'original_title': original_title,
                    'original_type': original_type,
                    'original_reporting_period': original_reporting_period,
                    'original_deadline': original_deadline,
                    'new_title': new_title,
                    'new_reporting_period': new_reporting_period,
                    'new_deadline': new_deadline,
                    'type': new_type
                })
                
                # Preview assignments
                assignments = Assignment.query.filter_by(engagement_id=eng_id).all()
                for assignment in assignments:
                    resolution = next((r for r in assignment_resolutions.values() 
                                    if str(r.get('assignment_id')) == str(assignment.id)), None)
                    
                    original_employee = assignment.employee
                    original_start = assignment.start_date
                    original_end = assignment.end_date
                    
                    if resolution:
                        if resolution['action'] == 'skip':
                            continue
                        elif resolution['action'] == 'replace':
                            employee = Employee.query.get(resolution['new_employee_id'])
                    else:
                        employee = original_employee
                    
                    new_start = assignment.start_date + relativedelta(months=months_offset)
                    new_end = assignment.end_date + relativedelta(months=months_offset)
                    
                    preview_data['assignments'].append({
                        'engagement_title': new_title,
                        'original_employee_name': f"{original_employee.first_name} {original_employee.last_name}",
                        'employee_name': f"{employee.first_name} {employee.last_name}",
                        'original_start_date': original_start.isoformat(),
                        'original_end_date': original_end.isoformat(),
                        'start_date': new_start.isoformat(),
                        'end_date': new_end.isoformat()
                    })
            
            return preview_data

    def execute_rollforward(self, engagement_ids, months_offset, pattern_replacements, assignment_resolutions):
        with self.app.app_context():
            try:
                result = {
                    'engagements': [],
                    'assignments': []
                }
                
                for eng_id in engagement_ids:
                    engagement = Engagement.query.get(eng_id)
                    if not engagement:
                        continue
                    
                    # Apply pattern replacements to create new engagement
                    new_title = engagement.engagement_title
                    new_type = engagement.engagement_type
                    new_reporting_period = engagement.fiscal_year
                    
                    for pattern in pattern_replacements:
                        if pattern['field'] == 'engagement_type' and pattern['find'] in new_type:
                            new_type = new_type.replace(pattern['find'], pattern['replace'])
                        elif pattern['field'] == 'title' and pattern['find'] in new_title:
                            new_title = new_title.replace(pattern['find'], pattern['replace'])
                        elif pattern['field'] == 'reporting_period' and pattern['find'] in str(new_reporting_period):
                            new_reporting_period = str(new_reporting_period).replace(pattern['find'], pattern['replace'])

                    # Create new engagement
                    new_engagement = Engagement(
                        engagement_title=new_title,
                        engagement_type=new_type,
                        partner_id=engagement.partner_id,
                        fiscal_year=new_reporting_period
                    )
                    
                    if engagement.deadline:
                        new_deadline = engagement.deadline + relativedelta(months=months_offset)
                        new_engagement.deadline = new_deadline
                    
                    db.session.add(new_engagement)
                    db.session.flush()  # Get new engagement ID
                    
                    result['engagements'].append({
                        'id': new_engagement.id,
                        'title': new_engagement.engagement_title,
                        'type': new_engagement.engagement_type,
                        'reporting_period': new_engagement.fiscal_year,
                        'deadline': new_engagement.deadline.strftime('%m/%d/%Y') if new_engagement.deadline else None
                    })
                    
                    # Create new assignments based on resolutions
                    assignments = Assignment.query.filter_by(engagement_id=eng_id).all()
                    for assignment in assignments:
                        resolution = assignment_resolutions.get(str(assignment.id))
                        
                        if resolution and resolution['action'] == 'skip':
                            continue
                        
                        employee_id = resolution['new_employee_id'] if resolution and resolution['action'] == 'replace' else assignment.employee_id
                        
                        new_assignment = Assignment(
                            engagement_id=new_engagement.id,
                            employee_id=employee_id,
                            start_date=assignment.start_date + relativedelta(months=months_offset),
                            end_date=assignment.end_date + relativedelta(months=months_offset)
                        )
                        
                        db.session.add(new_assignment)
                        db.session.flush()
                        
                        employee = Employee.query.get(employee_id)
                        result['assignments'].append({
                            'id': new_assignment.id,
                            'engagement_title': new_engagement.engagement_title,
                            'employee_name': f"{employee.first_name} {employee.last_name}",
                            'start_date': new_assignment.start_date.isoformat(),
                            'end_date': new_assignment.end_date.isoformat()
                        })
                
                db.session.commit()
                return result
                
            except Exception as e:
                db.session.rollback()
                print(f"Error in execute_rollforward: {str(e)}")
                return {'error': str(e)}

def check_and_create_user():
    with server.app_context():
        if User.query.count() == 0:
            if not create_first_user():
                return False
    return login()

def create_first_user():
    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title("Create First User")
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    dialog.iconbitmap(icon_path)
    
    window_width = 300
    window_height = 180
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')

    dialog.configure(bg='#f0f0f0')

    tk.Label(dialog, text="Username:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    username_entry = tk.Entry(dialog, font=('Arial', 10))
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    username_entry.focus()

    tk.Label(dialog, text="Password:", bg='#f0f0f0', font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    password_entry = tk.Entry(dialog, show='*', font=('Arial', 10))
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(dialog, text="Confirm Password:", bg='#f0f0f0', font=('Arial', 10)).grid(row=2, column=0, padx=10, pady=10, sticky='e')
    confirm_password_entry = tk.Entry(dialog, show='*', font=('Arial', 10))
    confirm_password_entry.grid(row=2, column=1, padx=10, pady=10)

    result = [False]

    def on_create():
        username = username_entry.get()
        password = password_entry.get()
        confirm_password = confirm_password_entry.get()
        if username and password and confirm_password:
            if password == confirm_password:
                with server.app_context():
                    new_user = User(username=username)
                    new_user.set_password(password)
                    db.session.add(new_user)
                    db.session.commit()
                result[0] = True
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Passwords do not match", parent=dialog)
        else:
            messagebox.showerror("Error", "Please fill in all fields", parent=dialog)

    create_button = tk.Button(dialog, text="Create User", command=on_create, bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'))
    create_button.grid(row=3, column=0, columnspan=2, pady=10)

    dialog.bind('<Return>', lambda event: on_create())

    dialog.wait_window()
    return result[0]



def login():
    root = tk.Tk()
    root.withdraw()

    dialog = tk.Toplevel(root)
    dialog.title("Staff Scheduler Login")
    
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.ico')
    dialog.iconbitmap(icon_path)
    
    window_width = 300
    window_height = 150
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    dialog.geometry(f'{window_width}x{window_height}+{x}+{y}')

    dialog.configure(bg='#f0f0f0')

    tk.Label(dialog, text="Username:", bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, padx=10, pady=10, sticky='e')
    username_entry = tk.Entry(dialog, font=('Arial', 10))
    username_entry.grid(row=0, column=1, padx=10, pady=10)
    username_entry.focus()

    tk.Label(dialog, text="Password:", bg='#f0f0f0', font=('Arial', 10)).grid(row=1, column=0, padx=10, pady=10, sticky='e')
    password_entry = tk.Entry(dialog, show='*', font=('Arial', 10))
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    result = [False]

    def on_ok():
        username = username_entry.get()
        password = password_entry.get()
        if username and password:
            with server.app_context():
                user = User.query.filter_by(username=username).first()
                if user and user.check_password(password):
                    api.current_user_id = user.id
                    print(f"User {user.username} with ID {user.id} logged in")
                    log_entry = UserLog(user_id=user.id, action='login')
                    db.session.add(log_entry)
                    db.session.commit()
                    result[0] = True
                    dialog.destroy()
                else:
                    messagebox.showerror("Login Failed", "Invalid username or password", parent=dialog)
        else:
            messagebox.showerror("Login Failed", "Please enter both username and password", parent=dialog)


    login_button = tk.Button(dialog, text="Login", command=on_ok, font=('Arial', 10, 'bold'))
    login_button.grid(row=2, column=0, columnspan=2, pady=10)

    # Bind the Enter key to the on_ok function
    dialog.bind('<Return>', lambda event: on_ok())

    dialog.wait_window()
    return result[0]


debug_mode = settings['General'].getboolean('Debug')
if __name__ == '__main__':
    # Check for updates
    update_info = check_for_updates()
    if update_info['update_available']:
        root = tk.Tk()
        root.withdraw()
        update_choice = messagebox.askyesno(
            "Update Available",
            f"Version {update_info['version']} is available. Would you like to update now?",
            icon='info'
        )
        if update_choice:
            download_and_install_update(update_info['download_url'])

    api = Api()
    apply_migrations(server)
    
    settings = get_settings()
    
    if settings['General'].getboolean('CurrentlyOpen', False):
        root = tk.Tk()
        root.withdraw()
        user_choice = messagebox.askyesno(
            "Warning",
            "The application appears to be already running or was not closed properly. Do you want to continue?",
            icon='warning'
        )
        if not user_choice:
            sys.exit(0)
    
    if not check_and_create_user():
        sys.exit(0)
    
    settings['General']['CurrentlyOpen'] = 'True'
    with open('settings.ini', 'w') as configfile:
        settings.write(configfile)
    
    def on_closed():
        settings = get_settings()
        settings['General']['CurrentlyOpen'] = 'False'
        with open('settings.ini', 'w') as configfile:
            settings.write(configfile)
        
        # Log the logout event
        api.logout()
    
    window = webview.create_window("Scheduler", create_application(), js_api=api, width=1024, height=768)
    window.events.closed += on_closed
    
    webview.start(debug=debug_mode)

