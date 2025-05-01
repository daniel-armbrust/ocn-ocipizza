#
# modules/utils.py
#

import re

from app.settings import Settings

settings = Settings()

def extract_digits(input_string: str):
    # Regular expression pattern to match digits
    pattern = r'\d+'

    # Find all matches of digits in the input string
    digits_list = re.findall(pattern, input_string)

    # Concatenate the matched digits into a single string
    digits = ''.join(digits_list)

    return digits


def check_password_complexity(password: str):
    password_length = len(password)

    # Minimum length check
    if password_length < settings.user_min_password_length:
        return False, f'Password must be at least {settings.user_min_password_length} characters long.'
    
    if password_length > settings.user_max_password_length:
        return False, f'The password can be a maximum of {settings.user_min_password_length} characters long.'

    # Uppercase, lowercase, numbers, and special characters check
    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'
    
    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'
    
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number.'
    
    if not re.search(r'[!@#$%^&*\\/\+\)\(\:\>\<]', password):
        return False, 'Password must contain at least one special character (!@#$%^&*))><\:).'

    return True, None


def check_telephone(telephone: str):
    """Validate phone number.

    """
    digits = extract_digits(telephone)

    if re.match(r'\d{10,11}$', digits):
        return True
    else:
        return False


def check_email(email: str):
    if email:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    else:
        return False


def check_new_user_data(data: dict):
    """Validate user data for registration.

    Parameters:
    data (dict): Dictionary that contains data to register a new user.
                 data = {'email': '', 'name': '', 'password': '', 'telephone': ''}   
    """
    try:
        email = data['email']
        password = data['password']
        name = data['name']
        telephone = data['telephone']
    except KeyError:
        return False, {}
    
    is_email_valid = check_email(email)

    if not is_email_valid:
        return False, {'email': 'The email is invalid or exists.'}
    
    is_complex, message = check_password_complexity(password)
    
    if not is_complex:
        return False, {'password': message}
    
    is_telephone_valid = check_telephone(telephone)

    if not is_telephone_valid:
        return False, {'telephone', 'The telephone is not valid.'}
    
    if not re.match(r'^[A-Za-z\ ]{2,}$', name):
        return False, {'name': 'The user name is not valid.'}
    
    return True, {}