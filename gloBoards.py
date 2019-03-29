import requests
from flask import session

glo_api = 'https://gloapi.gitkraken.com/v1/glo'

# Class GloBoardsApi init instance creates session variable token
class GloBoardsApi:
    def __init__(self, glo_token):
        self.glo_token = {'access_token': glo_token}

    def get_boards(self):
        r = requests.get(glo_api + '/boards', params=self.glo_token)
        return r.json()
    
    def get_columns(self, board_id):
        payload = self.glo_token
        payload["fields"] = "columns"
        r = requests.get(glo_api + '/boards/{}'.format(board_id), params=payload)
        return r.json()

    def get_cards(self, board_id):
        payload = self.glo_token
        r = requests.get(glo_api + '/boards/{}/cards'.format(board_id), params=payload)
        return r.json()

    def get_labels(self):
        pass

    def get_attachments(self):
        pass

    def get_comments(self):
        pass
    
    def get_userInfo(self):
        pass
    
    def move_card(self, board_id, card_id, new_column_id):
        payload = {"column_id" : new_column_id}
        requests.post(glo_api + '/boards/{}/cards/{}'.format(board_id, card_id), json=payload, params=self.glo_token)

    def create_card(self, board_id, card_data):
        requests.post(glo_api + '/boards/{}/cards'.format(board_id), json=card_data, params=self.glo_token)

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