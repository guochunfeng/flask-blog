# -*- coding:utf-8 -*-
from flask import render_template,redirect,request,url_for,flash
from flask.ext.login import login_user,login_required,logout_user
from . import auth
from .. import db
from ..models import User
from ..email import send_email
from .forms import LoginForm
from .forms import RegistrationForm,ChangePasswordForm
from flask.ext.login import current_user
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
	reload(sys)
	sys.setdefaultencoding(defaultencoding)
@auth.route('/change_password',methods=['GET','POST'])
def change_password():
	form=ChangePasswordForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			user.password=form.new_password.data
			db.session.add(user)
			flash('密码修改已经成功')
			return redirect(url_for('auth.login'))
		else:
			flash('密码不正确')
			return redirect('auth.change_password.html')
	return render_template('auth/change_password.html',form=form)

@auth.route('/login',methods=['GET','POST'])
def login():
	form=LoginForm()
	if form.validate_on_submit():
		user=User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user,form.remember_me.data)
			return redirect(request.args.get('next') or url_for('main.index'))
		flash('密码和用户名输入的不正确')
	return render_template('auth/login.html',form=form)
@auth.route('/logout')
def logout():
	logout_user()
	flash('You have been logged out')
	return redirect(url_for('main.index'))
@auth.route('/register',methods=['GET','POST'])
def register():
	form=RegistrationForm()
	if form.validate_on_submit():
		user=User(email=form.email.data,username=form.username.data,password=form.password.data)
		db.session.add(user)
		db.session.commit()
		token=user.generate_confirmation_token()
		send_email(user.email,'账户确认','auth/email/confirm',user=user,token=token)
		flash('一个确认邮件已经发给你，请注意查收')
		return redirect(url_for('main.index'))
	return render_template('auth/register.html',form=form)
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
	if current_user.confirmed:
		return redirect(url_for(main.index))
	if current_user.confirm(token):
		flash('你已经确认了账户，谢谢')
	else:
		flash('确认链接是无效的或已经过期了')
	return redirect(url_for('main.index'))
@auth.before_app_request
def before_request():
	if current_user.is_authenticated :
		current_user.ping()
		if not current_user.confirmed \
				and request.endpoint \
				and request.endpoint[:5]!='auth.'\
				and request.endpoint !='static':
			return redirect(url_for('auth.unconfirmed'))
@auth.route('/unconfirmed')
def unconfirmed():
	if current_user.is_anonymous or current_user.confirmed:
		return redirect(url_for('main.index'))
	return render_template('auth/unconfirmed.html')
@auth.route('/confirm')
@login_required
def resend_confirmation():
	token=current_user.generate_confirmation_token()
	send_email(current_user.email,'Confirm Your Account','auth/email/confirm',user=current_user,token=token)
	flash('一个新的确认邮件已经发给你了，请注意查收')
	return redirect(url_for('main.index'))