# MacPorts templates

The Macports template file `macports.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: macports.yml
```

This file provides the following job templates:

- [`.macports:base`](#.macports:base)

## `.macports:base` {: #.macports:base }

### Description {: #.macports:base-description }

The base MacPorts job template provides a default `before_script`
to install the latest release of MacPorts into the job's build directory,
providing a customisable MacPorts instance unique to that job.

The job can be configured using the following variables:

| Name              | Default                      | Purpose                                  |
| ----------------- | ---------------------------- | ---------------------------------------- |
| `MACPORTS_CCACHE` | `"false"`                    | if `"true"` install and configure ccache |
| `MACPORTS_PREFIX` | `${CI_PROJECT_DIR}/macports` | where to install MacPorts                |

### Example usage {: #.macports:base-example }

```yaml
macports:
  extends:
    - .macports:base
  script:
    - port install python310
    - python3.10 --version
```
