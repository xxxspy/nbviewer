#-----------------------------------------------------------------------------
#  Copyright (C) 2013 The IPython Development Team
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file COPYING, distributed as part of this software.
#-----------------------------------------------------------------------------

import io
import os

from tornado import (
    gen,
    web,
)
from tornado.log import app_log

from ..base import (
    cached,
    RenderingHandler,
)


class LocalFileHandler(RenderingHandler):
    """Renderer for /localfile

    Serving notebooks from the local filesystem
    """
    @cached
    @gen.coroutine
    def get(self, path):

        localfile_path = os.path.abspath(
            self.settings.get('localfile_path', ''))

        abspath = os.path.abspath(os.path.join(
            localfile_path,
            path
        ))

        app_log.info("looking for file: '%s'" % abspath)

        if not abspath.startswith(localfile_path):
            app_log.warn("directory traversal attempt: '%s'" % localfile_path)
            raise web.HTTPError(404)

        if not os.path.exists(abspath):
            raise web.HTTPError(404)
        if not os.path.isfile(abspath):
            base_url='/localfile'
            contents=os.listdir(abspath)
            dirs=[]
            others=[]
            ipynbs=[]
            entries=[]
            for c in contents:
                e={}
                e['name']=c 
                e['url']=os.path.join(base_url,path,c)
                subpath=os.path.join(abspath,c)
                if os.path.isdir(subpath):
                    e['class']='fa-folder-open'
                    dirs.append(e)
                elif os.path.isfile(subpath):
                    if c.endswith('.ipynb'):
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
            html=self.render_template('treelist.html',
                entries=entries,breadcrumbs=breadcrumbs,tree_type='localfile',
                tree_label='localfiels')
            yield self.cache_and_finish(html)
        else:
            with io.open(abspath, encoding='utf-8') as f:
                nbdata = f.read()
            provider_url=os.path.join(base_url,path)
            yield self.finish_notebook(nbdata, download_url=path,
                                        provider_url=provider_url,
                                       msg="file from localfile: %s" % path,
                                       public=False,
                                       format=self.format,
                                       request=self.request)

