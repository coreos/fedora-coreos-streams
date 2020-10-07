import json, sys, datetime, dateutil.tz

update = json.load(open(sys.argv[1]))
stream = update["stream"]
releases = update.get("releases", None)
if not releases:
    print(f"{stream} has no rollouts")
    sys.exit(0)
release = update["releases"][-1]
version = release["version"]
rollout = release["metadata"].get("rollout", None)
if not rollout:
    print(f"latest entry {version} on {stream} is not a rollout")
    sys.exit(0)


start_percentage = rollout["start_percentage"]
# totally just going to ignore floating-point concerns here
if int(start_percentage * 100) == 100:
    print(f"{stream} rollout of {version} at 100%")
else:
    ts = datetime.datetime.fromtimestamp(rollout["start_epoch"],
                                         datetime.timezone.utc)
    raleigh_ts = ts.astimezone(dateutil.tz.gettz("America/Toronto"))
    berlin_ts = ts.astimezone(dateutil.tz.gettz("Europe/Berlin"))
    mins = rollout["duration_minutes"]
    hrs = mins / 60.0
    ts_now = datetime.datetime.now(datetime.timezone.utc)
    if ts_now > ts:
        delta_str = str(ts_now - ts).split(".")[0]
        delta_str = f"{delta_str} ago"
    else:
        delta_str = str(ts - ts_now).split(".")[0]
        delta_str = f"in {delta_str}"
    print(f"{stream}")
    print(f"    version: {version}")
    print(f"    start: {ts} UTC ({delta_str})")
    print(f"           {raleigh_ts} Raleigh/New York/Toronto")
    print(f"           {berlin_ts} Berlin/France/Poland")
    print(f"    duration: {mins}m ({hrs}h)")
