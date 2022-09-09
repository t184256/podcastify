# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
import pytz
import types

import yt_dlp
import feedgen.feed

import podcastify.get_mimetype


YOUTUBE_DL_OPTIONS = {
    'playlist_items': '10::-1',  # consider only the latest 10 videos
}

def channel_to_rss(url, video_url_maker, config=None):
    print(config)
    overrides = (config['overrides']
                 if config is not None and 'overrides' in config else {})
    print(overrides)
    with yt_dlp.YoutubeDL(YOUTUBE_DL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        info = ydl.sanitize_info(info)

    def get_overrideable(info_name, overrideable_name=None):
        overrideable_name = overrideable_name or info_name
        return overrides.get(overrideable_name) or info[info_name]

    fg = feedgen.feed.FeedGenerator()
    fg.load_extension('podcast')
    fg.id(get_overrideable('channel_url', 'id'))
    fg.link(href=get_overrideable('channel_url', 'link'), rel='self')
    title = get_overrideable('title')
    if title.endswith(' - Videos') and not 'title' in overrides:
        title = title[:-len(' - Videos')]
    fg.title(title)
    fg.description(get_overrideable('description') or
                   get_overrideable('title'))
    fg.podcast.itunes_author(get_overrideable('uploader'))
    t = (best_thumbnail(info)
         if not 'thumbnail' in overrides else overrides('thumbnail'))
    if t:
        fg.logo(t)

    for e in info['entries']:
        if 'duration' not in e:
            print(f"SKIPPING {e['title']}: no duration")
            continue
        if 'is_live' not in e and e.is_live:
            print(f"SKIPPING {e['title']}: is_live=True")
            continue
        fe = fg.add_entry()
        fe.id(e['id'])
        fe.title(e['fulltitle'])
        fe.description(e['description'] or e['fulltitle'])
        fe.podcast.itunes_duration(e['duration'])

        t = best_thumbnail(e)
        if t:
            # HACK: bypass overzealous validation
            fe.podcast._PodcastEntryExtension__itunes_image = t

        if 'release_timestamp' in e and e['release_timestamp']:
            ts = datetime.datetime.utcfromtimestamp(e['release_timestamp'])
            ts = pytz.utc.fromutc(ts)
            fe.pubDate(ts)
        elif 'upload_date' in e and e['upload_date']:
            ts = datetime.datetime.strptime(e['upload_date'], '%Y%m%d')
            ts = pytz.utc.fromutc(ts)
            fe.pubDate(ts)

        fe.enclosure(video_url_maker(e['id']),
                     str(e['filesize_approx']),
                     podcastify.get_mimetype.by_ext(e['ext']))

    return fg.rss_str(pretty=True)


def best_thumbnail(info):
    def ratio(t):
        if t['width'] > t['height']:
            return t['width'] / t['height']
        else:
            return t['height'] / t['width']

    if 'thumbnails' in info:
        t = info['thumbnails'][0]
        thumbnails = [t for t in info['thumbnails']
                      if 'width' in t and 'height' in t]
        if thumbnails:
            best_thumbnail = thumbnails[0]
            for t in thumbnails:
                # take the most squarish thumbnail of of them all...
                if 1 <= ratio(t) <= ratio(best_thumbnail):
                    # ... and the largest one among the equally squarish
                    if (ratio(t) == ratio(best_thumbnail) and
                            t['width'] <= best_thumbnail['width']):
                        continue
                    best_thumbnail = t
            return best_thumbnail['url']
