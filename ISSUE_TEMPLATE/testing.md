First, verify that you meet all the [prerequisites](https://github.com/coreos/fedora-coreos-streams/blob/master/release-prereqs.md)

Name this issue `testing: new release on YYYY-MM-DD` with today's date. Once the pipeline spits out the new version ID, you can append it to the title e.g. `(31.20191117.2.0)`.

# Pre-release

## Promote testing-devel changes to testing

From the checkout for `fedora-coreos-config` (replace `upstream` below with
whichever remote name tracks `coreos/`):

- [ ] `git fetch upstream`
- [ ] `git checkout testing`
- [ ] `git reset --hard upstream/testing`
- [ ] `/path/to/fedora-coreos-releng-automation/scripts/promote-config.sh testing-devel`
- [ ] Sanity check promotion with `git show`
- [ ] Open PR against the `testing` branch on https://github.com/coreos/fedora-coreos-config
- [ ] Post a link to the PR as a comment to this issue
- [ ] Ideally have at least one other person check it and approve
- [ ] Once CI has passed, merge it

## Build

- [ ] Start a [pipeline build](https://jenkins-fedora-coreos.apps.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline/build?delay=0sec) (select `testing`, leave all other defaults)
- [ ] Post a link to the job as a comment to this issue
- [ ] Wait for the job to finish

## Sanity-check the build

Using the [the build browser](https://builds.coreos.fedoraproject.org/browser) for the `testing` stream:

- [ ] Verify that the parent commit and version match the previous `testing` release (in the future, we'll want to integrate this check in the release job)
- [ ] Check [kola AWS run](https://jenkins-fedora-coreos.apps.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline-kola-aws) to make sure it didn't fail

# ⚠️ Release ⚠️

IMPORTANT: this is the point of no return here. Once the OSTree commit is
imported into the unified repo, any machine that manually runs `rpm-ostree
upgrade` will have the new update.

## Importing OSTree commit

In the future, the OSTree commit import will be integrated in the release job.

- [ ] Open an issue on https://pagure.io/releng to ask for the OSTree commit to be imported (include a URL to the .sig which should be alongside the tarfile in the bucket and signed by the primary Fedora key, also include the ref you'd like to import, i.e. `fedora/x86_64/coreos/testing`)
- [ ] Post a link to the issue as a comment in this issue
- [ ] Wait for releng to process the request
- [ ] Verify that the OSTree commit and its signature are present and valid by booting a VM at the previous release (e.g. `cosa run -d /path/to/previous.qcow2`) and verifying that `rpm-ostree upgrade` works and `rpm-ostree status` shows a valid signature.

## Run the release job

- [ ] Run the [release job](https://jenkins-fedora-coreos.apps.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline-release/build?delay=0sec), filling in for parameters `testing` and the new version ID
- [ ] Post a link to the job as a comment to this issue
- [ ] Wait for job to finish

At this point, Cincinnati will see the new release on its next refresh and create a corresponding node in the graph without edges pointing to it yet.

## Refresh metadata (stream and updates)

From a checkout of this repo:

- [ ] Update stream metadata, by running:


```
fedora-coreos-stream-generator -releases=https://fcos-builds.s3.amazonaws.com/prod/streams/testing/releases.json  -output-file=streams/testing.json -pretty-print
```

- Update the updates metadata, editing `updates/testing.json`:
  - [ ] Find the last-known-good release (whose `rollout` has a `start_percentage` of `1.0`) and set its `version` to the most recent completed rollout
  - [ ] Delete releases with completed rollouts
  - Add a new rollout:
    - [ ] Set `version` field to the new version
    - [ ] Set `start_epoch` field to a future timestamp for the rollout start (e.g. `date -d '2019/09/10 14:30UTC' +%s`)
    - [ ] Set `start_percentage` field to `0.0`
    - [ ] Set `duration_minutes` field to a reasonable rollout window (e.g. `2880` for 48h)
  - [ ] Update the `last-modified` field to current time (e.g. `date -u +%Y-%m-%dT%H:%M:%SZ`)

A reviewer can validate the `start_epoch` time by running `date -u -d @<EPOCH>`. An example of encoding and decoding in one step: `date -d '2019/09/10 14:30UTC' +%s | xargs -I{} date -u -d @{}`. 

- [ ] Commit the changes and open a PR against the repo.
- [ ] Post a link to the PR as a comment to this issue
- [ ] Wait for the PR to be approved.
- [ ] Once approved, merge it and push the content to S3:

```
aws s3 sync --acl public-read --cache-control 'max-age=60' --exclude '*' --include 'streams/*' --include 'updates/*' . s3://fcos-builds
```

- [ ] Verify the new version shows up on [the download page](https://getfedora.org/en/coreos/download/)
- [ ] Verify the incoming edges are showing up in the update graph:

```
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=x86_64&stream=testing&rollout_wariness=0'
```

NOTE: In the future, most of these steps will be automated and a syncer will push the updated metadata to S3.
