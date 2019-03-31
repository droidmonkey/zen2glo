from flask import g, session, flash, request, render_template, redirect, url_for
from flask import current_app as app
from datetime import datetime

import requests

from . import main
from .. import github
from .. import zenhub
from .. import gloBoards
from ..utils import has_github_access, has_glo_access, has_zenhub_access, glo_required, zen_required

@main.route('/')
def root():
    if has_glo_access():
        return redirect(url_for('.dashboard'))
    else:
        payload = {'client_id' : app.config["CLIENT_ID"], 'state' : app.config["SECRET"], 'scope' : 'board:write'}
        return render_template('index.html', **payload)

@main.route('/callback')
def glo_callback():
    if not has_glo_access() and request.args.get('state') == app.config["SECRET"]:
        payload = {'grant_type' : 'authorization_code', 'client_id' : app.config["CLIENT_ID"], 
            'client_secret' : app.config["CLIENT_SECRET"], 'code' : request.args.get('code')}
        r = requests.post('https://api.gitkraken.com/oauth/access_token', data=payload)
        data = r.json()

        if 'access_token' in data:
            session.permanent = True
            session['glo_token'] = data['access_token']
        else:
            return "ERROR: Failed to authorize with Glo!"

    return redirect(url_for('.dashboard'))

@main.route('/login-github')
def login_github():
    return github.authorize(scope="public_repo,read:org,read:user")

@main.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = url_for('.dashboard')
    if oauth_token is None:
        flash("Authorization failed.", "danger")
        return redirect(next_url)

    session['github_token'] = oauth_token

    github_user = github.get('/user')
    session['github_user_id'] = github_user['id']
    session['github_user_login'] = github_user['login']
    return redirect(next_url)

@main.route('/login-zenhub', methods=['POST'])
def login_zenhub():
    if not has_zenhub_access() and request.form.get('zenhub_token'):
        session['zenhub_token'] = request.form.get('zenhub_token')
    return redirect(url_for('.zenhub_refresh'))

@main.route('/dashboard')
@glo_required
def dashboard():
    glo_boards = sorted(g.glo.get_boards(), key=lambda x: x.name.lower())
    return render_template('dashboard.html', glo_data=glo_boards)

@main.route('/dashboard/zenhub-refresh')
@zen_required(github)
def zenhub_refresh():
    boards = []
    repos = g.zenhub.get_repos()
    for repo in repos:
        board = g.zenhub.get_board(repo["full_name"])
        if board.is_valid():
            boards.append({'repo_name' : board.repo_fullname, 'repo_id' : board.repo_id})
    
    session["zenhub_boards"] = boards
    return redirect(url_for(".dashboard"))

@main.route('/dashboard/zenhub/<owner>/<repo>')
@zen_required(github)
def show_zenhub_board(owner, repo):
    board = g.zenhub.get_board(owner + "/" + repo)
    return render_template('zenhub_preview.html', zenhub_board=board)

@main.route('/dashboard/match')
@glo_required
@zen_required(github)
def match():
    glo_board_id = request.args.get("glo_board_id", None)
    zen_board_id = request.args.get("zen_board_id", None)
    
    if glo_board_id and zen_board_id:
        glo_board = g.glo.get_board(glo_board_id)
        zen_board = g.zenhub.get_board(zen_board_id)

        status, message = gloBoards.match_glo_to_zen(g.glo, glo_board, zen_board)
        if status:
            flash(f"Transfer to Glo Board {glo_board.name} successful!", "success")
        else:
            flash(f"Transfer failed: {message}!", "danger")

    return redirect(url_for(".dashboard"))

@main.route('/logout')
def logout():
    session.clear()
    return render_template('logoutSuccess.html')


@main.app_errorhandler(404)
def page_not_found(e):
	return render_template('404.html',current_time=datetime.utcnow()), 404

@main.app_errorhandler(500)
def internal_server_error(e):
	return render_template('500.html', current_time=datetime.utcnow()), 500

@github.access_token_getter
def github_token():
    if has_github_access():
        return session['github_token']
