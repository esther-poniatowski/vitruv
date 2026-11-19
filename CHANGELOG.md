# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- The command `vitruv boundaries check`, which reports each crossing of a boundary between the
  tools of a set under ten rules, as text or as a findings log in the profile of Elenchos. The
  analyst declares the tools in a boundary table of format `vitruv:boundaries@1`, whose schema and
  annotated template the package ships; the tools declare nothing for Vitruv.
- The dependencies `pyyaml` and `jsonschema`, and the extra `test`, which installs Elenchos.

### Fixed

- `-v`/`--version` prints the version without a command. The option was not eager, so the command
  line stopped with "Missing command" and status 2.
