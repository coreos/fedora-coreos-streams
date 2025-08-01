---
name: testing release checklist
about:  testing release checklist template
title: "testing: new release on <YYYY-MM-DD>"
labels: jira,kind/release
warning: |
    ⚠️ Template generated by https://github.com/coreos/repo-templates; do not edit downstream
---

First, verify that you meet all the [prerequisites](https://github.com/coreos/fedora-coreos-streams/blob/main/RELEASE.md#prerequisites)

Edit the issue title to include today's date. Once the pipeline spits out the new version ID, you can append it to the title e.g. `(31.20191117.2.0)`.

# Pre-release

## Promote testing-devel changes to testing

- [ ] Add the `ok-to-promote` label to the issue
- [ ] Review the promotion PR against the `testing` branch on https://github.com/coreos/fedora-coreos-config
- [ ] Once CI has passed, merge it

<details>
<summary>Manual alternative</summary>

Sometimes you need to run the process manually like if you need to add an extra commit to change something in `manifest.yaml`. The steps for this are:

- `git fetch upstream`
- `git checkout testing`
- `git reset --hard upstream/testing`
- `/path/to/fedora-coreos-releng-automation/scripts/promote-config.sh testing-devel`
- Open PR against the `testing` branch on https://github.com/coreos/fedora-coreos-config

</details>

## Build

- [ ] Start a [build job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/build/) (select `testing` and enable `EARLY_ARCH_JOBS`, leave all other defaults). This will automatically run multi-arch builds.
- Post links to the jobs as a comment to this issue
    - [ ] x86_64
    - [ ] aarch64 ([multi-arch build job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/build-arch/))
    - [ ] ppc64le ([multi-arch build job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/build-arch/))
    - [ ] s390x ([multi-arch build job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/build-arch/))
- Wait for the jobs to finish and succeed
    - [ ] x86_64
    - [ ] aarch64
    - [ ] ppc64le
    - [ ] s390x

## Sanity-check the build

Using the [the build browser for the `testing` stream](https://builds.coreos.fedoraproject.org/browser?stream=testing):

- Verify that the parent commit and version match the previous `testing` release (in the future, we'll want to integrate this check in the release job)
    - [ ] x86_64
    - [ ] aarch64
    - [ ] ppc64le
    - [ ] s390x
- Check [kola extended upgrade runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/blue/organizations/jenkins/kola-upgrade/activity/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
    - [ ] ppc64le
    - [ ] s390x
- Check [kola AWS runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-aws/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
- Check [kola OpenStack runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-openstack/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
- Check [kola Azure runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-azure/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
- Check [kola GCP runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-gcp/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64

# ⚠️ Release ⚠️

IMPORTANT: this is the point of no return here. Once the OSTree commit is
imported into the unified repo, any machine that manually runs `rpm-ostree
upgrade` will have the new update.

## Run the release job

- [ ] Run the [release job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/release/), filling in for parameters `testing` and the new version ID
- [ ] Post a link to the job as a comment to this issue
- [ ] Wait for job to finish

At this point, Cincinnati will see the new release on its next refresh and create a corresponding node in the graph without edges pointing to it yet.

## Refresh metadata (stream and updates)

- [ ] Wait for all releases that will be released simultaneously to reach this step in the process
- [ ] Go to the [rollout workflow](https://github.com/coreos/fedora-coreos-streams/actions/workflows/rollout.yml), click "Run workflow", and fill out the form

<details>
<summary>Rollout general guidelines</summary>

|Risk|Day of the week|Rollout Start Time|Time allocation|
| -------- | ------- | ------- | ------- |
|risky| Tuesday | 2PM UTC | 72H |
|common| Tuesday | 2PM UTC | 48H |
|rapid| Tuesday | 2PM UTC | 24H |

When setting a rollout start time ask "when would be the best time to react to
any errors or regressions from updates?". Commonly we select 2PM UTC so that the
rollout's start at 10am EST(±1 for daylight savings), but these can be fluid and
adjust after talking with the fedora-coreos IRC. Note, this is impacted by the
day of the week and holidays.

The later in the week the release gets held up due to unforeseen issues the more
likely the rollout time allocation will need to shrink or the release will need
to be deferred.
</details>

<details>
<summary>Manual alternative</summary>

- Make sure your `fedora-coreos-stream-generator` binary is up-to-date.

From a checkout of this repo:

- Update stream metadata, by running:

```
fedora-coreos-stream-generator -releases=https://fcos-builds.s3.amazonaws.com/prod/streams/testing/releases.json  -output-file=streams/testing.json -pretty-print
```

- Add a rollout.  For example, for a 48-hour rollout starting at 10 AM ET the same day, run:

```
./rollout.py add testing <version> "10 am ET today" 48
```

- Commit the changes and open a PR against the repo
</details>

- [ ] Verify that the expected OS versions appear in the PR on https://github.com/coreos/fedora-coreos-streams
- [ ] Post a link to the resulting PR as a comment to this issue
- [ ] Review and approve the PR, then wait for someone else to approve it also
- [ ] Once approved, merge it and verify that the [`sync-stream-metadata` job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/sync-stream-metadata/) syncs the contents to S3
- [ ] Verify the new version shows up on [the download page](https://getfedora.org/en/coreos/download?stream=testing)
- Verify the incoming edges are showing up in the update graph.
    - [ ] [x86_64](https://builds.coreos.fedoraproject.org/graph?stream=testing&basearch=x86_64)
    - [ ] [aarch64](https://builds.coreos.fedoraproject.org/graph?stream=testing&basearch=aarch64)
    - [ ] [ppc64le](https://builds.coreos.fedoraproject.org/graph?stream=testing&basearch=ppc64le)
    - [ ] [s390x](https://builds.coreos.fedoraproject.org/graph?stream=testing&basearch=s390x)

<details>
  <summary>Update graph manual check</summary>

```
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=x86_64&stream=testing&rollout_wariness=0'
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=aarch64&stream=testing&rollout_wariness=0'
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=ppc64le&stream=testing&rollout_wariness=0'
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=s390x&stream=testing&rollout_wariness=0'
```

</details>

NOTE: In the future, most of these steps will be automated.

## Housekeeping

- [ ] If one doesn't already exist, [open an issue](https://github.com/coreos/fedora-coreos-streams/issues/new?template=testing.md) in this repo for the next release in this stream. Use the approximate date of the release in the title.
- [ ] Issues opened via the previous link will automatically create a linked Jira card. Assign the GitHub issue and Jira card to the next person in the [rotation](https://hackmd.io/WCA8XqAoRvafnja01JG_YA).
