import sys, os

# FIXME to the right path for trex_stl_lib
cur_dir = os.path.dirname(__file__)
stl_dir = "trex_client/stl/"
sys.path.insert(0, os.path.join(cur_dir, stl_dir))

STL_PROFILES_PATH = os.path.join(os.pardir, 'profiles')
