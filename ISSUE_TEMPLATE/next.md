First, verify that you meet all the [prerequisites](https://github.com/coreos/fedora-coreos-streams/blob/main/RELEASE.md#prerequisites)

Edit the issue title to include today's date. Once the pipeline spits out the new version ID, you can append it to the title e.g. `(31.20191117.2.0)`.

# Pre-release

## Promote next-devel changes to next

- [ ] Add the `ok-to-promote` label to the issue
- [ ] Review the promotion PR against the `next` branch on https://github.com/coreos/fedora-coreos-config
- [ ] Once CI has passed, merge it

<details>
<summary>Manual alternative</summary>

Sometimes you need to run the process manually like if you need to add an extra commit to change something in `manifest.yaml`. The steps for this are:

- `git fetch upstream`
- `git checkout next`
- `git reset --hard upstream/next`
- `/path/to/fedora-coreos-releng-automation/scripts/promote-config.sh next-devel`
- Open PR against the `next` branch on https://github.com/coreos/fedora-coreos-config

</details>

## Build

- [ ] Start a [build job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/build/) (select `next`, leave all other defaults). This will automatically run multi-arch builds.
- Post links to the jobs as a comment to this issue
    - [ ] x86_64
    - [ ] aarch64 ([multi-arch build job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/build-arch/))
- Wait for the jobs to finish and succeed
    - [ ] x86_64
    - [ ] aarch64

## Sanity-check the build

Using the [the build browser for the `next` stream](https://builds.coreos.fedoraproject.org/browser?stream=next):

- Verify that the parent commit and version match the previous `next` release (in the future, we'll want to integrate this check in the release job)
    - [ ] x86_64
    - [ ] aarch64
- Check [kola AWS runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-aws/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
- Check [kola OpenStack runs](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-openstack/) to make sure they didn't fail
    - [ ] x86_64
    - [ ] aarch64
- [ ] Check [kola Azure run](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-azure/) to make sure it didn't fail
- [ ] Check [kola GCP run](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/kola-gcp/) to make sure it didn't fail

# ⚠️ Release ⚠️

IMPORTANT: this is the point of no return here. Once the OSTree commit is
imported into the unified repo, any machine that manually runs `rpm-ostree
upgrade` will have the new update.

## Run the release job

- [ ] Run the [release job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/release/), filling in for parameters `next` and the new version ID
- [ ] Post a link to the job as a comment to this issue
- [ ] Wait for job to finish

At this point, Cincinnati will see the new release on its next refresh and create a corresponding node in the graph without edges pointing to it yet.

## Refresh metadata (stream and updates)

- [ ] Wait for all releases that will be released simultaneously to reach this step in the process
- [ ] Go to the [rollout workflow](https://github.com/coreos/fedora-coreos-streams/actions/workflows/rollout.yml), click "Run workflow", and fill out the form

<details>
<summary>Manual alternative</summary>

- Make sure your `fedora-coreos-stream-generator` binary is up-to-date.

From a checkout of this repo:

- Update stream metadata, by running:

```
fedora-coreos-stream-generator -releases=https://fcos-builds.s3.amazonaws.com/prod/streams/next/releases.json  -output-file=streams/next.json -pretty-print
```

- Add a rollout.  For example, for a 48-hour rollout starting at 10 AM ET the same day, run:

```
./rollout.py add next <version> "10 am ET today" 48
```

- Commit the changes and open a PR against the repo
</details>

- [ ] Verify that the PR contains the expected OS versions
- [ ] Post a link to the resulting PR as a comment to this issue
- [ ] Review and approve the PR, then wait for someone else to approve it also
- [ ] Once approved, merge it and verify that the [`sync-stream-metadata` job](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/job/sync-stream-metadata/) syncs the contents to S3
- [ ] Verify the new version shows up on [the download page](https://getfedora.org/en/coreos/download?stream=next)
- Verify the incoming edges are showing up in the update graph.
    - [ ] [x86_64](https://builds.coreos.fedoraproject.org/graph?stream=next&basearch=x86_64)
    - [ ] [aarch64](https://builds.coreos.fedoraproject.org/graph?stream=next&basearch=aarch64)

<details>
  <summary>Update graph manual check</summary>

```
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=x86_64&stream=next&rollout_wariness=0'
curl -H 'Accept: application/json' 'https://updates.coreos.fedoraproject.org/v1/graph?basearch=aarch64&stream=next&rollout_wariness=0'
```

</details>

NOTE: In the future, most of these steps will be automated.

## Housekeeping

- [ ] If one doesn't already exist, [open an issue](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release,jira&template=next.md) in this repo for the next release in this stream. Use the approximate date of the release in the title.
- [ ] Issues opened via the previous link will automatically create a linked Jira card. Assign the GitHub issue and Jira card to the next person in the [rotation](https://hackmd.io/WCA8XqAoRvafnja01JG_YA).
