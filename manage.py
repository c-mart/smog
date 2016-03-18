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
    testuser = models.User('test@test.com', 'Test User', 'test')
    testpost = models.Post('My First Post',
                           '''Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum sed mi consequat sapien aliquet imperdiet. Praesent luctus justo non viverra lacinia. Nulla nulla ante, suscipit non leo at, pellentesque vehicula tortor. Nulla vestibulum mauris odio. Morbi eget quam a massa suscipit tempor nec eu risus. Curabitur ut quam sagittis, tempus augue quis, vehicula massa. Cras luctus enim a ornare iaculis.

Aenean a euismod diam, eu pharetra velit. Phasellus scelerisque, est lobortis vehicula gravida, metus nisl laoreet dui, non imperdiet sem dui vel tellus. Vestibulum aliquam vulputate enim, eu scelerisque odio ullamcorper nec. Donec scelerisque ex quam, non feugiat orci egestas non. Fusce ultrices aliquam risus a ornare. Integer non ligula sit amet eros blandit volutpat. Ut ultrices eleifend metus, sed fringilla dui pretium vitae. Mauris ac mi feugiat, porttitor turpis vitae, pretium tortor. Quisque at mauris at lectus pellentesque commodo. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Sed tempor sem quis aliquet placerat. Aliquam fermentum at nisl eu fermentum.
                           ''',
                           1)
    db.session.add_all((testuser, testpost))
    db.session.commit()

if __name__ == '__main__':
    manager.run()

