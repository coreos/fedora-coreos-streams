First, verify that you meet all the [prerequisites](https://github.com/coreos/fedora-coreos-streams/blob/main/release-prereqs.md)

Name this issue `testing: new release on YYYY-MM-DD` with today's date. Once the pipeline spits out the new version ID, you can append it to the title e.g. `(31.20191117.2.0)`.

# Pre-release

## Promote testing-devel changes to testing

- [ ] Add the `ok-to-promote` label to the issue
- [ ] Review the promotion PR opened by the bot against the `testing` branch on https://github.com/coreos/fedora-coreos-config
- [ ] Once CI has passed, merge it

## Build

- [ ] Start a [pipeline build](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline/build?delay=0sec) (select `testing`, leave all other defaults)
- [ ] Post a link to the jobs as a comment to this issue
    - [ ] x86_64
    - [ ] aarch64 ([multi-arch pipeline](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/multi-arch-pipeline/))
- [ ] Wait for the job to finish and succeed
    - [ ] x86_64
    - [ ] aarch64

## Sanity-check the build

Using the [the build browser for the `testing` stream](https://builds.coreos.fedoraproject.org/browser?stream=testing):

- [ ] Verify that the parent commit and version match the previous `testing` release (in the future, we'll want to integrate this check in the release job)
    - [ ] x86_64
    - [ ] aarch64
- [ ] Check [kola AWS runs](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/kola-aws/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
- [ ] Check [kola GCP run](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/kola-gcp/) to make sure it didn't fail
- [ ] Check [kola OpenStack run](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/kola-openstack/) to make sure it didn't fail

# ⚠️ Release ⚠️

IMPORTANT: this is the point of no return here. Once the OSTree commit is
imported into the unified repo, any machine that manually runs `rpm-ostree
upgrade` will have the new update.

## Run the release job

- [ ] Run the [release job](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/fedora-coreos/job/fedora-coreos-fedora-coreos-pipeline-release/build?delay=0sec), filling in for parameters `testing` and the new version ID
- [ ] Post a link to the job as a comment to this issue
- [ ] Wait for job to finish
- [ ] Verify that the OSTree commit and its signature are present and valid by booting a VM at the previous release (e.g. `cosa run --qemu-image /path/to/previous.qcow2`) and verifying that `rpm-ostree upgrade --bypass-driver` works and `rpm-ostree status` shows a valid signature.
    - [ ] x86_64
    - [ ] aarch64 (optional)
        - Can easily bring up instance from previous release in stream with:
            - `cosa kola spawn -b fcos --stream testing --arch=aarch64 -p aws --aws-credentials-file /srv/creds`

At this point, Cincinnati will see the new release on its next refresh and create a corresponding node in the graph without edges pointing to it yet.

## Refresh metadata (stream and updates)

From a checkout of this repo:

- [ ] Update stream metadata, by running:


```
fedora-coreos-stream-generator -releases=https://fcos-builds.s3.amazonaws.com/prod/streams/testing/releases.json  -output-file=streams/testing.json -pretty-print
```

- [ ] Add a rollout.  For a 48-hour rollout starting at 10 AM ET, run:

```
./rollout.py add testing <version> "10 am ET" 48
```

- [ ] Commit the changes and open a PR against the repo.  Paste the output of `make print-rollouts` into the PR description.
- [ ] Post a link to the PR as a comment to this issue
- [ ] Wait for the PR to be approved.
- [ ] Once approved, merge it and verify that the [`sync-stream-metadata` job](https://jenkins-fedora-coreos.apps.ocp.ci.centos.org/job/sync-stream-metadata/) syncs the contents to S3
- [ ] Verify the new version shows up on [the download page](https://getfedora.org/en/coreos/download?stream=testing)
- [ ] Verify the incoming edges are showing up in the update graph.
    - [ ] [x86_64](https://builds.coreos.fedoraproject.org/graph?stream=testing&basearch=x86_64)
    - [ ] [aarch64](https://builds.coreos.fedoraproject.org/graph?stream=testing&basearch=aarch64)

<details>
  <summary>Update graph manual check</summary>

```
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=x86_64&stream=testing&rollout_wariness=0'
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=aarch64&stream=testing&rollout_wariness=0'
```

</details>

NOTE: In the future, most of these steps will be automated.

## Housekeeping

- [ ] If one doesn't already exist, [open an issue](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release,jira&template=testing.md) in this repo for the next release in this stream. Use the approximate date of the release in the title.
- [ ] Issues opened via the previous link will automatically create a linked Jira card. Assign the GitHub issue and Jira card to the next person in the [rotation](https://hackmd.io/WCA8XqAoRvafnja01JG_YA).
