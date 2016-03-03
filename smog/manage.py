from smog import app, db, models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def populate_db():
    """Adds a test user and creates default site settings"""
    testuser = models.User('test@test.com', 'Test User', 'changeme123')
    db.session.add(testuser)
    settings = models.SiteSettings()
    db.session.add(settings)
    db.session.commit()

if __name__ == '__main__':
    manager.run()

