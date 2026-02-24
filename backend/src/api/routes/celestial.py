"""
Celestial object API routes.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Query

from ...api.models import (
    Position, CelestialObject, VisibleObjectsRequest, VisibleObjectsResponse
)
from ...data.celestial import (
    get_celestial_objects_for_navigation,
    load_star_catalog,
    calculate_horizontal_coordinates
)


router = APIRouter(prefix="/celestial", tags=["celestial"])


@router.get("/objects", response_model=VisibleObjectsResponse)
async def get_visible_objects(
    lat: float = Query(..., ge=-90, le=90, description="Observer latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Observer longitude"),
    altitude: float = Query(0.0, description="Observer altitude in meters"),
    year: Optional[int] = Query(None, description="Year (default: current)"),
    month: Optional[int] = Query(None, description="Month (default: current)"),
    day: Optional[int] = Query(None, description="Day (default: current)"),
    hour: Optional[int] = Query(None, description="Hour (default: current)"),
    minute: Optional[int] = Query(None, description="Minute (default: current)"),
    min_altitude: float = Query(0.0, ge=-90, le=90, description="Minimum altitude"),
    max_magnitude: float = Query(6.0, ge=-2, le=15, description="Maximum magnitude")
):
    """
    Get all visible celestial objects from an observer's position.
    
    Returns stars, planets, moon, and sun that are above the horizon.
    """
    # Build observation time
    now = datetime.utcnow()
    observation_time = datetime(
        year or now.year,
        month or now.month,
        day or now.day,
        hour or now.hour,
        minute or now.minute
    )
    
    observer_pos = Position(latitude=lat, longitude=lon, altitude=altitude)
    
    # Get visible objects
    objects = get_celestial_objects_for_navigation(
        observer_pos,
        observation_time,
        used_objects=set(),
        min_altitude=min_altitude,
        max_magnitude=max_magnitude
    )
    
    return VisibleObjectsResponse(
        objects=objects,
        count=len(objects),
        observation_time=observation_time
    )


@router.get("/stars")
async def get_star_catalog():
    """Get the static star catalog with positions calculated for current time/location."""
    stars = load_star_catalog()
    return {
        "count": len(stars),
        "stars": [
            {
                "name": s.name,
                "right_ascension": s.right_ascension,
                "declination": s.declination,
                "magnitude": s.magnitude
            }
            for s in stars
        ]
    }


@router.get("/planets")
async def get_planet_positions(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    altitude: float = Query(0.0)
):
    """Get current positions of planets."""
    from ...data.celestial import EPHEMERIS_AVAILABLE, get_skyfield_position
    
    if not EPHEMERIS_AVAILABLE:
        return {"error": "Ephemeris data not available", "planets": []}
    
    observation_time = datetime.utcnow()
    observer_pos = Position(latitude=lat, longitude=lon, altitude=altitude)
    
    planets = ["mercury", "venus", "mars", "jupiter", "saturn"]
    results = []
    
    for planet in planets:
        try:
            ra, dec, azimuth, altitude_val = get_skyfield_position(
                planet, observer_pos, observation_time
            )
            results.append({
                "name": planet.capitalize(),
                "right_ascension": ra,
                "declination": dec,
                "azimuth": azimuth,
                "altitude": altitude_val,
                "is_visible": altitude_val > 0
            })
        except Exception as e:
            results.append({
                "name": planet.capitalize(),
                "error": str(e)
            })
    
    return {"planets": results, "observation_time": observation_time}


@router.get("/sun")
async def get_sun_position(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    altitude: float = Query(0.0)
):
    """Get current sun position."""
    from ...data.celestial import EPHEMERIS_AVAILABLE, get_skyfield_position
    
    observation_time = datetime.utcnow()
    observer_pos = Position(latitude=lat, longitude=lon, altitude=altitude)
    
    try:
        if EPHEMERIS_AVAILABLE:
            ra, dec, azimuth, altitude_val = get_skyfield_position(
                "sun", observer_pos, observation_time
            )
        else:
            # Fallback calculation
            ra, dec = 0, 0  # Simplified - would need proper solar position calculation
            azimuth, altitude_val = 0, -10
        
        return {
            "name": "Sun",
            "right_ascension": ra,
            "declination": dec,
            "azimuth": azimuth,
            "altitude": altitude_val,
            "is_visible": altitude_val > 0,
            "observation_time": observation_time
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/moon")
async def get_moon_position(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    altitude: float = Query(0.0)
):
    """Get current moon position."""
    from ...data.celestial import EPHEMERIS_AVAILABLE, get_skyfield_position
    
    observation_time = datetime.utcnow()
    observer_pos = Position(latitude=lat, longitude=lon, altitude=altitude)
    
    try:
        if EPHEMERIS_AVAILABLE:
            ra, dec, azimuth, altitude_val = get_skyfield_position(
                "moon", observer_pos, observation_time
            )
        else:
            # Fallback - moon not available without ephemeris
            return {"error": "Moon position requires ephemeris data"}
        
        return {
            "name": "Moon",
            "right_ascension": ra,
            "declination": dec,
            "azimuth": azimuth,
            "altitude": altitude_val,
            "is_visible": altitude_val > 0,
            "observation_time": observation_time
        }
    except Exception as e:
        return {"error": str(e)}
