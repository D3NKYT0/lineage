# -*- encoding: utf-8 -*-
"""
Gunicorn Configuration File
"""

import multiprocessing

# Bind the server to all interfaces on port 8000
bind = '0.0.0.0:5005'

# Number of worker processes. A good starting point is (2 x CPUs) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class (sync is the default, gevent or uvicorn can be used for async)
worker_class = 'sync'

# Access log file location (stdout by default)
accesslog = '-'

# Error log file location (stdout by default)
errorlog = '-'

# Log level (debug, info, warning, error, critical)
loglevel = 'info'

# Capture output from print statements and errors
capture_output = True

# Graceful timeout for worker processes (in seconds)
timeout = 30

# Max requests a worker will process before restarting (helps manage memory leaks)
max_requests = 1000
max_requests_jitter = 50
