#-----------------------------------------------------------------------------
#  Copyright (C) 2013 The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------
from tornado import web
from tornado.log import app_log
from tornado import gen
from .utils import transform_ipynb_uri

from .providers import (
    provider_handlers,
    provider_uri_rewrites,
)
from .providers.base import (
    BaseHandler,
    format_prefix,
)
from .auth.github_auth import GithubLoginHandler
from .auth.handlers import AdminHandler
import os
#-----------------------------------------------------------------------------
# Handler classes
#-----------------------------------------------------------------------------

class Custom404(BaseHandler):
    """Render our 404 template"""
    def prepare(self):
        raise web.HTTPError(404)


class IndexHandler(BaseHandler):
    """Render the index"""
    def get(self):
        self.finish(self.render_template('index.html', sections=self.frontpage_sections))



class FAQHandler(BaseHandler):
    """Render the markdown FAQ page"""
    def get(self):
        self.finish(self.render_template('faq.md'))


class CreateHandler(BaseHandler):
    """handle creation via frontpage form

    only redirects to the appropriate URL
    """
    uri_rewrite_list = None

    def post(self):
        value = self.get_argument('gistnorurl', '')
        redirect_url = transform_ipynb_uri(value, self.get_provider_rewrites())
        app_log.info("create %s => %s", value, redirect_url)
        self.redirect(redirect_url)

    def get_provider_rewrites(self):
        # storing this on a class attribute is a little icky, but is better
        # than the global this was refactored from.
        if self.uri_rewrite_list is None:
            # providers is a list of module import paths
            providers = self.settings['provider_rewrites']

            type(self).uri_rewrite_list = provider_uri_rewrites(providers)
        return self.uri_rewrite_list
class SearchLocalHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        s=self.get_argument('keyword','')
        if not s:
            self.redirect('/')
        else:
            import os
            localfile_path=self.settings.get('localfile_path','')
            if localfile_path and localfile_path != os.path.abspath(""):
                localfile_path=os.path.abspath(localfile_path)
                base_url='/localfile'
                ipynbs=[]
                nbdirs=[]
                for dirname,dirs,files in os.walk(localfile_path):
                    print (dirname,dirs,files)
                    for d in dirs:
                        if s in d:
                            e={}
                            e['name']=d 
                            e['url']=os.path.join(base_url,dirname.replace(localfile_path,''))
                            e['class']='fa-folder-open'
                            nbdirs.append(e)
                    for f in files:
                        if s in f and f.endswith('.ipynb'):
                            e={}
                            e['name']=f 
                            e['url']=os.path.join(base_url,dirname.replace(localfile_path,''))
                            e['class']='fa-book'
                            ipynbs.append(e)
                entries=nbdirs
                entries.extend(ipynbs)
            else:
                entries=[]
            html=self.render_template('treelist.html',
                entries=entries,tree_type='localfile',
                tree_label='localfiels',user='xxxspy')
            yield self.cache_and_finish(html)

#-----------------------------------------------------------------------------
# Default handler URL mapping
#-----------------------------------------------------------------------------

def format_handlers(formats, handlers):
    return [
        (prefix + url, handler, {
            "format": format,
            "format_prefix": prefix
        })
        for format in formats
        for url, handler in handlers
        for prefix in [format_prefix + format]
    ]


def init_handlers(formats, providers):
    pre_providers = [
        ('/', IndexHandler),
        ('/index.html', IndexHandler),
        (r'/faq/?', FAQHandler),
        (r'/create/?', CreateHandler),
        # don't let super old browsers request data-uris
        (r'.*/data:.*;base64,.*', Custom404),
    ]
    if 'GITHUB_CLIENT_ID' in os.environ and 'GITHUB_CLIENT_SECRET' in os.environ:
        pre_providers.append((r'/admin/?',AdminHandler))
        pre_providers.append((r'/auth/github/?',GithubLoginHandler))
    post_providers = [
        (r'/(robots\.txt|favicon\.ico)', web.StaticFileHandler),
        (r'.*', Custom404),
    ]

    handlers = provider_handlers(providers)

    return (
        pre_providers +
        handlers +
        format_handlers(formats, handlers) +
        post_providers
    )
