import requests
from distutils.util import strtobool

GLO_API = 'https://gloapi.gitkraken.com/v1/glo'

# Interface with the Glo API
class GloBoardsApi:
    def __init__(self, glo_token):
        self.auth_header = {"Authorization": f"Bearer {glo_token}"}
        self._reset()

    def _reset(self):
        self.last_message = ""
        self.last_url = ""
        self.last_hasmore = False

    def _send_request(self, endpoint, method="get", params={}, payload={}):
        self._reset()
        self.last_url = f"{GLO_API}/{endpoint}"
        method = method.lower()

        try:
            if method == "get":
                r = requests.get(self.last_url, headers=self.auth_header, params=params)
            elif method == "post":
                r = requests.post(self.last_url, headers=self.auth_header, params=params, json=payload)
            elif method == "delete":
                r = requests.delete(self.last_url, headers=self.auth_header)
            else:
                raise TypeError(f"Invalid request method {method} passed.")

            # Raise an HTTPError if we receive a bad response
            r.raise_for_status()

            # Return the json package
            self.last_hasmore = r.headers.get("has-more", "false") == "true"
            return r.json()
        except requests.exceptions.RequestException as e:
            self.last_message = e.response.json().get("message", str(e))
            return None

    def _get_multiple_pages(self, endpoint, params={}):
        ret = []
        page = 1
        self.last_hasmore = True
        while self.last_hasmore:
            params["page"] = page
            data = self._send_request(endpoint, params=params)
            if data:
                ret.extend(data)
            else:
                return None
            page += 1
        return data

    def get_board(self, board_id):
        board = self._send_request(f"boards/{board_id}", params={"fields": "columns,name"})
        if board:
            cards = self.get_cards(board_id)
            return GloBoard(board, cards)

    def get_boards(self):
        boards = self._get_multiple_pages("boards", params={"fields": "columns,name"})
        if boards:
            return [GloBoard(x) for x in boards]

    def get_cards(self, board_id):
        return self._get_multiple_pages(f"boards/{board_id}/cards", params={"per_page": 100})

    def get_attachments(self, board_id, card_id):
        return self._send_request(f"boards/{board_id}/cards/{card_id}/attachments")

    def get_comments(self, board_id, card_id):
        return self._send_request(f"boards/{board_id}/cards/{card_id}/comments")
    
    def get_userInfo(self):
        return self._send_request("user")
    
    def save_card(self, board_id, card):
        return self._send_request(f"boards/{board_id}/cards/{card['id']}", method="post", payload=card)

    def create_card(self, board_id, card):
        return self._send_request(f"boards/{board_id}/cards", method="post", payload=card)

    def batch_cards(self, board_id, cards):
        return self._send_request(f"boards/{board_id}/cards/batch", method="post", payload=cards)

    def create_column(self, board_id, column_name, position=0):
        return self._send_request(f"boards/{board_id}/columns", method="post", payload={"name": column_name, "position": position})

# Definition for a Glo Board
# Returned as a result of calling get_boards from the API
class GloBoard:
    def __init__(self, glo_board, glo_cards=None):
        self.board_data = glo_board
        self.cards = glo_cards

        self.id = self.board_data["id"]
        self.name = self.board_data["name"]
        self.columns = self.board_data["columns"]

    def find_card(self, id="", name=""):
        for card in self.cards:
            if card["id"] == id or card["name"] == name:
                return card

    def find_column(self, id="", name=""):
        for column in self.columns:
            if column["id"] == id or column["name"] == name:
                return column

    def add_cards(self, glo_cards):
        self.cards = glo_cards

    def cards_in_column(self, column_id):
        if self.cards:
            cards = [card for card in self.cards if card.get("column_id", None) == column_id]
            cards.sort(key=lambda x: x.get("position", -1))
            return cards

def match_glo_to_zen(glo_api, glo_board, zen_board):
    # Create columns to match ZenHub pipelines
    position = len(glo_board.columns)
    for pipeline in zen_board.pipelines:
        # Find or create a column for this pipeline
        column = glo_board.find_column(name=pipeline["name"])
        if not column:
            column = glo_api.create_column(glo_board.id, pipeline["name"], position)
            if not column:
                return False, f"Failed to create new column {pipeline['name']}; {glo_api.last_message}"
        
        # Move existing glo cards into new columns
        for issue in sorted(pipeline["issues"], key=lambda x: x.get("position", -1)):
            github_issue = zen_board.github_issue(issue["issue_number"])
            if github_issue:
                card = glo_board.find_card(name=github_issue["title"])
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