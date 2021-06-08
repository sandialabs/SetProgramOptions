[![pipeline status](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/SetProgramOptions/badges/master/pipeline.svg)](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/SetProgramOptions/-/commits/master)
[![coverage report](https://gitlab-ex.sandia.gov/trilinos-devops-consolidation/code/SetProgramOptions/badges/master/coverage.svg)](http://10.202.35.89:8080/SetProgramOptions/coverage/index.html)
[![Generic badge](https://img.shields.io/badge/docs-latest-green.svg)](http://10.202.35.89:8080/SetProgramOptions/doc/index.html)

SetProgramOptions
=================
The `SetProgramOptions` package extends `ConfigParserEnhanced` to enable the processing
of **.ini** files that specify *Program Options*.

`SetProgramOptions` supports all the _operations_ that `ConfigParserEnhanced` supports
and adds some of its own.

| Operation  | Format                                        | Defined By             |
| ---------- | --------------------------------------------- | ---------------------- |
| use        | `use <section>`                               | `ConfigParserEnhanced` |
| opt-set    | `opt-set Param1 [Param2..ParamN] [: <VALUE>]` | `SetProgramOptions`    |
| opt-remove | `opt-remove Param [SUBSTR]`                   | `SetProgramOptions`    |


INI File Format
---------------
A **.ini** file that can be processed by `SetProgramOptions` can be formatted like this:
```ini
[SECTION_A]
opt-set cmake

TOOD: FINISH THIS README!
```

### Variable Expansion within VALUE fields
Variables can be added to the VALUE fields in handled instructions, but they have their
own format that must be used:
```
${VARNAME|VARTYPE}
```
- `VARNAME` is the variable name that you might expect for a bash style environment variable
  that might be defined like this: `export VARNAME=VALUE`.
- `VARTYPE` is the **type** of the variable that is being declared. For `SetProgramOptions`
  the only recognized type is `ENV` which defines _environment variables_. Subclasses such
  as `SetProgramOptionsCMake` define their own types.

We do not provide a **default** type for this because we wish it to be _explicit_ that this
is a pseudo-type and do not with it to be confused with some specific variable type since that
meaning can change depending on the kind of generator being used. For example, `${VARNAME}`
is an _environment variable_ within a bash context but in a CMake fragment file it would be
an _internal cmake variable_ and `$ENV{VARNAME}` would be an _environment variable_.
By not providing a default we force type consideration to be made explicitly during the creation
of the .ini file.


Operations Explained
--------------------


### `use`
TODO


### `opt-set`
TODO


### `opt-remove`
TODO


SetProgramOptions Examples
--------------------------
TODO



SetProgramOptionsCMake
======================
`SetProgramOptionsCMake` is a subclass of `SetProgramOptions` that adds additional additional
operations and generators to handle processing CMake options:
- Adds `opt-set-cmake-var`
- Adds `cmake_fragment` generator
- Adds `CMAKE` type to variables.

New operations defined in `SetProgramOptionsCMake`:

| Operation           | Format                                                           | Defined By               |
| ------------------- | ---------------------------------------------------------------- | ------------------------ |
| `opt-set-cmake-var` | `opt-set-cmake-var VARNAME [TYPE] [FORCE] [PARENT_SCOPE]: VALUE` | `SetProgramOptionsCMake` |


INI File Format
---------------
A **.ini** file that can be processed by `SetProgramOptions` can be formatted like this:
```ini
[SECTION_A]
opt-set cmake

TOOD: FINISH THIS README!
```


Operations Explained
--------------------


### `opt-set-cmake-var`
TODO


SetProgramOptionsCMake Examples
-------------------------------
TODO
