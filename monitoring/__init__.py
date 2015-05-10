import os
from fabric.api import *
from fabric.contrib.files import *
from fabric.contrib.project import *
from glob import glob
from config import *
from StringIO import StringIO

files_dir = os.path.join(base_dir, "monitoring/files")
hosts_dir = os.path.join(base_dir, "monitoring/hosts")

@roles('monitoring_host')
def setup_monitoring_host():
    rsync_project(local_dir=("%s/" % hosts_dir), remote_dir="/etc/icinga2/conf.d/hosts", delete=True)
    run("systemctl reload icinga2")

@roles('monitoring_remotes')
def setup_monitoring_remote():
    run("apt-get update -qq")
    run("apt-get install monitoring-plugins-basic -qq -y")

    if not exists("/var/lib/nagios"):
        run("useradd --create-home --home /var/lib/nagios --shell /bin/bash --system nagios")
    if not exists("/var/lib/nagios/.ssh"):
        run("mkdir /var/lib/nagios/.ssh")

    put(os.path.join(files_dir, "nagios-shell"), "/usr/local/bin/nagios-shell", mode=0755)

    output = StringIO()
    output.write('command="/usr/local/bin/nagios-shell",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty ')
    output.write(monitoring_pubkey)
    put(output, "/var/lib/nagios/.ssh/authorized_keys")

    run("chown -R root:nagios /var/lib/nagios/.ssh")
    run("chmod -R 750 /var/lib/nagios/.ssh")

@task(default=True)
def monitoring():
    execute(setup_monitoring_host)
    execute(setup_monitoring_remote)
