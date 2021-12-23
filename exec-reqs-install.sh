#!/usr/bin/env bash
#
# Install just the dependencies of this project (not the project itself)
# into the local user space.
#

# Source the common helpers script.
source scripts/common.bash

# Check if we're in a virtual environment
pip_opt_user=""
if [ -z ${VIRTUAL_ENV} ]; then
    # if not in virtual environment
    pip_opt_user="--user"
fi

printf "${yellow}"
print_banner "INSTALL REQUIRED PACKAGES"
printf "${normal}"

python_exe="python3"

execute_command "which ${python_exe:?}"
execute_command "${python_exe:?} --version"

options=(
    -m pip
    install
    ${pip_opt_user}
    -r requirements.txt
    -r requirements-build.txt
    -r requirements-test.txt
    -r doc/requirements.txt
)

cmd="${python_exe} ${options[@]}"
execute_command_checked "${cmd} > _test-reqs-install.log 2>&1"

