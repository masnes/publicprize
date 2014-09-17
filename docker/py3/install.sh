#!/bin/sh
chmod -R a+rX /cfg
export HOME=/root
cd $HOME
rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum install -y git gcc zlib-devel bzip2-devel readline-devel sqlite-devel openssl-devel tar postgresql-devel
cat > /etc/profile.d/publicprize.sh <<'EOF'
expr "x$PS1" : 'x\[' > /dev/null && export PS1='\W$ '
export WORKON_HOME=$HOME/Envs
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV=true
export PATH="$HOME/.pyenv/bin:$PATH"
test -d $WORKON_HOME && {
    eval "$(pyenv init -)"
    eval "$(pyenv virtualenv-init -)"
    pyenv virtualenvwrapper
    workon py3
}
EOF
chmod 644 /etc/profile.d/publicprize.sh

sh /cfg/install-user.sh

useradd run_user
su - run_user -c 'sh /cfg/install-user.sh'
