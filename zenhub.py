import requests

ZEN_API = 'https://api.zenhub.io'

class ZenHub:
    def __init__(self, zenhub_token, github):
        self.zenhub_token = zenhub_token
        self.github = github

    def get_board(self, repo_fullname):
        github_repo = self.github.get('/repos/' + repo_fullname)
        r = requests.get('{}/p1/repositories/{}/board?access_token={}'.format(ZEN_API, github_repo['id'], self.zenhub_token))
        github_repo['zenhub'] = r.json()
        return github_repo

    def get_issue(self, board, issue_id):
        github_issue = self.github.get('/repos/{}/issues/{}'.format(board["full_name"], issue_id))
        r = requests.get('{}/p1/repositories/{}/issues/{}?access_token={}'.format(ZEN_API, board["id"], issue_id, self.zenhub_token))
        github_issue['zenhub'] = r.json()
        return github_issue

class Board:
    def __init__(self, zenhub, repo_fullname):
        self.zenhub = zenhub
        self.board = zenhub.get_board(repo_fullname)
        self.repo_fullname = repo_fullname
        self.issues = {}

    def pipelines(self):
        return self.board['zenhub']['pipelines']

    def issue(self, issue_id):
        if issue_id not in self.issues:
            self.issues[issue_id] = self.zenhub.get_issue(self.board, issue_id)
        return self.issues[issue_id]

