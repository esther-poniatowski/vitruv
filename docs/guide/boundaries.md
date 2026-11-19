# Boundaries between tools

The command `vitruv boundaries check` reports each crossing of a boundary between the tools of a set. The analyst who checks the set declares the tools in a boundary table, and the tools themselves declare nothing for Vitruv. The rules restate three drivers of a decision on the roles of tools, and each rule has an identifier, written in the findings log.

## 1. Drivers

- **Declared reads.** A tool reads only its own files, files fixed by a widely accepted convention, and the published contracts of the tools that it declares as dependencies.
- **Owner implementations.** A tool parses, validates or serializes a format of another tool only through an implementation published by the owner. A declared producer may write a document in the format of another tool, and validate it with the implementation or the schema of the owner. A schema may refer to a schema of the owner by its absolute `$id`.
- **Agnostic tools.** No output, schema, message or test of a tool names a tool that depends on it, a consumer, a renderer, or an internal module of another tool.

## 2. Rules

| Identifier | Driver | Case | Located at |
| --- | --- | --- | --- |
| `reads/undeclared-format` | declared reads | a file holds a marker of a format of another tool, and the tool does not declare that it uses the format | the marker |
| `reads/sibling-path` | declared reads | a file reaches the folder of another tool by a relative path: `../<folder>`, a traversal `parents[n]` or `.parent` joined to the folder, or a `join` of `".."` with the folder | the path |
| `reads/undeclared-dependency` | declared reads | a file imports a package of another tool that the tool does not declare as a dependency | the import |
| `implementations/undeclared-owner` | owner implementations | the tool uses a format whose owner it does not declare as a dependency, or through an implementation that is not the published interface of the owner | the folder of the tool |
| `implementations/unused-owner-implementation` | owner implementations | the tool declares that it uses a format through an implementation of its owner, and no file imports or names that implementation | the folder of the tool |
| `implementations/copied-file` | owner implementations | a file has the bytes of a file published by another tool, or declares as its `$id` a published `$id` or an `$id` marker of another tool | the file |
| `implementations/foreign-namespace` | owner implementations | a file names a contract identifier in the namespace of another tool, which that tool does not own | the identifier |
| `agnostic/dependent-name` | agnostic tools | a file names a tool that depends on the tool, unless the tool also depends on it | the name |
| `agnostic/entity-name` | agnostic tools | a file holds a marker of an entity that the tool may not know | the marker |
| `agnostic/internal-import` | agnostic tools | a file imports a module of another tool outside the public interface of that tool | the import |

Every finding has the level `error`. Its resource is the file, or the folder of the tool, relative to the workspace; its discriminator is the offending text. A check of one tool and a check of every tool therefore give one finding one identity.

The scan of a tool reads the files that Git tracks in its folder, or every file of a folder that is no Git working tree. By default, the scan leaves out the documentation and the development configuration of the tool, since they hold no output, schema, message or test:

- `docs/`, and the Markdown and reStructuredText files;
- `.github/`, `.vscode/` and `config/tools/`;
- `pyproject.toml`, `package.json`, `tsconfig*.json`, `environment.yml` and `conda.recipe/`;
- `.gitignore`, `.gitattributes` and `.gitmessage`.

A marker is a literal, searched as written. When a marker ends a contract identifier before its version, such as `kleisis:schema-registry@`, the marker covers every version. A name of a tool is a word, searched without case. An import is read from the syntax tree of a Python file, and from the module specifiers of a TypeScript or JavaScript file. A module belongs to the public interface of its owner when it equals an interface, or lies below one through components that do not open on `_`.

## 3. Boundary table

The table is a YAML file of format `vitruv:boundaries@1`, published as the JSON Schema [boundaries.schema.json](../../src/vitruv/schemas/boundaries.schema.json). The packaged [template](../../src/vitruv/templates/boundaries.yml) explains each key. A table holds three sections:

- `defaults`: the folder of the workspace that holds the tools, and the files outside the scan;
- `tools`: each tool by name, with its folder, the words naming it, its dependencies, its import roots and its public interface. The tool also lists the formats that it owns, with their markers and published files, and the formats of other tools that it uses, each with the implementation of the owner. Globs may restrict its scan;
- `entities`: the consumers, renderers and layouts that no tool may name, each with its markers and the tools that may name it.

A tool uses a format `through` one of three implementations of the owner:

- a module of the interface of the owner;
- the `$id` of a published schema of the owner;
- the name of the owner, when the command of the owner reads the document, such as the configuration of the owner held by the tool. The name of a tool is also the namespace of the contracts that it owns.

The table states the architecture intended by the analyst, not the dependencies that the tools declare today: each finding is a gap between the code and that architecture.

## 4. Command

```sh
vitruv boundaries check --table boundaries.yml --workspace ~/Documents
vitruv boundaries check --table boundaries.yml --workspace ~/Documents --tool kleisis
vitruv boundaries check --table boundaries.yml --workspace ~/Documents --format sarif --output build/boundaries.sarif
```

The option `--tool` checks one tool; the other tools of the table still supply its dependents and the files that they publish. The option `--format` takes `text`, the default, or `sarif`, which writes a findings log in the profile of the gate Elenchos.

The exit status is 0 without finding, 1 with findings, and 2 when the check cannot run. The check cannot run on an unreadable or invalid table, on a tool absent from the table or from the workspace, or on an unreadable published file. With `--format sarif`, the log then holds a failed run that states why.

## 5. Reach

The rules detect a crossing that leaves a literal in the files of a tool: a marker, a path, a name, an import, a copied file or a contract identifier. When a second implementation shares no literal with its owner, the rules miss it, as they miss a converter of field paths written again from a specification, or a segmentation of documents written again. Such defects stay enforced by review, and by the decisions that move each concern to one owner.
