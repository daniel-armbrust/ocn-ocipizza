#
# wsgi.py
#

from app import create_app
from app.settings import Settings

app = create_app()

if __name__ == '__main__':
    settings = Settings()

    if settings.env != 'development':
        app.run(host='0.0.0.0', port=5000, debug=False)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)