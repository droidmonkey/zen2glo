import requests
from distutils.util import strtobool

GLO_API = 'https://gloapi.gitkraken.com/v1/glo'

# Interface with the Glo API
class GloBoardsApi:
    def __init__(self, glo_token):
        self.glo_token = {'access_token': glo_token}

    def _get_multiple_pages(self, api, payload):
        data = []
        i = 1
        has_more = "true"
        while strtobool(has_more):
            payload["page"] = i
            r = requests.get(api, params=payload)
            data.extend(r.json())
            has_more = r.headers.get("has-more", "false")
            i += 1
        return data

    def get_boards(self):
        payload = self.glo_token
        payload["fields"] = "columns,name"
        boards = self._get_multiple_pages(GLO_API + '/boards', payload)
        return [GloBoard(x) for x in boards]

    def get_cards(self, board_id):
        payload = self.glo_token
        payload["per_page"] = 100
        return self._get_multiple_pages(GLO_API + '/boards/{}/cards'.format(board_id), payload)

    def get_attachments(self, board_id, card_id):
        payload = self.glo_token
        r = requests.get(GLO_API + '/boards/{}/cards/{}/attachments'.format(board_id,card_id), params=payload)
        data=r.json()
        return data

    def get_comments(self, board_id, card_id):
        payload = self.glo_token
        r = requests.get(GLO_API + '/boards/{}/cards/{}/comments'.format(board_id,card_id), params=payload)
        data=r.json()
        return data
    
    def get_userInfo(self):
        payload = self.glo_token
        r = requests.get(GLO_API + '/user', params=payload)
        data=r.json()
        return data
    
    def move_card(self, board_id, card_id, new_column_id):
        payload = {"column_id" : new_column_id}
        requests.post(GLO_API + '/boards/{}/cards/{}'.format(board_id, card_id), json=payload, params=self.glo_token)

    def create_card(self, board_id, card_data):
        requests.post(GLO_API + '/boards/{}/cards'.format(board_id), json=card_data, params=self.glo_token)

    def batch_cards(self, board_id, cards):
        requests.post(GLO_API + '/boards/{}/cards/batch'.format(board_id), json=cards)

# Definition for a Glo Board
# Returned as a result of calling get_boards from the API
class GloBoard:
    def __init__(self, glo_board, glo_cards=None):
        self.board_data = glo_board
        self.cards = glo_cards

        self.id = self.board_data["id"]
        self.name = self.board_data["name"]
        self.columns = self.board_data["columns"]

    def add_cards(self, glo_cards):
        self.cards = glo_cards

    def cards_in_column(self, column_id):
        cards = [card for card in self.cards if card.get("column_id", None) == column_id]
        cards.sort(key=lambda x: x.get("position", -1))
        return cards

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