#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '0.1'
__author__ = 'xxxspy (675495787@qq.com)'

'''
Nbviewer login handler with weibo auth using OAuth 2.
'''

from .providers.base import BaseHandler
import os
import json



class GithubAuMix(object):
	def get_current_user(self):
		user=self.get_secret_cookie('user')
		return user


class AdminHandler(GithubAuMix,BaseHandler):
	def get_current_user(self):
		user=super(AdminHandler,self).get_current_user()
		if user.id in self.settings.admin_user_ids:
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



