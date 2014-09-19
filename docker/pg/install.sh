#!/bin/sh
chmod -R a+rX /cfg
export HOME=/root
cd $HOME
. ~/.bash_profile

yum install -y postgresql-server
chkconfig --del postgresql
cp /etc/skel/.??* ~postgres
# Doesn't work in Docker, and deprecated anyway
echo 'PG_OOM_ADJ=' >> /etc/sysconfig/pgsql/postgresql
