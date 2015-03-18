import random
from bintrees import BinaryTree
import pytest

from tdigest.tdigest import TDigest, Centroid


@pytest.fixture()
def empty_tdigest():
    return TDigest()


@pytest.fixture()
def example_centroids():
    return BinaryTree([
        (0.5, Centroid(0.5, 1)),
        (1.1, Centroid(1.1, 1)),
        (1.5, Centroid(1.5, 1)),
    ])


@pytest.fixture()
def example_random_data():
    return [random.random() for _ in xrange(100)]


class TestTDigest():

    def test_add_centroid(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        new_centroid = Centroid(0.9, 1)
        empty_tdigest._add_centroid(new_centroid)
        assert (empty_tdigest.C - BinaryTree([
            (0.5, Centroid(0.5, 1)),
            (new_centroid.mean, new_centroid),
            (1.1, Centroid(1.1, 1)),
            (1.5, Centroid(1.5, 1)),
        ])).is_empty()

        last_centroid = Centroid(10., 1)
        empty_tdigest._add_centroid(last_centroid)
        assert (empty_tdigest.C - BinaryTree([
            (0.5, Centroid(0.5, 1)),
            (new_centroid.mean, new_centroid),
            (1.1, Centroid(1.1, 1)),
            (1.5, Centroid(1.5, 1)),
            (last_centroid.mean, last_centroid),
        ])).is_empty()

    def test_compute_centroid_quantile(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        empty_tdigest.n = 3

        assert empty_tdigest._compute_centroid_quantile(
            example_centroids[0.5]) == (1 / 2. + 0) / 3
        assert empty_tdigest._compute_centroid_quantile(
            example_centroids[1.1]) == (1 / 2. + 1) / 3
        assert empty_tdigest._compute_centroid_quantile(
            example_centroids[1.5]) == (1 / 2. + 2) / 3

    def test_get_closest_centroids(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        assert empty_tdigest._get_closest_centroids(
            0.0) == [example_centroids[0.5]]
        assert empty_tdigest._get_closest_centroids(
            2.0) == [example_centroids[1.5]]
        assert empty_tdigest._get_closest_centroids(
            1.1) == [example_centroids[1.1]]
        assert empty_tdigest._get_closest_centroids(
            1.2) == [example_centroids[1.1]]
        assert empty_tdigest._get_closest_centroids(
            1.4) == [example_centroids[1.5]]
        assert empty_tdigest._get_closest_centroids(
            1.3) == [example_centroids[1.5], example_centroids[1.1]]

    def test_compress(self, empty_tdigest, example_random_data):
        empty_tdigest.batch_update(example_random_data)
        precompress_n, precompress_len = empty_tdigest.n, len(empty_tdigest)
        empty_tdigest.compress()
        postcompress_n, postcompress_len = empty_tdigest.n, len(empty_tdigest)
        assert postcompress_n == precompress_n
        assert postcompress_len <= precompress_len


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
