# Prerequisites for performing a release

- access to the official CentOS CI fedora-coreos namespace
- access to the AWS S3 fcos-builds bucket
- the following packages installed: `awscli gnupg2 git`
- [`fedora-coreos-stream-generator`](https://github.com/coreos/fedora-coreos-stream-generator/)
- your GPG key linked to your FAS account
- a checkout and GitHub fork of [`this repo`](https://github.com/coreos/fedora-coreos-streams)
- a checkout and GitHub fork of [`fedora-coreos-config`](https://github.com/coreos/fedora-coreos-config)
- a checkout of [`fedora-coreos-releng-automation`](https://github.com/coreos/fedora-coreos-releng-automation)
