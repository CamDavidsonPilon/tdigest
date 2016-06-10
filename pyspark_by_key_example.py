from __future__ import print_function

from random import random
from operator import add 
from tdigest import TDigest

data = sc.parallelize([(0, random()) for _ in range(1000)] + 
                      [(1, random() + 1) for _ in range(1000)] + 
                      [(2, random() + 2) for _ in range(1000)], 10)

def initialise_digest(v):
    d = TDigest()
    d.update(v)
    return d

def update_digest(d, v):
    d.update(v)
    return d

percentiles = data\
    .combineByKey(initialise_digest, update_digest, add)\
    .map(lambda kv: (kv[0], kv[1].percentile(95)))\
    .collect()
    
print(percentiles)
