# Code Quality templates

The Code Quality template file `codequality.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: codequality.yml
```

This file provides the following job templates:

- [`.codequality:combine`](#.codequality:combine)

## `.codequality:combine` {: #.codequality:combine }

### Description {: #.codequality:cache-description }

Combines multiple
[Code Quality](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html)
reports into a single report, to work around the GitLab limitation
that
[only a single Code Quality report can be displayed](https://docs.gitlab.com/ee/user/project/merge_requests/code_quality.html#only-a-single-code-quality-report-is-displayed-but-more-are-defined).

The following variables can be used to configure the build:

| Name               | Default    | Purpose                                    |
| ------------------ | ---------- | ------------------------------------------ |
| `CODEQUALITY_GLOB` | `"*.json"` | glob string to identify reports to combine |

### Example usage {: #.codequality:cache-example }

```yaml
include:
  - project: computing/gitlab-ci-templates
    file:
      - codequality.yml
      - python.yml

flake8:
  stage: analysis
  extends:
    - .python:flake8
  # upload flake8 report as artifact to be used by codequality
  artifacts:
    paths:
      - flake8.json

radon:
  stage: analysis
  extends:
    - .python:radon
  # upload radon report as artifact to be used by codequality
  artifacts:
    paths:
      - radon.json

codequality:
  stage: .post
  extends:
    - .codequality:combine
  needs:
    - flake8
    - radon
```
