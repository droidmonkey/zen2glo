import requests
from flask import session

glo_api = 'https://gloapi.gitkraken.com/v1/glo'

# Class GloBoardsApi init instance creates session variable token
class GloBoardsApi:
    def __init__(self, glo_token):
        self.payload = {'access_token': glo_token}

    def get_boards(self):
        r = requests.get(glo_api + '/boards', params = self.payload)
        return r.json()
    
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