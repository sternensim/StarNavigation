"""
Unit tests for pure math functions in src/core/navigation.py.

These functions have no external dependencies and are fully deterministic,
making them ideal candidates for thorough unit testing.
"""
import math

import pytest

from src.api.models import Position
from src.core.navigation import (
    EARTH_RADIUS_KM,
    calculate_compass_direction,
    circular_distance,
    haversine_distance,
    move_in_direction,
    to_degrees,
    to_radians,
)


# ---------------------------------------------------------------------------
# to_radians / to_degrees
# ---------------------------------------------------------------------------

class TestToRadians:
    def test_zero(self):
        assert to_radians(0) == 0.0

    def test_180_is_pi(self):
        assert to_radians(180) == pytest.approx(math.pi)

    def test_360_is_two_pi(self):
        assert to_radians(360) == pytest.approx(2 * math.pi)

    def test_90_is_half_pi(self):
        assert to_radians(90) == pytest.approx(math.pi / 2)

    def test_negative(self):
        assert to_radians(-90) == pytest.approx(-math.pi / 2)


class TestToDegrees:
    def test_zero(self):
        assert to_degrees(0) == 0.0

    def test_pi_is_180(self):
        assert to_degrees(math.pi) == pytest.approx(180.0)

    def test_two_pi_is_360(self):
        assert to_degrees(2 * math.pi) == pytest.approx(360.0)

    def test_negative(self):
        assert to_degrees(-math.pi / 2) == pytest.approx(-90.0)

    def test_roundtrip(self):
        for angle in [0, 30, 45, 60, 90, 135, 180, 270, 360]:
            assert to_degrees(to_radians(angle)) == pytest.approx(angle)


# ---------------------------------------------------------------------------
# circular_distance
# ---------------------------------------------------------------------------

class TestCircularDistance:
    def test_same_angle(self):
        assert circular_distance(45.0, 45.0) == pytest.approx(0.0)

    def test_simple_difference(self):
        assert circular_distance(0.0, 90.0) == pytest.approx(90.0)

    def test_wraparound_short_path(self):
        # 350° to 10° is 20°, not 340°
        assert circular_distance(350.0, 10.0) == pytest.approx(20.0)

    def test_opposite_sides(self):
        assert circular_distance(0.0, 180.0) == pytest.approx(180.0)

    def test_symmetry(self):
        assert circular_distance(30.0, 200.0) == circular_distance(200.0, 30.0)

    def test_never_exceeds_180(self):
        for a in range(0, 360, 10):
            for b in range(0, 360, 10):
                assert circular_distance(a, b) <= 180.0

    def test_360_equals_0(self):
        # 360° and 0° are the same point
        assert circular_distance(360.0, 0.0) == pytest.approx(0.0)

    def test_270_to_90(self):
        assert circular_distance(270.0, 90.0) == pytest.approx(180.0)


# ---------------------------------------------------------------------------
# haversine_distance
# ---------------------------------------------------------------------------

class TestHaversineDistance:
    def test_same_position_is_zero(self):
        pos = Position(latitude=52.5, longitude=13.4)
        assert haversine_distance(pos, pos) == pytest.approx(0.0, abs=1e-6)

    def test_one_degree_latitude_near_equator(self):
        # 1° of latitude ≈ 111.195 km
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=1.0, longitude=0.0)
        dist = haversine_distance(pos1, pos2)
        assert dist == pytest.approx(111.195, rel=0.001)

    def test_one_degree_longitude_at_equator(self):
        # 1° of longitude at equator ≈ 111.195 km
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.0, longitude=1.0)
        dist = haversine_distance(pos1, pos2)
        assert dist == pytest.approx(111.195, rel=0.001)

    def test_berlin_to_munich(self):
        # Real-world reference: ~504 km
        berlin = Position(latitude=52.5200, longitude=13.4050)
        munich = Position(latitude=48.1351, longitude=11.5820)
        dist = haversine_distance(berlin, munich)
        assert dist == pytest.approx(504.0, rel=0.01)

    def test_symmetry(self):
        pos1 = Position(latitude=10.0, longitude=20.0)
        pos2 = Position(latitude=30.0, longitude=40.0)
        assert haversine_distance(pos1, pos2) == pytest.approx(haversine_distance(pos2, pos1))

    def test_antipodal_points(self):
        # Opposite ends of Earth ≈ π × R ≈ 20015 km
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.0, longitude=180.0)
        dist = haversine_distance(pos1, pos2)
        assert dist == pytest.approx(math.pi * EARTH_RADIUS_KM, rel=0.001)

    def test_north_south_poles(self):
        north = Position(latitude=90.0, longitude=0.0)
        south = Position(latitude=-90.0, longitude=0.0)
        dist = haversine_distance(north, south)
        assert dist == pytest.approx(math.pi * EARTH_RADIUS_KM, rel=0.001)

    def test_altitude_ignored(self):
        # haversine uses lat/lon only — altitude doesn't affect the result
        pos1 = Position(latitude=0.0, longitude=0.0, altitude=0.0)
        pos2 = Position(latitude=0.0, longitude=0.0, altitude=8848.0)
        assert haversine_distance(pos1, pos2) == pytest.approx(0.0, abs=1e-6)


# ---------------------------------------------------------------------------
# calculate_compass_direction
# ---------------------------------------------------------------------------

class TestCalculateCompassDirection:
    def test_due_north(self):
        # Moving north: bearing should be ~0°
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=1.0, longitude=0.0)
        bearing = calculate_compass_direction(pos1, pos2)
        assert bearing == pytest.approx(0.0, abs=0.1)

    def test_due_south(self):
        pos1 = Position(latitude=1.0, longitude=0.0)
        pos2 = Position(latitude=0.0, longitude=0.0)
        bearing = calculate_compass_direction(pos1, pos2)
        assert bearing == pytest.approx(180.0, abs=0.1)

    def test_due_east(self):
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.0, longitude=1.0)
        bearing = calculate_compass_direction(pos1, pos2)
        assert bearing == pytest.approx(90.0, abs=0.1)

    def test_due_west(self):
        pos1 = Position(latitude=0.0, longitude=1.0)
        pos2 = Position(latitude=0.0, longitude=0.0)
        bearing = calculate_compass_direction(pos1, pos2)
        assert bearing == pytest.approx(270.0, abs=0.1)

    def test_northeast(self):
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=1.0, longitude=1.0)
        bearing = calculate_compass_direction(pos1, pos2)
        assert 0.0 < bearing < 90.0

    def test_result_always_in_0_to_360(self):
        positions = [
            (Position(latitude=0, longitude=0), Position(latitude=1, longitude=1)),
            (Position(latitude=10, longitude=20), Position(latitude=-5, longitude=-15)),
            (Position(latitude=-45, longitude=170), Position(latitude=45, longitude=-170)),
        ]
        for p1, p2 in positions:
            b = calculate_compass_direction(p1, p2)
            assert 0.0 <= b < 360.0

    def test_berlin_to_munich_is_roughly_southwest(self):
        berlin = Position(latitude=52.5200, longitude=13.4050)
        munich = Position(latitude=48.1351, longitude=11.5820)
        bearing = calculate_compass_direction(berlin, munich)
        # Munich is SW of Berlin: between 180° and 270°
        assert 180.0 < bearing < 270.0


# ---------------------------------------------------------------------------
# move_in_direction
# ---------------------------------------------------------------------------

class TestMoveInDirection:
    def test_move_north_increases_latitude(self):
        pos = Position(latitude=0.0, longitude=0.0)
        result = move_in_direction(pos, bearing_degrees=0.0, distance_km=100.0)
        assert result.latitude > pos.latitude
        assert result.longitude == pytest.approx(pos.longitude, abs=0.01)

    def test_move_east_increases_longitude(self):
        pos = Position(latitude=0.0, longitude=0.0)
        result = move_in_direction(pos, bearing_degrees=90.0, distance_km=100.0)
        assert result.longitude > pos.longitude
        assert result.latitude == pytest.approx(pos.latitude, abs=0.01)

    def test_move_south_decreases_latitude(self):
        pos = Position(latitude=10.0, longitude=0.0)
        result = move_in_direction(pos, bearing_degrees=180.0, distance_km=100.0)
        assert result.latitude < pos.latitude

    def test_move_west_decreases_longitude(self):
        pos = Position(latitude=0.0, longitude=10.0)
        result = move_in_direction(pos, bearing_degrees=270.0, distance_km=100.0)
        assert result.longitude < pos.longitude

    def test_distance_is_approximately_correct(self):
        pos = Position(latitude=0.0, longitude=0.0)
        distance_km = 200.0
        result = move_in_direction(pos, bearing_degrees=45.0, distance_km=distance_km)
        actual_distance = haversine_distance(pos, result)
        assert actual_distance == pytest.approx(distance_km, rel=0.001)

    def test_roundtrip_north_south(self):
        pos = Position(latitude=10.0, longitude=20.0)
        north = move_in_direction(pos, bearing_degrees=0.0, distance_km=500.0)
        back = move_in_direction(north, bearing_degrees=180.0, distance_km=500.0)
        assert back.latitude == pytest.approx(pos.latitude, abs=0.01)
        assert back.longitude == pytest.approx(pos.longitude, abs=0.01)

    def test_altitude_is_preserved(self):
        pos = Position(latitude=0.0, longitude=0.0, altitude=1500.0)
        result = move_in_direction(pos, bearing_degrees=90.0, distance_km=100.0)
        assert result.altitude == pytest.approx(1500.0)

    def test_zero_distance_returns_same_position(self):
        pos = Position(latitude=48.0, longitude=11.0)
        result = move_in_direction(pos, bearing_degrees=45.0, distance_km=0.0)
        assert result.latitude == pytest.approx(pos.latitude, abs=1e-8)
        assert result.longitude == pytest.approx(pos.longitude, abs=1e-8)

    def test_one_degree_north_at_equator(self):
        # Moving ~111 km north from equator should add roughly 1 degree of latitude
        pos = Position(latitude=0.0, longitude=0.0)
        result = move_in_direction(pos, bearing_degrees=0.0, distance_km=111.195)
        assert result.latitude == pytest.approx(1.0, abs=0.01)
