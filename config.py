import os
import yaml
from net import Session
from application import App, User, Url


def get_config(path):
    if not path or not os.path.exists(path):
        raise Exception('Config file \'{0}\' not found.'.format(path))

    with open(path) as f:
        markup = f.read()

    return yaml.load(markup)


def get_users(config):
    users = []
    for u in config['users']:
        users.append(User(
            u['username'],
            u['password'],
            u['vars']
        ))
    return users


def get_urls(config):
    public_urls = []
    for u in config['urls']['public']:
        public_urls.append(Url(
            u['path'],
            u['methods'],
            u.get('payload', None)
        ))

    authentication_urls = []
    for u in config['urls']['authentication']:
        authentication_urls.append(Url(
            u['path'],
            u['methods'],
            u.get('payload', None)
        ))

    authorization_urls = []
    for u in config['urls']['authorization']:
        authorization_urls.append(Url(
            u['path'],
            u['methods'],
            u.get('payload', None)
        ))

    return public_urls, authentication_urls, authorization_urls


def get_session(config):
    settings = config['settings']
    session = Session(
        auth=settings['auth'],
        root_url=settings['root'],
        login_path=settings['login'],
        login_username_field=settings['username_field'],
        login_password_field=settings['password_field'],
        csrf_cookie_name=settings['csrf_cookie'],
        csrf_form_name=settings['csrf_form'],
        csrf_header_name=settings['csrf_header']
    )
    return session


def get_app(config_path):
    """
    Loads app configuration from disk.
    """
    config = get_config(config_path)
    app = App(config['app'], get_session(config))
    app.users = get_users(config)
    app.anon_urls, app.auth_urls, app.user_urls = get_urls(config)

    return app
