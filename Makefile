.PHONY: syntax-check print-rollouts

syntax-check:
	@find streams updates -iname '*.json' | sort | xargs -n 1 python3 -c 'import json, sys; json.load(open(sys.argv[1]))'
	@find release-notes -iname '*.yml' | sort | xargs -n1 python3 ci/check-release-notes.py

print-rollouts:
	@find updates -iname '*.json' -printf '%f\n' | cut -f1 -d. | sort | xargs ./rollout.py print
