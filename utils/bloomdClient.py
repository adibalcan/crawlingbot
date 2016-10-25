
import sys
sys.path.append('utils')
try:
    from utils.pybloomd import BloomdClient
except:
    from pybloomd import BloomdClient

client = BloomdClient(["BLOOM_IP"])
bloom = client.create_filter("domains")