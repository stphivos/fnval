from requests import HTTPError
from output import Result


class Url:
    def __init__(self, path, methods):
        self.path = path
        self.methods = methods


class User:
    def __init__(self, username, password, vars):
        self.username = username
        self.password = password
        self.vars = vars

    def __str__(self):
        return self.username


class App:
    def __init__(self, name, session):
        self.name = name
        self.session = session
        self.users = []
        self.anon_urls = []
        self.auth_urls = []
        self.user_urls = []
        self.results = []

    def get_urls_of(self, user):
        """
        Generate list of user-specific urls by replacing template vars with user vars.

        e.g. For user with var playlist_id=1 the following conversion will happen:
        PUT /playlist/{playlist_id}/ -> PUT /playlist/1/
        """
        urls = []

        for url in self.user_urls:
            user_path = url.path

            for key, value in user.vars.items():
                user_path = user_path.replace('{' + key + '}', str(value))

            # if key not in user vars url is locked for user -> skip
            if '{' in user_path or '}' in user_path:
                continue

            urls.append(Url(user_path, url.methods))

        return urls

    def access(self, url, user=None, should_fail=False):
        """
        Make request to url with every specified method and supplied user to verify the result is as expected.
        """
        for method in url.methods:
            username = user.username if user else 'anonymous'
            test_template = '{0} {1}'
            test_name = test_template.format('Deny' if should_fail else 'Allow', username)

            result = Result(url.path, method.upper(), test_name)

            try:
                result.response = self.session.request(url.path, method=method, user=user)
                result.is_error = should_fail
            except HTTPError as ex:
                result.response = ex.response
                result.is_error = not should_fail
            finally:
                self.results.append(result)

    def validate_anon_urls(self):
        """
        Validate public urls are accessible to anonymous users.
        """
        for url in self.anon_urls:
            self.access(url)

    def validate_auth_urls(self):
        """
        Validate urls that should be accessible to all authenticated users.
        """
        for url in self.auth_urls:
            self.access(url, should_fail=True)

            for user in self.users:
                self.access(url, user)

    def validate_user_urls(self):
        """
        Validate urls that should be accessible to a specific authenticated user only.

        E.g. A user may have access to request a delete of an article with id 5 - which he or she authored,
        using url template DELETE /article/article_id/ if there is an article_id = 5 in that user's vars.
        """
        for user in self.users:
            urls = self.get_urls_of(user)

            for url in urls:
                self.access(url, user)

            for other_user in [x for x in self.users if x != user]:
                for url in urls:
                    self.access(url, other_user, should_fail=True)

    def validate(self):
        """
        Validate all app urls against configured checks.
        """
        self.results = []
        self.validate_anon_urls()
        self.validate_auth_urls()
        self.validate_user_urls()
