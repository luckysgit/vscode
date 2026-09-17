"""Trusted launcher: apply hard limits BEFORE entering the deny-default sandbox."""
import os
import resource
import sys

for kind, limit in [(resource.RLIMIT_CPU, 2),
                    (resource.RLIMIT_FSIZE, 0), (resource.RLIMIT_NOFILE, 32),
                    (resource.RLIMIT_CORE, 0)]:
    hard = resource.getrlimit(kind)[1]
    if hard != resource.RLIM_INFINITY:
        limit = min(limit, hard)
    resource.setrlimit(kind, (limit, limit))
os.execv('/usr/bin/sandbox-exec', ['/usr/bin/sandbox-exec', *sys.argv[1:]])
