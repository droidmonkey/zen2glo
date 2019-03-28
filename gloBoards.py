import requests

glo_api = 'https://gloapi.gitkraken.com/v1/glo'

class GloBoardsApi:
    def __init__(self, client_id, client_secret, state):
        self.glo_api = glo_api
        self.client_id = client_id
        self.client_secret = client_secret
        self.state = state
        self.payload = {'client_id' : self.client_id, 'state' : self.state, 'scope' : 'board:read'}

class Pipeline:
    def __init__(self, name, issues):
        self.name = name
        self.issues = issues

class Board:
    def __init__(self, zenhub_token, github, repo_fullname):
        self.zenhub_token = zenhub_token
        self.github = github

        # TODO: perform api error checking
        self.repo = github.get('/repos/' + repo_fullname)
        
        r = requests.get('{}/p1/repositories/{}/board?access_token={}'.format(zen_api, self.repo['id'], self.zenhub_token))
        self.board = r.json()

        self._load_pipelines()

    def _load_pipelines(self):
        self.pipelines = []
        for pipeline in self.board['pipelines']:
            self.pipelines.append(Pipeline(pipeline['name'], pipeline['issues']))

    # Populate issues with GitHub data
    def populate_issues(self):
        pass
