from flask_migrate import upgrade

def apply_migrations(app):
    with app.app_context():
        upgrade()
        print("Migrations applied successfully.")