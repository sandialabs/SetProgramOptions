#!/usr/bin/env python3
# -*- mode: python; py-indent-offset: 4; py-continuation-offset: 4 -*-
"""
Example app for SetConfiguration
"""
from __future__ import print_function  # python 2 -> 3 compatiblity

import os
from pprint import pprint

import setconfiguration



def find_config_ini(filename="config.ini", rootpath="." ):
    """
    Recursively searches for a particular file among the subdirectory structure.
    If we find it, then we return the full relative path to `pwd` to that file.

    The _first_ match will be returned.

    Args:
        filename (str): The _filename_ of the file we're searching for. Default: 'config.ini'
        rootpath (str): The _root_ path where we will begin our search from. Default: '.'

    Returns:
        String containing the path to the file if it was found. If a matching filename is not
        found then `None` is returned.

    """
    output = None
    for dirpath,dirnames,filename_list in os.walk(rootpath):
        if filename in filename_list:
            output = os.path.join(dirpath, filename)
            break
    if output is None:
        raise FileNotFoundError("Unable to find {} in {}".format(filename, os.getcwd()))  # pragma: no cover
    return output



def test_setconfiguration(filename="config.ini"):
    print("filename    : {}".format(filename))
    print("")

    parser = setconfiguration.SetConfigurationCMake(filename=filename)
    parser.debug_level = 5
    parser.exception_control_level = 4
    parser.exception_control_compact_warnings = True

    # pre-parse all sections
    # parser.parse_all_sections()

    section_name = "TEST_CONFIGURATION_A"

    parse_section(parser, section_name)

    return



def parse_section(parser, section):

    # Test out something that might be experimental
    experimental(parser, section)

    #data = parser.parse_section(section)
    data = parser.configparserenhanceddata[section]

    print("\nData")
    print("====")
    pprint(data, width=120)

    # Print the loginfo from the last search
    print("\nLogInfo")
    print("=======")
    #parser._loginfo_print(pretty=True)
    handler_list = [ (d['type'], d['name']) for d in parser._loginfo if d['type'] in ['handler-entry','handler-exit']]
    pprint(handler_list, width=120)

    return data



def experimental(parser, section):
    return 0



def main():
    """
    main app
    """
    fname_ini = "config_test_setconfigurationcmake.ini"
    fpath_ini = find_config_ini(filename=fname_ini)

    test_setconfiguration(filename=fpath_ini)



if __name__ == "__main__":
    main()
    print("Done.")

