# Importing the OSTree content into the unified repo

As part of the release process, we need to be able to get
the OSTree commit into the unified Fedora repo:

https://ostree.fedoraproject.org/

This will be done automatically via a dedicated
[importer](https://github.com/coreos/fedora-coreos-releng-automation/tree/main/coreos-ostree-importer)
in the future, though for now, we are required to file
issues like [this one](https://pagure.io/releng/issue/9182)
to get help from releng.

Releng then will roughly do the following from a machine
with the unified OSTree repo mounted in:

- download the tarball and the signature
- verify the tarball using signature
- untar the tarball into some temporary directory
- perform a pull-local into the unified repo:

```
ostree pull-local \
    --repo=/path/to/mounted/unified/repo \
    /path/to/extracted/tarball \
    $ref
```

- and finally update the summary file:

```
ostree summary --repo=/path/to/mounted/unified/repo --update
```
