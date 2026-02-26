"""
Integration tests for the navigation API endpoints.

Uses FastAPI's TestClient (backed by httpx) so no server needs to be running.
The /navigation/calculate endpoint calls the real Skyfield celestial data, so
those tests mock the data layer to stay fast and deterministic.
"""
from datetime import datetime
from unittest.mock import patch

import pytest

from src.api.models import CelestialObject, Position


# ---------------------------------------------------------------------------
# Health / root endpoints
# ---------------------------------------------------------------------------

class TestHealthEndpoints:
    def test_health_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "healthy"}

    def test_root_returns_api_info(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        body = resp.json()
        assert "name" in body
        assert "version" in body
        assert "endpoints" in body


# ---------------------------------------------------------------------------
# GET /api/v1/navigation/direction
# ---------------------------------------------------------------------------

class TestDirectionEndpoint:
    BASE = "/api/v1/navigation/direction"

    def test_due_north(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": 0.0, "from_lon": 0.0,
            "to_lat": 1.0, "to_lon": 0.0,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["bearing"] == pytest.approx(0.0, abs=0.5)
        assert body["cardinal_direction"] == "N"

    def test_due_east(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": 0.0, "from_lon": 0.0,
            "to_lat": 0.0, "to_lon": 1.0,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["bearing"] == pytest.approx(90.0, abs=0.5)
        assert body["cardinal_direction"] == "E"

    def test_due_south(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": 1.0, "from_lon": 0.0,
            "to_lat": 0.0, "to_lon": 0.0,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["bearing"] == pytest.approx(180.0, abs=0.5)
        assert body["cardinal_direction"] == "S"

    def test_due_west(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": 0.0, "from_lon": 1.0,
            "to_lat": 0.0, "to_lon": 0.0,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert body["bearing"] == pytest.approx(270.0, abs=0.5)
        assert body["cardinal_direction"] == "W"

    def test_response_has_required_fields(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": 52.52, "from_lon": 13.40,
            "to_lat": 48.14, "to_lon": 11.58,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "bearing" in body
        assert "cardinal_direction" in body

    def test_bearing_in_valid_range(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": -45.0, "from_lon": 170.0,
            "to_lat": 45.0, "to_lon": -170.0,
        })
        assert resp.status_code == 200
        bearing = resp.json()["bearing"]
        assert 0.0 <= bearing < 360.0

    def test_invalid_latitude_returns_422(self, client):
        resp = client.get(self.BASE, params={
            "from_lat": 999.0, "from_lon": 0.0,
            "to_lat": 0.0, "to_lon": 0.0,
        })
        assert resp.status_code == 422

    def test_missing_params_returns_422(self, client):
        resp = client.get(self.BASE, params={"from_lat": 0.0})
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /api/v1/navigation/export/gpx
# ---------------------------------------------------------------------------

class TestExportGpxEndpoint:
    BASE = "/api/v1/navigation/export/gpx"

    def test_returns_200(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "gpx",
            "name": "test_route",
        }
        resp = client.post(self.BASE, json=payload)
        assert resp.status_code == 200

    def test_format_field_is_gpx(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "gpx",
            "name": "test_route",
        }
        resp = client.post(self.BASE, json=payload)
        assert resp.json()["format"] == "gpx"

    def test_content_is_valid_xml(self, client, sample_waypoints):
        import xml.etree.ElementTree as ET
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "gpx",
            "name": "my_route",
        }
        resp = client.post(self.BASE, json=payload)
        content = resp.json()["content"]
        # Should parse without error
        ET.fromstring(content)

    def test_gpx_contains_waypoint_coordinates(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "gpx",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        content = resp.json()["content"]
        assert "52.52" in content
        assert "13.4" in content

    def test_gpx_uses_provided_name(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "gpx",
            "name": "MyCustomRoute",
        }
        resp = client.post(self.BASE, json=payload)
        assert "MyCustomRoute" in resp.json()["content"]

    def test_waypoint_with_no_reference_object(self, client):
        from src.api.models import Waypoint
        wp = Waypoint(
            position=Position(latitude=10.0, longitude=20.0),
            reference_object=None,
            reason="target_reached",
            timestamp=datetime(2024, 1, 1, 0, 0, 0),
            distance_to_target=0.0,
        )
        payload = {
            "waypoints": [wp.model_dump(mode="json")],
            "format": "gpx",
            "name": "solo",
        }
        resp = client.post(self.BASE, json=payload)
        assert resp.status_code == 200
        assert "Direct" in resp.json()["content"]

    def test_empty_waypoints_returns_200(self, client):
        payload = {"waypoints": [], "format": "gpx", "name": "empty"}
        resp = client.post(self.BASE, json=payload)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/v1/navigation/export/geojson
# ---------------------------------------------------------------------------

class TestExportGeoJsonEndpoint:
    BASE = "/api/v1/navigation/export/geojson"

    def test_returns_200(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        assert resp.status_code == 200

    def test_format_field_is_geojson(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        assert resp.json()["format"] == "geojson"

    def test_content_is_feature_collection(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        content = resp.json()["content"]
        assert content["type"] == "FeatureCollection"
        assert "features" in content

    def test_two_waypoints_includes_linestring_first(self, client, sample_waypoints):
        payload = {
            "waypoints": [wp.model_dump(mode="json") for wp in sample_waypoints],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        features = resp.json()["content"]["features"]
        assert features[0]["geometry"]["type"] == "LineString"

    def test_single_waypoint_has_no_linestring(self, client, sample_waypoints):
        payload = {
            "waypoints": [sample_waypoints[0].model_dump(mode="json")],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        features = resp.json()["content"]["features"]
        types = [f["geometry"]["type"] for f in features]
        assert "LineString" not in types

    def test_point_coordinates_are_lon_lat_order(self, client, sample_waypoints):
        # GeoJSON standard: [longitude, latitude]
        payload = {
            "waypoints": [sample_waypoints[0].model_dump(mode="json")],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        features = resp.json()["content"]["features"]
        point_feature = next(f for f in features if f["geometry"]["type"] == "Point")
        coords = point_feature["geometry"]["coordinates"]
        # sample_waypoints[0] has lat=52.52, lon=13.40
        assert coords[0] == pytest.approx(13.40)   # longitude first
        assert coords[1] == pytest.approx(52.52)   # latitude second

    def test_properties_contain_reason(self, client, sample_waypoints):
        payload = {
            "waypoints": [sample_waypoints[0].model_dump(mode="json")],
            "format": "geojson",
            "name": "test",
        }
        resp = client.post(self.BASE, json=payload)
        features = resp.json()["content"]["features"]
        point_feature = next(f for f in features if f["geometry"]["type"] == "Point")
        assert "reason" in point_feature["properties"]

    def test_empty_waypoints_returns_200(self, client):
        payload = {"waypoints": [], "format": "geojson", "name": "empty"}
        resp = client.post(self.BASE, json=payload)
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# POST /api/v1/navigation/calculate  (mocked celestial layer)
# ---------------------------------------------------------------------------

def _make_star(name: str, azimuth: float, altitude: float = 45.0) -> CelestialObject:
    return CelestialObject(
        name=name,
        right_ascension=1.0,
        declination=0.0,
        magnitude=2.0,
        object_type="star",
        azimuth=azimuth,
        altitude=altitude,
        is_visible=True,
    )


# Multiple north-pointing stars ensure the algorithm can always make progress
# toward a northern target even after earlier stars are marked as "used".
MOCK_OBJECTS = [
    _make_star("NorthStar1", azimuth=0.0,   altitude=70.0),
    _make_star("NorthStar2", azimuth=2.0,   altitude=65.0),
    _make_star("NorthStar3", azimuth=358.0, altitude=60.0),
    _make_star("NorthStar4", azimuth=4.0,   altitude=55.0),
    _make_star("NorthStar5", azimuth=356.0, altitude=50.0),
    _make_star("EastStar",   azimuth=90.0,  altitude=30.0),
    _make_star("SouthStar",  azimuth=180.0, altitude=20.0),
    _make_star("WestStar",   azimuth=270.0, altitude=30.0),
]


def mock_get_visible(_position, _time, used_objects, **kwargs):
    """Return all mock objects not yet used.

    The route handler calls get_celestial_objects_for_navigation with extra
    keyword arguments (min_altitude, max_magnitude) so we accept **kwargs.
    """
    return [o for o in MOCK_OBJECTS if o.name not in used_objects]


def mock_get_object_position(obj, _position, *args):
    """Return the object's azimuth/altitude unchanged (stationary mock).

    The route handler calls get_object_position_at_location with a third
    positional argument (observation_time) so we accept *args.
    """
    return obj.azimuth, obj.altitude


class TestCalculateEndpoint:
    BASE = "/api/v1/navigation/calculate"
    PATCH_VISIBLE = "src.api.routes.navigation.get_celestial_objects_for_navigation"
    PATCH_POSITION = "src.api.routes.navigation.get_object_position_at_location"

    def _post(self, client, payload):
        return client.post(self.BASE, json=payload)

    def _base_payload(self, **overrides):
        payload = {
            "start": {"latitude": 0.0, "longitude": 0.0},
            "target": {"latitude": 1.0, "longitude": 0.0},
            "observation_time": "2024-06-21T22:00:00",
            # 10 km steps: NorthStar1 alone can guide all ~111 km to the target
            # in one follow-sequence (≈11 steps), so the route succeeds with
            # fewer objects and without exhausting the pool.
            "step_size_km": 10.0,
            "max_iterations": 50,
            "max_routes": 1,
            "prioritize_major": False,
            "planets_only": False,
        }
        payload.update(overrides)
        return payload

    def test_returns_200_with_mock_celestial_data(self, client):
        with patch(self.PATCH_VISIBLE, side_effect=mock_get_visible), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload())
        assert resp.status_code == 200

    def test_response_contains_routes_list(self, client):
        with patch(self.PATCH_VISIBLE, side_effect=mock_get_visible), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload())
        body = resp.json()
        assert "routes" in body
        assert isinstance(body["routes"], list)
        assert len(body["routes"]) >= 1

    def test_route_has_required_fields(self, client):
        with patch(self.PATCH_VISIBLE, side_effect=mock_get_visible), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload())
        route = resp.json()["routes"][0]
        for field in ("id", "label", "waypoints", "total_distance", "direct_distance",
                      "iterations", "used_objects", "target_reached_cutoff"):
            assert field in route, f"Missing field: {field}"

    def test_max_routes_1_returns_at_most_1_route(self, client):
        with patch(self.PATCH_VISIBLE, side_effect=mock_get_visible), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload(max_routes=1))
        assert len(resp.json()["routes"]) <= 1

    def test_max_routes_3_can_return_multiple(self, client):
        with patch(self.PATCH_VISIBLE, side_effect=mock_get_visible), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload(max_routes=3))
        assert resp.status_code == 200
        assert len(resp.json()["routes"]) >= 1

    def test_waypoints_have_position(self, client):
        with patch(self.PATCH_VISIBLE, side_effect=mock_get_visible), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload())
        waypoints = resp.json()["routes"][0]["waypoints"]
        assert len(waypoints) > 0
        for wp in waypoints:
            assert "position" in wp
            assert "latitude" in wp["position"]
            assert "longitude" in wp["position"]

    def test_invalid_start_coordinates_returns_422(self, client):
        payload = self._base_payload()
        payload["start"] = {"latitude": 999.0, "longitude": 0.0}
        resp = self._post(client, payload)
        assert resp.status_code == 422

    def test_missing_start_returns_422(self, client):
        payload = self._base_payload()
        del payload["start"]
        resp = self._post(client, payload)
        assert resp.status_code == 422

    def test_no_visible_objects_returns_400(self, client):
        with patch(self.PATCH_VISIBLE, return_value=[]), \
             patch(self.PATCH_POSITION, side_effect=mock_get_object_position):
            resp = self._post(client, self._base_payload())
        assert resp.status_code == 400
