# Installation:

- install Git:

    - `$ sudo apt-get install git-core`

- Install build essentials
    - `$ sudo apt-get install build-essential`

- get pyenv: [https://github.com/yyuu/pyenv](https://github.com/yyuu/pyenv) (or use the installer [https://github.com/yyuu/pyenv-installer](https://github.com/yyuu/pyenv-installer))
    - add the following to .bashrc:

        `export PYENV_ROOT="$HOME/.pyenv"`
        `export PATH="$PYENV_ROOT/bin:$PATH"`
        `if which pyenv > /dev/null; then eval "$(pyenv init -)"; fi`

    - install python 2.6:

      `$ pyenv install 2.6.9`
      `$ pyenv rehash`

- get pyenv-virtualenv: [https://github.com/yyuu/pyenv-virtualenv](https://github.com/yyuu/pyenv-virtualenv) (only if you didn't use the installer)
    - create a new virtualenv for python 2.6:

        `$ pyenv virtualenv 2.6.9 some-virtalenv-name`

    - activate the virtualenv:

        `$ pyenv activate some-virtualenv-name`

- get the source for ScrumDo: [https://github.com/ScrumDoLLC/ScrumDo/tree/production](https://github.com/ScrumDoLLC/ScrumDo/tree/production)




# Agile Story Management Web Site

Visit [ScrumDo.com](http://www.ScrumDo.com) to use it.

Visit [ScrumDo.org](http://www.ScrumDo.org) to start developing.

Follow us on [twitter](http://twitter.com/#!/ScrumDo)

