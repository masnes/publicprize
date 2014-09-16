#!/bin/sh
export HOME=/root
cd $HOME
rpm -Uvh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
yum install -y git gcc zlib-devel bzip2-devel readline-devel sqlite-devel openssl-devel tar
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
cat >> ~/.bashrc <<'EOF'
function reset_ps1 {
    export PS1='\W$ '
}
expr "x$PS1" : 'x\[' > /dev/null && reset_ps1

test "$VIRTUAL_ENV" && {
    type workon >/dev/null 2>&1 || {
        unset VIRTUAL_ENV
	    export VIRTUAL_ENV
	    reset_ps1
    }
}
export WORKON_HOME=$HOME/Envs
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV=true
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv virtualenvwrapper
test -d $WORKON_HOME/py3 && workon py3
EOF

export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.4.1
pyenv global 3.4.1
pip install virtualenvwrapper
git clone https://github.com/yyuu/pyenv-virtualenvwrapper.git ~/.pyenv/plugins/pyenv-virtualenvwrapper
. ~/.bashrc
pyenv virtualenvwrapper
mkvirtualenv py3
workon py3
