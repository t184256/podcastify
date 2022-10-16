# SPDX-FileCopyrightText: 2022 Alexander Sosedkin <monk@unboiled.info>
# SPDX-License-Identifier: AGPL-3.0-or-later

import hashlib
import math
import sys

import cachetools.func
import requests


API_URL = 'https://sponsor.ajay.app'


def strtime(seconds):
    seconds = round(seconds)
    if seconds > 3600:
        h, r = seconds // 3600, seconds % 3600
        m, s = r // 60, r % 60
        return f'{h}:{m:02d}:{s:02d}'
    else:
        m, s = seconds // 60, seconds % 60
        return f'{m}:{s:02d}'


@cachetools.func.ttl_cache(maxsize=2048, ttl=5*60)
def query(video_id):
    h = hashlib.sha256(video_id.encode()).hexdigest()
    url = f'{API_URL}/api/skipSegments/{h[:4]}'

    r = None
    try:
        j = requests.get(url, timeout=3).json()
        for je in j:
            if je['videoID'] == video_id:
                r = je
        if r is not None:
            assert 'segments' in r
            for s in r['segments']:
                assert 'actionType' in s
                assert 'category' in s
                assert 'segment' in s
                assert len(s['segment']) == 2
    except Exception as e:
        print(f'sponsorblock error: {e}', file=sys.stderr)
    return r


def pretty(r):
    t = 'Sponsorblock:\n'
    for s in r['segments']:
        t += f'* {s["actionType"]} {s["category"]}:'
        t += f' {strtime(s["segment"][0])} - {strtime(s["segment"][1])}\n'
    return t
