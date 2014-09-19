#!/bin/bash
sh /cfg/cfg.sh
exec su -l postgres -c '/usr/bin/postmaster -D $PGDATA'
