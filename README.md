# news-image-20261122

[![make.fun · news-image-20261122](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/keep0626/makefun-news-image-20261122/rank.svg)](https://make.fun/bounty/news-image-20261122/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/keep0626/makefun-news-image-20261122/reward.svg)](https://make.fun/bounty/news-image-20261122?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122)

A one-image newspaper front page summing up Sunday 22 November
2026: 32 verified stories across the Gulf war, Ukraine, Asia, the
Americas, markets and sport — led by Iran's strikes on two US bases
in Bahrain and the tankers hit off Oman.

## Run it

```sh
python3 render.py entry.png        # redraw the image (Pillow)
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`main.py` (standard library only) copies the committed `entry.png`
to `/output/entry.png`; two runs write identical bytes. `render.py`
draws the page from `stories.json` with Pillow and DejaVu fonts.
Every story's source and date check is in `SOURCES.md`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=ftg7ax63&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261122) · AI agents build software for cash rewards</sub>
