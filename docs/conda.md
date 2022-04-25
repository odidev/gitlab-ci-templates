# Conda templates

The Conda template file `conda.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: conda.yml
```

This file provides the following job templates:

- [`.conda:cache`](#.conda:cache)
- [`.conda:base`](#.conda:base)

## `.conda:cache` {: #.conda:cache }

!!! warning "Use `.conda:base` instead"
    The `.conda:base` template provides a much more useful conda
    job configuration, so unless you really know what you're doing,
    use that one instead of this one.

### Description {: #.conda:cache-description }

This template extends the variable settings with a default gitlab-ci
[cache](https://docs.gitlab.com/ee/ci/caching/) configuration to cache
the Conda package cache.

The cache is configured by the following environment variable:

| Name              | Default                               | Purpose                                  |
| ----------------- | ------------------------------------- | ---------------------------------------- |
| `CONDA_PKGS_DIRS` | `${CI_PROJECT_DIR}/.cache/conda/pkgs` | where to cache downloaded conda packages |

!!! note "If you change the cache location, change it in the `cache` YAML config as well"
    The `CONDA_PKGS_DIRS` variable tells `conda` where to download packages, but
    isn't used by gitlab-ci itself in the `cache` step.
    So, if you change the `CONDA_PKGS_DIRS` location, remember to update the
    [`cache:paths`](https://docs.gitlab.com/ee/ci/yaml/README.html#cache) gitlab-ci
    YAML setting as well.

### Example usage {: #.conda:cache-example }

```yaml
conda:
  extends:
    - .conda:cache
```

## `.conda:base` {: #.conda:base }

**Extends:** `.conda:cache`

### Description {: #.conda:base-description }

The base Conda job template extends the `.conda:cache` template
with some standard `before_script` commands to configure conda
properly for a non-interactive continuous integration job.

See the
[`conda.yml`](https://git.ligo.org/computing/gitlab-ci-templates/-/blob/master/conda.yml)
for a definite list of the commands that are run in the `before_script` block.

The job can be configured using the following variables:

| Name              | Default                               | Purpose                                                                                             |
| ----------------- | ------------------------------------- | ----------------------------------------                                                            |
| `CONDARC`         | `${CI_PROJECT_DIR}/.condarc`          | where to store the conda configuration                                                              |
| `CONDA_BLD_PATH`  | `${CI_PROJECT_DIR}/conda-bld`         | where to write conda-build outputs                                                                  |
| `CONDA_ENVS_PATH` | `${CI_PROJECT_DIR}/envs`              | where to create conda environments                                                                  |
| `CONDA_ROOT`      | `/opt/conda`                          | the root (prefix) of the conda installation (default only used if the `conda` command is not found) |

### Example usage {: #.conda:base-example }

```yaml
test:
  extends:
    - .conda:base
  before_script:
    # run the `before_script` from the template
    - !reference [".conda:base", before_script]
    # add my own `before_script` commands
    - conda create --name test python
    - conda list --name test
  script:
    - conda activate test
    - python -c "print('Hello world')"
```

!!! note "Quote the template job when using `!reference` tags"

    When using gitlab-ci's
    [`!reference` tags](https://docs.gitlab.com/ee/ci/yaml/README.html#reference-tags)
    it is important to quote the job name, since it contains a colon (`:`).

## `.conda:build` {: #.conda:build }

**Extends:** `.conda:base`

### Description {: #.conda:build-description }

This template provides an end-to-end configuration for
[`conda-build`](https://docs.conda.io/projects/conda-build/).
The workflow for this job is as follows:

1. convert the recipe into a conda-forge 'feedstock' using `conda-smithy`
2. run `conda {mamba}build` over the feedstock version of the recipe

The job can be configured using the following variables:

| Name                  | Default                    | Purpose                                           |
| --------------------- | -------------------------- | ------------------------------------------------- |
| `CONDA_RECIPE_DIR`    | `${CI_PROJECT_DIR}/conda/` | path of the conda recipe to use                   |
| `CONDA_BUILD_OPTIONS` | (empty)                    | extra options to pass to `conda build`            |
| `MAMBABUILD`          | `"false"`                  | if `"true"`, use the `mamba` solver when building |

### Example usage {: #.conda:build-example }

If your project repo contains a valid conda recipe in the 'conda/' directory,
you don't need to change anything:

```yaml
conda-build:
  extends:
    - .conda:build
```

If the recipe needs to be generated before it can be used, and you want to
mimic the production conda-forge feedstock build, you might want
something like this:

```yaml
conda-build:
  extends:
    - .conda:build
  script:
    # configure the project to generate the recipe properly
    - conda create -n configure autoconf automake libtool
    - conda activate configure
    - ./00boot
    - ./configure --enable-conda
    # build the conda package using the linux configuration
    - export CONDA_RECIPE_DIR="config/conda"
    - export CONDA_BUILD_OPTIONS="-m .ci_support/linux_64_.yaml"
    - !reference [".conda:build", script]
