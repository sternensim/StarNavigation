"""
Pydantic models for API request/response validation.
"""
from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Position(BaseModel):
    """Geographic position on Earth."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees (-90 to 90)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees (-180 to 180)")
    altitude: float = Field(0.0, ge=-500, le=9000, description="Altitude in meters above sea level")


class CelestialObject(BaseModel):
    """A celestial object (star, planet, moon, sun)."""
    name: str = Field(..., description="Name of the celestial object")
    right_ascension: float = Field(..., ge=0, lt=24, description="Right ascension in hours (0-24)")
    declination: float = Field(..., ge=-90, le=90, description="Declination in degrees (-90 to 90)")
    magnitude: float = Field(..., description="Apparent magnitude (lower is brighter)")
    object_type: Literal["star", "planet", "moon", "sun"] = Field(..., description="Type of celestial object")
    
    # Dynamic properties (calculated based on observer position and time)
    azimuth: Optional[float] = Field(None, ge=0, lt=360, description="Azimuth in degrees (0-360, 0=North)")
    altitude: Optional[float] = Field(None, ge=-90, le=90, description="Altitude above horizon in degrees")
    is_visible: Optional[bool] = Field(None, description="Whether object is currently visible")


class Waypoint(BaseModel):
    """A point along the navigation route."""
    position: Position = Field(..., description="Geographic position of waypoint")
    reference_object: Optional[CelestialObject] = Field(None, description="Celestial object used to reach this point")
    reason: Literal["target_reached", "object_lost", "closest_approach"] = Field(
        ..., description="Reason for stopping at this waypoint"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Time when waypoint was reached")
    distance_to_target: Optional[float] = Field(None, description="Distance to target in km at this waypoint")


class NavigationRequest(BaseModel):
    """Request body for navigation calculation."""
    start: Position = Field(..., description="Starting position")
    target: Position = Field(..., description="Target destination")
    observation_time: Optional[datetime] = Field(None, description="Observation time (default: now)")
    step_size_km: float = Field(10.0, gt=0, le=100, description="Step size in km for following objects")
    max_iterations: int = Field(100, ge=10, le=1000, description="Maximum navigation iterations")


class NavigationResponse(BaseModel):
    """Response from navigation calculation."""
    waypoints: List[Waypoint] = Field(..., description="List of waypoints along the route")
    total_distance: float = Field(..., description="Total route distance in km")
    direct_distance: float = Field(..., description="Direct distance from start to target in km")
    iterations: int = Field(..., description="Number of iterations used")
    used_objects: List[str] = Field(..., description="Names of celestial objects used")
    target_reached_cutoff: float = Field(..., description="Dynamic cutoff distance (km) for determining if target is reached")


class VisibleObjectsRequest(BaseModel):
    """Request visible celestial objects at a location and time."""
    position: Position = Field(..., description="Observer position")
    observation_time: Optional[datetime] = Field(None, description="Observation time (default: now)")
    min_altitude: float = Field(0.0, ge=-90, le=90, description="Minimum altitude above horizon")
    max_magnitude: float = Field(6.0, ge=-2, le=15, description="Maximum magnitude (faintest visible)")


class VisibleObjectsResponse(BaseModel):
    """Response with visible celestial objects."""
    objects: List[CelestialObject] = Field(..., description="List of visible celestial objects")
    count: int = Field(..., description="Total number of visible objects")
    observation_time: datetime = Field(..., description="Time of observation")


class GeocodeResult(BaseModel):
    """Result from geocoding search."""
    name: str = Field(..., description="Place name")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    country: Optional[str] = Field(None, description="Country")
    region: Optional[str] = Field(None, description="Region/State")


class ExportRequest(BaseModel):
    """Request to export route data."""
    waypoints: List[Waypoint] = Field(..., description="Waypoints to export")
    format: Literal["gpx", "geojson"] = Field(..., description="Export format")
    name: str = Field("celestial_route", description="Name of the route")
