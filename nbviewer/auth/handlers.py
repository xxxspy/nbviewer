#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1'
__author__ = 'xxxspy (675495787@qq.com)'

'''
Nbviewer login handler with weibo auth using OAuth 2.
'''

from ..providers.base import BaseHandler
import os
import json
from tornado.httputil import url_concat
from tornado.escape import to_basestring
from .utils import json_bytes_serializer
from json import dump

class User(object):
	def __init__(self,id,name,login,email,access_token):
		self.id=id 
		self.login=login
		self.name=name
		self.email=email
		self.access_token=access_token



class GithubAuMix(object):
	def get_current_user(self):
		user=self.get_secure_cookie('user')
		if user:
			if type(user)==bytes:
				user=to_basestring(user)
			user=json.loads(user,object_hook=json_bytes_serializer('from_json'))
			user=User(**user)
		return user


class AdminHandler(GithubAuMix,BaseHandler):
	def get_current_user(self):
		user=super(AdminHandler,self).get_current_user()
		if user is None:return 
		if user.id in self.settings.get('admin_user_ids',[]):
			return user
		else:
			return None	

	def auth_redirect(self):
		next_url=self.request.uri
		url=self.settings['github_login_url']
		client_secret=os.environ['GITHUB_CLIENT_SECRET']
		client_id=os.environ['GITHUB_CLIENT_ID']
		if client_secret and client_id:
			redirect_url=url_concat(url,{'client_id':client_id,'next':next_url})
		else: 
			redirect_url='/'
		print ('redirect to %s' % redirect_url)
		self.redirect(redirect_url)
	
	def get(self,*arge,**kwargs):
		if not self.current_user:
			self.auth_redirect()
		else:
			self.finish(self.render_template('admin.html', sections=self.frontpage_sections))
	def post(self,*args,**kwargs):
		if not self.current_user:
			return self.get(*args,**kwargs)
		errors=[]
		text=self.get_argument('text')
		target=self.get_argument('target')
		section=self.get_argument('section')
		if not (text and target and section):
			errors.append('error:short of argument : text=%s,target=%s,section=%s' %(text,argument,section))
		print(self.request.files)
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
		sections=self.frontpage_sections
		finded=False
		for sec in sections:
			if sec['header']==section:
				sec['links'].insert(0,{'text':text,'target':target,'img':img_url})
				finded=True
				break
		if not finded:
			errors.append('error:cannot find section %s .' % section)

		if errors:
			self.finish(self.render_template('admin.html',sections=self.frontpage_sections,messages=errors))
		else:
			fpath=self.settings['frontpage_json_file']
			dump(sections,open(fpath,'w'))
			self.redirect('/admin',messages=['info:success!'])
	def delete(self,*args,**kwargs):
		print ('get...............................')
		if not self.current_user:
			return self.get(*args,**kwargs)
		errors=[]
		text=self.get_argument('text')
		target=self.get_argument('target')
		section=self.get_argument('section')
		img=self.get_argument('img')
		if not (text and target and section and img):
			errors.append('error:short of argument : text=%s,target=%s,section=%s,img=%s' %(text,argument,section,img))
			section_headers=[s['header'] for s in self.settings['frontpage_sections']]
			if not section in section_headers:
				errors.append('error:cannot find seciotn %s' % section)

		file_metas=self.request.files['img']
		imgdir=os.path.join(os.path.dirname(os.path.dirname(__file__)),'static','img','example-nb')
		imgpath=os.path.join(imgdir,img)
		if not os.path.exists(imgpath):
			errors.append('error: cannot find img %s' % imgpath)
		if errors:
			self.finish(self.render_template('admin.html',sections=self.frontpage_sections,messages=errors))
		else:
			for i,sec in enumerate(self.frontpage_sections):
				if sec.header==section:
					for j,link in enumerate(sec.links) :
						if link['text']==text and \
							link['target']==target and \
							link['img']==img:
							os.remove(imgpath)
							del sec.links[j]
							fpath=self.settings['frontpage_json_file']
							dump(self.frontpage_sections,open(fpath,'w'))
							return self.get('/admin')




