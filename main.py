from flask import Flask
from flask import request, render_template, redirect, url_for, flash
from flask import session
from flask_github import GitHub
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime

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

glo_api = 'https://gloapi.gitkraken.com/v1/glo'
zen_api = 'https://api.zenhub.io'

# Glo API Credentials for Jon
#client_id = os.getenv("CLIENT_IDj")
#client_secret = os.getenv("CLIENT_SECRETj")
#state = os.getenv("STATEj")

 # Glo API Credentials for Z
client_id = os.getenv("CLIENT_IDz")
client_secret = os.getenv("CLIENT_SECRETz")
state = os.getenv("STATEz")


@app.route('/')
def root():
    if has_glo_access():
      return redirect(url_for('dashboard'))
   
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
    return redirect(next_url)

@app.route('/login-zenhub', methods=['POST'])
def login_zenhub():
    if not has_zenhub_access() and request.form.get('zenhub_token'):
        session['zenhub_token'] = request.form.get('zenhub_token')

    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if not has_glo_access():
        return redirect(url_for('root'))

    payload = {'access_token' : session['glo_token']}
    r = requests.get(glo_api + '/boards', params=payload)
    return render_template('dashboard.html', data=r.json(), 
        github=has_github_access(), zenhub=has_zenhub_access(),
        zenhub_boards=find_zenhub_boards('refresh' in request.args))

@app.route('/dashboard/<board_id>')
def show_board(board_id):
    if not has_glo_access():
        return redirect(url_for('root'))

    payload = {'access_token' : session['glo_token'], 'fields' : 'name,columns'}
    r = requests.get(glo_api + '/boards/' + board_id, params=payload)
    return render_template('dashboard.html', data=r.json())

@app.route('/logout')
def logout():
    session.pop('glo_token', None)
    session.pop('zenhub_token', None)
    session.pop('github_token', None)
    return redirect(url_for('root'))

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html',current_time=datetime.utcnow()), 404

@app.errorhandler(500)
def internal_server_error(e):
	return render_template('500.html', current_time=datetime.utcnow()), 500

def find_zenhub_boards(force=False):
    if not force and 'zenhub_boards' in session:
        return session['zenhub_boards']

    boards = []
    if has_github_access() and has_zenhub_access():
        repos = github.get('/user/repos')
        for repo in repos:
            r = requests.get('{}/p1/repositories/{}/board?access_token={}'.format(zen_api, repo['id'], session['zenhub_token']))
            board = r.json()
            if is_zenhub_board_valid(board):
                boards.append({'repo_name' : repo['full_name'], 'repo_id' : repo['id']})
                
    session['zenhub_boards'] = boards
    return boards

@github.access_token_getter
def github_token():
    if has_github_access():
        return session['github_token']

def get_zenhub_board(repo_id):
    if repo_id:
        r = requests.get('{}/p1/repositories/{}/board?access_token={}'.format(zen_api, repo_id, session['zenhub_token']))
        return r.json()

def is_zenhub_board_valid(board):
    if 'pipelines' in board:
        for pipeline in board['pipelines']:
            if 'issues' in pipeline and len(pipeline['issues']) > 0:
                return True
    return False

def has_glo_access():
    return 'glo_token' in session

def has_github_access():
    return 'github_token' in session

def has_zenhub_access():
    return 'zenhub_token' in session

if __name__ == '__main__':
    app.run(host='127.0.0.1')