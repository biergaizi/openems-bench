openems-bench
======================

This repository contains various scripts for evalutating openEMS simulation
performance.

### Configuration

The `config` directory is used for configuration. `config/config.sh` is the
configuration file, it's used for:

1. Specifying different git repo URLs, git branches, and CFLAGS for
building openEMS.

2. Maximum number of threads.

3. Whether a proxy server is used for git.

### Building

The `build` directory is used for cloning and building customized version
of openEMS, under the control of `config.sh`.

Run `make` to start the build. All dependencies must be installed from
the host before running the build.

Source code from cloned into `build/src`, and binaries are installed into
`build/prog`.

### Running

The `run` directory is used for running benchmarks. It contains Octave
and Python benchmarks from openEMS's examples, and also a few Python
benchmarks from the 3rd-party pyems project.

For automation on different operating systems, all benchmark scripts are
designed to run using custom openEMS builds in the `build` directory. Other
openEMS installations cannot be used.

### Post-Processing

The `postprocessing` directory contains scripts used for data analysis
and plotting. They're not needed for running benchmarks, and are only
used for processing test results.
