server:
    identity: "Knot DNS"
    version: "Yo!"

    user: knot:knot

    listen: 0.0.0.0@53
    listen: ::@53

key:
  - id: key_{{ slave.name }}
    algorithm: hmac-md5
    secret: {{ slave.secret }}

remote:
  - id: master
    address: {{ dns_master }}@53
    key: key_{{ slave.name }}

acl:
  - id: acl_{{ slave.name }}
    address: {{ dns_master }}
    action: notify
    key: key_{{ slave.name }}

template:
  - id: default
    storage: "/var/lib/knot/slave"
    master: master
    acl: acl_{{ slave.name }}

zone:
{% for zone in zones %}
  - domain: {{ zone }}
{% endfor %}

log:
    # Log info and more serious events to syslog.
  - to: syslog
    any: info

    # Log warnings, errors and criticals to stderr.
  - to: stderr
    any: warning

