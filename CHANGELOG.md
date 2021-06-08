Changelog
=========
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
## [X.Y.Z] - YYYY-MM-DD or [Unreleased]
#### Added
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
#### Todo (for Unreleased)
-->

## [0.2.X] - <!-- YYYY-MM-DD or --> [Unreleased]
#### Added
- `common.py` - moved some free-functions to this.
- Improved *variable* processing. Variables should now be encoded in our pseudo-langauge
  that has a syntax like this: `${VARNAME|VARTYPE}`.
  - `ENV` - is the only 'type' that is known to `SetProgramOptions`
  - `CMAKE` - is known to `SetProgramOptionsCMake`, which denotes a "CMake" variable
    which would be part of the internal state. This mostly makes sense when generating
    CMake Fragments, but we also attempt to track variables that are set when generating
    BASH output and will perform expansions when a prevoulsly set value is known.
#### Changed
- _values_ containing spaces in them will have double quotes (`"`) added to them.
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
- Modified `_gen_option_entry` to detect values with spaces in them and add quotes (`"`) to the string.
#### Todo (for Unreleased)



## [0.1.0] - 2021-04-29
#### Added
- Initial version release. From now on changes should be noted in the
  CHANGELOG.
#### Changed
#### Deprecated
#### Removed
#### Fixed
#### Security
#### Internal
#### Todo (for Unreleased)


