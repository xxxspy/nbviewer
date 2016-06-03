#encoding:utf8
import urllib
import tornado.ioloop
import tornado.web
import tornado.auth
import tornado.httpclient
import tornado.escape
import tornado.httputil
import logging
import os



class GithubMixin(tornado.auth.OAuth2Mixin):
    """ Github OAuth Mixin, based on FacebookGraphMixin
    """

    _OAUTH_AUTHORIZE_URL = 'https://github.com/login/oauth/authorize'
    _OAUTH_ACCESS_TOKEN_URL = 'https://github.com/login/oauth/access_token'
    _API_URL = 'https://api.github.com'

    def get_authenticated_user(self, redirect_uri, client_id, client_secret,
                              code, callback, extra_fields=None):
        """ Handles the login for Github, queries /user and returns a user object
        """
        logging.debug('gau ' + redirect_uri)
        http = tornado.httpclient.AsyncHTTPClient()
        args = {
          "redirect_uri": redirect_uri,
          "code": code,
          "client_id": client_id,
          "client_secret": client_secret,
        }

        http.fetch(self._oauth_request_token_url(**args),
            self.async_callback(self._on_access_token, redirect_uri, client_id,
                                client_secret, callback, fields))

    def _on_access_token(self, redirect_uri, client_id, client_secret,
                        callback, fields, response):
        """ callback for authentication url, if successful get the user details """
        if response.error:
            logging.warning('Github auth error: %s' % str(response))
            callback(None)
            return

        args = tornado.escape.parse_qs_bytes(
                tornado.escape.native_str(response.body))

        if 'error' in args:
            logging.error('oauth error ' + args['error'][-1])
            raise Exception(args['error'][-1])

        session = {
            "access_token": args["access_token"][-1],
        }

        self.github_request(
            method="/user",
            callback=self.async_callback(
                self._on_get_user_info, callback, session),
            access_token=session["access_token"],
            )

    def _on_get_user_info(self, callback, session, user):
        """ callback for github request /user to create a user """
        logging.debug('user data from github ' + str(user))
        if user is None:
            callback(None)
            return
        callback({
            "login": user["login"],
            "name": user["name"],
            "email": user["email"],
            "access_token": session["access_token"],
        })

    def github_request(self, path, callback, access_token=None,
                method='GET', body=None, **args):
        """ Makes a github API request, hands callback the parsed data """
        args["access_token"] = access_token
        url = tornado.httputil.url_concat(self._API_URL + path, args)
        logging.debug('request to ' + url)
        http = tornado.httpclient.AsyncHTTPClient()
        if body is not None:
            body = tornado.escape.json_encode(body)
            logging.debug('body is' +  body)
        http.fetch(url, callback=self.async_callback(
                self._parse_response, callback), method=method, body=body)

    def _parse_response(self, callback, response):
        """ Parse the JSON from the API """
        if response.error:
            logging.warning("HTTP error from Github: %s", response.error)
            callback(None)
            return
        try:
            json = tornado.escape.json_decode(response.body)
        except Exception:
            logging.warning("Invalid JSON from Github: %r", response.body)
            callback(None)
            return
        if isinstance(json, dict) and json.get("error_code"):
            logging.warning("Facebook error: %d: %r", json["error_code"],
                            json.get("error_msg"))
            callback(None)
            return
        callback(json)





class GithubLoginHandler(tornado.web.RequestHandler, GithubMixin):

    _OAUTH_REDIRECT_URL = 'http://localhost:8888/auth/github'

    @tornado.web.asynchronous
    def get(self):
        # we can append next to the redirect uri, so the user gets the
        # correct URL on login
        next=self.get_argument('next','/')
        redirect_uri = tornado.httputil.url_concat(
                self._OAUTH_REDIRECT_URL, {'next': next})
        client_id=os.envrion['GITHUB_CLIENT_ID']
        client_secret=os.envrion['GITHUB_CLIENT_SECRET']
        # if we have a code, we have been authorized so we can log in
        if self.get_argument("code", False):

            self.get_authenticated_user(
                redirect_uri=redirect_uri,
                client_id=client_id,
                client_secret=client_secret,
                code=self.get_argument("code"),
                callback=self.async_callback(self._on_login)
            )
            return

        # otherwise we need to request an authorization code
        self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=client_id,
                )
                # extra_params={"scope": self.settings['github_scope'], "foo":1})

    def _on_login(self, user):
        """ This handles the user object from the login request """
        if user:
            logging.info('logged in user from github: ' + str(user))
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")
        self.redirect(self.get_argument("next","/"))

