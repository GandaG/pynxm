# Copyright 2019 Daniel Nunes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A python wrapper for the Nexus API."""

__version__ = "0.1.0"

import json
import platform
import uuid
import webbrowser

import requests
from websocket import create_connection

USER_AGENT = "pynxm/{} ({}; {}) {}/{}".format(
    __version__,
    platform.platform(),
    platform.architecture()[0],
    platform.python_implementation(),
    platform.python_version(),
)
BASE_URL = "https://api.nexusmods.com/v1/"


class LimitReachedError(Exception):
    """
    Exception raised when the request rate limit has been reached.
    """

    pass


class RequestError(Exception):
    """
    Exception raised when a request returns an error code.
    """

    pass


class Nexus(object):
    """
    The class used for connecting to the Nexus API.
    Requires an API key from your Nexus account.
    """

    def __init__(self, api_key):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "user-agent": USER_AGENT,
                "apikey": api_key,
                "content-type": "application/json",
            }
        )
        self.nexus_headers: dict = {}

    @classmethod
    def sso(cls, app_slug, sso_token, sso_id=None):
        """
        Application login via Single Sign-On (SSO).

        :param app_slug: A string with the application slug.
        :param sso_token: A string with the connection token.
        :param sso_id: An optional string with an id used in previous connections.
        :return: A 'Nexus' instance, ready to be used.
        """
        ws = create_connection("wss://sso.nexusmods.com")
        if sso_id is None:
            sso_id = str(uuid.uuid4())
        ws.send(json.dumps({"id": sso_id, "token": sso_token}))
        webbrowser.open(
            "https://www.nexusmods.com/"
            "sso?id={}&application={}".format(sso_id, app_slug)
        )
        api_key = ws.recv()
        return cls(api_key)

    def _make_request(self, operation, endpoint, payload=None, data=None, headers=None):
        if payload is None:
            payload = {}
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        response = self.session.request(
            operation.upper(),
            BASE_URL + endpoint,
            params=payload,
            data=data,
            headers=headers,
            timeout=30,
        )
        status_code = response.status_code
        self.nexus_headers = {k: v for k, v in response.headers.items() if "X-" in k}
        if status_code not in (200, 201):
            if status_code == 429:
                raise LimitReachedError(
                    "You have reached your request limit. "
                    "Please wait one hour before trying again."
                )
            elif status_code in (503, 504):
                raise RequestError("Status Code {} - {}".format(status_code, response.reason))
            else:
                try:
                    msg = response.json()["message"]
                except KeyError:
                    msg = response.json()["error"]
                raise RequestError("Status Code {} - {}".format(status_code, msg))
        return response.json()

    def colour_schemes_list(self):
        """
        Returns a list of all colour schemes, including the
        primary, secondary and 'darker' colours.
        """
        return self._make_request("get", "colourschemes.json")

    def user_details(self):
        """
        Returns the user's details.
        """
        return self._make_request("get", "users/validate.json")

    def user_tracked_list(self):
        """
        Returns a list of all the mods being tracked by the current user.
        """
        return self._make_request("get", "user/tracked_mods.json")

    def user_tracked_add(self, game, mod_id):
        """
        Tracks this mod with the current user.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        """
        self._make_request(
            "post",
            "user/tracked_mods.json",
            payload={"domain_name": game},
            data={"mod_id": mod_id},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

    def user_tracked_delete(self, game, mod_id):
        """
        Stop tracking this mod with the current user.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        """
        self._make_request(
            "delete",
            "user/tracked_mods.json",
            payload={"domain_name": game},
            data={"mod_id": mod_id},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

    def user_endorsements_list(self):
        """
        Returns a list of all endorsements for the current user.
        """
        return self._make_request("get", "user/endorsements.json")

    def game_details(self, game):
        """
        Returns specified game, along with download count, file count and categories.

        :param game: A string with Nexus' game domain.
        """
        return self._make_request("get", "games/{}.json".format(game))

    def game_list(self, include_unapproved=False):
        """
        Returns a list of all games.

        :param include_unapproved: A boolean on whether to include unapproved games.
        """
        return self._make_request(
            "get", "games.json", payload={"include_unapproved": include_unapproved}
        )

    def game_updated_list(self, game, period):
        """
        Returns a list of mods that have been updated in a given period,
        with timestamps of their last update.

        :param game: A string with Nexus' game domain.
        :param period: Acceptable values: '1d' (1 day), '1w' (1 week) or '1m' (1 month).
        """
        if period not in ("1d", "1w", "1m"):
            raise ValueError("Allowed values for 'period' argument: '1d', '1w', '1m'.")
        return self._make_request(
            "get", "games/{}/mods/updated.json".format(game), payload={"period": period}
        )

    def game_latest_added_list(self, game):
        """
        Retrieve 10 latest added mods for a specified game.

        :param game: A string with Nexus' game domain.
        """
        return self._make_request("get", "games/{}/mods/latest_added.json".format(game))

    def game_latest_updated_list(self, game):
        """
        Retrieve 10 latest updated mods for a specified game.

        :param game: A string with Nexus' game domain.
        """
        return self._make_request(
            "get", "games/{}/mods/latest_updated.json".format(game)
        )

    def game_trending_list(self, game):
        """
        Retrieve 10 trending mods for a specified game.

        :param game: A string with Nexus' game domain.
        """
        return self._make_request("get", "games/{}/mods/trending.json".format(game))

    def mod_details(self, game, mod_id):
        """
        Retrieve specified mod details, from a specified game.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        """
        return self._make_request("get", "games/{}/mods/{}.json".format(game, mod_id))

    def mod_search(self, game, md5_hash):
        """
        Searches for a mod given its md5 hash.

        :param game: A string with Nexus' game domain.
        :param md5_hash: Mod md5 hash.
        """
        return self._make_request(
            "get", "games/{}/mods/md5_search/{}.json".format(game, md5_hash)
        )

    def mod_endorse(self, game, mod_id):
        """
        Endorse a mod.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        """
        return self._make_request(
            "post", "games/{}/mods/{}/endorse.json".format(game, mod_id)
        )

    def mod_abstain(self, game, mod_id):
        """
        Abstain from endorsing a mod.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        """
        return self._make_request(
            "post", "games/{}/mods/{}/abstain.json".format(game, mod_id)
        )

    def mod_file_list(self, game, mod_id, categories=None):
        """
        Lists all files for a specific mod.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        :param categories: Filter file category.
                           Accepts either a list of categories or a comma-separated
                           string of categories.
                           Possible categories: 'main', 'update', 'optional',
                           'old_version' and 'miscellaneous'.
        """
        if isinstance(categories, (tuple, list)):
            payload = {"category": ",".join(categories)}
        elif isinstance(categories, str):
            payload = {"category": categories}
        else:
            payload = None
        return self._make_request(
            "get", "games/{}/mods/{}/files.json".format(game, mod_id), payload=payload
        )

    def mod_file_details(self, game, mod_id, file_id):
        """
        View a specified mod file, using a specified game and mod.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        :param file_id: A string with the file id.
        """
        return self._make_request(
            "get", "games/{}/mods/{}/files/{}.json".format(game, mod_id, file_id)
        )

    def mod_file_download_link(self, game, mod_id, file_id, nxm_key=None, expires=None):
        """
        Generate download link for mod file.

        Note: For non-premium users, see the Nexus API docs
        on how to obtain the key/expires strings.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        :param file_id: A string with the file id.
        :param nxm_key: A string with the nxm file key.
        :param expires: A string with the nxm expires.
        """
        if None in (nxm_key, expires):
            payload = None
        else:
            payload = {"key": nxm_key, "expires": expires}
        return self._make_request(
            "get",
            "games/{}/mods/{}/files/{}/"
            "download_link.json".format(game, mod_id, file_id),
            payload=payload,
        )

    def mod_changelog_list(self, game, mod_id):
        """
        Returns list of changelogs for mod.

        :param game: A string with Nexus' game domain.
        :param mod_id: A string the mod id.
        """
        return self._make_request(
            "get", "games/{}/mods/{}/changelogs.json".format(game, mod_id)
        )
