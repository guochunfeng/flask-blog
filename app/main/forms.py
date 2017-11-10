#coding=utf-8 
from flask_wtf import FlaskForm 
from wtforms import StringField,PasswordField,BooleanField,SubmitField,SelectField,TextAreaField
from wtforms.validators import Required,Length,Regexp
from flask.ext.pagedown import PageDown
from flask.ext.pagedown.fields import PageDownField
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
class CommentForm(FlaskForm):
	body=StringField('',validators=[Required()])
	submit=SubmitField('提交评论')
class NameForm(FlaskForm):
	name=StringField('What is your name',validators=[Required()])
	submit=SubmitField('Submit')
class EditProfileForm(FlaskForm):
	name=StringField('昵称',validators=[Length(0,64)])
	location=StringField('地址',validators=[Length(0,64)])
	about_me=TextAreaField('关于我')
	submit=SubmitField('提交')
class EditProfileAdiminForm(FlaskForm):
	email=StringField('邮件',validators=[Required(),Length(1,64)])
	username=StringField('Username',validators=[Required(),Length(1,64),Regexp('[A-Za-z][A-Za-z0-9_.]*$',0,
		'Usernames must have only letters,''numbers,dots or underscores')])
	confirmed=BooleanField('确认')
	role=SelectField('Confirmed')
	name=StringField('昵称',validators=[Length(0,64)])
	location=StringField('地址',validators=[Length(0,64)])
	about_me=TextAreaField('关于我')
	submit=SubmitField('提交')
	def __init__(self,user,*arg,**kwargs):
		super(EditProfileAdiminForm,self).__init__(*arg,**kwargs)
		self.role.choice=[(role.id,role.name)for role in Role.query.order_by(Role.name).all()]
		self.user=user
	def validate_email(self,field):
		if field.data!=self.user.email and \
			User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')
	def validate_username(self,fielf):
		if field.data!=self.user.username and \
			User.query.filter_by(username=field.data).first():
			raise ValidationError('Username already in use. ')

class PostForm(FlaskForm):
	title=StringField("标题",validators=[Required()])
	body=PageDownField("正文",validators=[Required()])
	submit=SubmitField("提交")