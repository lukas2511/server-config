from fabric.api import *
from fabric.contrib.files import *

import dns
import monitoring

env.user = 'root'
env.use_ssh_config = True

