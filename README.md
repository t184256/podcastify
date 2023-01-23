# podcastify

A trivial Flask app that generates video podcast feeds
for Youtube channels/playlists, and probably all other stuff
[yt-dlp](https://github.com/yt-dlp/yt-dlp) can handle.
Also enables fetching the videos themselves.

Sounds very similar to [podsync](https://github.com/mxpv/podsync),
except it doesn't need a YouTube API token.

Doesn't require any disk space at all and barely needs any RAM.
This design imposes some limitations though.

A more featureful evolution of this software is [yousable](https://github.com/t184256/yousable),
offering:
* livestream recording
* cutting out sponsor ads and more using Sponsorblock

at the expense of requiring storage disk space.

If you aren't willing to host an open Youtube relay,
an absolutely trivial authentication mechanism is available,
see `secrets` in the example `config.yml`.
