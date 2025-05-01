#
# app/user/views.py
#
from urllib.parse import urlparse

from flask import render_template, request, make_response, redirect, url_for
from flask_login import login_user, logout_user, login_required
from flask import flash as flask_flash
from flask import current_app as app
from flask_jwt_extended import create_access_token

from . import user_blueprint
from .user import User, MyUserMixin
from .password import Password
from .forms import LoginForm, NewUserForm, PasswordRecoveryForm, \
    NewPasswordForm

from app.modules.functions import Functions
from app.modules import utils

@user_blueprint.route('/login/form', methods=['GET', 'POST'])
def login_form_view():   
    next_url = request.args.get('next', None)

    form = LoginForm()
   
    if request.method == 'POST':
        if form.validate_on_submit(): 
            email = request.form.get('email')
            password = request.form.get('password')

            next_url = request.form.get('next', None)

            user = User()            
            is_password_correct = user.check_password(email, password)           

            if is_password_correct:
                user_id = user.get_id(email)
                
                user_mixin = MyUserMixin(user_id)  
                login_user(user_mixin, remember=True)

                access_token = create_access_token(identity=user_id)                

                if (next_url is not None) and (next_url != 'None'):
                    flask_flash(u'Login efetuado com sucesso.', 'success')        
                    resp = make_response(redirect(urlparse(next_url)))
                else:
                    flask_flash(u'Login efetuado com sucesso. É hora de pedir PIZZA!', 'success')        
                    resp = make_response(redirect(url_for('main.home')))

                # JWT
                resp.set_cookie(key=app.__settings.jwt_cookie_name, 
                                value=access_token,
                                max_age=app.__settings.expire_ts, 
                                expires=app.__settings.jwt_cookie_expire_ts, 
                                domain=app.__settings.domain, path='/', 
                                secure=app.__settings.cookie_secure, 
                                httponly=True)

                return resp
            
            else:
                flask_flash(u'E-mail ou senha inválidos!', 'error')        
 
    return render_template('user_login_form.html', form=form, next_url=next_url,
                           web_config=app.__settings.web_config,
                           api_config=app.__settings.api_config)


@user_blueprint.route('/logout', methods=['GET'])
@login_required
def logout_view():    
    logout_user()

    return redirect(url_for('main.home', next=None))


@user_blueprint.route('/new/form', methods=['GET', 'POST'])
def add_user_form_view():
    """Formulário para cadastro de usuário.

    """
    form = NewUserForm()   

    if request.method == 'POST':        
        if form.validate_on_submit():
            form_dict = request.form.to_dict()
            form_dict.pop('csrf_token')

            user = User()

            user_exists = user.exists(
                email=form_dict['email'], 
                telephone=form_dict['telephone']
            )

            if user_exists:
                flask_flash(u'E-mail ou telefone já existem.', 'error')  

                return redirect(url_for('user.add_user_form_view', next=None))               
            else:
                fn = Functions()
                fn.fn_ocid = app.__settings.fn_user_register_ocid
                invoke_status = fn.invoke(json_message=form_dict)
                                
                # TODO: log
                if invoke_status is True:
                    flask_flash(u'Cadastro efetuado com sucesso! Aguarde o e-mail para confirmar o seu cadastro.', 'success')
                else:
                    flask_flash(u'Erro ao cadastrar o usuário. Tente novamente mais tarde.', 'error')

                return redirect(url_for('main.home', next=None))                        
        
        flask_flash(u'Erro ao cadastrar o novo usuário.', 'error')       
            
    return render_template('user_add_form.html', form=form,
                           web_config=app.__settings.web_config,
                           api_config=app.__settings.api_config)


@user_blueprint.route('/new/confirm', methods=['GET'])
def user_confirm_view():
    """Página para o usuário confirmar o seu cadastro.

    """
    email = request.args.get('e', type=str)
    token = request.args.get('t', type=str)
    
    is_email_valid = utils.check_email(email)

    if is_email_valid and token:
        user = User()
        activated = user.activate(email=email, token=token)

        if activated:
            flask_flash(u'Conta ativada com sucesso.', 'success')            

            return redirect(url_for('user.login_form_view', next=None))  

    flask_flash(u'Link expirado ou dados inválidos.', 'error')

    return redirect(url_for('main.home', next=None))    


@user_blueprint.route('/password/recovery/form', methods=['GET', 'POST'])
def password_recovery_form_view():
    """Página para recuperar a senha do usuário.

    """
    form = PasswordRecoveryForm()

    if request.method == 'POST':        
        if form.validate_on_submit():
            form_dict = request.form.to_dict()
            form_dict.pop('csrf_token')
            
            user = User()
            is_email_valid = user.check_email(email=form_dict['email'])

            if is_email_valid:                                                
                fn = Functions()
                fn.fn_ocid = app.__settings.fn_password_recovery_ocid
                invoke_status = fn.invoke(json_message=form_dict)
                
                # TODO: log
                if invoke_status is True:
                    flask_flash(u'Foi enviado um e-mail para a recuperação da sua senha.', 'success')
                else:
                    flask_flash(u'Erro ao processar a solicitação. Tente novamente mais tarde.', 'error')    

                return redirect(url_for('main.home', next=None))
            else:
                flask_flash(u'Usuário não encontrado.', 'error')

                return redirect(url_for('user.password_recovery_form_view', next=None))

    return render_template('user_passwdrecovery_form.html', form=form,
                           web_config=app.__settings.web_config,
                           api_config=app.__settings.api_config)


@user_blueprint.route('/new/password/form', methods=['GET', 'POST'])
def new_password_form_view():
    """Página para definir uma nova senha.

    """
    email = request.args.get('e', type=str)
    token = request.args.get('t', type=str)

    form = NewPasswordForm()

    if request.method == 'GET':
        if not email or not token:
            return redirect(url_for('main.home', next=None))

    if request.method == 'POST':        
        if form.validate_on_submit():
            form_dict = request.form.to_dict()          

            user = User()
            is_email_valid = user.check_email(email=form_dict['email'])

            if is_email_valid:
                user_id = user.get_id(email=form_dict['email'])

                password = Password()
                password.user_id = user_id
                password.email = form_dict['email']
                password.token = form_dict['token']
                password.password = form_dict['password']
                password_set = password.set()

                if password_set is True:
                    flask_flash(u'Nova senha definida com sucesso.', 'success')            

                    return redirect(url_for('user.login_form_view', next=None))  
                else:
                    flask_flash(u'Erro ao processar a solicitação. Tente novamente mais tarde.', 'error')    

            else:                
                flask_flash(u'Usuário não encontrado.', 'error')

            return redirect(url_for('main.home', next=None))
    
    return render_template('user_new_password_form.html', form=form,
                           email=email, token=token,
                           web_config=app.__settings.web_config,
                           api_config=app.__settings.api_config)


@user_blueprint.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    return render_template('user_account.html', 
                           web_config=app.__settings.web_config,
                           api_config=app.__settings.api_config)
