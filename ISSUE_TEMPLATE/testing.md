First, verify that you meet all the [prerequisites](https://github.com/coreos/fedora-coreos-streams/blob/master/release-prereqs.md)

# Pre-release

## Promote testing-devel changes

From the checkout for `fedora-coreos-config` (replace `upstream` below with
whichever remote name tracks `coreos/`):

- [ ] `git fetch upstream`
- [ ] `git checkout testing`
- [ ] `git reset --hard upstream/testing`
- [ ] `/path/to/fedora-coreos-releng-automation/scripts/promote-config.sh testing-devel`
- [ ] Sanity check promotion with `git show`
- [ ] Open PR against the `testing` branch on https://github.com/coreos/fedora-coreos-config
- [ ] Ideally have at least one other person check it and approve before merging

## Build

- [ ] Start a [pipeline build](https://jenkins-fedora-coreos.apps.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline/build?delay=0sec) (select `testing`, and fill in version number using the `N.YYYYMMDD.P` format, pending finalization of https://github.com/coreos/fedora-coreos-tracker/issues/81)
- [ ] Wait for the job to finish

## Sanity-check the build

Using the [the build browser](https://builds.coreos.fedoraproject.org/browser) for the `testing` stream:

- [ ] Verify that the parent commit and version match the previous `testing` release (in the future, we'll want to integrate this check in the release job)
- [ ] Run kola on AMI to sanity check it (this will be run automatically on all builds in the future):

```
kola -p aws run --aws-ami <ami-id> --aws-region us-east-1 --parallel 10 -b fcos
```

## Sign the CHECKSUMS file for releng

This is a stopgap until we do signing through fedora-messaging.

- [ ] Download the `CHECKSUMS` file locally:

```
aws s3 cp s3://fcos-builds/prod/streams/testing/builds/$VERSION/CHECKSUMS .
```

- [ ] **Confirm that the SHA256 of the `CHECKSUMS` file you just downloaded matches the one from the pipeline Jenkins log output**
- [ ] Sign it with your key: `gpg2 --output CHECKSUMS.sig --detach-sign CHECKSUMS`
- [ ] Push your signature to the bucket:

```
aws s3 cp --acl=public-read CHECKSUMS.sig s3://fcos-builds/prod/streams/testing/builds/$VERSION/CHECKSUMS.sig
```

# ⚠️ Release ⚠️

IMPORTANT: this is the point of no return here. Once the OSTree commit is
imported into the unified repo, any machine that manually runs `rpm-ostree
upgrade` will have the new update.

## Signing artifacts and importing OSTree commit

In the future, the signing part will be integrated in the build job and the OSTree commit import will be integrated in the release job.

- [ ] Open an issue on https://pagure.io/releng similar to https://pagure.io/releng/issue/8578 to ask for the artifacts to be signed and OSTree commit to be imported
- [ ] Wait for releng to process the request
- [ ] Verify that the image artifact signatures are present and have the right ACL, e.g.:

```
aws s3 ls --recursive s3://fcos-builds/prod/streams/testing/builds/$VERSION/
curl -I https://builds.coreos.fedoraproject.org/prod/streams/testing/builds/$VERSION/x86_64/fedora-coreos-$VERSION-qemu.qcow2.xz.sig
```

- [ ] Verify that the OSTree commit and its signature are present and valid by booting a VM at the previous release (e.g. `cosa run -d /path/to/previous.qcow2`) and verifying that `rpm-ostree upgrade` works and `rpm-ostree status` shows a valid signature.

## Run the release job

- [ ] Run the [release job](https://jenkins-fedora-coreos.apps.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline-release/build?delay=0sec), filling in for parameters `testing` and the new version ID
- [ ] Wait for job to finish

At this point, Cincinnati will see the new release on its next refresh and create a corresponding node in the graph without edges pointing to it yet.

## Refresh metadata (stream and updates)

From a checkout of this repo:

- [ ] Update stream metadata, by running:


```
fedora-coreos-stream-generator -releases=https://fcos-builds.s3.amazonaws.com/prod/streams/testing/releases.json  -output-file=streams/testing.json -pretty-print
```

- [ ] Update updates metadata, editing `updates/testing.json` and replacing the oldest rollout with your new one:
  - [ ] Set `version` field to the new version
  - [ ] Set `start_epoch` field to a future timestamp for the rollout start (e.g. `date -d <DATE> +%s`)
  - [ ] Set `start_percentage` field to `0.0`
  - [ ] Set `duration_minutes` field to a reasonable rollout window (e.g. `2880` for 48h)
  - [ ] Update the `last-modified` field to current time (e.g. `date -u -Is`)

- [ ] Commit the changes and open a PR against the repo.
- [ ] Wait for the PR to be approved.
- [ ] Once approved, merge it and push the content to S3:

```
aws s3 cp --acl public-read --cache-control 'max-age=60' streams/testing.json s3://fcos-builds/streams/testing.json

aws s3 cp --acl public-read --cache-control 'max-age=60' updates/testing.json s3://fcos-builds/updates/testing.json
```

- [ ] Verify the new version shows up on [the download page](https://getfedora.org/en/coreos/download/)
- [ ] Verify the incoming edges are showing up in the update graph:

```
curl -H 'Accept: application/json' 'https://updates.coreos.stg.fedoraproject.org/v1/graph?basearch=x86_64&stream=testing&rollout_wariness=0'
```

NOTE: In the future, most of these steps will be automated and a syncer will push the updated metadata to S3.
