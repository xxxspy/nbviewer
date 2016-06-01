#-----------------------------------------------------------------------------
#  Copyright (C) 2013 The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

from sinastorage.bucket import KeyNotFound
from tornado import (
    gen,
    web,
)
from tornado.log import app_log

from ..base import (
    cached,
    RenderingHandler,
)


class SaeBucketHandler(RenderingHandler):
    """Renderer for /localfile

    Serving notebooks from the local filesystem
    """
    @cached
    @gen.coroutine
    def get(self, path):
        app_log.info('==============================')
        app_log.info('saehandler path:%s' % path)
        bucket=self.settings.get('sinabucket',None)
        if bucket is None:
            app_log.error('bucket is none')
            raise web.HTTPError(404)
        base_url='/sae'
        s='/'
        if not path:
            path=''
        if path.endswith('/') or path=='':#isdir
            dirs=[]
            others=[]
            ipynbs=[]
            entries=[]
            contents=bucket.listdir(path,delimiter=s)
            for c in contents:
                p,isdir=c[0],c[1]
                e={}
                e['name']=p.replace(path,'')
                e['url']=base_url + s + p
                if isdir:
                    e['class']='fa-folder-open'
                    dirs.append(e)
                elif p.endswith('.ipynb'):
                    e['class']='fa-book'
                    ipynbs.append(e)
                else:
                    e['url']='javascript:alert("not allowed type!");'
                    e['class']='fa-folder-close'
                    others.append(e)
            entries.extend(dirs)
            entries.extend(ipynbs)
            entries.extend(others)

            breadcrumbs=self.breadcrumbs(path,base_url)
            print(breadcrumbs)
            html=self.render_template('treelist.html',
                entries=entries,breadcrumbs=breadcrumbs,tree_type='localfile',
                tree_label='saefiels')
            yield self.cache_and_finish(html)
        else:
            try:
                nbdata = bucket[path].read()
            except KeyNotFound:
                raise web.HTTPError(404)

            provider_url=base_url+s+path
            yield self.finish_notebook(nbdata, download_url=path,
                                        provider_url=provider_url,
                                       msg="file from localfile: %s" % path,
                                       public=False,
                                       format=self.format,
                                       request=self.request)

    def breadcrumbs(self, path, base_url):
        """Generate a list of breadcrumbs"""
        breadcrumbs = []
        if not path:
            return breadcrumbs
        for name in path.split('/'):
            href = base_url = "%s/%s" % (base_url, name)
            if not href.endswith('/'):href +='/'
            breadcrumbs.append({
                'url' : href,
                'name' : name,
            })
        return breadcrumbs