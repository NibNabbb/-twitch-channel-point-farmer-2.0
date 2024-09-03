import requests
import logging

class TwitchAuth:
    API_BASE_URL = "https://api.twitch.tv/helix"
    OAUTH_URL = "https://id.twitch.tv/oauth2/token"

    def __init__(self, client_id, client_secret, grant_type="client_credentials"):
        self.client_id = client_id
        self.client_secret = client_secret
        self.grant_type = grant_type
        self.access_token = None
        self.expires_in = None
        self.token_type = None

    def authenticate(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type
        }

        try:
            response = requests.post(self.OAUTH_URL, data=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error during authentication: {str(e)}")
            return

        response_json = response.json()
        self.access_token = response_json["access_token"]
        self.expires_in = response_json["expires_in"]
        self.token_type = response_json["token_type"]

    def get_live_streams(self, user_id=None, user_login=None, game_id=None, stream_type="all", language=None, limit=20, before=None, after=None):
        url = f"{self.API_BASE_URL}/streams"

        params = {
            "user_id": user_id,
            "user_login": user_login,
            "game_id": game_id,
            "type": stream_type,
            "language": language,
            "first": limit,
            "before": before,
            "after": after
        }

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting live streams: {str(e)}")
            return None

        return response.json()

    def get_users_info(self, user_id=None, user_login=None):
        url = f"{self.API_BASE_URL}/users"

        params = {
            "id": user_id,
            "login": user_login
        }

        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}"
        }

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error getting user info: {str(e)}")
            return None

        return response.json()
