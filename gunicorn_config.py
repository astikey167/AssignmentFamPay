import multiprocessing

bind = "0.0.0.0:3001"
workers = 3
threads = 4
timeout = 1000
worker_class = "gevent"
log_level = "debug"