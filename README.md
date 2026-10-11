# apm-blog-feed

A trimmed copy of the Authority Property Management blog RSS feed
(https://www.authoritypm.com/feed/rss2), containing only the newest 10 posts.

The full site feed holds every post (~4 MB), which is larger than FeedBlitz's
1 MB feed limit. This repo publishes a small feed FeedBlitz can read:

**https://pirateblackspot.github.io/apm-blog-feed/feed.xml**

- `build_feed.py` – fetches the site feed and writes `feed.xml` (Python stdlib only).
  Full post content is kept only if the file stays under 400 KB.
- `.github/workflows/update-feed.yml` – runs every 2 hours (and on demand) and commits
  `feed.xml` only when it changed.
- `.github/workflows/keepalive.yml` – monthly timestamp commit so GitHub doesn't
  disable the schedule after 60 days of inactivity.
