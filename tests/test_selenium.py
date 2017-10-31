from selenium import webdriver
class SeleniumTestCase(unittest.TestCase):
	client=None
	@classmethod
	def setUpClass(cls):
		#启动Firefox
		try:
			cls.client=webdriver.Firefox()
		except:
			pass
		if cls.client:
			cls.app=create_app('testing')
			cls.app_context=cls.app.app_context()
			cls.app_context.push()
		#禁止日志，保持输出整洁
		import logging
		logger=logging.getLogger('werkzeug')
		logger.setLeverl("ERROR")
		#创建数据库，并使用一些虚拟数据填充
		db.create_all()
		Role.insert_roles()
		User.generate_fake(10)
		Post.generate_fake(10)
		#添加管理员
		admin_role=Role.query.filter_by(permissions=0xff).first()
		admin=User(email='john@example.com',
					username='john',password='cat',
					role=admin_role,confirmed=True)
		db.session.add(admin)
		db.session.commit()
		#在一个线程中启动Flask服务器
		threading.Thread(target=cls.app.run).start()
	@classmethod
	def tearDownClass(cls):
		if cls.client:
			cls.client.get('http://localhost:5000/shutdown')
			cls.client.close()
			db.drop_all()
			db.session.remove()
			cls.app_context.pop()
	def setUp(self):
		if not self.client:
			self.skipTest('Web browser not available')
	def tearDown(self):
		pass
class SeleniumTestCase(unittest.TestCase):
	def test_admin_home_page(self):
		self.client.get('http://localhost:5000/')
		self.assertTrue(re.search('Hello,\s+stranger!',self.client.page_source))
		self.client.find_element_by_link_text('Log In').click()
		self.assertTrue('<h1>Login</h1>'in self.client.page_source)
		self.client.find_element_by_name('email').send_keys('john@example.com')
		self.client.find_element_by_name('password').send_keys('cat')
		self.client.find_element_by_name('submit').click()
		self.assertTrue(re.search('Hello,\s+john',self.client.page_source))
		self.client.find_element_by_link_text('Profile').click()
		self.assertTrue('<h1>john</h1>'in self.client.page_source)
