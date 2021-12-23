#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
from pathlib import Path
from pprint import pprint
import setprogramoptions

def print_separator(label):
    print("")
    print(f"{label}")
    print("-"*len(label))
    return

def test_setprogramoptions(filename="config.ini"):
    print(f"filename: {filename}")

    section_name = "TEST_VAR_EXPANSION_UPDATE_01"
    print(f"section_name = {section_name}")

    parser = setprogramoptions.SetProgramOptionsCMake(filename=filename)
    parser.debug_level = 0
    parser.exception_control_level = 4
    parser.exception_control_compact_warnings = True

    data = parser.configparserenhanceddata[section_name]
    print_separator(f"parser.configparserenhanceddata[{section_name}]")
    pprint(data, width=120)

    print_separator("Show parser.options")
    pprint(parser.options, width=200, sort_dicts=False)

    print_separator("Bash Output")
    print("Note: The _second_ assignment to `CMAKE_CXX_FLAGS` is skipped by a BASH generator")
    print("      without a `FORCE` option since by definition all CMake `-D` options on a ")
    print("      BASH command line are both CACHE and FORCE. Within a CMake source fragment")
    print("      changing an existing CACHE var requires a FORCE option to be set so we should")
    print("      skip the second assignment to maintain consistency between the bash and cmake")
    print("      fragment generators with respect to the CMakeCache.txt file that would be")
    print("      generated.")
    print("      The `WARNING` message below is terse since it's in compact form -- disable")
    print("      the `exception_control_compact_warnings` flag to get the full warning message.")
    print("")
    option_list = parser.gen_option_list(section_name, generator="bash")
    print("")
    print(" \\\n    ".join(option_list))

    print_separator("CMake Fragment")
    option_list = parser.gen_option_list(section_name, generator="cmake_fragment")
    if len(option_list) > 0:
        print("\n".join(option_list))
    else:
        print("-")
    print("")

    return 0


def main():
    """
    main app
    """
    print(80*"-")
    print(f"- {Path(__file__).name}")
    print(80*"-")
    test_setprogramoptions(filename="example-03.ini")
    return 0


if __name__ == "__main__":
    main()
    print("Done.")
