#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Make Documentation - Started"
printf "${normal}\n"

execute_command "python3 -m pip uninstall -y setprogramoptions > _test-uninstall-spe.log 2>&1"

cd doc
execute_command_checked "./make_html_docs.sh"
cd ..

# only executes if the previous command didn't fail
execute_command "rm _test-uninstall-spe.log > /dev/null 2>&1"

printf "${yellow}"
print_banner "Make Documentation - Done"
printf "${normal}\n"
