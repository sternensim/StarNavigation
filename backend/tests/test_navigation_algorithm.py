"""
Unit tests for higher-level algorithm functions in src/core/navigation.py.

Covers: calculate_target_reached_cutoff, positions_equal,
        select_best_celestial_object, and NavigationState construction.
"""
import pytest

from src.api.models import CelestialObject, Position
from src.core.navigation import (
    MAX_TARGET_REACHED_CUTOFF_KM,
    TARGET_REACHED_CUTOFF_PERCENTAGE,
    NavigationError,
    NavigationState,
    calculate_target_reached_cutoff,
    positions_equal,
    select_best_celestial_object,
)


# ---------------------------------------------------------------------------
# calculate_target_reached_cutoff
# ---------------------------------------------------------------------------

class TestCalculateTargetReachedCutoff:
    def test_50km_route(self):
        # 5% of 50 km = 2.5 km
        assert calculate_target_reached_cutoff(50.0) == pytest.approx(2.5)

    def test_100km_route_hits_exact_cap(self):
        # 5% of 100 km = 5.0 km — exactly at the cap
        assert calculate_target_reached_cutoff(100.0) == pytest.approx(MAX_TARGET_REACHED_CUTOFF_KM)

    def test_200km_route_is_capped(self):
        assert calculate_target_reached_cutoff(200.0) == pytest.approx(MAX_TARGET_REACHED_CUTOFF_KM)

    def test_1000km_route_is_capped(self):
        assert calculate_target_reached_cutoff(1000.0) == pytest.approx(MAX_TARGET_REACHED_CUTOFF_KM)

    def test_10km_route(self):
        assert calculate_target_reached_cutoff(10.0) == pytest.approx(0.5)

    def test_zero_distance(self):
        assert calculate_target_reached_cutoff(0.0) == pytest.approx(0.0)

    def test_percentage_constant_applied(self):
        distance = 80.0
        expected = distance * TARGET_REACHED_CUTOFF_PERCENTAGE
        assert calculate_target_reached_cutoff(distance) == pytest.approx(expected)

    def test_result_never_exceeds_max(self):
        for d in [0, 10, 50, 100, 500, 10000]:
            assert calculate_target_reached_cutoff(d) <= MAX_TARGET_REACHED_CUTOFF_KM


# ---------------------------------------------------------------------------
# positions_equal
# ---------------------------------------------------------------------------

class TestPositionsEqual:
    def test_identical_positions_are_equal(self):
        pos = Position(latitude=52.52, longitude=13.40)
        assert positions_equal(pos, pos) is True

    def test_very_close_positions_within_default_tolerance(self):
        # 0.05 km apart — well within default 0.1 km tolerance
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.00045, longitude=0.0)  # ~50 m north
        assert positions_equal(pos1, pos2) is True

    def test_far_positions_are_not_equal(self):
        berlin = Position(latitude=52.52, longitude=13.40)
        munich = Position(latitude=48.14, longitude=11.58)
        assert positions_equal(berlin, munich) is False

    def test_custom_large_tolerance(self):
        berlin = Position(latitude=52.52, longitude=13.40)
        munich = Position(latitude=48.14, longitude=11.58)
        assert positions_equal(berlin, munich, tolerance_km=600.0) is True

    def test_custom_small_tolerance(self):
        # Positions ~50 m apart but tolerance is only 0.01 km (10 m)
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.00045, longitude=0.0)
        assert positions_equal(pos1, pos2, tolerance_km=0.01) is False

    def test_boundary_just_inside_tolerance(self):
        # tolerance = 1 km; distance ~0.9 km
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.008, longitude=0.0)  # ~890 m
        assert positions_equal(pos1, pos2, tolerance_km=1.0) is True

    def test_boundary_just_outside_tolerance(self):
        pos1 = Position(latitude=0.0, longitude=0.0)
        pos2 = Position(latitude=0.02, longitude=0.0)  # ~2.2 km
        assert positions_equal(pos1, pos2, tolerance_km=1.0) is False


# ---------------------------------------------------------------------------
# select_best_celestial_object
# ---------------------------------------------------------------------------

class TestSelectBestCelestialObject:
    def test_empty_list_returns_none(self):
        assert select_best_celestial_object(90.0, []) is None

    def test_single_object_is_returned(self, star_north):
        result = select_best_celestial_object(0.0, [star_north])
        assert result == star_north

    def test_picks_closest_azimuth_to_target(self, star_north, star_east, star_south):
        # Target bearing 85°: star_east (90°) is closest
        result = select_best_celestial_object(85.0, [star_north, star_east, star_south])
        assert result.name == star_east.name

    def test_picks_north_when_target_is_north(self, star_north, star_east, star_south):
        result = select_best_celestial_object(0.0, [star_north, star_east, star_south])
        assert result.name == star_north.name

    def test_picks_south_when_target_is_south(self, star_north, star_east, star_south):
        result = select_best_celestial_object(180.0, [star_north, star_east, star_south])
        assert result.name == star_south.name

    def test_wraparound_359_prefers_north_star(self, star_north, star_south):
        # Target 359° should prefer star at 0° (1° away) over star at 180° (179° away)
        result = select_best_celestial_object(359.0, [star_north, star_south])
        assert result.name == star_north.name

    def test_object_without_azimuth_is_skipped(self, star_north):
        no_azimuth = CelestialObject(
            name="No Azimuth Star",
            right_ascension=1.0,
            declination=0.0,
            magnitude=3.0,
            object_type="star",
            azimuth=None,
            altitude=30.0,
            is_visible=True,
        )
        # Only no_azimuth in list — should return None
        assert select_best_celestial_object(0.0, [no_azimuth]) is None

    def test_object_without_azimuth_skipped_when_others_present(self, star_north):
        no_azimuth = CelestialObject(
            name="No Azimuth Star",
            right_ascension=1.0,
            declination=0.0,
            magnitude=3.0,
            object_type="star",
            azimuth=None,
            altitude=30.0,
            is_visible=True,
        )
        result = select_best_celestial_object(0.0, [no_azimuth, star_north])
        assert result.name == star_north.name

    def test_prioritize_major_favors_planet_over_closer_star(self):
        # Star is 40° from target bearing; planet is 35° from target bearing.
        # Without prioritize_major:  star=40, planet=35 → planet already wins.
        # With prioritize_major: star=40 (no bonus), planet=max(0, 35-30)=5 → planet wins by larger margin.
        # Use a star that's closer to the target than the planet so we can demonstrate
        # the bonus actually matters:
        #   star at 10° off → score=10 (no bonus)
        #   planet at 35° off → score=max(0, 35-30)=5 → planet wins despite being farther away.
        star_close = CelestialObject(
            name="CloseButDimStar",
            right_ascension=1.0,
            declination=0.0,
            magnitude=3.0,
            object_type="star",
            azimuth=100.0,   # 10° off target bearing of 90°
            altitude=30.0,
            is_visible=True,
        )
        planet_far = CelestialObject(
            name="FarPlanet",
            right_ascension=2.0,
            declination=0.0,
            magnitude=-1.5,
            object_type="planet",
            azimuth=125.0,   # 35° off target bearing of 90°
            altitude=40.0,
            is_visible=True,
        )
        # Without bonus: star wins (10 < 35)
        result_normal = select_best_celestial_object(90.0, [star_close, planet_far], prioritize_major=False)
        assert result_normal.name == star_close.name

        # With bonus: planet effective score = max(0, 35-30) = 5 < star score 10 → planet wins
        result_major = select_best_celestial_object(90.0, [star_close, planet_far], prioritize_major=True)
        assert result_major.name == planet_far.name

    def test_least_changes_favors_higher_altitude(self):
        low = CelestialObject(
            name="LowStar",
            right_ascension=1.0,
            declination=0.0,
            magnitude=2.0,
            object_type="star",
            azimuth=90.0,
            altitude=5.0,   # low — less bonus
            is_visible=True,
        )
        high = CelestialObject(
            name="HighStar",
            right_ascension=2.0,
            declination=0.0,
            magnitude=2.0,
            object_type="star",
            azimuth=95.0,   # 5° further from target
            altitude=90.0,  # zenith — maximum bonus (20°)
            is_visible=True,
        )
        # Target bearing 90°:
        #   low: score = 0° (exact match) - altitude_bonus(5/90*20) ≈ 1.1° → ~0° (max 0)
        #   high: score = 5° - 20° → 0°
        # With least_changes both end up at score 0; whichever is encountered first wins.
        # The test verifies that a high-altitude object far from target *can* beat a low one.
        # Use a more extreme case where the difference is clear:
        high2 = CelestialObject(
            name="HighStar2",
            right_ascension=2.0,
            declination=0.0,
            magnitude=2.0,
            object_type="star",
            azimuth=105.0,  # 15° off target
            altitude=90.0,  # zenith → 20° bonus → effective score = 0
            is_visible=True,
        )
        very_low = CelestialObject(
            name="VeryLowStar",
            right_ascension=1.0,
            declination=0.0,
            magnitude=2.0,
            object_type="star",
            azimuth=91.0,   # 1° off target
            altitude=1.0,   # almost on horizon → ~0.2° bonus → effective score ≈ 0.8°
            is_visible=True,
        )
        result = select_best_celestial_object(90.0, [very_low, high2], optimize_for="least_changes")
        assert result.name == high2.name


# ---------------------------------------------------------------------------
# NavigationState construction
# ---------------------------------------------------------------------------

class TestNavigationState:
    def test_default_fields(self):
        start = Position(latitude=0.0, longitude=0.0)
        target = Position(latitude=10.0, longitude=10.0)
        state = NavigationState(current_position=start, target_position=target)
        assert state.used_objects == set()
        assert state.waypoints == []
        assert state.iteration_count == 0

    def test_custom_used_objects(self):
        start = Position(latitude=0.0, longitude=0.0)
        target = Position(latitude=1.0, longitude=1.0)
        state = NavigationState(
            current_position=start,
            target_position=target,
            used_objects={"Sirius", "Polaris"},
        )
        assert "Sirius" in state.used_objects
        assert "Polaris" in state.used_objects


# ---------------------------------------------------------------------------
# NavigationError
# ---------------------------------------------------------------------------

class TestNavigationError:
    def test_is_exception(self):
        err = NavigationError("no objects")
        assert isinstance(err, Exception)

    def test_message(self):
        err = NavigationError("test message")
        assert str(err) == "test message"
