import requests
from distutils.util import strtobool

GLO_API = 'https://gloapi.gitkraken.com/v1/glo'

# Interface with the Glo API
class GloBoardsApi:
    def __init__(self, glo_token):
        self.glo_token = glo_token
        self.def_params = self._build_params()
        self.last_message = ""

    def _build_params(self, additional_params={}):
        params = {"access_token": self.glo_token}
        params.update(additional_params)
        return params

    def _get_multiple_pages(self, api, params):
        data = []
        page = 1
        has_more = "true"
        while strtobool(has_more):
            params["page"] = page
            r = requests.get(api, params=params)
            data.extend(r.json())
            has_more = r.headers.get("has-more", "false")
            page += 1
        return data

    def get_board(self, board_id):
        params = self._build_params({"fields": "columns,name"})
        r = requests.get(f"{GLO_API}/boards/{board_id}", params=params)
        if r.status_code == 200:
            cards = self.get_cards(board_id)
            return GloBoard(r.json(), cards)
        else:
            self.last_message = r.json()["message"]

    def get_boards(self):
        params = self._build_params({"fields": "columns,name"})
        boards = self._get_multiple_pages(f"{GLO_API}/boards", params)
        return [GloBoard(x) for x in boards]

    def get_cards(self, board_id):
        params = self._build_params({"per_page": 100})
        return self._get_multiple_pages(f"{GLO_API}/boards/{board_id}/cards", params=params)

    def get_attachments(self, board_id, card_id):
        r = requests.get(GLO_API + '/boards/{}/cards/{}/attachments'.format(board_id,card_id), params=self.def_params)
        data=r.json()
        return data

    def get_comments(self, board_id, card_id):
        r = requests.get(GLO_API + '/boards/{}/cards/{}/comments'.format(board_id,card_id), params=self.def_params)
        data=r.json()
        return data
    
    def get_userInfo(self):
        r = requests.get(GLO_API + '/user', params=self.def_params)
        data=r.json()
        return data
    
    def save_card(self, board_id, card):
        r = requests.post(f"{GLO_API}/boards/{board_id}/cards/{card['id']}", 
                          json=card, 
                          params=self.def_params)
        if r.status_code == 200:
            return r.json()
        else:
            self.last_message = r.json()["message"]

    def create_card(self, board_id, card_data):
        requests.post(f"{GLO_API}/boards/{board_id}/cards", json=card_data, params=self.def_params)

    def batch_cards(self, board_id, cards):
        requests.post(f"{GLO_API}/boards/{board_id}/cards/batch", json=cards, params=self.def_params)

    def create_column(self, board_id, column_name, position=0):
        r = requests.post(f"{GLO_API}/boards/{board_id}/columns", 
                          json={"name": column_name, "position": position},
                          params=self.def_params)
        if r.status_code == 201:
            return r.json()
        else:
            self.last_message = r.json()["message"]

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
        if self.cards:
            cards = [card for card in self.cards if card.get("column_id", None) == column_id]
            cards.sort(key=lambda x: x.get("position", -1))
            return cards

    def card_by_name(self, card_name):
        for card in self.cards:
            if card["name"] == card_name:
                return card

def match_glo_to_zen(glo_api, glo_board, zen_board):
    # Create columns to match ZenHub pipelines
    position = len(glo_board.columns)
    for pipeline in zen_board.pipelines:
        column = glo_api.create_column(glo_board.id, pipeline["name"], position)
        if not column:
            return False, f"Failed to create new column {pipeline['name']}; {glo_api.last_message}"
        
        # Move existing glo cards into new columns
        for issue in sorted(pipeline["issues"], key=lambda x: x.get("position", -1)):
            github_issue = zen_board.github_issue(issue["issue_number"])
            if github_issue:
                card = glo_board.card_by_name(github_issue["title"])
                if card:
                    card["position"] = issue["position"]
                    card["column_id"] = column["id"]
                    if not glo_api.save_card(glo_board.id, card):
                        return False, f"Failed to move card {github_issue['title']}; {glo_api.last_message}"
        
        position += 1

    return True, "Success"    

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