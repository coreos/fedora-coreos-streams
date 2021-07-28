#!/usr/bin/python3

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import dateutil.tz
from itertools import islice
import json
import os
import requests
import string
import time

RELEASES = string.Template("https://builds.coreos.fedoraproject.org/prod/streams/${stream}/releases.json")


def load(path):
    '''Load an update JSON file.'''
    with open(path) as fh:
        return json.load(fh)


def save(path, data):
    '''Save an update JSON file, updating the last-modified timestamp.'''
    if not os.path.exists(path):
        raise Exception(f'Refusing to create {path}')
    now = datetime.now(timezone.utc).isoformat(timespec='seconds'). \
            replace('+00:00', 'Z')
    data['metadata']['last-modified'] = now
    with open(path, 'w') as fh:
        json.dump(data, fh, indent='  ')
        fh.write('\n')


def add(info, version, start, duration, barrier=None, deadend=None):
    '''Append a new rollout.  Start is an arbitrary human-readable string;
    duration is in hours.'''
    import dateparser  # pip install python3-dateparser
    start_time = dateparser.parse(start, settings={
        'PREFER_DATES_FROM': 'future'
    })
    if start_time is None:
        raise Exception(f"Couldn't parse '{start}'")

    release = {
        'version': version,
        'metadata': {
            'rollout': {
                'duration_minutes': duration * 60,
                'start_epoch': int(start_time.timestamp()),
                'start_percentage': 0.0,
            }
        }
    }
    if barrier:
        release['metadata']['barrier'] = {
            'reason': barrier,
        }
    if deadend:
        release['metadata']['deadend'] = {
            'reason': deadend,
        }
    info['releases'].append(release)


def clean(info):
    '''Normalize the release list.'''
    completed_rollout = {'start_percentage': 1.0}

    # Drop timing parameters for completed rollouts
    for rel in info['releases']:
        roll = rel['metadata'].get('rollout')
        if roll and roll.get('duration_minutes'):
            # Have in-progress rollout
            end = roll.get('start_epoch', 0) + 60 * roll['duration_minutes']
            if end < time.time():
                # It's stale; terminate it
                rel['metadata']['rollout'] = completed_rollout

    # Drop completed rollouts except for the last one
    predicate = lambda rel: rel['metadata'].get('rollout') == completed_rollout
    for rel in islice(filter(predicate, reversed(info['releases'])), 1, None):
        del rel['metadata']['rollout']

    # Drop releases that have no rollout, barrier, or deadend
    def predicate(rel):
        for section in 'barrier', 'deadend', 'rollout':
            if section in rel['metadata']:
                return True
        return False
    info['releases'] = [rel for rel in info['releases'] if predicate(rel)]


def report(info, skip_version_check=False):
    '''Summarize the latest rollout.'''
    stream = info["stream"]
    if not info["releases"]:
        print(f"{stream} has no rollouts")
        return
    release = info["releases"][-1]
    version = release["version"]
    rollout = release["metadata"].get("rollout", None)
    if not rollout:
        print(f"latest entry {version} on {stream} is not a rollout")
        return

    latest_info = "unvalidated"
    if not skip_version_check:
        releases_url = RELEASES.substitute(stream=stream)
        releases = requests.get(releases_url).json()["releases"]
        versions = [r["version"] for r in releases]
        if versions[-1] == version:
            latest_info = "latest"
        elif version in versions:
            latest_info = "*** NOT LATEST ***"
        else:
            latest_info = "*** UNRELEASED (TYPO?) ***"

    start_percentage = rollout["start_percentage"]
    # totally just going to ignore floating-point concerns here
    if int(start_percentage * 100) == 100:
        print(f"{stream} rollout of {version} at 100%")
        return
    ts = datetime.fromtimestamp(rollout["start_epoch"], timezone.utc)
    raleigh_ts = ts.astimezone(dateutil.tz.gettz("America/Toronto"))
    berlin_ts = ts.astimezone(dateutil.tz.gettz("Europe/Berlin"))
    mins = rollout["duration_minutes"]
    hrs = mins / 60.0
    ts_now = datetime.now(timezone.utc)
    if ts_now > ts:
        delta_str = str(ts_now - ts).split(".")[0]
        delta_str = f"{delta_str} ago"
    else:
        delta_str = str(ts - ts_now).split(".")[0]
        delta_str = f"in {delta_str}"
    print(f"{stream}")
    print(f"    version: {version} ({latest_info})")
    print(f"    start: {ts} UTC ({delta_str})")
    print(f"           {raleigh_ts} Raleigh/New York/Toronto")
    print(f"           {berlin_ts} Berlin/France/Poland")
    print(f"    duration: {mins}m ({hrs}h)")


def path(stream):
    '''Get the relative path of an update JSON file for a stream.'''
    return f'updates/{stream}.json'


def _do_add(args):
    selftest()
    info = load(path(args.stream))
    clean(info)
    add(info, args.version, args.start, args.duration, barrier=args.barrier,
            deadend=args.deadend)
    report(info, args.skip_version_check)
    save(path(args.stream), info)


def _do_clean(args):
    selftest()
    for stream in args.stream:
        info = load(path(stream))
        clean(info)
        save(path(stream), info)


def _do_print(args):
    for stream in args.stream:
        info = load(path(stream))
        report(info, args.skip_version_check)


def _main():
    parser = argparse.ArgumentParser(description='Manage rollouts.')
    # "dest" to work around https://bugs.python.org/issue29298
    subcommands = parser.add_subparsers(title='subcommands', required=True,
            dest='command')

    add = subcommands.add_parser('add',
            description='Add a rollout and clean up old ones.')
    add.set_defaults(func=_do_add)
    add.add_argument('stream',
            help='stream name (e.g. "testing")')
    add.add_argument('version',
            help='new release version (e.g. "34.20210501.2.0")')
    add.add_argument('start',
            help='rollout start (e.g. "10 am")')
    add.add_argument('duration', metavar='duration-hours', type=int,
            help='rollout duration (e.g. "48")')
    add.add_argument('--skip-version-check', action='store_true',
                     help='skip validating versions')
    group = add.add_mutually_exclusive_group()
    group.add_argument('--barrier', metavar='reason',
            help='make this version a barrier with the specified reason URL')
    group.add_argument('--deadend', metavar='reason',
            help='make this version a deadend with the specified reason URL')

    clean = subcommands.add_parser('clean',
            description='Clean up old rollouts.')
    clean.set_defaults(func=_do_clean)
    clean.add_argument('stream', nargs='+')

    print_ = subcommands.add_parser('print',
            description='Print latest rollout.')
    print_.set_defaults(func=_do_print)
    print_.add_argument('--skip-version-check', action='store_true',
                        help='skip validating versions')
    print_.add_argument('stream', nargs='+')

    args = parser.parse_args()
    args.func(args)


def selftest():
    def try_add(input, output, *args, **kwargs):
        info = deepcopy(input)
        clean(info)
        add(info, *args, **kwargs)
        # Start time will vary
        info['releases'][-1]['metadata']['rollout']['start_epoch'] = \
                output['releases'][-1]['metadata']['rollout']['start_epoch']
        if info != output:
            print(f"Expected: {json.dumps(output, indent='  ')}")
            print(f"Found: {json.dumps(info, indent='  ')}")
            raise Exception(f"Self-test failed when adding {args} {kwargs}")

    input = {
        "stream": "stable",
        "metadata": {
            "last-modified": "2021-07-21T20:10:18Z"
        },
        "releases": [
            {
                "version": "31.20200517.3.0",
                "metadata": {
                    "deadend": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/480#issuecomment-631724629"
                    }
                }
            },
            {
                "version": "32.20200615.3.0",
                "metadata": {
                    "barrier": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/484"
                    },
                    "rollout": {
                        "start_percentage": 1.0
                    }
                }
            },
            {
                "version": "34.20210511.3.0",
                "metadata": {
                    "barrier": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/829"
                    },
                    "rollout": {
                        "duration_minutes": 2880,
                        "start_epoch": 1616742400,
                        "start_percentage": 5.0
                    }
                }
            },
            {
                "version": "34.20210611.3.0",
                "metadata": {
                    "rollout": {
                        "duration_minutes": 2880,
                        "start_epoch": 1616752400,
                        "start_percentage": 0.0
                    }
                }
            },
            {
                "version": "34.20210626.3.1",
                "metadata": {
                    "barrier": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/829"
                    },
                    "rollout": {
                        "duration_minutes": 1440,
                        "start_epoch": 1616762400,
                        "start_percentage": 0.0
                    }
                }
            }
        ]
    }
    output = {
        "stream": "stable",
        "metadata": {
            "last-modified": "2021-07-21T20:10:18Z"
        },
        "releases": [
            {
                "version": "31.20200517.3.0",
                "metadata": {
                    "deadend": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/480#issuecomment-631724629"
                    }
                }
            },
            {
                "version": "32.20200615.3.0",
                "metadata": {
                    "barrier": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/484"
                    }
                }
            },
            {
                "version": "34.20210511.3.0",
                "metadata": {
                    "barrier": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/829"
                    }
                }
            },
            {
                "version": "34.20210626.3.1",
                "metadata": {
                    "barrier": {
                        "reason": "https://github.com/coreos/fedora-coreos-tracker/issues/829"
                    },
                    "rollout": {
                        "start_percentage": 1.0
                    }
                }
            },
            {
                "version": "35.20210801.3.0",
                "metadata": {
                    "rollout": {
                        "duration_minutes": 1440,
                        "start_epoch": 0,
                        "start_percentage": 0.0
                    }
                }
            }
        ]
    }
    try_add(input, output, '35.20210801.3.0', '10 AM', 24)

    input = {
        "stream": "stable",
        "metadata": {
            "last-modified": "2021-07-21T20:10:18Z"
        },
        "releases": []
    }
    output = {
        "stream": "stable",
        "metadata": {
            "last-modified": "2021-07-21T20:10:18Z"
        },
        "releases": [
            {
                "version": "31.20200517.3.0",
                "metadata": {
                    "rollout": {
                        "duration_minutes": 1440,
                        "start_epoch": 0,
                        "start_percentage": 0.0
                    },
                    "deadend": {
                        "reason": "a reason"
                    }
                }
            }
        ]
    }
    try_add(input, output, '31.20200517.3.0', '10 AM', 24, deadend="a reason")

    output = {
        "stream": "stable",
        "metadata": {
            "last-modified": "2021-07-21T20:10:18Z"
        },
        "releases": [
            {
                "version": "31.20200517.3.0",
                "metadata": {
                    "rollout": {
                        "duration_minutes": 1440,
                        "start_epoch": 0,
                        "start_percentage": 0.0
                    },
                    "barrier": {
                        "reason": "a reason"
                    }
                }
            }
        ]
    }
    try_add(input, output, '31.20200517.3.0', '10 AM', 24, barrier="a reason")


if __name__ == '__main__':
    _main()
