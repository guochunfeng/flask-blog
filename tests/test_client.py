import unittest
from app import create_app, db
from app.models import User,Role
class FlaskClientTestCase(unittest.TestCase):
	def setUp():
		self.app=create_app('testing')
		self.app_context=self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client=self.app.test_client(use_cookies=True)
	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()
	def test_home_page(self):
		response=self.client.get(url_for('main.index'))
		self.assertTrue=('Stranger' in response.get_data(as_text=True))
	def test_register_and_login(self):
		response=self.client.post(url_for('auth.register'),data={
			'email':'john@example.com',
			'username':'john',
			'password':'cat',
			'password2':'cat',
			})
		self.assertTrue(response.status_code==302)
		response=self.client.post(url_for('auth.login'),data={
			'email':'john@example.com',
			'password':'cat'},follow_redicts=True)
		data=response.get_data(as_text=True)
		self.assertTrue(re.search('Hello,\s+john',data))
		self.assertTrue('you have not confirmed your accout yet' in data)

		user=User.query.filter_by(email='john@example.com').first()
		token=user.generate_confirmation_token()
		response=self.client.get(url_for('auth.confirm',token=token),follow_redicts=True)
		data=response.get_data(as_text=True)
		self.assertTrue('You have confirmed your account' in data)

		response=self.clinet.get(url_for('auth.logout'),follow_redicts=True)
		data=response.get_data(as_text=True)
		self.assertTrue('You have been logged out' in data)
class APITestCase(unittest,TestCase):
	def get_api_headers(self,username,password):
		return{
		'Authorization':'Basic'+b64encode((username+':'+password).encode('utf-8')).decode('utf-8'),
		'Accept':'application/json',
		'Content-Type':'application/json'
		}
	def test_no_auth(self):
		response=self.client.get(url_for('api.get_posts'),Content-Type='application/json')
		self.assertTrue(response.status_code==401)
	def test_posts(self):
		r=Role.query.filter_by(name='User').first()
		self.assertIsNoNone(r)
		u=User(email='john@example.com',password='cat',confirmed=True,role=r)
		db.session.add(u)
		db.session.commit()
		#写一篇文章
		response=self.clinet.post(
			url_for('api.new_post'),
			headers=self.get_auth_header('john@example.com','cat'),
			data=json.dumps({'body':'body of the *blog* post'}))
		self.assertTrue(response.status_code==201)
		url=response.headers.get('Location')
		self.assertIsNoNone(url)
		#获取刚刚发布的文章
		response=self.clinet.get(
			url,
			heads=self.get_auth_header('john@example.com','cat'))
		self.assertTrue(response.status_code==200)
		josn_response=json.loads(response.data.decode('utf-8'))
		self.assertTrue(josn_response['url']==url)
		self.assertTrue(josn_response['body']=='body of the *blog* post')
		self.assertTrue(josn_response['body_html']=='<p>body of the <em>blog</em> post</p>')