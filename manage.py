from smog import app, db, models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    """Adds a test user and creates default site settings"""
    db.create_all()
    settings = models.SiteSettings()
    db.session.add(settings)
    testuser = models.User('test@test.com', 'Test User', 'changeme123')
    db.session.add(testuser)
    db.session.commit()

if __name__ == '__main__':
    manager.run()

