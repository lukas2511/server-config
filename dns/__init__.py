import os
from fabric.api import *
from fabric.contrib.files import *
from glob import glob
from config import *

template_dir = os.path.join(dns_dir, "templates")

@task
def setup_knot():
    if not exists("/etc/apt/sources.list.d/knot.list"):
        run("wget -q -O - http://deb.knot-dns.cz/nightly/apt.key | apt-key add -")
        append("/etc/apt/sources.list.d/knot.list", "deb http://deb.knot-dns.cz/nightly/ jessie main")
    run("apt-get update -qq")
    run("apt-get install knot -qq -y")

    if env.host == dns_master:
        with cd("/var/lib/knot"):
            if not exists("master"):
                run("mkdir master")
            if not exists("kasp"):
                run("mkdir kasp")
                with cd("kasp"):
                    run("keymgr init")
                    run("keymgr policy add default_rsa")

    with cd("/var/lib/knot"):
        if not exists("slave"):
            run("mkdir slave")

def configure_knot_master():
    for zone in zones:
        if not exists("/var/lib/knot/kasp/zone_%s.json" % zone):
            with cd("/var/lib/knot/kasp"):
                run("keymgr zone add %s policy default_rsa" % zone)
    put(os.path.join(zones_dir, '*.*'), "/var/lib/knot/master/")

    context = {
        'zones': zones,
        'slaves': dns_slaves,
        'update_secret': update_secret,
    }

    upload_template("master.tpl", "/etc/knot/knot.conf", context=context, use_jinja=True, template_dir=template_dir)
    run("chown knot: /etc/knot/knot.conf; chmod 600 /etc/knot/knot.conf");

    run("chown -R knot: /var/lib/knot")
    run("systemctl reload knot")

def configure_knot_slave():
    context = {
        'zones': zones,
        'dns_master': dns_master,
        'slave': list(slave for slave in dns_slaves if slave['address'] == env.host)[0],
    }

    upload_template("slave.tpl", "/etc/knot/knot.conf", context=context, use_jinja=True, template_dir=template_dir)

    run("chown -R knot: /var/lib/knot")
    run("systemctl reload knot")

@task(default=True)
def knot():
    if env.host == dns_master:
        configure_knot_master()
    else:
        configure_knot_slave()

