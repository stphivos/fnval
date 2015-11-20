import requests
from requests import HTTPError
from requests.auth import HTTPBasicAuth, HTTPDigestAuth


class AuthType(object):
    basic, digest, session = range(3)


class RequestMethod(object):
    get, post, put, delete = range(4)


class Session(object):
    def __init__(self, auth, root_url, login_path, *args, **kwargs):
        self._auth = auth
        self.auth_type = getattr(AuthType, auth, None)
        self.root_url = root_url
        self.login_path = login_path
        self.login_username_field = kwargs.get('login_username_field', 'username')
        self.login_password_field = kwargs.get('login_password_field', 'password')
        self.csrf_cookie_name = kwargs.get('csrf_cookie_name', '')
        self.csrf_form_name = kwargs.get('csrf_form_name', '')
        self.csrf_header_name = kwargs.get('csrf_header_name', '')
        self.validate()

    def validate(self):
        """
        Enforces instance variable combinations are valid.
        """
        if not self.root_url:
            raise Exception('Root url not specified.')

        if self.auth_type == AuthType.session and not self.login_path:
            raise Exception('Login url not specified for auth type session.')

        # TODO: Verify support for basic and digest authentication.
        if self.auth_type != AuthType.session:
            raise NotImplementedError('Auth type {0} is not yet supported.'.format(self._auth))

    def connect(self, session, user):
        """
        Make initial connection to server to obtain authentication headers if needed.
        """
        url = self.root_url + self.login_path

        resp = session.get(url)
        resp.raise_for_status()

        csrf = {self.csrf_form_name: session.cookies[self.csrf_cookie_name]}
        credentials = {self.login_username_field: user.username, self.login_password_field: user.password}

        resp = session.post(url, data=dict(credentials, **csrf), allow_redirects=False)
        resp.raise_for_status()

        headers = {self.csrf_header_name: session.cookies[self.csrf_cookie_name], 'Referer': url}
        return headers

    def get_session(self, user):
        """
        Create a new session based on configured auth type and specified user credentials.
        """
        session = requests.session()
        headers = None

        if user:
            if self.auth_type == AuthType.session:
                headers = self.connect(session, user)
            else:
                session.auth = {
                    AuthType.basic: HTTPBasicAuth(user.username, user.password),
                    AuthType.digest: HTTPDigestAuth(user.username, user.password),
                }[self.auth_type]

        return session, headers

    def get_function(self, method, user):
        """
        Get function instance based on specified method. This should not be limited to http only.
        """
        session, headers = self.get_session(user)

        func = {
            RequestMethod.get: session.get,
            RequestMethod.post: session.post,
            RequestMethod.put: session.put,
            RequestMethod.delete: session.delete
        }[getattr(RequestMethod, method, None)]

        return func, headers

    def request(self, url, method, user=None):
        """
        Make the request to target url and enforce a 2xx status code was received.
        """
        if user and not self.auth_type:
            raise Exception('Auth type {0} is invalid.'.format(self._auth))

        func, headers = self.get_function(method, user)
        if not func:
            raise Exception('Request method {0} is invalid.'.format(method))

        res = func(self.root_url + url, headers=headers, allow_redirects=False)
        if res.status_code >= 300:
            raise HTTPError('%s Error: %s for %s %s' % (res.status_code, res.reason, method, res.url), response=res)

        return res
