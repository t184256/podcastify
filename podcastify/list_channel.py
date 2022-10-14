# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime
import pytz
import sys
import types

import yt_dlp
import feedgen.feed

import podcastify.get_mimetype
import podcastify.chapters_extensions


YOUTUBE_DL_OPTIONS = {
    'match_filter': yt_dlp.utils.match_filter_func(
        '!is_live'
        ' & live_status != is_upcoming'
        ' & live_status != is_live'
    ),
}


def channel_to_rss(feed_config, video_url_maker):
    assert 'url' in feed_config
    overrides = (feed_config['overrides']
                 if feed_config and 'overrides' in feed_config else {})
    yt_dl_options = {
        **YOUTUBE_DL_OPTIONS,
        **feed_config.get('extra_yt_dl_options', {}),
        'playlist_items': f'{feed_config.get("max_entries", 5)}::-1'
    }
    with yt_dlp.YoutubeDL(yt_dl_options) as ydl:
        info = ydl.extract_info(feed_config['url'], download=False)
        info = ydl.sanitize_info(info)

    def get_overrideable(info_name, overrideable_name=None):
        overrideable_name = overrideable_name or info_name
        return overrides.get(overrideable_name) or info[info_name]

    fg = feedgen.feed.FeedGenerator()
    fg.load_extension('podcast')
    fg.register_extension(
        'chapters',
        podcastify.chapters_extensions.SimpleChaptersExtension,
        podcastify.chapters_extensions.SimpleChaptersEntryExtension
    )
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
            print(f"SKIPPING {e['title']}: no duration", file=sys.stderr)
            continue
        if 'is_live' in e and e['is_live']:
            print(f"SKIPPING {e['title']}: is_live=True", file=sys.stderr)
            continue
        LIVE_STATUSES = ('was_live', 'not_live', 'post_live')
        live_status = e.get('live_status')
        if live_status and live_status not in LIVE_STATUSES:
            print(f"SKIPPING {e['title']}: live_status={e['live_status']}",
                  file=sys.stderr)
            continue
        print(f'* {e["fulltitle"]} [{live_status}]', file=sys.stderr)
        fe = fg.add_entry()
        fe.id(e['id'])
        fe.title(e['fulltitle'])
        fe.link({'href': e['original_url']})
        fe.description(e['description'] or e['fulltitle'])
        fe.podcast.itunes_duration(e['duration'])
        if 'chapters' in e and e['chapters']:
            for chapter in e['chapters']:
                fe.chapters.add(chapter['start_time'], chapter['title'])

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

        filesize_approx = (str(e['filesize_approx'])
                           if 'filesize_approx' in e else '7777M')

        mime = (podcastify.get_mimetype.by_ext(e['ext']) if 'ext' in e else
                podcastify.get_mimetype.by_id(e['id']))
        fe.enclosure(video_url_maker(e['id']), filesize_approx, mime)

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
