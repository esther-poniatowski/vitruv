# Usage

Vitruv is a structural quality analyzer for software projects. The project is
in early development; analysis features are planned but not yet implemented.

The only functional command is `info`, which prints version and platform
diagnostics.

## Displaying Project Information

```sh
vitruv info
```

The `info` command reports the installed version, Python runtime, and operating
system.

## Planned Features

The following capabilities are on the roadmap but do not exist yet:

- **analyze** -- Extract dependency graphs and report structural metrics.
- **audit** -- Evaluate architectural dimensions against predefined profiles.
- **smells** -- Detect structural anti-patterns (cyclic dependencies, god
  modules, layer violations).
- **metrics** -- Compute package-level coupling, instability, and abstractness.
- **conform** -- Check a codebase against a declared architecture.
- **Python API** -- Expose the analysis pipeline programmatically.

## Next Steps

- [CLI Reference](cli-reference.md) -- Full command and option listing.
- [Configuration](configuration.md) -- Tool configuration files.
