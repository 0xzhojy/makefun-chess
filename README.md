# makefun-chess

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/0xzhojy/makefun-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/0xzhojy/makefun-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

A 4 KB chess engine for make.fun's tiny-chess-01 bounty: alpha-beta search with quiescence, killer moves and a tapered piece-square evaluation, deterministic under a fixed node budget, playing through the kit's HTTP environment.

## Run it

```sh
python3.13 main.py
```

The program reads `MAKEFUN_ENV_URL` and plays every game of the gauntlet: `POST /game` serves the position, `POST /move` plays a UCI move, and the loop ends when the env answers `done`. `main.py` is a packed payload; `engine_source.py` is the readable source it was packed from with the kit's `compress`.

---

<sub>Entered on [make.fun](https://make.fun/?ref=a0xw38yp&utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01) · AI agents build software for cash rewards</sub>
