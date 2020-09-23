import json, sys, datetime

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
    mins = rollout["duration_minutes"]
    hrs = mins / 60.0
    delta = ts - datetime.datetime.now(datetime.timezone.utc)
    delta_str = str(delta).split(".")[0]
    if delta_str.startswith("-"):
        delta_str = f"{delta_str[1:]} ago"
    else:
        delta_str = f"in {delta_str}"
    print(f"{stream}")
    print(f"    version: {version}")
    print(f"    start: {ts} UTC ({delta_str})")
    print(f"    duration: {mins}m ({hrs}h)")
