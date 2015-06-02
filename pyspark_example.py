from random import random
from operator import add 
from tdigest import TDigest

data = sc.parallelize([_ for _ in random()])

def digest_partitions(values):
    digest = TDigest()
    digest.batch_update(values)
    return [digest]

digest = data.mapPartitions(digest_partitions).reduce(add)  # to be more efficent, use treeReduce
print digest.percentile(0.95)

