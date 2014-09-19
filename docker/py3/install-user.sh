#!/bin/sh
cp /etc/skel/.??* $HOME
git clone https://github.com/biviosoftware/emacs.git
rm -f ~/.emacs
ln -s ~/emacs/b-dot-emacs.el ~/.emacs
curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash
export WORKON_HOME=$HOME/Envs
export PYENV_VIRTUALENVWRAPPER_PREFER_PYVENV=true
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv install 3.4.1
pyenv global 3.4.1
pip install virtualenvwrapper
git clone https://github.com/yyuu/pyenv-virtualenvwrapper.git ~/.pyenv/plugins/pyenv-virtualenvwrapper
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"
pyenv virtualenvwrapper
mkvirtualenv py3
workon py3
