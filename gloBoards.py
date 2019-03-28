import requests

glo_api = 'https://gloapi.gitkraken.com/v1/glo'

class Issue:
    def __init__(self, id, position):
        self.id = id
        self.position = position

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
