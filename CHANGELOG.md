# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed

- `-v`/`--version` prints the version without a command. The option was not eager, so the command
  line stopped with "Missing command" and status 2.
