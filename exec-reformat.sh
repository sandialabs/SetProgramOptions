#!/usr/bin/env bash

# Source the common helpers script
source scripts/common.bash

printf "${yellow}"
print_banner "Reformatting - Started"
printf "${normal}\n"

exclude_dirs=(
    .git
    doc
    __pycache__
    deps
    venv-*
)

exclude_opts=()
for exc in ${exclude_dirs[*]}; do
    exclude_opts+=("-e")
    exclude_opts+=("${exc}")
done

execute_command "yapf -vv -i -p -r ${exclude_opts[*]} ."

printf "${yellow}"
print_banner "Reformatting - Done"
printf "${normal}\n"

