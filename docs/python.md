# Python templates

The Python template file `python.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: python.yml
```

This file provides the following job templates:

- [`.python:cache`](#.python:cache)
- [`.python:base`](#.python:base)
- [`.python:build`](#.python:build)
- [`.python:coverage`](#.python:coverage)
- [`.python:test`](#.python:test)
- [`.python:coverage-combine`](#.python:coverage-combine)
- [`.python:unittest`](#.python:unittest)
- [`.python:pytest`](#.python:pytest)
- [`.python:flake8`](#.python:flake8)
- [`.python:radon`](#.python:radon)
- [`.python:mkdocs`](#.python:mkdocs)
- [`.python:sphinx`](#.python:sphinx)
- [`.python:twine`](#.python:twine)

## `.python:cache` {: #.python:cache }

### Description {: #.python:cache-description }

Configures caching of the `pip` cache directory via the following
variable:

| Name            | Default                        | Purpose                                |
| --------------- | ------------------------------ | -------------------------------------- |
| `PIP_CACHE_DIR` | `${CI_PROJECT_DIR}/.cache/pip` | where to store downloaded pip packages |

### Example usage {: #.python:cache-example }

```yaml
pip:
  extends:
    - .python:cache
```

## `.python:base` {: #.python:base }

**Extends:** `.python:cache`

### Description {: #.python:base-description }

The base Python job template.
This template configures Pip caching, the `PYTHON` environment variable,
and a default docker image (`python`).

### Example usage {: #.python:base-example }

```yaml
python:
  extends:
    - .python:base
  before_script:
    - python -m pip install numpy
  script:
    - python -c "import numpy; print(numpy.sqrt((1, 2, 3, 4)))"

### Job templates

This file provides the following job templates:

#### `.python:base`

The base Python job template that just configures local `pip` caching and
a default `image: python`.

Example usage:

```yaml
test:
  extends:
    - .python:base
  before_script:
    - python -m pip install pytest
  script:
    - python -m pytest
```

## `.python:build` {: #.python:build }

**Extends:** `.python:base`

### Description {: #.python:build-description }

The `.python:build` job template provides an end-to-end
distribution build configuration, effectively running the
following command to build a project:

```bash
python -m build --sdist --wheel .
```

The outputs are uploaded as
[job artifacts](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

The following variables can be used to configure the build:

| Name             | Default  | Purpose                                                                                                                  |
| ---------------- | -------- | ------------------------------------------------------------------------------------------------------------------------ |
| `PYTHON`         | `python` | the path of the python interpreter to use                                                                                |
| `BUILD_REQUIRES` | (empty)  | extra packages to `pip install` before running `python -m build` (use `"-r <file>"` to install from a requirements file) |
| `BUILD_OPTIONS`  | (empty)  | extra options to pass to `python -m build`                                                                               |
| `SRCDIR`         | `"."`    | path of source directory for `python -m build`                                                                           |
| `SDIST`          | `true`   | if `true`, run `sdist` to generate a tarball, otherwise don't                                                            |
| `WHEEL`          | `true`   | if `true`, run `wheel` to generate a wheel, otherwise don't                                                              |

### Example usage {: #.python:build-example }

The default options are most likely enough for your project:

```yaml
build:
  extends:
    - .python:build
```

To disable the `wheel` build:

```yaml
tarball:
  extends:
    - .python:build
  variables:
    WHEEL: "false"
```

## `.python:coverage` {: #.python:coverage }

**Extends:** `.python:base`

### Description {: #.python:coverage-description }

A base template for Python test jobs that use
[Coverage.py](https://coverage.readthedocs.io/) to measure code coverage.
The template just configures printing and uploading of coverage reports
from a test suite run.

For most projects it would probably make more sense to use
one of the harness-specific templates for `unittest` or `pytest` below.

### Example usage {: #.python:coverage-example }

```yaml
test:
  extends:
    - .python:coverage
  before_script:
    # install coverage
    - python -m pip install coverage
  script:
    - python -m coverage run --source mylib ./script.py
```

## `.python:test` {: #.python:test }

!!! warning "`.python:test` is deprecated, use `.python:coverage`

    The `.python:test` template was renamed `.python:coverage` and may
    be recreated in a different format in the future, please update your
    workflow to use `.python:coverage`.

## `.python:coverage-combine` {: #.python:coverage-combine }

**Extends:** `.python:combine`

### Description {: #.python:coverage-combine-description }

This job executes `python -m coverage combine` to combine coverage
reports from multiple jobs.
The combined report is then converted to XML and uploaded as a
[`coverage_report`](https://docs.gitlab.com/ee/ci/yaml/artifacts_reports.html#artifactsreportscoverage_report)
artifact.

The job can be configured using the following variables:

| Name            | Default      | Purpose                                                |
| --------------- | ------------ | ------------------------------------------------------ |
| `COVERAGE_GLOB` | `.coverage*` | The glob path to use to find individual coverage files |

!!! info "Source files need to exist"

    `python -m coverage combine` requires the source files referenced in the
    coverages files to exist for the combining to work properly.
    You may need to configure
    [`[paths]`](https://coverage.readthedocs.io/en/stable/config.html#paths)
    in your Coverage.py configuration to get this to work properly.

### Example usage {: #.python:coverage-combine-example }

```yaml
.test:
  extends:
    - .python:coverage
  script:
    - python -m coverage run --source mylib ./script.py
  # disable coverage total report from individual jobs
  coverage: null
  artifacts:
    paths:
      # upload all .coverage files as artifacts
      - .coverage*

test:3.9
  extends:
    - .test
  image: python:3.9

test:3.10
  extends:
    - .test
  image: python:3.10

coverage:
  extends:
    - .python:coverage-combine
```

## `.python:unittest` {: #.python:unittest }

**Extends:** `.python:coverage`

### Description {: #.python:unittest-description }

This job runs a [`unittest`](https://docs.python.org/library/unittest.html)
suite for a Python project.

With default options, this job approximately runs the following:

```bash
pip install .
python -m unittest discover
```

The job can be configured using the following variables:

| Name               | Default                   | Purpose                                                                                                                |
| ------------------ | ------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `PYTHON`           | `python`                  | the path of the python interpreter to use                                                                              |
| `PIP_OPTIONS`      | (empty)                   | options to pass to `pip install`                                                                                       |
| `TESTS_REQUIRE`    | (empty)                   | extra packages to `pip install` before running `unittest` (use `"-r <file>"` to install from a requirements file)      |
| `INSTALL_TARGET`   | `"."`                     | the path to pass to `pip install` to install the project                                                               |
| `UNITTEST_OPTIONS` | `"discover"`              | extra options to pass to `python -m unittest`                                                                          |
| `COVERAGE_TARGET`  | `${CI_PROJECT_NAME//-/_}` | the path to pass to `coverage --source={}` to measure coverage                                                         |

### Example usage {: #.python:unittest-example }

To run `unittest` after installing the `mylib-*.tar.gz` file created by the `tarball` job:

```yaml
test:
  extends:
    - .python:unittest
  needs:
    - tarball
  variables:
    GIT_STRATEGY: none
    INSTALL_TARGET: "mylib-*.tar.gz"
    COVERAGE_TARGET: "mylib"
```

## `.python:pytest` {: #.python:pytest }

**Extends:** `.python:coverage`

### Description {: #.python:pytest-description }

This job installs a project and runs `pytest`, uploading JUnit XML test
and coverage reports.

With default options, this job approximately runs the following script:

```bash
pip install .
pip install pytest
pytest --cov=${CI_PROJECT_NAME}
```

The job can be configured using the following variables:

| Name              | Default                   | Purpose                                                                                                           |
| ----------------- | ------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `PYTHON`          | `python`                  | the path of the python interpreter to use                                                                         |
| `PIP_OPTIONS`     | (empty)                   | options to pass to `pip install`                                                                                  |
| `TESTS_REQUIRE`   | (empty)                   | extra packages to `pip install` before running `pytest` (use `"-r <file>"` to install from a requirements file)   |
| `INSTALL_TARGET`  | `"."`                     | the path to pass to `pip install` to install the project                                                          |
| `PYTEST_OPTIONS`  | (empty)                   | extra options to pass to pytest                                                                                   |
| `COVERAGE_TARGET` | `${CI_PROJECT_NAME//-/_}` | the path to pass to `pytest --cov={}` to measure coverage                                                         |

### Example usage {: #.python:pytest-example }

For projects that include pytest configurations in the repository
and don't need any plugins, you can just use the template without
any additions:

```yaml
test:
  extends:
    - .python:pytest
```

To configure the template to install from a tarball, then run
tests using `pytest-xdist` with coverage measured from the
installed library:

```yaml
test:
  extends:
    - .python:pytest
  variables:
    GIT_STRATEGY: none
    TESTS_REQUIRE: "pytest-xdist"
    INSTALL_TARGET: "myproject-*.tar.*"
    COVERAGE_TARGET: "my_library"
    PYTEST_OPTIONS: "--pyargs my_library"
```

In this instance the job effectively runs this script:

```bash
pip install myproject-*.tar.*
pip install pytest pytest-xdist
pytest --cov=my_library --pyargs my_library
```

## `.python:mkdocs` {: #.python:mkdocs }

### Description {: #.python:mkdocs-description }

This job runs `mkdocs build`, uploading the output `site/` directory as a
[job artifact](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

With default options, this job approximately runs the following script:

```bash
pip install mkdocs
mkdocs build .
```

The template can be configured using the following variables:

| Name             | Default    | Purpose                                                                                                         |
| ---------------- | ---------- | --------------------------------------------------------------------------------------------------------------- |
| `PYTHON`         | `python`   | the path of the python interpreter to use                                                                       |
| `REQUIREMENTS`   | (empty)    | extra packages to `pip install` before running `mkdocs` (use `"-r <file>"` to install from a requirements file) |
| `MKDOCS_OPTIONS` | (empty)    | extra options to pass to `mkdocs`                                                                               |

### Example usage {: #.python:mkdocs-example }

(Including gitlab `pages` job):

```yaml
mkdocs:
  extends:
    - .python:mkdocs
  variables:
    REQUIREMENTS: "-r requirements.txt"

pages:
  needs: [mkdocs]
  script:
    - mv -v site public
  artifacts:
    paths:
      - public
```

## `.python:sphinx` {: #.python:sphinx }

**Extends:** `.python:base`

### Description {: #.python:sphinx-description }

This job runs `sphinx`, uploading the HTML output directory `html/` as a
[job artifact](https://docs.gitlab.com/ee/ci/pipelines/job_artifacts.html).

With default options, this job approximately runs the following script:

```bash
cd docs
make html
```

However, if `docs/Makefile` isn't found, the following is run:

```bash
cd docs
sphinx-build -b html . ..
```

The template can be configured using the following variables:

| Name             | Default  | Purpose                                                                                                         |
| ---------------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| `BUILDER`        | `"html"` | the sphinx builder to use                                                                                       |
| `PYTHON`         | `python` | the path of the python interpreter to use                                                                       |
| `REQUIREMENTS`   | (empty)  | extra packages to `pip install` before running `sphinx` (use `"-r <file>"` to install from a requirements file) |
| `SPHINX_OPTIONS` | (empty)  | extra options to pass to `sphinx`                                                                               |
| `SOURCEDIR`      | `"docs"` | directory containing documentation sources                                                                      |

### Example usage {: #.python:sphinx-example }

Example usage (including gitlab `pages` job):

```yaml
sphinx:
  extends:
    - .python:sphinx
  variables:
    REQUIREMENTS: "-r docs/requirements.txt"

pages:
  needs: [sphinx]
  script:
    - mv -v html public
  artifacts:
    paths:
      - public
```

## `.python:flake8` {: #.python:flake8 }

**Extends:** `.python:base`

### Description {: #.python:flake8-description }

This template runs the `flake8` linter over the project source,
uploading a code quality report.

With default options, this job approximately runs the following script:

```bash
pip install flake8
flake8
```

The template can be configured using the following variables:

| Name             | Default  | Purpose                                                 |
| ---------------- | -------- | ------------------------------------------------------- |
| `PYTHON`         | `python` | the path of the python interpreter to use               |
| `REQUIREMENTS`   | (empty)  | other packages to `pip install` before running `flake8` |
| `FLAKE8_TARGET`  | `"."`    | the path over which to run `flake8`                     |
| `FLAKE8_OPTIONS` | (empty)  | extra options to pass to `flake8`                       |

### Example usage {: #.python:flake8-example }

```yaml
lint:
  extends:
    - .python:flake8
```

## `.python:radon` {: #.python:radon }

**Extends:** `.python:base`

### Description {: #.python:radon-description }

This template runs the [Radon](https://radon.readthedocs.io/) code
analysis tool over the project source, uploading a code quality report.

With default options, this job approximately runs the following script:

```bash
pip install radon
radon cc .
```

The template can be configured using the following variables:

| Name            | Default  | Purpose                                                |
| --------------- | -------- | ------------------------------------------------------ |
| `PYTHON`        | `python` | the path of the python interpreter to use              |
| `REQUIREMENTS`  | (empty)  | other packages to `pip install` before running `radon` |
| `radon_TARGET`  | `"."`    | the path over which to run `radon`                     |
| `radon_OPTIONS` | (empty)  | extra options to pass to `radon`                       |

### Example usage {: #.python:radon-example }

```yaml
cc:
  extends:
    - .python:radon
```

## `.python:twine` {: #.python:twine }

**Extends:** `.python:base`

### Description {: #.python:twine }

This template runs `twine` to upload packages to the Python Package Index
(PyPI).

With default options, this job approximately runs the following script:

```bash
pip install twine
twine upload *.tar.* *.whl
```

The template can be configured using the following variables:

| Name                  | Default     | Purpose                                                                  |
| --------------------- | ----------- | ------------------------------------------------------------------------ |
| `PYTHON`              | `python`    | the path of the python interpreter to use                                |
| `PIP_OPTIONS`         | (empty)     | options to pass to `pip install`                                         |
| `TWINE_USERNAME`      | `__token__` | PyPI username                                                            |
| `TWINE_PASSWORD`      | (empty)     | PyPI password (set this using a protected [group or protected variable]) |

[group or protected variable]: https://git.ligo.org/help/ci/variables/index.md#add-a-cicd-variable-to-a-project

### Example usage {: #.python:twine }

```yaml
upload:
  extends:
    - .python:twine
```
