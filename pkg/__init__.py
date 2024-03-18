from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate

migrate=Migrate()
csrf=CSRFProtect()
def create_app():
    from pkg.models import db
    from pkg import config

    app=Flask(__name__, instance_relative_config=True)
    

    app.config.from_pyfile('config.py')
    app.config .from_object(config.TestConfig)
    #db=sqlalchemly()
    db.init_app(app) #We moved the instantation of db to models.py 
    csrf.init_app(app) 
    migrate.init_app(app, db)
    return app

app = create_app()
#Brings all your routes here

# csrf=CSRFProtect(app) #Alternative
from pkg import user_routes, admin_routes


