# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

import functools
import os
import re
import subprocess
import sys

import flask
import ruamel.yaml

import podcastify.get_mimetype
import podcastify.list_channel


config_file = os.getenv("PODCASTIFY_CONFIG") or sys.argv[1]
with open(config_file) as cf:
    config = ruamel.yaml.YAML(typ='safe').load(cf)


app = flask.Flask(__name__)


@app.route('/')
def root():
    return ('query /feed/<channel>, '
            '/youtube/feed/channel/<name> or '
            '/youtube/video/<id>')


def secret_required(f):
    @functools.wraps(f)
    def decorator(*args, **kwargs):
        secret = flask.request.args.get('secret')
        if config['secrets'] is not None and secret not in config['secrets']:
            return 'invalid secret!', 401
        return f(*args, **kwargs)
    return decorator


def video_url_maker(id_):
    baseurl = flask.url_for('root', _external=True).rstrip('/')
    secret = flask.request.args.get('secret')
    return f'{baseurl}/youtube/video/{id_}?secret={secret}'


@app.route('/feed/<feed_name>')
@secret_required
def feed(feed_name):
    if feed_name not in config['feeds']:
        return f'`{feed_name}` not in config.feeds', 400
    feed_config = config['feeds'][feed_name]
    print(feed_config)
    return podcastify.list_channel.channel_to_rss(feed_config['url'],
                                                  video_url_maker,
                                                  config=feed_config)


@app.route('/youtube/feed/channel/<channel_name>')
@secret_required
def youtube_channel_feed(channel_name):
    if not re.match(r'[\w\-]{4,24}', channel_name):
        return f'`{channel_name}` feels suspicions', 400
    url = f'https://youtube.com/channel/{channel_name}'
    return podcastify.list_channel.channel_to_rss(url, video_url_maker)


@app.route('/youtube/video/<id_>')
@secret_required
def fetch(id_):
    if not re.match(r'[\w\-]{10,12}', id_):
        return f'`{id_}` feels suspicions', 400
    s = subprocess.Popen((
        'yt-dlp',
        '--no-color', '--no-cache-dir', '--no-progress', '--no-playlist',
        f'https://youtube.com/watch?v={id_}',
        '-o', '-'), stdout=subprocess.PIPE)
    return flask.send_file(s.stdout,
                           mimetype=podcastify.get_mimetype.by_id(id_))


def main():
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()
