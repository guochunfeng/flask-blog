#coding=utf-8 
from datetime import datetime
from flask import render_template,session,redirect,url_for,request,current_app,flash,make_response
from . import main
from .forms import NameForm,PostForm,CommentForm,EditProfileForm,EditProfileAdiminForm
from .. import db
from ..models import User,Post,Comment
from flask.ext.login import login_user,login_required,current_user
from ..decorators import admin_required,permission_required
from ..models import Permission
from flask.ext.sqlalchemy import get_debug_queries
#编辑文章
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
	post=Post.query.get_or_404(id)
	if current_user!=post.author and not current_user.can(Permission.ADMINISTER):
		abort(403)
	form=PostForm()
	if form.validate_on_submit():
		post.body=form.body.data
		post.title=form.title.data
		db.session.add(post)
		flash('文章已经编辑成功')
		return redirect(url_for('.post',id=post.id))
	form.body.data=post.body
	form.title.data=post.title
	return render_template('edit_post.html',form=form)
#评论的路由
@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
	post=Post.query.get_or_404(id)
	form=CommentForm()
	if form.validate_on_submit():
		comment=Comment(body=form.body.data,post=post,author=current_user._get_current_object())
		db.session.add(comment)
		flash('评论已经成功')
		return redirect(url_for('.post',id=post.id,page=-1))
	page=request.args.get('page',1,type=int)
	if page==-1:
		page=(post.comments.count()-1)/\
			current_app.config['FLASK_COMMETS_PER_PAGE']+1
	pagination=post.comments.order_by(Comment.timestamp.asc()).paginate(page,per_page=current_app.config['FLASK_COMMETS_PER_PAGE'],error_out=False)
	comments=pagination.items
	return render_template('post.html',posts=[post],form=form,comments=comments,pagination=pagination)
#写博客的路由
@main.route('/write_blog',methods=['GET','POST'])
def write_blog():
	form=PostForm()
	if form.validate_on_submit():
		post=Post(body=form.body.data,title=form.title.data,author=current_user._get_current_object())
		db.session.add(post)
		db.session.commit()
		return redirect(url_for('.post',id=post.id))
	return render_template('write_blog.html',form=form)
#主页的路由
@main.route('/',methods=['GET','POST'])
def index():
	form=PostForm()
	if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
		post=Post(body=form.body.data,author=current_user._get_current_object())
		db.session.add(post)
		return redirect(url_for('.index'))
	show_followed=False
	if current_user.is_authenticated:
		show_followed=bool(request.cookies.get('show_followed',''))
	if show_followed:
		query=current_user.followed_posts
	else:
		query=Post.query
	page=request.args.get('page',1,type=int)
	pagination=query.order_by(Post.timestamp.desc()).paginate(page,
		per_page=current_app.config['FLASK_POSTS_PER_PAGE'],error_out=False)
	posts=pagination.items
	return render_template('index.html',form=form,posts=posts,pagination=pagination,show_followed=show_followed)
#用户资料界面的路由
@main.route('/user/<username>')
def user(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		abort(404)
	posts=user.posts.order_by(Post.timestamp.desc()).all()
	return render_template('user.html',user=user,posts=posts)
#编辑个人信息的路由
@main.route('/edit-profile',methods=['GET','POST'])
@login_required
def edit_profile():
	form=EditProfileForm()
	if form.validate_on_submit():
		current_user.name=form.name.data
		current_user.location=form.location.data
		current_user.about_me=form.about_me.data
		db.session.add(current_user)
		flash('你的个人信息已经被修改成功')
		return redirect(url_for('.user',username=current_user.username))
	form.name.data=current_user.name
	form.location.data=current_user.location
	form.location.data=current_user.about_me
	return render_template('edit_profile.html',form=form)
#管理员编辑个人信息
@main.route('/edit-profile/<int:id>',methods=['GET','POST'])
@login_required
@admin_required
def edit_profile_admin(id):
	user=User.query.get_or_404(id)
	form=EditProfileAdiminForm(user=user)
	if form.validate_on_submit():
		user.email=form.email.data
		user.username=form.username.data
		user.confirmed=form.confirmed.data
		user.role=Role.query.get(form.role.data)
		user.name=form.name.data
		user.location=form.location.data
		user.about_me=form.about_me.data
		db.session.add(user)
		flash('The profile has been updated')
		return redirect(url_for('.user',username=username))
	form.email.data=user.email
	form.username.data=user.username
	form.confirmed.data=user.confirmed
	form.role.data=user.role_id
	form.name.data=user.name
	form.location.data=user.location
	form.about_me.data=user.about_me
	return render_template('edit_profile.html',form=form,user=user)
#关注用户
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid User')
		return redirect(url_for('.index'))
	if current_user.is_following(user):
		flash('你已经关注了')
		return redirect(url_for('.user',username=username))
	current_user.follow(user)
	flash('成功关注 %s'%username)
	return redirect(url_for('.user',username=username))
#取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid User')
		return redirect(url_for('.index'))
	if not current_user.is_following(user):
		flash('You are already unfollowing this user')
		return redirect(url_for('.user',username=username))
	current_user.unfollow(user)
	flash('You are now unfollowing %s'%username)
	return redirect(url_for('.user',username=username))
#粉丝列表
@main.route('/followers/<username>')
def followers(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid User')
		return redirect(url_for('.index'))
	page=request.args.get('page',1,type=int)
	pagination=user.followers.paginate(page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
	follows=[{'user':item.follower,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',user=user,title="Followers of",endpoint='.followers',
		pagination=pagination,follows=follows)
#关注者列表
@main.route('/followed/<username>')
def followed(username):
	user=User.query.filter_by(username=username).first()
	if user is None:
		flash('Invalid User')
		return redirect(url_for('.index'))
	page=request.args.get('page',1,type=int)
	pagination=user.followed.paginate(page,per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],error_out=False)
	followed=[{'user':item.followed,'timestamp':item.timestamp} for item in pagination.items]
	return render_template('followers.html',user=user,title="Followed by ",endpoint='.followed',
		pagination=pagination,follows=followed)
#所有用户发表的文章
@main.route('/all')
@login_required
def show_all():
	resp=make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed','',max_age=30*24*60*60)
	return resp
#所有关注用户发表的文章
@main.route('/followed')
@login_required
def show_followed():
	resp=make_response(redirect(url_for('.index')))
	resp.set_cookie('show_followed','1',max_age=30*24*60*60)
	return resp
#管理员的管理评论
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
	page=request.args.get('page',1,type=int)
	pagination=Comment.query.order_by(Comment.timestamp.desc()).paginate(page,
		per_page=current_app.config['FLASK_COMMETS_PER_PAGE'],error_out=Flase)
	comments=pagination.items
	return render_template('moderate.html',comments=comments,pagination=pagination,page=page)
#管理员使评论可见
@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
	comment=Comment.query.get_or_404(id)
	comment.disabled=False
	db.session.add(comment)
	return redict(url_for('.moderate',page=request.args.get('page',1,type=int)))
#管理员使评论不可见
@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
	comment=Comment.query.get_or_404(id)
	comment.disabled=True
	db.session.add(comment)
	return redict(url_for('.moderate',page=request.args.get('page',1,type=int)))
@main.route('/shutdown')
def server_shutdown():
	if not current_app.testing:
		abort(405)
	shutdown=request.environ.get('werkzeug.server.shutdown')
	if not shutdown:
		abort(500)
	shutdown
	return 'Shutting Down...'
@main.after_app_request
def after_request(response):
	for query in get_debug_queries():
		if query.duration>=current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
			current_app.logger.warning('Slow query:%s\n Parameters:%s\nDuration:%f\nContext:%s\n'%(
				query.statement,query.parameters,query.duration,query.context))
	return response



