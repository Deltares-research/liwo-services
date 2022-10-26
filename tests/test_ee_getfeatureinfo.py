import ee

import pytest

store = {}


@pytest.fixture
def image():
    """Image with a constant 42"""
    ee.Initialize()
    image = ee.Image(42).rename(["b1"])
    mapid = image.getMapId()["mapid"]
    return image


@pytest.fixture
def loaded():
    """store an image in the store and load it again"""
    mapid_42 = None
    for i in range(40, 50):
        image = ee.Image(i).rename(["b1"])
        mapid = image.getMapId()["mapid"]
        serialized = ee.data.serializer.toJSON(image)
        # store the images per map id
        store[mapid] = serialized
        if i == 42:
            mapid_42 = mapid

    # now load #42
    loaded = ee.deserializer.fromJSON(store[mapid_42])
    return loaded


@pytest.fixture
def serialized(image):
    serialized = ee.data.serializer.toJSON(image)
    return serialized


@pytest.fixture
def deserialized(serialized):
    return ee.deserializer.fromJSON(serialized)


@pytest.fixture
def point():
    return ee.Geometry.Point(0, 0)


def test_get_feature_info(image, serialized, deserialized, point):
    """create a map and get information on a point"""
    scale = 100
    image_result = image.reduceRegion(ee.Reducer.first(), point, scale).getInfo()["b1"]

    deserialized_result = deserialized.reduceRegion(
        ee.Reducer.first(), point, scale
    ).getInfo()["b1"]

    assert image_result == 42
    assert deserialized_result == 42


def test_get_loaded_feature_info(loaded, point):
    """create a map and get information on a point"""
    scale = 100
    loaded_result = loaded.reduceRegion(ee.Reducer.first(), point, scale).getInfo()[
        "b1"
    ]
    assert loaded_result == 42
