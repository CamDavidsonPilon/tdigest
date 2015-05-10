# tdigest
### Efficient percentile estimation of streaming or distributed data
[![Latest Version](https://pypip.in/v/tdigest/badge.png)](https://pypi.python.org/pypi/tdigest/)


This is a Python implementation of Ted Dunning's [t-digest](https://github.com/tdunning/t-digest) data structure. The t-digest data structure is designed around computing accurate estimates from either streaming data, or distributed data. These estimates are percentiles, quantiles, trimmed means, etc. Two t-digests can be added, making the data structure ideal for map-reduce settings, and can be serialized into much less than 10kB (instead of storing the entire list of data).

See a blog post about it here: [Percentile and Quantile Estimation of Big Data: The t-Digest](http://dataorigami.net/blogs/napkin-folding/19055451-percentile-and-quantile-estimation-of-big-data-the-t-digest)


### Installation
```
pip install tdigest
```

### Usage

```
from tdigest import TDigest
from numpy.random import random

T1 = TDigest()
for _ in range(5000):
    T1.update(random())

print T1.percentile(0.15) # about 0.15


T2 = TDigest()
T2.batch_update(random(5000))
print T2.percentile(0.15)

T = T1 + T2
T.percentile(0.3) # about 0.3
```



