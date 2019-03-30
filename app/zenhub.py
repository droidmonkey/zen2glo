import requests

ZEN_API = 'https://api.zenhub.io'

class ZenHub:
    def __init__(self, zenhub_token, github):
        self.zenhub_token = zenhub_token
        self.github = github

    def get_repos(self):
        return self.github.get('/user/repos')

    def get_board(self, repo_fullname):
        repo = self.github.get('/repos/' + repo_fullname)
        issues = self.github.get('/repos/' + repo_fullname + '/issues')
        r = requests.get('{}/p1/repositories/{}/board?access_token={}'.format(ZEN_API, repo['id'], self.zenhub_token))
        return Board(repo, issues, r.json())

    def get_issue(self, board, issue_id):
        issue = self.github.get('/repos/{}/issues/{}'.format(board.repo_fullname, issue_id))
        r = requests.get('{}/p1/repositories/{}/issues/{}?access_token={}'.format(ZEN_API, board.repo_id, issue_id, self.zenhub_token))
        issue['zenhub'] = r.json()
        return issue

class Board:
    def __init__(self, github_repo, github_issues, zenhub_board):
        self.github_repo = github_repo
        self.github_issues = github_issues
        self.zenhub_board = zenhub_board

        # Extract commonly used fields
        self.repo_name = self.github_repo["name"]
        self.repo_fullname = self.github_repo["full_name"]
        self.repo_id = self.github_repo["id"]
        self.repo_url = self.github_repo["html_url"]
        self.pipelines = self.zenhub_board.get("pipelines", None)

    # Determine if this is a valid ZenHub board if it contains issues
    # in any of the pipelines
    def is_valid(self):
        for pipeline in self.pipelines:
            if 'issues' in pipeline and len(pipeline["issues"]) > 0:
                return True

    def github_issue(self, issue_number):
        for issue in self.github_issues:
            if issue["number"] == issue_number:
                return issue
        return None

    # Returns list of issues in a pipeline sorted by their position
    def pipeline_issues(self, pipeline_id):
        for pipeline in self.pipelines:
            if pipeline["id"] == pipeline_id:
                return sorted(pipeline["issues"], key=lambda x: x.get("position", -1))
        return []
