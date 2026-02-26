"""
Shared pytest fixtures for the NavigationApp backend test suite.
"""
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.api.models import Position, CelestialObject, Waypoint


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def berlin():
    """Position fixture: Berlin, Germany."""
    return Position(latitude=52.5200, longitude=13.4050)


@pytest.fixture
def munich():
    """Position fixture: Munich, Germany."""
    return Position(latitude=48.1351, longitude=11.5820)


@pytest.fixture
def origin():
    """Position fixture: (0, 0) — null island."""
    return Position(latitude=0.0, longitude=0.0)


@pytest.fixture
def observation_time():
    """A fixed UTC observation time for deterministic tests."""
    return datetime(2024, 6, 21, 22, 0, 0)  # Summer solstice, 22:00 UTC


@pytest.fixture
def star_north():
    """A star directly north of the observer (azimuth=0)."""
    return CelestialObject(
        name="North Star",
        right_ascension=2.53,
        declination=89.26,
        magnitude=1.97,
        object_type="star",
        azimuth=0.0,
        altitude=45.0,
        is_visible=True,
    )


@pytest.fixture
def star_east():
    """A star directly east of the observer (azimuth=90)."""
    return CelestialObject(
        name="East Star",
        right_ascension=6.0,
        declination=0.0,
        magnitude=2.0,
        object_type="star",
        azimuth=90.0,
        altitude=30.0,
        is_visible=True,
    )


@pytest.fixture
def star_south():
    """A star directly south of the observer (azimuth=180)."""
    return CelestialObject(
        name="South Star",
        right_ascension=12.0,
        declination=-30.0,
        magnitude=2.5,
        object_type="star",
        azimuth=180.0,
        altitude=20.0,
        is_visible=True,
    )


@pytest.fixture
def planet_east():
    """A planet near east (azimuth=85) — should win with prioritize_major."""
    return CelestialObject(
        name="Jupiter",
        right_ascension=5.5,
        declination=22.0,
        magnitude=-2.0,
        object_type="planet",
        azimuth=85.0,
        altitude=40.0,
        is_visible=True,
    )


@pytest.fixture
def sample_waypoints():
    """Two simple waypoints for export tests."""
    wp1 = Waypoint(
        position=Position(latitude=52.52, longitude=13.40),
        reference_object=None,
        reason="target_reached",
        timestamp=datetime(2024, 6, 21, 22, 0, 0),
        distance_to_target=0.0,
    )
    wp2 = Waypoint(
        position=Position(latitude=48.14, longitude=11.58),
        reference_object=CelestialObject(
            name="Sirius",
            right_ascension=6.75,
            declination=-16.72,
            magnitude=-1.46,
            object_type="star",
            azimuth=200.0,
            altitude=35.0,
            is_visible=True,
        ),
        reason="object_lost",
        timestamp=datetime(2024, 6, 21, 23, 0, 0),
        distance_to_target=10.0,
    )
    return [wp1, wp2]
