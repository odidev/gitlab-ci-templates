# RHEL templates

The RHEL template file `rhel.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: rhel.yml
```

This file provides the following job templates

- [`.rhel:cache`](#.rhel:cache)
- [`.rhel:base`](#.rhel:base)
- [`.rhel:srpm`](#.rhel:srpm)
- [`.rhel:rpm`](#.rhel:rpm)
- [`.rhel:lint`](#.rhel:lint)

## `.rhel:cache` {: #.rhel:cache }

### Description {: #.rhel:cache-description }

Configures caching of resources used by `yum` (RHEL <= 7) or `dnf` (RHEL >= 8).

### Example usage {: #.rhel:cache-example }

```yaml
rhel:
  extends:
    - .rhel:cache
```

## `.rhel:base` {: #.rhel:base }

**Extends:** `.rhel:cache`

### Description {: #.rhel:base-description }

The base RHEL job template.
This template configures YUM/DNF caching, optionally disables
any repositories specified by the user, and enables
the CentOS 8
[PowerTools](https://wiki.centos.org/AdditionalResources/Repositories)
repository or [EPEL](https://fedoraproject.org/wiki/EPEL) as part of the
`before_script` stage.

For best results, the `before_script` of this template should always be
executed, either by not overwriting that section of the template, or via
by using a
[`!reference` tag](https://docs.gitlab.com/ee/ci/yaml/README.html#reference-tags).

The job can be configured using the following variables:

| Name            | Default | Purpose                                                              |
| --------------- | ------- | -------------------------------------------------------------------- |
| `DISABLE_REPOS` | (empty) | space-separated list of RPM repositories to disable                  |
| `EPEL`          | `false` | if `true`, configure EPEL package repo and install `epel-rpm-macros` |
| `POWERTOOLS`    | `false` | if `true`, enable the CentOS 8 PowerTools repo module                |

### Example usage {: #.rhel:base-example }

This example adds extra commands to the `before_script` stage while
using a
[`!reference` tag](https://docs.gitlab.com/ee/ci/yaml/README.html#reference-tags)
to execute all of the template commands as well:

```yaml
rhel:
  extends:
    - .rhel:base
  image: rockylinux:8
  before_script:
    - !reference [".rhel:base", before_script]
    - dnf -y -q install python3
  script:
    - python3 --version
```

!!! note "Quote the template job name when using `!reference` tags"

    When using gitlab-ci's
    [`!reference` tags](https://docs.gitlab.com/ee/ci/yaml/README.html#reference-tags)
    it is important to quote the job name, since it contains a colon (`:`).

## `.rhel:srpm` {: #.rhel:srpm }

**Extends:** `.rhel:base`

### Description {: #.rhel:srpm-description }

This job builds a source RPM (SRPM, `.src.rpm`) from a tarball.
The `.src.rpm` file is uploaded as a
[job artifact](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

With default options, this job approximately runs the following:

```bash
rpmbuild -ts ${TARBALL}
```

The job can be configured using the following variables:

| Name                | Default                      | Purpose                                                              |
| ------------------- | ---------------------------- | -------------------------------------------------------------------- |
| `EPEL`              | `false`                      | if `true`, configure EPEL package repo and install `epel-rpm-macros` |
| `POWERTOOLS`        | `false`                      | if `true`, enable the CentOS 8 PowerTools repo module                |
| `RPMBUILD_OPTIONS`  | (empty)                      | options to pass to `rpmbuild`                                        |
| `SRPM_DEPENDENCIES` | (empty)                      | extra packages to `yum install` before building the source RPM       |
| `TARBALL`           | `${CI_PROJECT_NAME}-*.tar.*` | the source tarball to build from                                     |

### Example usage {: #.rhel:srpm-example }

To build a source RPM using a tarball from a previous stage:

```yaml
srpm:
  extends:
    - .rhel:srpm
  needs:
    - tarball
  variables:
    TARBALL: myproject-*.tar.gz
```

## `.rhel:rpm` {: #.rhel:rpm }

**Extends:** `.rhel:base`

### Description {: #.rhel:rpm-description }

This job takes in a source RPM and builds one or more binary RPMs (`.rpm`s).
The `.rpm` packagese are uploaded as
[job artifacts](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

With default options, this job approximately runs the following:

```bash
yum-builddep ${SRPM}
rpmbuild --rebuild ${SRPM}
```

The job can be configured using the following variables:

| Name               | Default                        | Purpose                                                                                                            |
| ------------------ | ------------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| `EPEL`             | `false`                        | if `true`, configure EPEL package repo and install `epel-rpm-macros`                                               |
| `POWERTOOLS`       | `false`                        | if `true`, enable the CentOS 8 PowerTools repo module                                                              |
| `RPM_DEPENDENCIES` | `""` (empty)                   | extra packages to `yum install` before building the binary RPMs (build requirements do not need to be listed here) |
| `RPMBUILD_OPTIONS` | (empty)                        | options to pass to `rpmbuild`                                                                                      |
| `SRPM`             | `${CI_PROJECT_NAME}-*.src.rpm` | the source RPM to build from                                                                                       |

### Example usage {: #.rhel:rpm-example }

```yaml
rpm:
  extends:
    - .rhel:rpm
  needs:
    - srpm
  variables:
    SRPM: "myproject_*.dsc"
```

To build out source and binary RPMs for a Python project in a
single job, one might consider something like this:

```yaml
rpm:
  extends:
    # extend from the 'rpm' template to upload
    # the binary packages as artifacts automatically
    - .rhel:rpm
  before_script:
    # run the `before_script` for the source package template
    - !reference [".rhel:srpm", before_script]
    # run the `before_script` for the binary package template
    - !reference [".rhel:rpm", before_script]
  script:
    # generate a tarball
    - python setup.py sdist --dist-dir .
    # generate the source package
    - !reference [".rhel:srpm", before_script]
    # generate the binary package
    - !reference [".rhel:rpm", before_script]
```

## `.rhel:lint` {: #.rhel:lint }

**Extends:** `.rhel:base`

### Description {: #.rhel:lint-description }

Runs [`rpmlint`](https://github.com/rpm-software-management/rpmlint)
against one or more RPMs.

The job can be configured using the following variables:

| Name             | Default   | Purpose                      |
| ---------------- | --------- | ---------------------------- |
| `RPMLINT_OPTIONS | `--info`  | options to pass to `rpmlint` |
| `RPMS`           | `"*.rpm"` | input files for `rpmlint`    |

### Example usage {: #.rhel:lint-example }

```yaml
rpmlint:
  extends:
    - .rhel:lint
  needs:
    # pull in packages from the `rpm` job
    - rpm
```
