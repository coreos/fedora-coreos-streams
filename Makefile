.PHONY: syntax-check
syntax-check:
	@find streams updates -iname '*.json' | sort | xargs -n 1 python3 -c 'import json, sys; json.load(open(sys.argv[1]))'

.PHONY: print-rollouts
print-rollouts:
	@find updates -iname '*.json' -printf '%f\n' | cut -f1 -d. | sort | xargs ./rollout.py print
