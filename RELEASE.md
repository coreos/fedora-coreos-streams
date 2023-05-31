# Releasing Fedora CoreOS

## Prerequisites

- Access to the [fedora-coreos-pipeline namespace](https://jenkins-fedora-coreos-pipeline.apps.ocp.fedoraproject.org/) in the Fedora OpenShift instance

## Checklist

The steps for doing a release are in the tickets created in the
[coreos/fedora-coreos-streams](https://github.com/coreos/fedora-coreos-streams/)
repository. An overview of the process can be seen in
[this video](https://dustymabe.fedorapeople.org/videos/2021-10-04_FCOS-Release-Process.mp4).

Those issues are generally created at the end of the previous release but if
you need to manually create one, you can use the following links:
- [stable](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release,jira&title=stable:%20new%20release%20on%20YYYY-MM-DD&template=stable.md)
- [testing](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release,jira&title=testing:%20new%20release%20on%20YYYY-MM-DD&template=testing.md)
- [next](https://github.com/coreos/fedora-coreos-streams/issues/new?labels=kind/release,jira&title=next:%20new%20release%20on%20YYYY-MM-DD&template=next.md)

## Pipeline failures & recovery

If a part of a pipeline run fails there may be options available that don't
require you to start from the very beginning.

- fedora-coreos-pipeline
    - if the top level pipeline fails you'll need to restart it likely
      with FORCE checked in the build parameters.
- multi-arch-pipeline
    - Assuming the top level pipeline passed you can start another multi-arch
      pipeline run with the exact same parameters as the original multi-arch
      pipeline run that was automatically kicked off by top level pipeline.
        - Open the failed job and look at the build parameters that were used.
        - Start a new job copy and pasting the exact build parameters.
- kola-{aws,gcp,openstack}
    - These jobs are just tests, that don't produce any artifacts.
    - If one of these jobs fail you can start a new job, but make
      sure to use the exact same build parameters as the original failed job.

## Release managers

FCOS release managers are not part of the normal release rotation but pay
attention to most releases and make sure they are progressing (PR reviews,
debugging issues). The current release managers are:

- Dusty Mabe
- Jonathan Lebon

## Release executors

Release executors perform scheduled biweekly releases. The current set of
release executors are (in alphabetical order, see below for the rotation):

- Adam Piasecki
- Clement Verna
- Michael Armijo
- Steven Presti

The build pipeline for releases will typically get started on Monday. Assuming
things go smoothly rollouts will start on Tuesday. If there are any conflicts
in the schedule we can easily swap a rotation with someone else.

## Standby release executors

Standby release executors perform any release outside of the normal biweekly
schedule. The current set of standby executors are (in alphabetical order,
see below for the rotation):

- Benjamin Gilbert
- Gursewak Singh
- Luca Bruno
- Renata Ravanelli
- Timothée Ravier

## Current release schedule

See the schedule in <https://hackmd.io/WCA8XqAoRvafnja01JG_YA>.
