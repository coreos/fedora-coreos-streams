.PHONY: syntax-check
syntax-check:
	@find streams updates -iname '*.json' | xargs -n 1 python3 -c 'import json, sys; json.load(open(sys.argv[1]))'

.PHONY: print-rollouts
print-rollouts:
	@find updates -iname '*.json' | xargs -n 1 python3 -c '\
	import json, sys, datetime; \
	update = json.load(open(sys.argv[1])); \
	stream = update["stream"]; \
	release = update["releases"][-1]; \
	version = release["version"]; \
	rollout = release["metadata"]["rollout"]; \
	ts = datetime.datetime.fromtimestamp(rollout["start_epoch"]); \
	mins = rollout["duration_minutes"]; \
	hrs = mins / 60.0; \
	print(f"{stream} rollout of {version} scheduled for {ts} UTC for {mins}m ({hrs}h)");'
