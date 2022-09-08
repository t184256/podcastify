# podcastify

A trivial Flask app that generates video podcast feeds
for Youtube channels/playlists.
Also enables fetching the videos themselves.

Built upon [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Sounds very similar to [podsync](https://github.com/mxpv/podsync),
except it doesn't need a YouTube API token.

If you aren't willing to host an open Youtube relay,
an absolutely trivial authentication mechanism is available,
see `secrets` in the example `config.yml`.
