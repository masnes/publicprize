#!/bin/sh
chmod -R a+rX /cfg
export HOME=/root
cd $HOME

rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum install -y \
    bzip2-devel \
    emacs-nox \
    gcc \
    git \
    openssl-devel \
    postgresql-devel \
    readline-devel \
    sqlite-devel \
    tar \
    zlib-devel \

cat > /etc/skel/.psqlrc <<'EOF'
\pset pager
\set AUTOCOMMIT off
EOF
chmod 644 /etc/skel/.psqlrc
cat > /etc/profile.d/publicprize.sh <<'EOF'
export PS1='\W$ '
test "x$(id -u)" == x0 && export PS1='\W# '
export WORKON_HOME=$HOME/Envs
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV=true
export PATH="$HOME/.pyenv/bin:$PATH"
test -d $WORKON_HOME && {
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    pyenv virtualenvwrapper
    workon py3
}
export PGDATA=/var/lib/pgsql/data
EOF
chmod 644 /etc/profile.d/publicprize.sh

sh /cfg/install-user.sh

useradd run_user
su - run_user -c 'sh /cfg/install-user.sh'
