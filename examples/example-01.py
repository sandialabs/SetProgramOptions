#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
from pathlib import Path
import setprogramoptions

print(80*"-")
print(f"- {Path(__file__).name}")
print(80*"-")

filename = "example-01.ini"
popts = setprogramoptions.SetProgramOptions(filename)

section = "MY_LS_COMMAND"
popts.parse_section(section)
bash_options = popts.gen_option_list(section, generator="bash")
print(" ".join(bash_options))

print("Done")
