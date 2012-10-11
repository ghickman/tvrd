tvrd
====

Install
-------
Install into `/opt`:

    cd /opt
    git clone git://github.com/ghickman/tvrd.git


Create a virtual env:

    virtualenv --distribute venv


Create a log directory:

    sudo mkdir /var/log/tvrd
    sudo chown <user>:<group> /var/log/tvrd


Create a supervisor config in `/etc/supervisor/conf.d/tvrd.conf`:

    [program:tvrd]
    command=/opt/tvrd/venv/bin/python /opt/tvrd/main.py <folder to watch>
    user=<user>
    autostart=true
    autorestart=true
    redirect_stderr=True


Update supervisor:

    sudo supervisorctl update


Set up log rotation in `/etc/logrotate.d/tvrd` (with sudo):

    /var/log/tvrd/* {
        missingok
        nocompress
        rotate 5
        size 100M
    }


Profit.
