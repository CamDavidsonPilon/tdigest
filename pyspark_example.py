from __future__ import print_function

from random import random
from operator import add 
from tdigest import TDigest

data = sc.parallelize([random() for _ in range(1000)], 10)

def digest_partitions(values):
    digest = TDigest()
    digest.batch_update(values)
    return [digest]

digest = data.mapPartitions(digest_partitions).reduce(add)  # to be more efficent, use treeReduce
print(digest.percentile(95))

