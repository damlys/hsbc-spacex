# SpaceX Launches — Python CLI with argparse

Command-line tool (`spacex.py`) that fetches SpaceX launch data from the public API and produces useful summaries.

Machine requirements and setup:

```
$ python3 --version
Python 3.14.0

$ pip3 --version
pip 25.3

$ pip3 install -r requirements.txt
```

Usage examples:

```
$ ./spacex.py --help
$ ./spacex.py --action report
$ ./spacex.py --action payloads -v
$ ./spacex.py --action launchpads --refresh --cache .cache/launches.json
```

CLI arguments:

- `--action report|payloads|launchpads` (required)
- `--verbose` or `-v` (optional): increases logging detail
- `--refresh` (optional): ignores cache and refetches from API
- `--cache PATH` (optional): path to cache file (default: `launches.json`)

Results:

```
$ ./spacex.py --help
usage: spacex.py [-h] --action ACTION [-v] [--refresh] [--cache CACHE]

options:
  -h, --help            show this help message and exit
  --action ACTION       report, payloads or launchpads
  -v, --verbose         increases logging detail
  --refresh             ignores cache and refetches from API
  --cache CACHE         path to cache file

$ ./spacex.py --action report
Year 2022 summary:
Total: 62 | Successful: 43 | Failed: 0 | Success ratio: 100.00%

$ ./spacex.py --action payloads
Average payloads per launch: 0.25

$ ./spacex.py --action launchpads
Count of launches per launchpad ID:
- 5e9e4501f509094ba4566f84 - 34
- 5e9e4502f509094188566f88 - 17
- 5e9e4502f509092b78566f87 - 11
```
