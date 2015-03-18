from random import shuffle, random, choice
import bisect
from operator import itemgetter
from bintrees import FastBinaryTree as BinaryTree


class Centroid(object):

    def __init__(self, mean, count):
        self.mean = float(mean)
        self.count = float(count)

    def update(self, x, delta_weight):
        self.count += delta_weight
        self.mean += delta_weight * (x - self.mean) / self.count
        return

    def __repr__(self):
        return """<Centroid: mean=%.4f, count=%d>""" % (self.mean, self.count)

    def __eq__(self, other):
        return self.mean == other.mean and self.count == other.count


class TDigest(object):

    def __init__(self, delta=0.02, K=50):
        self.C = BinaryTree()
        self.n = 0
        self.delta = delta
        self.K = K

    def __add__(self, other_digest):
        C1 = list(self.C.values())
        C2 = list(other_digest.C.values())
        shuffle(C1)
        shuffle(C2)
        data = C1 + C2
        new_digest = TDigest(self.delta, self.K)
        for c in data:
            new_digest.update((c.mean, c.count))

        return new_digest

    def __len__(self):
        return len(self.C)

    def __repr__(self):
        return """<T-Digest: n=%d, centroids=%d>""" % (self.n, len(self))

    def _add_centroid(self, centroid):
        self.C.insert(centroid.mean, centroid)
        return

    def _compute_centroid_quantile(self, centroid):
        denom = self.n
        cumulative_sum = sum(
            c_i.count for c_i in self.C.value_slice(0, centroid.mean))
        return (centroid.count / 2. + cumulative_sum) / denom

    def batch_update(self, values):
        w = 1
        for x in values:
            self.update((x, w))
        return

    def _get_closest_centroids(self, x):
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

    def update(self, (x, w)):
        self.n += w

        if len(self) == 0:
            self._add_centroid(Centroid(x, w))
            return

        S = self._get_closest_centroids(x)

        while len(S) != 0 and w > 0:
            j = choice(range(len(S)))
            c_j = S[j]

            q = self._compute_centroid_quantile(c_j)
            if c_j.count + w > 4 * self.n * self.delta * q * (1 - q):
                S.pop(j)
                continue

            delta_w = min(4 * self.n * self.delta * q * (1 - q) - c_j.count, w)
            self._update_centroid(c_j, x, delta_w)
            w -= delta_w
            S.pop(j)

        if w > 0:
            self._add_centroid(Centroid(x, w))

        if len(self) > self.K / self.delta:
            self.compress()

        return

    def _update_centroid(self, centroid, x, w):
        self.C.pop(centroid.mean)
        centroid.update(x, w)
        self._add_centroid(centroid)

    def compress(self):
        T = TDigest(self.delta, self.K)
        C = list(self.C.values())
        shuffle(C)
        for c_i in C:
            T.update((c_i.mean, c_i.count))
        self.C = T.C

    def percentile(self, q):
        if not (0 <= q <= 1):
            raise ValueError("q must be between 0 and 1, inclusive.")

        t = 0
        q *= self.n

        for i, key in enumerate(self.C.keys()):
            k = self.C[key].count
            if q < t + k:
                if i == 0:
                    delta = self.C.succ_item(key)[1].mean - self.C[key].mean
                elif i == len(self) - 1:
                    delta = self.C[key].mean - self.C.prev_item(key)[1].mean
                else:
                    delta = (
                        self.C.succ_item(key)[1].mean - self.C.prev_item(key)[1].mean) / 2.
                return self.C[key].mean + ((q - t) / k - 0.5) * delta
            t += k
        return self.C.max_item()[1].mean

    def quantile(self, q):
        t = 0
        N = float(self.n)
        for i, key in enumerate(self.C.keys()):
            if i == len(self) - 1:
                delta = (self.C[key].mean - self.C.prev_item(key)[1].mean) / 2.
            else:
                delta = (self.C.succ_item(key)[1].mean - self.C[key].mean) / 2.
            z = max(-1, (q - self.C[key].mean) / delta)
            if z < 1:
                return t / N + self.C[key].count / N * (z + 1) / 2
            t += self.C[key].count
        return 1


if __name__ == '__main__':
    from numpy import random
    import numpy as np

    T1 = TDigest()
    x = random.random(size=10000)
    T1.batch_update(x)

    print len(T1)
    print T1.percentile(0.2)
    print np.percentile(x, 20)
    T1.compress()
    print len(T1)
    print T1.percentile(0.2)
