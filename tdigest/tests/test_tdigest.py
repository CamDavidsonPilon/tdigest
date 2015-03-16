import pytest

from tdigest.tdigest import TDigest, Centroid


@pytest.fixture()
def empty_tdigest():
    return TDigest()

@pytest.fixture()
def example_centroids():
    return [
        Centroid(0.5, 1),
        Centroid(1.1, 1),
        Centroid(1.5, 1),
    ]


class TestTDigest():


    def test_add_centroid(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        new_centroid = Centroid(0.9, 1)
        empty_tdigest._add_centroid(new_centroid)
        assert empty_tdigest.C == [
            Centroid(0.5, 1),
            new_centroid,
            Centroid(1.1, 1),
            Centroid(1.5, 1),
        ]

        last_centroid = Centroid(10., 1)
        empty_tdigest._add_centroid(last_centroid)
        assert empty_tdigest.C == [
            Centroid(0.5, 1),
            new_centroid,
            Centroid(1.1, 1),
            Centroid(1.5, 1),
            last_centroid
        ]    

    def test_compute_centroid_quantile(self, empty_tdigest, example_centroids):
        empty_tdigest.C = example_centroids
        empty_tdigest.n = 3 

        assert empty_tdigest._compute_centroid_quantile(example_centroids[0]) == (1/2. + 0) / 3
        assert empty_tdigest._compute_centroid_quantile(example_centroids[1]) == (1/2. + 1) / 3
        assert empty_tdigest._compute_centroid_quantile(example_centroids[2]) == (1/2. + 2) / 3



