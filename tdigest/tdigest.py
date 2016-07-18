from __future__ import print_function

from random import choice
from bintrees import FastRBTree as RBTree
import pyudorandom
from itertools import chain

class Centroid(object):

    def __init__(self, mean, count):
        self.mean = float(mean)
        self.count = float(count)

    def __repr__(self):
        return """<Centroid: mean=%.8f, count=%d>""" % (self.mean, self.count)

    def __eq__(self, other):
        return self.mean == other.mean and self.count == other.count

    def update(self, x, weight):
        self.count += weight
        self.mean += weight * (x - self.mean) / self.count
        return


class TDigest(object):

    def __init__(self, delta=0.01, K=25):
        self.C = RBTree()
        self.n = 0
        self.delta = delta
        self.K = K

    def __add__(self, other_digest):
        data = list(chain(self.C.values(), other_digest.C.values()))
        new_digest = TDigest(self.delta, self.K)
        
        if len(data) > 0:
            for c in pyudorandom.items(data):
                new_digest.update(c.mean, c.count)

        return new_digest

    def __len__(self):
        return len(self.C)

    def __repr__(self):
        return """<T-Digest: n=%d, centroids=%d>""" % (self.n, len(self))

    def _add_centroid(self, centroid):
        if centroid.mean not in self.C:
            self.C.insert(centroid.mean, centroid)
        else:
            self.C[centroid.mean].update(centroid.mean, centroid.count)

    def _compute_centroid_quantile(self, centroid):
        denom = self.n
        cumulative_sum = sum(
            c_i.count for c_i in self.C.value_slice(-float('Inf'), centroid.mean))
        return (centroid.count / 2. + cumulative_sum) / denom

    def _update_centroid(self, centroid, x, w):
        self.C.pop(centroid.mean)
        centroid.update(x, w)
        self._add_centroid(centroid)

    def _find_closest_centroids(self, x):
        try:
            ceil_key = self.C.ceiling_key(x)
        except KeyError:
            floor_key = self.C.floor_key(x)
            return [self.C[floor_key]]

        try:
            floor_key = self.C.floor_key(x)
        except KeyError:
            ceil_key = self.C.ceiling_key(x)
            return [self.C[ceil_key]]

        if abs(floor_key - x) < abs(ceil_key - x):
            return [self.C[floor_key]]
        elif abs(floor_key - x) == abs(ceil_key - x) and (ceil_key != floor_key):
            return [self.C[ceil_key], self.C[floor_key]]
        else:
            return [self.C[ceil_key]]

    def _theshold(self, q):
        return 4 * self.n * self.delta * q * (1 - q)

    def update(self, x, w=1):
        """
        Update the t-digest with value x and weight w.

        """
        self.n += w

        if len(self) == 0:
            self._add_centroid(Centroid(x, w))
            return

        S = self._find_closest_centroids(x)

        while len(S) != 0 and w > 0:
            j = choice(list(range(len(S))))
            c_j = S[j]

            q = self._compute_centroid_quantile(c_j)

            # This filters the out centroids that do not satisfy the second part
            # of the definition of S. See original paper by Dunning. 
            if c_j.count + w > self._theshold(q):
                S.pop(j)
                continue

            delta_w = min(self._theshold(q) - c_j.count, w)
            self._update_centroid(c_j, x, delta_w)
            w -= delta_w
            S.pop(j)

        if w > 0:
            self._add_centroid(Centroid(x, w))

        if len(self) > self.K / self.delta:
            self.compress()

        return

    def batch_update(self, values, w=1):
        """
        Update the t-digest with an iterable of values. This assumes all points have the 
        same weight.
        """
        for x in values:
            self.update(x, w)
        self.compress()
        return

    def compress(self):
        T = TDigest(self.delta, self.K)
        C = list(self.C.values())
        for c_i in pyudorandom.items(C):
            T.update(c_i.mean, c_i.count)
        self.C = T.C

    def percentile(self, p):
        """ 
        Computes the percentile of a specific value in [0,100].

        """
        if not (0 <= p <= 100):
            raise ValueError("p must be between 0 and 100, inclusive.")

        t = 0
        p = float(p)/100.
        p *= self.n

        for i, key in enumerate(self.C.keys()):
            c_i = self.C[key]
            k = c_i.count
            if p < t + k:
                if i == 0:
                    return c_i.mean
                elif i == len(self) - 1:
                    return c_i.mean
                else:
                    delta = (self.C.succ_item(key)[1].mean - self.C.prev_item(key)[1].mean) / 2.
                return c_i.mean + ((p - t) / k - 0.5) * delta

            t += k
        return self.C.max_item()[1].mean

    def quantile(self, q):
        """ 
        Computes the quantile of a specific value, ie. computes F(q) where F denotes
        the CDF of the distribution. 

        """
        t = 0
        N = float(self.n)

        for i, key in enumerate(self.C.keys()):
            c_i = self.C[key]
            if i == len(self) - 1:
                delta = (c_i.mean - self.C.prev_item(key)[1].mean) / 2.
            else:
                delta = (self.C.succ_item(key)[1].mean - c_i.mean) / 2.
            z = max(-1, (q - c_i.mean) / delta)

            if z < 1:
                return t / N + c_i.count / N * (z + 1) / 2

            t += c_i.count
        return 1

    def trimmed_mean(self, p1, p2):
        """
        Computes the mean of the distribution between the two percentiles p1 and p2.
        This is a modified algorithm than the one presented in the original t-Digest paper. 

        """
        if not (p1 < p2):
            raise ValueError("p1 must be between 0 and 100 and less than p2.")

        s = k = t = 0
        p1 /= 100.
        p2 /= 100.
        p1 *= self.n
        p2 *= self.n
        for i, key in enumerate(self.C.keys()):
            c_i = self.C[key]
            k_i = c_i.count
            if p1 < t + k_i:
                if i == 0:
                    delta = self.C.succ_item(key)[1].mean - c_i.mean
                elif i == len(self) - 1:
                    delta = c_i.mean - self.C.prev_item(key)[1].mean
                else:
                    delta = (self.C.succ_item(key)[1].mean - self.C.prev_item(key)[1].mean) / 2.
                nu = ((p1 - t) / k_i - 0.5) * delta
                s += nu * k_i * c_i.mean
                k += nu * k_i

            if p2 < t + k_i:
                return s/k
            t += k_i

        return s/k



if __name__ == '__main__':
    from numpy import random
    import numpy as np

    T1 = TDigest()
    x = random.random(size=10000)
    T1.batch_update(x)

    print(abs(T1.percentile(50) - 0.5))
    print(abs(T1.percentile(10) - .1))
    print(abs(T1.percentile(90) - 0.9))
    print(abs(T1.percentile(1) - 0.01))
    print(abs(T1.percentile(0.1) - 0.001))
    print(T1.trimmed_mean(0.5, 1.))





