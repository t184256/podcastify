# podcastify

A trivial Flask app that generates video podcast feeds
for Youtube channels/playlists, and probably all other stuff
[yt-dlp](https://github.com/yt-dlp/yt-dlp) can handle.
Also enables fetching the videos themselves.

Sounds very similar to [podsync](https://github.com/mxpv/podsync),
except it doesn't need a YouTube API token.

If you aren't willing to host an open Youtube relay,
an absolutely trivial authentication mechanism is available,
see `secrets` in the example `config.yml`.
