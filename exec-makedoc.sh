#!/usr/bin/env bash

python3 -m pip uninstall -y setconfiguration

./exec-reqs-install.sh

cd doc
./make_html_docs.sh
err=$?
exit $err

