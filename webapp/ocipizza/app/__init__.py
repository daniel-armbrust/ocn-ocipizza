#
# ocipizza/app/__init__.py
#

from flask import Flask
from flask_login import LoginManager, login_manager
from flask_wtf.csrf import CSRFProtect
from flask_jwt_extended import JWTManager

from app.settings import Settings
from app.user.user import MyUserMixin
from app.modules.nosql import NoSQL

def create_app():
    app = Flask(__name__)

    settings = Settings()
    app.__settings = settings

    app.config['SECRET_KEY'] = settings.secret_key
    app.config['JWT_SECRET_KEY'] = settings.secret_key
    
    app.config['SESSION_COOKIE_NAME'] = settings.session_cookie_name    
    app.config['PERMANENT_SESSION_LIFETIME'] = settings.session_cookie_expire_ts
    app.config['SESSION_COOKIE_DOMAIN'] = settings.domain
    app.config['SESSION_COOKIE_SECURE'] = settings.cookie_secure
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'        
    
    if settings.env != 'development':        
        app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'        
        app.config['SERVER_NAME'] = f"{settings.web_config['scheme']}://{settings.web_config['host']}"
    
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    jwt = JWTManager()
    jwt.init_app(app)
    
    # Flask-Login
    # https://flask-login.readthedocs.io/en/latest/
    login_manager = LoginManager()    
    login_manager.init_app(app)
    login_manager.login_view = 'user.login_form_view'
    login_manager.login_message = 'É necessário realizar o login para acessar essa página.'

    @login_manager.user_loader
    def user_loader(user_id):  
        user = MyUserMixin(user_id)
        #user.id = user_id
        return user       

    if settings.html_minify is True:
        from flask_minify import minify

        app.config['MINIFY_HTML'] = True
        app.config['MINIFY_HTML_TEMPLATE'] = {
            'remove_comments': True,
            'remove_empty_space': True,
            'remove_optional_attribute_quotes': False
        }
        
        minify(app=app)       
    
    # Init and get the OCI NoSQL handle.
    # A handle has memory and network resources associated with it. To minimize 
    # network activity as well as resource allocation and deallocation overheads, 
    # it’s best to avoid repeated creation and closing of handles. So we create 
    # and globalize the handle here for the entire app.
    app._nosql_handle = NoSQL.create_handler(settings.env)
  
    from app.main import main_blueprint
    from app.pizza import pizza_blueprint, api_pizza_blueprint 
    from app.order import order_blueprint, api_order_blueprint
    from app.user import user_blueprint, api_user_blueprint
    from app.location import api_location_blueprint

    app.register_blueprint(main_blueprint, url_prefix='/')   

    app.register_blueprint(pizza_blueprint, url_prefix='/pizza')
    app.register_blueprint(api_pizza_blueprint, url_prefix='/pizzas')
    csrf.exempt(api_pizza_blueprint)
    
    app.register_blueprint(order_blueprint, url_prefix='/order')
    app.register_blueprint(api_order_blueprint, url_prefix='/orders')
    csrf.exempt(api_order_blueprint)
    
    app.register_blueprint(user_blueprint, url_prefix='/user')  
    app.register_blueprint(api_user_blueprint, url_prefix='/users')  
    csrf.exempt(api_user_blueprint)

    app.register_blueprint(api_location_blueprint, url_prefix='/locations')  
    csrf.exempt(api_location_blueprint)
   
    return app