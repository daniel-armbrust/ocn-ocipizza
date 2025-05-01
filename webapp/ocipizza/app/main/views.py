#
# /app/main/views.py
#

from flask import render_template

from app.settings import Settings
from . import main_blueprint

settings = Settings()

@main_blueprint.route('/')
def home():
    return render_template('main_home.html', 
                           web_config=settings.web_config,
                           api_config=settings.api_config)