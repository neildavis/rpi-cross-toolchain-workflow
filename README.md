# RPi Cross Toolchains & Workflows #

## Introduction ##

This repository hosts tools and [GitHub Actions](https://docs.github.com/en/actions)
[workflows](https://docs.github.com/en/actions/writing-workflows) to aid automated (CI/CD)
building of ARM based software targeted at the Raspberry Pi series of SBCs using GitHub's x86_64 Linux 
[hosted runners](https://docs.github.com/en/actions/using-github-hosted-runners/using-github-hosted-runners)

## Overview ##

To 'cross build' for an ARM based system like Raspberry Pi on a x86_64 system like a Linux PC
or GitHub's
[`Ubuntu` hosted runners](https://docs.github.com/en/actions/using-github-hosted-runners/using-github-hosted-runners/about-github-hosted-runners#standard-github-hosted-runners-for-public-repositories)
requires two main components:

1. A '*cross toolchain*' - consisting of the tools (compiler,.assembler, linker etc) to build for the ***target*** (ARM) OS,
but run on the ***host*** (x86_64) OS. These toolchains are commonly created using
[`crosstool-ng`](https://crosstool-ng.github.io/)
2. A '*sysroot*' - consisting of the set of dependent headers & libraries pre-built for the ***target*** (ARM) OS, but residing on the ***host*** (x86_64) OS. This is commonly achieved by use of tools like
[`rsync`](https://en.wikipedia.org/wiki/Rsync) to copy the base file system from a target device to the build host.
Unfortunately this is awkward to setup in a *generalized* way (supporting *arbitrary dependencies*) in cloud based CI/CD
systems like GitHub Actions.

This repo supports both of the above requirements in different ways:

### 1. Cross Toolchains (a.k.a 'x-tools') ###

This repo hosts `crosstool-ng` config files suitable for development for Raspberry Pi devices running
the ['bookworm'](https://www.raspberrypi.com/news/bookworm-the-new-version-of-raspberry-pi-os/) version
of Raspberry Pi OS in both 32-bit (`armhf`) and 64-bit (`arm64`/`aarch64`) flavours.

In addition, a [GitHub Actions Workflow](.github/workflows/rpi-x-tools.yml) is employed to build the
toolchains which are then made available for download as
[releases on the project page](https://github.com/neildavis/rpi-cross-toolchain-workflow/releases)

These toolchains are useful in both standard desktop and cloud hosted CI/CD workflows.

The toolchains are conventionally stored in a directory named after the 'tuple' in a
root `x-tools` directory from the the user's `$HOME` directory. e.g. 

* `$HOME/x-tools/armv6-rpi-linux-gnueabihf` - for the 32-bit (`armhf`) toolchain
* `$HOME/x-tools/aarch64-rpi3-linux-gnu` - for the 64-bit (`arm64`/`aarch64`) toolchain

so it it is recommended that the tarballs are extracted directly to `$HOME/`

#### CMake Support ###

Each toolchain provides
[cmake-toolchains](https://cmake.org/cmake/help/latest/manual/cmake-toolchains.7.html)
files for use with the
[`-DCMAKE_TOOLCHAIN_FILE`](https://cmake.org/cmake/help/latest/variable/CMAKE_TOOLCHAIN_FILE.html) variable in the `cmake` subdir. These toolchain files assume the conventional paths described above.


### 2. Sysroots ###

A sysroot for Raspberry Pi OS can be built using [`debootstrap`](https://wiki.debian.org/Debootstrap).
[Pieter P](https://tttapa.github.io) has written an excellent
[guide](https://tttapa.github.io/Pages/Raspberry-Pi/C++-Development-RPiOS/index.html)
for this.

This repo wraps that process in a *parameterized* GitHub Actions
[reusable workflow](https://docs.github.com/en/actions/sharing-automations/reusing-workflows)
that can build the sysroot, including any specified `apt` package dependencies.

Since the sysroots are parameterized with arbitrary dependencies, it doesn't make sense to make
them available for download as releases. Instead the reusable workflow makes use of GitHub Actions
[caching](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/caching-dependencies-to-speed-up-workflows)
and provides the 'cache key' as an output to allow jobs in the *calling* workflow to restore the
sysroot.

## Usage ##

An example of how to use the *`x-tools`* toolchains and the `sysroot` reusable workflow to
cross-build a project containing a shared library and executable can be found in my
[lib_tm1637_rpi](https://github.com/neildavis/lib_tm1637_rpi) project by examining the
[workflow](https://github.com/neildavis/lib_tm1637_rpi/blob/main/.github/workflows/lib_tm1637_rpi.yml):

### Calling (e.g.)

This example snippet from the workflow linked above uses a
[matrix strategy](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow)
to build both 32-bit (`armhf`) and 64-bit (`arm64`) versions of the sysroots in the same workflow.

Note how we add the
[`libboost-program-options-dev`](https://packages.debian.org/sid/libboost-program-options-dev)
package to the sysroot. Additional packages can be specified separated by spaces if required.

```yaml
jobs:
  # ...
  linux-arm-sysroots:
    name: Build sysroots for ARM Linux
    strategy:
      matrix:
        arch: [armhf, arm64]
    uses: neildavis/rpi-cross-toolchain-workflow/.github/workflows/rpi-arm-sysroots.yml@v1
    with:
      deb_release: bookworm
      arch: ${{ matrix.arch }}
      apt_pkgs: "libboost-program-options-dev"
  # ...
```

These sysroots can then be used in a later dependent job including use of the `x-tools` releases
to cross-build the final artifacts (binary libraries & executables.):

Note: This example project is built using the cmake toolchains support.

```yaml
jobs:
  # ...
  lib_tm1637_rpi_build:
    name: Build & package libTM1637 binaries
    needs: [linux-arm-sysroots]
    runs-on: ubuntu-24.04
    strategy:
        matrix:
          tuple: [armv6-rpi-linux-gnueabihf, aarch64-rpi3-linux-gnu]
          include:
            - tuple: armv6-rpi-linux-gnueabihf
              arch: armhf
            - tuple: aarch64-rpi3-linux-gnu
              arch: arm64
    steps:
      # ...
      - name: Checkout source
        uses: actions/checkout@v4
        with:
          submodules: true
      - name: Restore sysroot from cache
        uses: actions/cache/restore@v4
        with:
          key: ${{ needs.linux-arm-sysroots.outputs[format('sysroot_cache_key_{0}', matrix.arch)] }}
          path: ${{ needs.linux-arm-sysroots.outputs[format('sysroot_path_{0}', matrix.arch)] }}
          fail-on-cache-miss: true
      - name: Install x-tools
        run: wget -qO- "https://github.com/neildavis/rpi-cross-toolchain-workflow/releases/latest/download/x-tools-${{ matrix.tuple }}.tar.gz" | tar xz -C $HOME
      - name: Cross build lib_tm1637_rpi
        run: |
          cmake -S . -B build -DCMAKE_TOOLCHAIN_FILE=$HOME/x-tools/${{ matrix.tuple }}/cmake/${{ matrix.tuple }}.cmake
          cmake --build build -j$(nproc)
    # ...
```