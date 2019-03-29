import requests
from flask import session

glo_api = 'https://gloapi.gitkraken.com/v1/glo'

# Class GloBoardsApi init instance creates session variable token
class GloBoardsApi:
    def __init__(self):
        self.gloBoardsToken = []
        print(f'gloBoards.py Line 10')
    def init_instance(self, gloBoardsToken):
        self.gloBoardsToken = gloBoardsToken
        self.payload = {'access_token': gloBoardsToken}
        #DEBUG
        print(f'gloBoards.py Line 15')

    def get_boards(self):
        if hasattr(self,'payload'): 
            r = requests.get(glo_api + '/boards', params = self.payload)
            boards = r.json()
            return boards
        else:
            print(f'gloBoards.py Line 23: ')

    
    def get_columns(self):
        pass

    def get_cards(self):
        pass

    def get_labels(self):
        pass

    def get_attachments(self):
        pass

    def get_comments(self):
        pass
    
    def get_userInfo(self):
        pass
'''
class GloBoard:
    def __init__(self, gloBoardsToken):
        self.gloBoardsToken = gloBoardsToken

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
'''
# Performs a full one-way transfer from zenhub to glo
# Does not link back to GitHub
def transfer_zen_to_glo(zen_board):
    # Glo API calls
    # 1. Create glo board (zen board name)
    # 2. Create Columns from pipelines
    # 3. Create Cards from Issues
    # 4. Import GitHub labels
    pass

def transfer_github_to_glo(github_project):
    pass