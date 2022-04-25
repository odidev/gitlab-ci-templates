# CMake templates

The CMake template file `cmake.yml` can be included via

```yaml
include:
  - project: computing/gitlab-ci-templates
    file: cmake.yml
```

This file provides the following job templates:

- [`.cmake:build`](#.cmake:build)
- [`.cmake:pack`](#.cmake:pack)

## `.cmake:build` {: #.cmake:build }

### Description {: #.cmake:build-description }

This template configures a `script` section to execute a standard
configure/build/install/test CMake execution.

With default options, this job approximately runs the following:

```bash
cmake
cmake --build .
cmake --build . --target install
ctest
```

The job can be configured using the following variables:

| Name              | Default  | Purpose                                                  |
| ----------------- | -------- | -------------------------------------------------------- |
| `CMAKE_ARGS`      | (empty)  | extra arguments to pass to `cmake` in the configure step |
| `OUT_OF_TREE`     | `true`   | if `true`, run the build in separate build directory     |

!!! note "Conda-forge compilers set `CMAKE_ARGS` on their own"
    The compilers provided by conda-forge declare a set of `CMAKE_ARGS`
    automatically when the environment is activated, so if you want to
    customise things, you should probably _append_ to that variable, rather
    than set it outright.

### Example usage {: #.cmake:build-example }

```yaml
build:
  extends:
    - .conda:base
    - .cmake:build
  before_script:
    - conda create -n build cmake
```

## `.cmake:pack` {: #.cmake:pack }

### Description {: #.cmake:pack-description }

This template defines a `script` to build a source distribution (tarball)
using CMake.

With default options, this job approximately runs the following:

```bash
cmake
cmake --build . --target package_source
```

The job can be configured using the following variables:

| Name              | Default  | Purpose                                                  |
| ----------------- | -------- | -------------------------------------------------------- |
| `CMAKE_ARGS`      | (empty)  | extra arguments to pass to `cmake` in the configure step |
| `OUT_OF_TREE`     | `true`   | if `true`, run the build in separate build directory     |

!!! note "Conda-forge compilers set `CMAKE_ARGS` on their own"

### Example usage {: #.cmake:pack-example }

```yaml
test:
  extends:
    - .cmake:pack
```
