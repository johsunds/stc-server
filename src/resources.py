from resource_management import Resource, ResourceCache
import requests
import json
from globals import client_id

TWITCH_HEADERS = {"Accept": "application/vnd.twitchtv.v5+json", "Client-ID": client_id}


def get(*args, **kwargs):
    response = requests.get(*args, **kwargs)
    if response.status_code != 200:
        raise requests.exceptions.RequestException("Bad status code: {}".format(response.status_code))
    return response


class BTTVEmotes(Resource):
    GLOBAL_ENDPOINT = "https://api.betterttv.net/2/emotes"
    CHANNEL_ENDPOINT = "https://api.betterttv.net/2/channels/{}"
    EMOTE_URL = "https://cdn.betterttv.net/emote/{}/1x"

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel

    def _renew_resource(self):
        if self.channel is None:
            response = get(self.GLOBAL_ENDPOINT, timeout=self.timeout)
        else:
            response = get(self.CHANNEL_ENDPOINT.format(self.channel), timeout=self.timeout)

        parsed_json = json.loads(response.content)
        return {emote["code"]: self.EMOTE_URL.format(emote["id"]) for emote in parsed_json["emotes"]}


class FFZEmotes(Resource):
    CHANNEL_ENDPOINT = "https://api.frankerfacez.com/v1/room/{}"

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel

    def _renew_resource(self):
        response = get(self.CHANNEL_ENDPOINT.format(self.channel))

        parsed_json = json.loads(response.content)
        sets = parsed_json["sets"]
        response = {}
        for emote_set in sets:
            emotes = sets[emote_set]["emoticons"]
            for emote in emotes:
                url = "https:{}".format(emote['urls']['1'])
                response[emote['name']] = url
        return response


class TwitchBadges(Resource):
    GLOBAL_ENDPOINT = "https://badges.twitch.tv/v1/badges/global/display?language=en"
    CHANNEL_ENDPOINT = "https://badges.twitch.tv/v1/badges/channels/{}/display?language=en"

    def __init__(self, channel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channel = channel

    def _renew_resource(self):
        new_resource = {}
        if self.channel is None:
            response = get(self.GLOBAL_ENDPOINT)
            parsed_json = json.loads(response.content)
            badges = parsed_json["badge_sets"]
            for badge in badges:
                versions = badges[badge]["versions"]
                for version in versions:
                    url = versions[version]["image_url_1x"]
                    name = "{}/{}".format(badge, version)
                    new_resource[name] = url
            return new_resource
        else:
            if self.channel not in channel_ids.ids:
                channel_ids.add(self.channel)

            if self.channel not in channel_ids.ids:
                return {}

            response = get(self.CHANNEL_ENDPOINT.format(channel_ids.ids[self.channel]))

            parsed_json = json.loads(response.content)
            if not parsed_json["badge_sets"]:
                return {}
            versions = parsed_json["badge_sets"]["subscriber"]["versions"]
            new_resource = {}
            for version in versions:
                url = versions[version]["image_url_1x"]
                name = "{}/{}".format(self.channel.lower(), version)
                new_resource[name] = url
            return new_resource


class TwitchIds:
    ENDPOINT = "https://api.twitch.tv/kraken/users?login={}"

    def __init__(self):
        self.ids = {}

    def add(self, channel):
        try:
            response = get(self.ENDPOINT.format(channel), headers=TWITCH_HEADERS)
            parsed_json = json.loads(response.content)

            if len(parsed_json["users"]) == 0:
                return {}

            channel_id = parsed_json["users"][0]["_id"]
            self.ids[channel] = channel_id
            return {channel: channel_id}
        except requests.exceptions.RequestException:
            return {}


resources = {"bttv": {"emotes": BTTVEmotes},
             "ffz": {"emotes": FFZEmotes},
             "twitch": {"badges": TwitchBadges, "ids": TwitchIds}}

cache = ResourceCache()

channel_ids = TwitchIds()
