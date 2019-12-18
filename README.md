# fedora-coreos-streams

Official stream metadata for Fedora CoreOS created by the
[generator](https://github.com/coreos/fedora-coreos-stream-generator/).

## Stream metadata

Latest FCOS stream metadata for different streams are available under the
`streams/` directory. To generate the latest stream metadata for the `testing`
stream, run:

```
fedora-coreos-stream-generator -releases=https://builds.coreos.fedoraproject.org/prod/streams/testing/releases.json -output-file=streams/testing.json -pretty-print
```

## Release checklist

File a new issue and follow the steps there, checking boxes as you go!

- [stable](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release&template=stable.md)
- [testing](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release&template=testing.md)
