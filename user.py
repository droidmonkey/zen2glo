import json

class User:
    def __init__(self, json_str=None):
        user = json.loads(json_str)
        self.github_token = user.get('github_token', None)
        self.zenhub_token = user.get('zenhub_token', None)
        self.glo_token = user.get('glo_token', None)

    def to_json(self):
        return json.dumps(self)

    def has_glo_access(self):
        return self.glo_token is not None

    def has_github_access(self):
        return self.github_token is not None

    def has_zenhub_access(self):
        return self.zenhub_token is not None
