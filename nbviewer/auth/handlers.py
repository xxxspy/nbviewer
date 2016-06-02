from .weibo import APIClient
from .providers.base import BaseHandler
def _create_auth_client():
	import os
	auth_key=os.environ.get('SINA_AUTH_APP_KEY','')
	auth_secret=os.environ.get('SINA_AUTH_APP_SECRET','')
	callback_url=os.environ.get('SINA_AUTH_CALLBACK_URL','')
	if auth_key and auth_secret and callback_url:
		client=APIClient(app_key=auth_key,app_secret=auth_secret,redirect_url=callback_url)
	else:
		client=None
	return client

class LoginCallbackHandler(BaseHandler):
	def get(self,*args,**kwargs):
		'''get code callback'''
		code=self.get_argument('code',None)
		from_url=self.get_argument('from','/')
		if code:
			client=self.settings.auth_client 
			r=client.request_access_token(code)
			access_token, expires_in, uid = r.access_token, r.expires_in, r.uid
			self.set_secure_cookie('user_id',uid,expires=expires_in)
			self.set_secure_cookie('access_token',access_token,expires=expires_in)
			self.redirect(from_url)	
		else:
			self.redirect('%s?from=%s' % (self.settings.login_url,from_url))


class WeiboLoginMix(object):
	def get_current_user(self):
		user_id=self.get_secret_cookie('user_id')
		return user_id


class AdminHandler(WeiboLoginMix,BaseHandler):
	def get(self,*arge,**kwargs):
		if not self.current_user:
			self.redirect(self.settings.login_url)
		else:
			self.finish(self.render_template('admin.html', sections=self.frontpage_sections))
	def post(self,*args,**kwargs):
		pass




