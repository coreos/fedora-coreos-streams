# fedora-coreos-streams

Official stream metadata for Fedora CoreOS created by the
[generator](https://github.com/coreos/fedora-coreos-stream-generator/).

## Stream metadata
Latest FCOS stream metadata for different streams are available under streams/ directory. Stream metadata is generated using [fedora-coreos-stream-generator(https://github.com/coreos/fedora-coreos-stream-generator). For example: to generate latest stream metadata for testing stream, run-

```
fedora-coreos-stream-generator -releases=https://builds.coreos.fedoraproject.org/prod/streams/testing/releases.json  -output-file=testing.json --pretty-print
```