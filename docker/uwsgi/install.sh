#!/bin/sh
chmod -R a+rX /cfg
export HOME=/root
cd $HOME
. ~/.bash_profile

su - run_user <<'EOF'
git clone --branch=master https://github.com/biviosoftware/publicprize.git
cd publicprize
pip install -e .
EOF
