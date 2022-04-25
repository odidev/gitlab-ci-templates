# Debian templates

The Debian template files `debian.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: debian.yml
```

This file provides the following job templates:

- [`.debian:cache`](#.debian:cache)
- [`.debian:base`](#.debian:base)
- [`.debian:dsc`](#.debian:dsc)
- [`.debian:deb`](#.debian:deb)
- [`.debian:lint`](#.debian:lint)

## `.debian:cache` {: #.debian:cache }

### Description {: #.debian:cache-description }

Configures caching of resources used by `apt`.

### Example usage {: #.debian:cache-example }

```yaml
deb:
  extends:
    - .debian:cache
```

## `.debian:base` {: #.debian:base }

**Extends:** `.debian:cache`

### Description {: #.debian:base-description }

The base Debian job template.
This template configures Apt caching, and executes a standard
`apt-get update` as part of the `before_script` stage.

### Example usage {: #.debian:base-example }

This example adds extra commands to the `before_script` stage while
using a
[`!reference` tag](https://docs.gitlab.com/ee/ci/yaml/README.html#reference-tags)
to execute all of the template commands as well:

```yaml
debian:
  extends:
    - .debian:base
  before_script:
    - !reference [".debian:base", before_script]
    - apt-get -y -q install python3
  script:
    - python3 --version
```

!!! note "Quote the template job name when using `!reference` tags"

    When using gitlab-ci's
    [`!reference` tags](https://docs.gitlab.com/ee/ci/yaml/README.html#reference-tags)
    it is important to quote the job name, since it contains a colon (`:`).

## `.debian:dsc` {: #.debian:dsc }

**Extends:** `.debian:base`

### Description {: #.debian:dsc-description }

This job builds a Debian source package (`.dsc`) from a tarball.
The `.dsc` file, along with the Debian `orig.tar` and `debian.tar` tarball
are uploaded as
[job artifacts](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

With default options, this job approximately runs the following:

```bash
tar -xf ${TARBALL}
dpkg-source <tar-directory>/
```

The job can be configured using the following variables:

| Name               | Default                      | Purpose                                                                       |
| ------------------ | ---------------------------- | ----------------------------------------------------------------------------- |
| `DSC_DEPENDENCIES` | (empty)                      | extra packages to `apt-get install` before building the Debian source package |
| `TARBALL`          | `${CI_PROJECT_NAME}-*.tar.*` | the source tarball to build from                                              |

### Example usage {: #.debian:dsc-example }

To build a Debian source package using a tarball from a previous stage:

```yaml
dsc:
  extends:
    - .debian:dsc
  needs:
    - tarball
  variables:
    TARBALL: myproject-*.tar.gz
```

## `.debian:deb` {: #.debian:deb }

**Extends:** `.debian:base`

### Description {: #.debian:deb-description }

This job takes in a Debian source package and associated files and
builds one or more binary Debian packages (`.deb`s).
The `.deb` packages, as well as any `.buildinfo` or `.changes` files
are uploaded as
[job artifacts](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

With default options, this job approximately runs the following:

```bash
dpkg-source --extract *.dsc src/
cd src
mk-build-deps --install --remove
dpkg-buildpackage -us -uc -b
```

The job can be configured using the following variables:

| Name  | Default                    | Purpose                             |
| ----- | -------------------------- | ----------------------------------- |
| `DSC` | `${CI_PROJECT_NAME}_*.dsc` | Debian source package to build from |

### Example usage {: #.debian:deb-example }

```yaml
deb:
  extends:
    - .debian:deb
  needs:
    - dsc
  variables:
    DSC: "myproject_*.dsc"
```

To build out Debian source and binary packages for a Python project in a
single job, one might consider something like this:

```yaml
deb:
  extends:
    # extend from the 'deb' template to upload
    # the binary packages as artifacts automatically
    - .debian:deb
  before_script:
    # run the `before_script` for the source package template
    - !reference [".debian:dsc", before_script]
    # run the `before_script` for the binary package template
    - !reference [".debian:deb", before_script]
  script:
    # generate a tarball
    - python setup.py sdist --dist-dir .
    # generate the source package
    - !reference [".debian:dsc", before_script]
    # generate the binary package
    - !reference [".debian:deb", before_script]
```

## `.debian:lint` {: #.debian:lint }

**Extends:** `.debian:base`

### Description {: #.debian:lint-description }

Runs [`lintian`](https://lintian.debian.org/) against one or more debian
package build outputs.

The job can be configured using the following variables:

| Name             | Default        | Purpose                      |
| ---------------- | -------------- | ---------------------------- |
| `LINTIAN_OPTIONS | `--color=auth` | options to pass to `lintian` |
| `LINTIAN_TARGET` | `"*.changes"`  | input files for `lintian`    |

### Example usage {: #.debian:lint-example }

```yaml
lintian:
  extends:
    - .debian:lint
  needs:
    # pull in packages from the `deb` job
    - deb
```
