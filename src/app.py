from flask import Flask, jsonify
import logging
from resources import BTTVEmotes, TwitchBadges, FFZEmotes, TwitchIds
from resource_management import ResourceCache

app = Flask(__name__)

cache = ResourceCache()

channel_ids = TwitchIds()

# preload global resources
cache.add_resource(BTTVEmotes(channel=None, name="bttv_emotes"))
cache.add_resource(TwitchBadges(channel=None, name="twitch_badges", channel_ids=channel_ids))


def lookup_resource(name, resource, channel=None):
    return cache[name] if name in cache else cache.add_resource(resource(channel=channel, name=name,
                                                                         channel_ids=channel_ids))


@app.route("/channel_id/<string:channel>")
def get_channel_id(channel):
    data = channel_ids.add(channel) if channel not in channel_ids.ids else channel_ids.ids[channel]
    if not data:
        return jsonify(message="channel id not found"), 404
    else:
        return jsonify(data), 200


@app.route("/globals")
def get_global_resources():
    response = {"emotes": cache["bttv_emotes"],
                "badges": cache["twitch_badges"]}
    return jsonify(response), 200


@app.route("/channel/<string:channel>")
def get_channel_resources(channel):
    bttv_emotes = lookup_resource("bttv_emotes_{}".format(channel), BTTVEmotes, channel)
    ffz_emotes = lookup_resource("ffz_emotes_{}".format(channel), FFZEmotes, channel)
    twitch_badges = lookup_resource("twitch_badges_{}".format(channel), TwitchBadges, channel)
    response = {"emotes": {**bttv_emotes, **ffz_emotes},
                "badges": twitch_badges}
    return jsonify(response), 200


if __name__ == "__main__":
    logging.basicConfig(filename="../server.log", level=logging.DEBUG,
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    app.run(debug=False)
