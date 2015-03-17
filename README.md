# tdigest
### Efficient percentile esimation of streaming or distributed data

This is a Python implementation of Ted Dunning's [t-digest](https://github.com/tdunning/t-digest) data structure. The t-digest data structure is designed around computing accurate estimates from either streaming data, or distributed data. These estimates are percentiles, quantiles, trimmed means, etc. Two t-digests can be added, making the data structure ideal for map-reduce settings, and can be serialized into much less than 10kB (instead of storing the entire list of data).

### Usage

```
from tdigest import TDigest
from numpy.random import random

T1 = TDigest()
for _ in range(1000):
    data = (random(), 1)
    T1.update(data)

print T1.percentile(0.15) # about 0.15


T2 = TDigest()
for _ in range(1000):
    data = (random(), 1)
    T2.update(data)

T = T1 + T2
T.percentile(0.5) # about 0.5
```


