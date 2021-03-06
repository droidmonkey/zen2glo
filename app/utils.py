from flask import g, session, flash, redirect, url_for
from functools import wraps

from .zenhub import ZenHub
from .gloBoards import GloBoardsApi

def has_glo_access():
    return 'glo_token' in session

def has_github_access():
    return 'github_token' in session

def has_zenhub_access():
    return 'zenhub_token' in session

def glo_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not has_glo_access():
            flash("Glo login is required to access!")
            return redirect(url_for('main.root'))
        g.glo = GloBoardsApi(session["glo_token"])
        return f(*args, **kwargs)
    return decorated_function

def zen_required(github):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not has_zenhub_access() or not has_github_access():
                flash("Zenhub token and GitHub login are required to access!")
                return redirect(url_for('main.dashboard'))
            g.zenhub = ZenHub(session["zenhub_token"], github)
            return f(*args, **kwargs)
        return decorated_function
    return decorator