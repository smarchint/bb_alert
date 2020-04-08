

COOKIE = ""  # required
ADDR_INT_ID = None  # int required

DEBUG = False

# this should be at the end of file 
try:
	from local_settings import *
except ImportError:
	pass