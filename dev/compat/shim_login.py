# -*- coding: utf-8 -*-
"""``flask.ext.login`` shim.

flask-login 0.2 (2014) exposed ``is_authenticated()`` / ``is_active()`` /
``is_anonymous()`` as *methods*; 0.6 turned them into properties.  The 2014 app
calls them as methods in every ``is_accessible`` override, so an anonymous
visitor hits ``TypeError: 'bool' object is not callable`` on every admin page.

Putting the method API back on ``AnonymousUserMixin`` restores the original
behaviour (403 for anonymous visitors) without touching the app code.
Logged-in users are unaffected: the project's own ``User`` model already
defines those methods.

Caveat: because a bound method is always truthy, flask-login's own
``@login_required`` decorator can no longer detect anonymous users.  This app
never uses it (it gates the admin through ``is_accessible``), so nothing here
depends on that.
"""

from flask_login import mixins as _mixins
from flask_login import (AnonymousUserMixin, LoginManager,  # noqa: F401
                         UserMixin, current_user, login_required, login_user,
                         logout_user)

__all__ = [
    "LoginManager", "UserMixin", "AnonymousUserMixin", "current_user",
    "login_required", "login_user", "logout_user",
]


def _is_authenticated(_self):
    return False


def _is_active(_self):
    return False


def _is_anonymous(_self):
    return True


# Patch the class itself: LoginManager copies this name into an instance
# attribute in __init__, so patching LoginManager alone would be ignored.
_mixins.AnonymousUserMixin.is_authenticated = _is_authenticated
_mixins.AnonymousUserMixin.is_active = _is_active
_mixins.AnonymousUserMixin.is_anonymous = _is_anonymous
