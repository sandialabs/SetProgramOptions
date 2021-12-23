#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
from pathlib import Path
import setprogramoptions

def print_separator(label):
    print("")
    print(f"{label}")
    print("-"*len(label))
    return

print(80*"-")
print(f"- {Path(__file__).name}")
print(80*"-")

filename = "example-02.ini"
popts = setprogramoptions.SetProgramOptionsCMake(filename)

section = "MYPROJ_CONFIGURATION_NINJA"
popts.parse_section(section)

# Generate BASH output
print_separator("Generate Bash Output")
bash_options = popts.gen_option_list(section, generator="bash")
print(" \\\n   ".join(bash_options))

# Generate a CMake Fragment
print_separator("Generate CMake Fragment")
cmake_options = popts.gen_option_list(section, generator="cmake_fragment")
print("\n".join(cmake_options))

print("\nDone")
