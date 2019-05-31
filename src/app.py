from flask import Flask, jsonify
import logging
from resources import resources, cache, channel_ids
from utils import lookup_key_sequence

logging.basicConfig(filename="../server.log", level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = Flask(__name__)

sources = ["twitch", "bttv", "ffz"]
resource_types = ["emotes", "badges", "ids"]
scopes = ["global", "channel"]


def resource_name(*args):
    return '_'.join(filter(None, args))


def resource_exists(source, resource_type):
    try:
        lookup_key_sequence((source, resource_type), resources)
        return True
    except KeyError:
        return False


@app.route("/twitch/channel_id/<channel>")
def get_channel_id(channel):
    data = channel_ids.add(channel) if channel not in channel_ids.ids else channel_ids.ids[channel]
    if not data:
        return jsonify(message="channel id not found"), 404
    else:
        return jsonify(data), 200


@app.route("/<source>/<resource_type>", defaults={"channel": None})
@app.route("/<source>/<resource_type>/<channel>")
def get_resource(source, resource_type, channel):
    if not resource_exists(source, resource_type):
        return jsonify(message="endpoint does not exist"), 400
    name = resource_name(source, resource_type, channel)
    if name in cache:
        data = cache[name]
    else:
        cache.add_resource(resources[source][resource_type](channel, name))
        data = cache[name]
    return jsonify(data), 200


if __name__ == "__main__":
    app.run(debug=True)
