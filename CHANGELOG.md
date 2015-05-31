## Changelog

### 0.1.2

 - the `TDigest` was not handling ints very well. For example, given `[1,2,2,2,2,2,3]`, it would return that the percentile was `3`. With the fix, it is possible that a centroid can exceed its size threshold.
 - `batch_update` function now has a kwarg to specify the weight of all elements in the inputted array.
