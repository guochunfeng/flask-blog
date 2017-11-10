#-*- coding: UTF-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError
from ..models import User
class LoginForm(FlaskForm):
	email=StringField('邮件',validators=[Required(),Length(1,64),Email()])
	password=PasswordField('密码',validators=[Required()])
	remember_me=BooleanField('记住密码')
	submit=SubmitField('登录')
class RegistrationForm(FlaskForm):
	email=StringField('邮件',validators=[Required(),Length(1,64),Email()])
	username=StringField('用户名',validators=[Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9]*$',0,
		'用户名必须是英文''数字,点 或者 下划线')])
	password=PasswordField('密码',validators=[Required(),EqualTo('password2',message='Passwords must match.')])
	password2=PasswordField('再次输入密码',validators=[Required()])
	remember_me=BooleanField('记住密码')
	submit=SubmitField('注册')
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already register.')
	def validate_username(self,field):
		if User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already register')
class PostForm (FlaskForm):
	body=TextAreaField("What's on your mind",validators=[Required()])
	submit=SubmitField('Submit')
class ChangePasswordForm(FlaskForm):
	email=StringField('Email',validators=[Required(),Length(1,64),Email()])
	password=PasswordField('Password',validators=[Required()])
	new_password=PasswordField('NewPassword',validators=[Required()])
	submit=SubmitField('Submit')