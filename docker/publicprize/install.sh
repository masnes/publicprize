#!/bin/sh
chmod -R a+rX /cfg
su - run_user <<'EOF'
git clone --branch=master https://github.com/biviosoftware/publicprize.git
cd publicprize
pip install -e .
EOF
