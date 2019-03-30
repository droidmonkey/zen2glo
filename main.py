from flask import Flask
from flask import g, session, flash, request, render_template, redirect, url_for
from flask_github import GitHub
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

import zenhub
import gloBoards
from utils import has_github_access, has_glo_access, has_zenhub_access, glo_required, zen_required

import requests
import os

app = Flask(__name__)

#Apply Flask Bootstrap
bootstrap = Bootstrap(app)
#Apply Flask Moment
moment = Moment(app)

# Flask Secret Key
app.secret_key = os.getenv('SECRET_KEY')

# Github Application named GloProjGithubAPI
app.config['GITHUB_CLIENT_ID'] = os.getenv('GITHUB_CLIENT_ID')
app.config['GITHUB_CLIENT_SECRET'] = os.getenv('GITHUB_SECRET')

github = GitHub(app)

client_id = os.getenv("CLIENT_IDz")
client_secret = os.getenv("CLIENT_SECRETz")
state = os.getenv("STATEz")

@app.route('/')
def root():
    if has_glo_access():
        return redirect(url_for('dashboard'))
    else:
        payload = {'client_id' : client_id, 'state' : state, 'scope' : 'board:read'}
        return render_template('index.html', **payload)

@app.route('/callback')
def glo_callback():
    if not has_glo_access() and request.args.get('state') == state:
        payload = {'grant_type' : 'authorization_code', 'client_id' : client_id, 
            'client_secret' : client_secret, 'code' : request.args.get('code')}
        r = requests.post('https://api.gitkraken.com/oauth/access_token', data=payload)
        data = r.json()

        if 'access_token' in data:
            session.permanent = True
            session['glo_token'] = data['access_token']
        else:
            return "ERROR: Failed to authorize with Glo!"

    return redirect(url_for('dashboard'))

@app.route('/login-github')
def login_github():
    return github.authorize(scope="public_repo,read:org,read:user")

@app.route('/github-callback')
@github.authorized_handler
def authorized(oauth_token):
    next_url = url_for('dashboard')
    if oauth_token is None:
        flash("Authorization failed.")
        return redirect(next_url)

    session['github_token'] = oauth_token

    github_user = github.get('/user')
    session['github_user_id'] = github_user['id']
    session['github_user_login'] = github_user['login']
    return redirect(next_url)

@app.route('/login-zenhub', methods=['POST'])
def login_zenhub():
    if not has_zenhub_access() and request.form.get('zenhub_token'):
        session['zenhub_token'] = request.form.get('zenhub_token')
    return redirect(url_for('zenhub_refresh'))

@app.route('/dashboard')
@glo_required
def dashboard():
    glo_boards = g.glo.get_boards()
    [board.add_cards(g.glo.get_cards(board.id)) for board in glo_boards]
    return render_template('dashboard.html', glo_data=glo_boards)

@app.route('/dashboard/zenhub-refresh')
@zen_required(github)
def zenhub_refresh():
    boards = []
    repos = g.zenhub.get_repos()
    for repo in repos:
        board = g.zenhub.get_board(repo["full_name"])
        if board.is_valid():
            boards.append({'repo_name' : board.repo_fullname, 'repo_id' : board.repo_id})
    
    session["zenhub_boards"] = boards
    return redirect(url_for("dashboard"))

@app.route('/dashboard/zenhub/<owner>/<repo>')
@zen_required(github)
def show_zenhub_board(owner, repo):
    board = g.zenhub.get_board(owner + "/" + repo)
    return render_template('zenhub_preview.html', zenhub_board=board)

@app.route('/logout')
def logout():
    session.clear()
    return render_template('logoutSuccess.html')


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html',current_time=datetime.utcnow()), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html', current_time=datetime.utcnow()), 500

@github.access_token_getter
def github_token():
    if has_github_access():
        return session['github_token']

if __name__ == '__main__':
    app.run(host='127.0.0.1')
