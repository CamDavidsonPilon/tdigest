from random import shuffle, random, choice
import bisect
from operator import itemgetter


class Centroid(object):

    def __init__(self, mean, count):
        self.mean = mean
        self.count = count

    def update(self, x, delta_weight):
        self.count += delta_weight
        self.mean += delta_weight*(x - self.mean)/self.count
        return 

    def __repr__(self):
        return """<Centroid: mean=%.4f, count=%d>"""%(self.mean, self.count) 


    def __eq__(self, other):
        return self.mean == other.mean and self.count == other.count

class TDigest(object):


    def __init__(self, delta=0.01, K=50):
        self.C = []
        self.n = 0
        self.delta = delta
        self.K = K

    def __add__(self, other_digest):
        C1 = list(self.C)
        C2 = list(other_digest.C)
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
        return """<T-Digest: n=%d, centroids=%d>"""%(self.n, len(self)) 


    def _add_centroid(self, centroid):
        means = map(lambda c: c.mean, self.C)
        ix = bisect.bisect(means, centroid.mean)
        self.C.insert(ix, centroid)
        return


    def _compute_centroid_quantile(self, centroid):
        denom = self.n
        cumulative_sum = sum(c_i.count for c_i in self.C if c_i.mean < centroid.mean)
        return (centroid.count / 2. + cumulative_sum)/denom


    def batch_update(self, values):
        w = 1
        for x in values:
            self.update((x, w))
        return

s
    def update(self, (x, w)):
        self.n += w

        if len(self) == 0:
            self._add_centroid(Centroid(x, w))
            return

        # terrible way to get the argmin. This also doesn't account for ties so has a natural bias. Works 
        # best for non-intergers inputs 
        ix, _ = min(enumerate(abs(c_i.mean - x) for c_i in self.C), key=itemgetter(1))
        S = [self.C[ix]]

        #z = min(abs(c_i.mean - x) for c_i in self.C)
        #S = filter(lambda c_i: abs(c_i.mean - x) == z, self.C)


        while len(S) != 0 and w > 0:
            j = choice(range(len(S)))
            c_j = S[j]

            q = self._compute_centroid_quantile(c_j)
            if c_j.count + w > 4 * self.n * self.delta * q * (1 - q):
                S.pop(j)
                continue

            delta_w = min(4 * self.n * self.delta * q * (1 - q) - c_j.count, w)
            c_j.update(x, delta_w)
            w -= delta_w
            S.pop(j)

        if w > 0:
            self._add_centroid(Centroid(x, w))

        if len(self) > self.K / self.delta:
            self.compress()
        
        return 


    def compress(self):
        T = TDigest(self.delta, self.K)
        C = self.C
        shuffle(C)
        for c_i in C:
            T.update((c_i.mean, c_i.count))
        self.C = T.C


    def percentile(self, q):
        if not (0 <= q <= 1):
            raise ValueError("q must be between 0 and 1, inclusive.")

        t = 0
        q *= self.n

        for i in range(len(self)):
            k = self.C[i].count
            if q < t + k:
                if i == 0:
                    delta = self.C[i+1].mean - self.C[i].mean
                elif i == len(self) -1 :
                    delta = self.C[i].mean - self.C[i-1].mean
                else:
                    delta = (self.C[i+1].mean - self.C[i-1].mean) / 2.
                return self.C[i].mean + ((q - t) / k - 0.5) * delta 
            t += k 
        return self.C[-1].mean


    def quantile(self, q):
        t = 0
        N = float(self.n)
        for i in range(len(self)):
            if i == len(self) - 1:
                delta = (self.C[i].mean - self.C[i-1].mean)/2.
            else:
                delta = (self.C[i+1].mean - self.C[i].mean)/2.
            z = max(-1, (q - self.C[i].mean)/delta)
            if z < 1:
                return t / N + self.C[i].count / N * (z + 1) / 2
            t += self.C[i].count 
        return 1


if __name__=='__main__':
    from numpy import random
    import numpy as np


    T1 = TDigest()
    for x in xrange(2000):
        x = (random.exponential(),1)
        T1.update(x)

    T2 = TDigest()
    for x in xrange(2000):
        x = (random.exponential(),1)
        T2.update(x)

    T3 = TDigest()
    for x in xrange(100000):
        x = (random.exponential(),1)
        T3.update(x)

    T = T1 + T2 + T3
    print len(T)
    print T.percentile(0.1)
    print np.log(1/0.9)


