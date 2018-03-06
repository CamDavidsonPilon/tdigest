# tdigest
### Efficient percentile estimation of streaming or distributed data
[![PyPI version](https://badge.fury.io/py/tdigest.svg)](https://badge.fury.io/py/tdigest)
[![Build Status](https://travis-ci.org/CamDavidsonPilon/tdigest.svg?branch=master)](https://travis-ci.org/CamDavidsonPilon/tdigest)


This is a Python implementation of Ted Dunning's [t-digest](https://github.com/tdunning/t-digest) data structure. The t-digest data structure is designed around computing accurate estimates from either streaming data, or distributed data. These estimates are percentiles, quantiles, trimmed means, etc. Two t-digests can be added, making the data structure ideal for map-reduce settings, and can be serialized into much less than 10kB (instead of storing the entire list of data).

See a blog post about it here: [Percentile and Quantile Estimation of Big Data: The t-Digest](http://dataorigami.net/blogs/napkin-folding/19055451-percentile-and-quantile-estimation-of-big-data-the-t-digest)


### Installation
*tdigest* is compatible with both Python 2 and Python 3. 

```
pip install tdigest
```

### Usage

#### Update the digest sequentially

```
from tdigest import TDigest
from numpy.random import random

digest = TDigest()
for x in range(5000):
    digest.update(random())

print(digest.percentile(15))  # about 0.15, as 0.15 is the 15th percentile of the Uniform(0,1) distribution
```

#### Update the digest in batches

```
another_digest = TDigest()
another_digest.batch_update(random(5000))
print(another_digest.percentile(15))
```

#### Sum two digests to create a new digest

```
sum_digest = digest + another_digest 
sum_digest.percentile(30)  # about 0.3
```

### API 

`TDigest.`

 - `update(x, w=1)`: update the tdigest with value `x` and weight `w`.
 - `batch_update(x, w=1)`: update the tdigest with values in array `x` and weight `w`.
 - `compress()`: perform a compression on the underlying data structure that will shrink the memory footprint of it, without hurting accuracy. Good to perform after adding many values. 
 - `percentile(p)`: return the `p`th percentile. Example: `p=50` is the median.
 - `cdf(x)`: return the CDF the value `x` is at. 
 - `trimmed_mean(p1, p2)`: return the mean of data set without the values below and above the `p1` and `p2` percentile respectively. 
 - `serialize()`: return a Python dictionary of the TDigest and internal Centroid values.
 - `deserialize()`: update from serialized dictionary values into the TDigest object.

 



