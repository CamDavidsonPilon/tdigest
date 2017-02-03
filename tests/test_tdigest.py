import pytest
from numpy import random
from numpy import percentile
from numpy import bitwise_and
from numpy import testing
from tdigest.tdigest import TDigest, Centroid
from tdigest.accumulation_tree import AccumulationTree

def RBTree(data):
    t = AccumulationTree(lambda centroid: centroid.count)
    for k, v in data:
        t.insert(k, v)
    return t

@pytest.fixture()
def empty_tdigest():
    return TDigest()


@pytest.fixture()
def example_positive_centroids():
    return RBTree([
        (0.5, Centroid(0.5, 1)),
        (1.1, Centroid(1.1, 1)),
        (1.5, Centroid(1.5, 1)),
    ])


@pytest.fixture()
def example_centroids():
    return RBTree([
        (-1.1, Centroid(-1.1, 1)),
        (-0.5, Centroid(-0.5, 1)),
        (0.1, Centroid(0.1, 1)),
        (1.5, Centroid(1.5, 1)),
    ])


@pytest.fixture()
def example_random_data():
    return random.randn(100)


class TestTDigest():

    def test_add_centroid(self, empty_tdigest, example_positive_centroids):
        empty_tdigest.C = example_positive_centroids
        new_centroid = Centroid(0.9, 1)
        empty_tdigest._add_centroid(new_centroid)
        assert (empty_tdigest.C - RBTree([
            (0.5, Centroid(0.5, 1)),
            (new_centroid.mean, new_centroid),
            (1.1, Centroid(1.1, 1)),
            (1.5, Centroid(1.5, 1)),
        ])).is_empty()

        last_centroid = Centroid(10., 1)
        empty_tdigest._add_centroid(last_centroid)
        assert (empty_tdigest.C - RBTree([
            (0.5, Centroid(0.5, 1)),
            (new_centroid.mean, new_centroid),
            (1.1, Centroid(1.1, 1)),
            (1.5, Centroid(1.5, 1)),
            (last_centroid.mean, last_centroid),
        ])).is_empty()

    def test_add_centroid_if_key_already_present(self, empty_tdigest, example_positive_centroids):
        empty_tdigest.C = example_positive_centroids
        new_centroid = Centroid(1.1, 5)
        empty_tdigest._add_centroid(new_centroid)
        assert (empty_tdigest.C - RBTree([
            (0.5, Centroid(0.5, 1)),
            (1.1, Centroid(1.1, 1 + 5)),
            (1.5, Centroid(1.5, 1)),
        ])).is_empty()

    def test_compute_centroid_quantile(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        empty_tdigest.n = 4

        assert empty_tdigest._compute_centroid_quantile(example_centroids[-1.1]) == (1 / 2. + 0) / 4
        assert empty_tdigest._compute_centroid_quantile(example_centroids[-0.5]) == (1 / 2. + 1) / 4
        assert empty_tdigest._compute_centroid_quantile(example_centroids[0.1]) == (1 / 2. + 2) / 4
        assert empty_tdigest._compute_centroid_quantile(example_centroids[1.5]) == (1 / 2. + 3) / 4



    def test_find_closest_centroids_works_with_positive_values(self, empty_tdigest, example_positive_centroids):
        empty_tdigest.C = example_positive_centroids
        assert empty_tdigest._find_closest_centroids(0.0) == [example_positive_centroids[0.5]]
        assert empty_tdigest._find_closest_centroids(2.0) == [example_positive_centroids[1.5]]
        assert empty_tdigest._find_closest_centroids(1.1) == [example_positive_centroids[1.1]]
        assert empty_tdigest._find_closest_centroids(1.2) == [example_positive_centroids[1.1]]
        assert empty_tdigest._find_closest_centroids(1.4) == [example_positive_centroids[1.5]]
        assert empty_tdigest._find_closest_centroids(1.3) == [example_positive_centroids[1.5],
                                                             example_positive_centroids[1.1]]


    def test_get_closest_centroids_works_with_negative_values(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        assert empty_tdigest._find_closest_centroids(0.0) == [example_centroids[0.1]]
        assert empty_tdigest._find_closest_centroids(-2.0) == [example_centroids[-1.1]]
        assert empty_tdigest._find_closest_centroids(-0.6) == [example_centroids[-0.5]]
        assert empty_tdigest._find_closest_centroids(-0.4) == [example_centroids[-0.5]]


    def test_compress(self, empty_tdigest, example_random_data):
        empty_tdigest.batch_update(example_random_data)
        precompress_n, precompress_len = empty_tdigest.n, len(empty_tdigest)
        empty_tdigest.compress()
        postcompress_n, postcompress_len = empty_tdigest.n, len(empty_tdigest)
        assert postcompress_n == precompress_n
        assert postcompress_len <= precompress_len

    def test_data_comes_in_sorted_does_not_blow_up(self, empty_tdigest):
        t = TDigest()
        for x in range(10000):
            t.update(x,1)

        assert len(t) < 5000

        t = TDigest()
        t.batch_update(range(10000))
        assert len(t) < 1000

    def test_extreme_percentiles_return_min_and_max(self, empty_tdigest):
        t = TDigest()
        data = random.randn(100000)
        t.batch_update(data)
        assert t.percentile(0) == data.min()
        assert t.percentile(100.) == data.max()

    def test_negative_extreme_percentile_is_still_positive(self, empty_tdigest):
        # Test https://github.com/CamDavidsonPilon/tdigest/issues/16
        t = TDigest()
        t.batch_update([62.0, 202.0, 1415.0, 1433.0])
        assert t.percentile(0.25) > 0

    def test_adding_centroid_with_exisiting_key_does_not_break_synchronicity(self, empty_tdigest, example_centroids):
        td = empty_tdigest
        td.C = example_centroids
        assert -1.1 in td.C
        td._add_centroid(Centroid(-1.1, 10))
        assert all([k == centroid.mean for k, centroid in td.C.items()])

    def test_quantile_with_single_centroid(self, empty_tdigest):
        td = empty_tdigest
        td.update(1)
        assert td.quantile(1) == 1

    def test_quantile_with_single_centroid_at_zero(self, empty_tdigest):
        td = empty_tdigest
        td.update(0)
        assert td.quantile(0) == 1



class TestStatisticalTests():

    def test_uniform(self):
        t = TDigest()
        x = random.random(size=10000)
        t.batch_update(x)

        assert abs(t.percentile(50) - 0.5) < 0.02
        assert abs(t.percentile(10) - .1) < 0.01
        assert abs(t.percentile(90) - 0.9) < 0.01
        assert abs(t.percentile(1) - 0.01) < 0.005
        assert abs(t.percentile(99) - 0.99) < 0.005
        assert abs(t.percentile(0.1) - 0.001) < 0.001
        assert abs(t.percentile(99.9) - 0.999) < 0.001

    def test_ints(self):
        t = TDigest()
        t.batch_update([1,2,3])
        assert t.percentile(50) == 2

        t = TDigest()
        x = [1,2,2,2,2,2,2,2,3]
        t.batch_update(x)
        assert t.percentile(50) == 2
        assert sum([c.count for c in t.C.values()]) == len(x)

    @pytest.mark.parametrize("percentile_range", [[0, 7], [27, 47], [39, 66], [81, 99], [77, 100], [0,100]])
    @pytest.mark.parametrize("data_size", [100, 1000, 5000])
    def test_trimmed_mean(self, percentile_range, data_size):
        p1 = percentile_range[0]
        p2 = percentile_range[1]

        t = TDigest()
        x = random.random(size=data_size)
        t.batch_update(x)

        tm_actual = t.trimmed_mean(p1, p2)
        tm_expected = x[bitwise_and(x >= percentile(x, p1), x <= percentile(x, p2))].mean()

        testing.assert_allclose(tm_actual, tm_expected, rtol= 0.01, atol= 0.01)

class TestCentroid():

    def test_update(self):
        c = Centroid(0, 0)
        value, weight = 1, 1
        c.update(value, weight)
        assert c.count == 1
        assert c.mean == 1

        value, weight = 2, 1
        c.update(value, weight)
        assert c.count == 2
        assert c.mean == (2 + 1.) / 2.

        value, weight = 1, 2
        c.update(value, weight)
        assert c.count == 4
        assert c.mean == 1 * 1 / 4. + 2 * 1 / 4. + 1 * 2 / 4.
