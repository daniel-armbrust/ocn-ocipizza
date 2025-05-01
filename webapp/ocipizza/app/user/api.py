#
# app/user/api.py
#
from flask import request, jsonify
from flask_jwt_extended import create_access_token

from . import api_user_blueprint
from .user import User

@api_user_blueprint.route('/login', methods=['POST'])
def login_api():
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    user = User()
    is_password_correct = user.check_password(email, password)

    if is_password_correct:
        user_id = user.get_id(email)
        access_token = create_access_token(identity=user_id)

        return jsonify({'status': 'success', 'message': 'Authentication successful.',
                        'data': {'token': access_token}})
        
    else:
        return jsonify({'status': 'fail', 'message': 'Bad username or password.', 
                        'data': 'null'}), 401


