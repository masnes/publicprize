#!/bin/sh
export HOME=/root
cd $HOME
. ~/.bashrc
git clone --branch=master https://github.com/biviosoftware/publicprize.git
cd publicprize
pip install .
