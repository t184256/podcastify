# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

import cachetools.func

import yt_dlp


# this shouldn't change at all, right? right?
@cachetools.func.ttl_cache(maxsize=2048, ttl=6*3600)
def by_id(id_):
    with yt_dlp.YoutubeDL({}) as ydl:
        info = ydl.extract_info(id_, download=False)
        info = ydl.sanitize_info(info)
    return by_ext(info['ext'])


def by_ext(ext):
     return f"video/{ext}"
