## Changelog

### 0.3.0
 - The definition of percentile was used incorrectly in tdigest. Previous to 0.3.0, 
  a percentile was defined between 0 and 1. In fact, a percentile is defined between 0 and 100 (hence the 'percent' in percentile). This follows other conventions, like in Numpy and Scipy. This affects the `TDigest.percentile` function. 

### 0.2.0
 - Make the *tdigest* library Python3 compatible. 

### 0.1.2

 - the `TDigest` was not handling ints very well. For example, given `[1,2,2,2,2,2,3]`, it would return that the percentile was `3`. With the fix, it is possible that a centroid can exceed its size threshold.
 - `batch_update` function now has a kwarg to specify the weight of all elements in the inputted array.
