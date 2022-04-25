# Docker templates

The Docker template file `docker.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: docker.yml
```

This file provides the following job templates:

- [`.docker:build`](#.docker:build)
- [`.docker:push`](#.docker:push)
- [`.docker:push:docker_io`](#.docker:push:docker_io)
- [`.docker:push:quay_io`](#.docker:push:quay_io)

## `.docker:build` {: #.docker:build }

### Description {: #.docker:build-description }

This template provides a basic `docker build` framework.

With default options, this job approximately runs the following:

```bash
# build
docker build .
# push to containers.ligo.org
docker login ... ${CI_REGISTRY}
docker push
```

The job can be configured using the following variables:

| Name                    | Default                        | Purpose                                                              |
| ----------------------- | ------------------------------ | -------------------------------------------------------------------- |
| `BUILD_PATH`            | `${CI_PROJECT_DIR}`            | directory to build                                                   |
| `DOCKERFILE`            | `${CI_PROJECT_DIR}/Dockerfile` | `Dockerfile` to parse                                                |
| `PUSH_TO_CI_REGISTRY`   | `"true"`                       | if `"true"`, `docker push` to `${CI_REGISTRY}` (containers.ligo.org) |
| `CI_REGISTRY_TAG`       | `${CI_COMMIT_REF_SLUG}`        | tag to append to image name for `${CI_REGISTRY}`                     |

!!! info "This is subtly different to gitlab's built-in `Build.gitlab-ci.yml` template"

    This template is subtly different to gitlab's built-in
    [`Build.gitlab-ci.yml`](https://gitlab.com/gitlab-org/gitlab/-/blob/master/lib/gitlab/ci/templates/Jobs/Build.gitlab-ci.yml)
    template, in that this template doesn't attempt to push a `latest` tag.

### Example usage {: #.docker:build-example }

This template is used to build the
[`igwn/base`](https://hub.docker.com/r/igwn/base)
docker images as follows:

```yaml
docker:build:
  extends:
    - .docker:build
  variables:
    # tag using the branch name
    CI_REGISTRY_TAG: "${CI_COMMIT_REF_SLUG}"
```

## `.docker:push` {: #.docker:push }

### Description {: #.docker:push-description }

This template provides a basic `docker push` framework.

With default options, this job approximately runs the following:

```bash
docker pull ${PULL_IMAGE}
docker tag ${PULL_IMAGE} ${REGISTRY}/${PUSH_IMAGE}
docker push ${REGISTRY}/${PUSH_IMAGE}
```

The job can be configured using the following variables:

| Name                  | Default                                  | Purpose                                             |
| --------------------- | ---------------------------------------- | --------------------------------------------------- |
| `PULL_IMAGE`          | `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA`      | the image to `pull`                                 |
| `PUSH_IMAGE`          | `$CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG` | the image (including tag) to `push`                 |
| `REGISTRY`            | `$CI_REGISTRY`                           | the registry to `push` to                           |
| `REGISTRY_USER_NAME`  | `gitlab-ci-token`                        | the user name to use when authenticating            |
| `REGISTRY_USER_TOKEN` | `$CI_JOB_TOKEN`                          | the user token/password to user when authenticating |

### Example usage {: #.docker:build-example }

To-retag the most recently pushed image as `latest` when pushing to the
default branch of the repository:

```yaml
docker:push:
  extends:
    - .docker:push
  needs:
    - docker:build
  variables:
    PUSH_IMAGE: "$CI_REGISTRY_IMAGE:latest"
  rules:
    - if: '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
```

## `.docker:push:docker_io` {: #.docker:push:docker_io }

### Description {: #.docker:push:docker_io-description }

This template provides a variant of [`.docker:push`](#.docker:push)
tuned to push to the docker registry at docker.io.

!!! tip "Pushing to docker.io requires credentials"

    This template requires the following additional variables to be defined,
    ideally using
    [project variables](https://docs.gitlab.com/ee/ci/variables/#add-a-cicd-variable-to-a-project):

    | Name               | Purpose                                                                                          |
    | ------------------ | ------------------------------------------------------------------------------------------------ |
    | `DOCKER_HUB_USER`  | The username to user when authenticating to <https://hub.docker.com> with `docker login`         |
    | `DOCKER_HUB_TOKEN` | The [access token](https://docs.docker.com/docker-hub/access-tokens/) to use when authenticating |

## `.docker:push:quay_io` {: #.docker:push:quay_io }

### Description {: #.docker:push:quay_io-description }

This template provides a variant of [`.docker:push`](#.docker:push)
tuned to push to the docker registry at [quay.io](https://quay.io/).

!!! tip "Pushing to quay.io requires credentials"

    This template requires the following additional variables to be defined,
    ideally using
    [project variables](https://docs.gitlab.com/ee/ci/variables/#add-a-cicd-variable-to-a-project):

    | Name            | Purpose                                                                                                    |
    | --------------- | ---------------------------------------------------------------------------------------------------------- |
    | `QUAY_USER`  | The username to user when authenticating to <https://quay.io> with `docker login`                          |
    | `QUAY_TOKEN` | The robot account [password](https://docs.quay.io/glossary/robot-accounts.html) to use when authenticating |
