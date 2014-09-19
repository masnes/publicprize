#!/bin/bash
test -d $PGDATA && exit 0

echo 'Initializing database'
su - postgres -c 'initdb --encoding=UTF8'
service postgresql start
echo "ALTER USER postgres PASSWORD '${PGPASSWORD-postpass}';COMMIT" | su - postgres -c 'psql template1'
service postgresql stop

perl -w -i.bak - $PGDATA/postgresql.conf <<'EOF'
use strict;
my($shmmax) = `sysctl -n kernel.shmmax`;
chomp($shmmax);
$shmmax = int($shmmax / 1048576);
my($tm) = int((`free -b` =~ /(\d+)/)[0] / 1048576);
my($size) = sub {
    my($factor, $max, $suffix) = @_;
    $suffix = 'MB'
        unless defined($suffix);
    my($n) = int($tm / $factor);
    $n = $max
        if $max && $n > $max;
    return $n . $suffix;
};
while (my $line = <>) {
    foreach my $x (
        [log_line_prefix => q{%t %d %p }],
        [archive_mode => 'off'],
        [archive_command => q{''}],
        [archive_timeout => 0],
	[timezone => 'UTC'],
	[client_encoding => 'UTF8'],
	[listen_addresses => '*'],
	[checkpoint_completion_target => '0.9'],
	[checkpoint_segments => 64],
	[log_checkpoints => 'on'],
        # https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server
        [max_connections => $size->(32, 128, '')],
	[effective_cache_size =>  $size->(2)],
	[maintenance_work_mem => $size->(32, 64)],
	[shared_buffers => $size->(4, int($shmmax * .5))],
	[wal_buffers => $size->(32, 16)],
	[work_mem => $size->(32, 16)],
    ) {
	my($p, $v) = @$x;
	$line =~ s/^\s*#?\s*$p\s*=.*/$p = '$v'/m;
    }
    print($line);
}
EOF

cat > $PGDATA/pg_hba.conf <<'EOF'
# TYPE  DATABASE    USER        CIDR-ADDRESS          METHOD
local   all         all                               trust
host    all         all         0.0.0.0/0             password
host    all         all         ::/0                  password
EOF

