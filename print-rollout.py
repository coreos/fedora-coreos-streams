import json, sys, datetime

update = json.load(open(sys.argv[1]))
stream = update["stream"]
release = update["releases"][-1]
version = release["version"]
rollout = release["metadata"]["rollout"]

start_percentage = rollout["start_percentage"]
# totally just going to ignore floating-point concerns here
if int(start_percentage * 100) == 100:
    print(f"{stream} rollout of {version} at 100%")
else:
    ts = datetime.datetime.fromtimestamp(rollout["start_epoch"])
    mins = rollout["duration_minutes"]
    hrs = mins / 60.0
    print(f"{stream} rollout of {version} scheduled for {ts} UTC for {mins}m ({hrs}h)")
