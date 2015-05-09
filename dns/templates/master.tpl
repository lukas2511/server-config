server:
    identity: "Knot DNS"
    version: "Yo!"

    user: knot:knot

    listen: 0.0.0.0@53
    listen: ::@53

key:
{% for slave in slaves %}
{% if slave.secret %}
  - id: key_{{ slave.name }}
    algorithm: hmac-md5
    secret: {{ slave.secret }}
{% endif %}
{% endfor %}
  - id: key_update
    algorithm: hmac-md5
    secret: {{ update_secret }}

remote:
{% for slave in slaves %}
  - id: {{ slave.name }}
    address: {{ slave.address }}@53
{% if slave.secret %}
    key: key_{{ slave.name }}
{% endif %}
{% endfor %}

acl:
{% for slave in slaves %}
  - id: acl_{{ slave.name }}
    address: {{ slave.address }}
{% if slave.secret %}
    key: key_{{ slave.name }}
{% endif %}
    action: xfer
{% endfor %}
  - id: acl_update
    action: update
    key: key_update

template:
  - id: default
    storage: /var/lib/knot/master
    dnssec-enable: on
    dnssec-keydir: /var/lib/knot/kasp
    semantic-checks: on
    notify: [{% for slave in slaves %}{{ slave.name }}{% if not loop.last %}, {% endif %}{% endfor %}]
    acl: [{% for slave in slaves %}acl_{{ slave.name }}{% if not loop.last %}, {% endif %}{% endfor %}, acl_update]
    serial-policy: unixtime

  - id: slave
    storage: "/var/lib/knot/slave"

zone:
{% for zone in zones %}
  - domain: {{ zone }}
    file: {{ zone }}
{% endfor %}

log:
    # Log info and more serious events to syslog.
  - to: syslog
    any: info

    # Log warnings, errors and criticals to stderr.
  - to: stderr
    any: warning

