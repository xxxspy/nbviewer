from .weibo import APIClient
from .providers.base import BaseHandler
import os
import json
def _create_auth_client():
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
	def get_current_user(self):
		user_id	=super(AdminHandler,self).get_current_user()
		if user_id in self.settings.admin_user_ids:
			return user_id
		else:
			return None	
	def get(self,*arge,**kwargs):
		if not self.current_user:
			self.redirect(self.settings.login_url)
		else:
			self.finish(self.render_template('admin.html', sections=self.frontpage_sections))
	def post(self,*args,**kwargs):
		if not self.current_user:
			self.redirect(self.settings.login_url)
		errors=[]
		text=self.get_argument('text')
		target=self.get_argument('target')
		section=self.get_argument('section')
		if not (text and target and section):
			errors.append('error:short of argument : text=%s,target=%s,section=%s' %(text,argument,section))
		file_metas=self.request.files['img']
		imgdir=os.path.join(os.path.dirname(os.path.dirname(__file__)),'static','img','example-nb')
		if file_metas:
			for meta in file_metas:
				fname=meta['filename']
				img_url=os.path.join('/static','img','example-nb',fname)
				fpath=os.path.join(imgdir,fname)
				if os.path.exists(fpath):
					errors.append('error:filename(%s) exists' % fname)
				else:
					with open(fpath,'wb') as f:
						f.write(meta['body'])
		else:
			errors.append('error: no img file!')

		if errors:
			self.finish(self.render_template('admin.html',sections=self.frontpage_sections,messages=errors))
		else:
			from json import dump
			sections=self.frontpage_sections
			sections[section]['links'].append({'text':text,'target':target,'img':img_url})
			fpath=self.settings.frontpage_json_file
			dump(sections,open(fpath,'w'))
			self.redirect('/admin',messages=['info:success!'])



