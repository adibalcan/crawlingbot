from utils.pybloomd import BloomdClient

client = BloomdClient(["107.170.243.148"])
bloom = client.create_filter("domains")