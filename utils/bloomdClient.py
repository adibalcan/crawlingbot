import sys
import config
sys.path.append('utils')
try:
    from utils.pybloomd import BloomdClient
except:
    from pybloomd import BloomdClient

client = BloomdClient([config.pybloomdServer])
bloom = client.create_filter("domains")