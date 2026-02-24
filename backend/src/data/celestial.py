"""
Celestial object data and position calculations.

This module provides:
1. A static star catalog (bright stars)
2. Skyfield integration for planets and the moon
3. Coordinate conversion (RA/Dec to Azimuth/Altitude)
"""
import json
import math
from datetime import datetime
from typing import List, Tuple, Optional
from pathlib import Path

from skyfield.api import Loader, wgs84
from skyfield import almanac
from skyfield.timelib import Time

from ..api.models import Position, CelestialObject


# Load Skyfield data
# The loader will download necessary files (de440.bsp for planets, etc.)
load = Loader('./skyfield_data')

# Try to load ephemeris, fall back to basic if not available
try:
    planets = load('de440.bsp')
    earth = planets['earth']
    EPHEMERIS_AVAILABLE = True
except Exception:
    EPHEMERIS_AVAILABLE = False
    earth = None

# Load timescale
ts = load.timescale()


# Bright Star Catalog - 50 brightest stars for navigation
# Data: Name, Right Ascension (hours), Declination (degrees), Magnitude
BRIGHT_STARS = [
    {"name": "Sirius", "ra": 6.7525, "dec": -16.7161, "mag": -1.46},
    {"name": "Canopus", "ra": 6.3992, "dec": -52.6956, "mag": -0.74},
    {"name": "Arcturus", "ra": 14.2611, "dec": 19.1875, "mag": -0.05},
    {"name": "Alpha Centauri", "ra": 14.6608, "dec": -60.8333, "mag": -0.01},
    {"name": "Vega", "ra": 18.6156, "dec": 38.7836, "mag": 0.03},
    {"name": "Capella", "ra": 5.2781, "dec": 46.0067, "mag": 0.08},
    {"name": "Rigel", "ra": 5.2422, "dec": -8.2017, "mag": 0.13},
    {"name": "Procyon", "ra": 7.6553, "dec": 5.2250, "mag": 0.38},
    {"name": "Achernar", "ra": 1.6286, "dec": -57.2367, "mag": 0.46},
    {"name": "Betelgeuse", "ra": 5.9192, "dec": 7.4071, "mag": 0.50},
    {"name": "Hadar", "ra": 14.0637, "dec": -60.3731, "mag": 0.61},
    {"name": "Altair", "ra": 19.8464, "dec": 8.8683, "mag": 0.77},
    {"name": "Acrux", "ra": 12.4433, "dec": -63.0990, "mag": 0.77},
    {"name": "Aldebaran", "ra": 4.5987, "dec": 16.5092, "mag": 0.85},
    {"name": "Antares", "ra": 16.4901, "dec": -26.4320, "mag": 0.96},
    {"name": "Spica", "ra": 13.4199, "dec": -11.1614, "mag": 0.98},
    {"name": "Pollux", "ra": 7.7553, "dec": 28.0262, "mag": 1.14},
    {"name": "Fomalhaut", "ra": 22.9609, "dec": -29.6222, "mag": 1.16},
    {"name": "Deneb", "ra": 20.6905, "dec": 45.2803, "mag": 1.25},
    {"name": "Mimosa", "ra": 12.7954, "dec": -59.6884, "mag": 1.25},
    {"name": "Regulus", "ra": 10.1396, "dec": 11.9672, "mag": 1.36},
    {"name": "Adhara", "ra": 6.9771, "dec": -28.9721, "mag": 1.50},
    {"name": "Castor", "ra": 7.5766, "dec": 31.8886, "mag": 1.58},
    {"name": "Gacrux", "ra": 12.5197, "dec": -57.1133, "mag": 1.64},
    {"name": "Bellatrix", "ra": 5.4189, "dec": 6.3497, "mag": 1.64},
    {"name": "Elnath", "ra": 5.4382, "dec": 28.6074, "mag": 1.65},
    {"name": "Miaplacidus", "ra": 9.2200, "dec": -69.7172, "mag": 1.68},
    {"name": "Alnilam", "ra": 5.6036, "dec": -1.2019, "mag": 1.69},
    {"name": "Alnair", "ra": 22.1372, "dec": -46.9608, "mag": 1.74},
    {"name": "Alnitak", "ra": 5.6793, "dec": -1.9426, "mag": 1.74},
    {"name": "Alioth", "ra": 12.9006, "dec": 55.9598, "mag": 1.77},
    {"name": "Dubhe", "ra": 11.0621, "dec": 61.7510, "mag": 1.79},
    {"name": "Mirfak", "ra": 3.4053, "dec": 49.8612, "mag": 1.80},
    {"name": "Wezen", "ra": 7.1399, "dec": -26.3932, "mag": 1.83},
    {"name": "Sargas", "ra": 17.5606, "dec": -42.9979, "mag": 1.84},
    {"name": "Kaus Australis", "ra": 18.4020, "dec": -34.3846, "mag": 1.85},
    {"name": "Avior", "ra": 8.3752, "dec": -59.5095, "mag": 1.86},
    {"name": "Alkaid", "ra": 13.7923, "dec": 49.3133, "mag": 1.86},
    {"name": "Menkalinan", "ra": 5.9924, "dec": 44.9474, "mag": 1.90},
    {"name": "Atria", "ra": 16.8111, "dec": -69.0277, "mag": 1.91},
    {"name": "Alhena", "ra": 6.6285, "dec": 16.3992, "mag": 1.93},
    {"name": "Peacock", "ra": 20.4275, "dec": -56.7351, "mag": 1.94},
    {"name": "Polaris", "ra": 2.5303, "dec": 89.2641, "mag": 1.97},
    {"name": "Mirzam", "ra": 6.3780, "dec": -17.9725, "mag": 1.98},
    {"name": "Alphard", "ra": 9.4598, "dec": -8.6586, "mag": 1.99},
    {"name": "Hamal", "ra": 2.1195, "dec": 23.4624, "mag": 2.01},
    {"name": "Algieba", "ra": 10.3328, "dec": 19.8415, "mag": 2.01},
    {"name": "Diphda", "ra": 0.7260, "dec": -17.9866, "mag": 2.04},
    {"name": "Nunki", "ra": 18.9218, "dec": -26.2963, "mag": 2.05},
    {"name": "Menkent", "ra": 14.0608, "dec": -36.3700, "mag": 2.06},
]


def load_star_catalog() -> List[CelestialObject]:
    """Load the bright star catalog as CelestialObject instances."""
    return [
        CelestialObject(
            name=star["name"],
            right_ascension=star["ra"],
            declination=star["dec"],
            magnitude=star["mag"],
            object_type="star"
        )
        for star in BRIGHT_STARS
    ]


def get_planet_list() -> List[Tuple[str, str]]:
    """Get list of planets available in ephemeris."""
    if not EPHEMERIS_AVAILABLE:
        return []
    
    return [
        ("mercury", "Mercury"),
        ("venus", "Venus"),
        ("mars", "Mars"),
        ("jupiter", "Jupiter"),
        ("saturn", "Saturn"),
    ]


def to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi


def calculate_local_sidereal_time(longitude: float, dt: datetime) -> float:
    """
    Calculate Local Sidereal Time (LST) in hours.
    
    LST is the right ascension currently crossing the observer's meridian.
    """
    # Julian date calculation
    year, month, day = dt.year, dt.month, dt.day
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    
    if month <= 2:
        year -= 1
        month += 12
    
    A = int(year / 100)
    B = 2 - A + int(A / 4)
    
    jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + hour / 24.0 + B - 1524.5
    
    # Julian centuries from J2000.0
    T = (jd - 2451545.0) / 36525.0
    
    # Greenwich Mean Sidereal Time at 0h UT
    GMST = 6.697374558 + 0.06570982441908 * (jd - 2451545.0) + 1.00273790935 * hour + 0.000026 * T * T
    
    # Add longitude (positive east)
    LST = GMST + longitude / 15.0
    
    # Normalize to 0-24 hours
    LST = LST % 24.0
    if LST < 0:
        LST += 24.0
    
    return LST


def calculate_horizontal_coordinates(
    celestial_obj: CelestialObject,
    observer_pos: Position,
    observation_time: datetime
) -> Tuple[float, float]:
    """
    Convert celestial coordinates (RA, Dec) to horizontal coordinates (azimuth, altitude).
    
    Args:
        celestial_obj: Celestial object with RA and Dec
        observer_pos: Observer's position
        observation_time: Time of observation
        
    Returns:
        Tuple of (azimuth_degrees, altitude_degrees)
        - Azimuth: 0-360 degrees, 0=North, 90=East
        - Altitude: -90 to 90 degrees, positive=above horizon
    """
    # Convert observation time to Local Sidereal Time (LST)
    lst = calculate_local_sidereal_time(observer_pos.longitude, observation_time)
    
    # Hour angle (LST - RA)
    ha = lst - celestial_obj.right_ascension
    ha_rad = to_radians(ha * 15)  # Convert hours to degrees, then to radians
    
    lat_rad = to_radians(observer_pos.latitude)
    dec_rad = to_radians(celestial_obj.declination)
    
    # Calculate altitude
    sin_alt = math.sin(dec_rad) * math.sin(lat_rad) + math.cos(dec_rad) * math.cos(lat_rad) * math.cos(ha_rad)
    sin_alt = max(-1.0, min(1.0, sin_alt))  # Clamp for numerical safety
    altitude = to_degrees(math.asin(sin_alt))
    
    # Calculate azimuth
    cos_az = (math.sin(dec_rad) - math.sin(lat_rad) * sin_alt) / (math.cos(lat_rad) * math.cos(math.asin(sin_alt)))
    cos_az = max(-1.0, min(1.0, cos_az))  # Clamp for numerical safety
    azimuth = to_degrees(math.acos(cos_az))
    
    # Determine correct quadrant for azimuth
    sin_az = -math.cos(dec_rad) * math.sin(ha_rad)
    if sin_az < 0:
        azimuth = 360 - azimuth
    
    return azimuth, altitude


def get_skyfield_position(
    body_name: str,
    observer_pos: Position,
    observation_time: datetime
) -> Tuple[float, float, float, float]:
    """
    Get position of a solar system body using Skyfield.
    
    Returns:
        Tuple of (ra_hours, dec_degrees, azimuth, altitude)
    """
    if not EPHEMERIS_AVAILABLE:
        raise RuntimeError("Skyfield ephemeris not available")
    
    # Create observer location
    observer = earth + wgs84.latlon(
        observer_pos.latitude,
        observer_pos.longitude,
        elevation_m=observer_pos.altitude
    )
    
    # Create time object
    t = ts.utc(
        observation_time.year,
        observation_time.month,
        observation_time.day,
        observation_time.hour,
        observation_time.minute,
        observation_time.second
    )
    
    # Get body
    if body_name.lower() == "sun":
        body = planets["sun"]
    elif body_name.lower() == "moon":
        body = planets["moon"]
    else:
        body = planets[body_name]
    
    # Calculate apparent position
    apparent = observer.at(t).observe(body).apparent()
    
    # Get RA and Dec
    ra, dec, _ = apparent.radec()
    ra_hours = ra.hours
    dec_degrees = dec.degrees
    
    # Get altitude and azimuth
    alt, az, _ = apparent.altaz()
    altitude = alt.degrees
    azimuth = az.degrees
    
    return ra_hours, dec_degrees, azimuth, altitude


def get_celestial_objects_for_navigation(
    observer_pos: Position,
    observation_time: datetime,
    used_objects: set,
    min_altitude: float = 0.0,
    max_magnitude: float = 6.0
) -> List[CelestialObject]:
    """
    Get all celestial objects available for navigation.
    
    Combines:
    - Bright stars from static catalog
    - Sun, Moon, and planets from Skyfield (if available)
    
    Args:
        observer_pos: Observer's position
        observation_time: Time of observation
        used_objects: Set of object names already used (to exclude)
        min_altitude: Minimum altitude above horizon (degrees)
        max_magnitude: Maximum magnitude (faintest visible)
        
    Returns:
        List of visible CelestialObject instances
    """
    visible_objects = []
    
    # Add stars from catalog
    stars = load_star_catalog()
    for star in stars:
        if star.name in used_objects:
            continue
        
        azimuth, altitude = calculate_horizontal_coordinates(star, observer_pos, observation_time)
        star.azimuth = azimuth
        star.altitude = altitude
        star.is_visible = altitude > min_altitude and star.magnitude < max_magnitude
        
        if star.is_visible:
            visible_objects.append(star)
    
    # Add solar system bodies if Skyfield is available
    if EPHEMERIS_AVAILABLE:
        solar_system_bodies = [
            ("sun", "sun", -26.7),
            ("moon", "moon", -12.7),
            ("mercury", "planet", 0.0),
            ("venus", "planet", -4.0),
            ("mars", "planet", 0.0),
            ("jupiter", "planet", -2.0),
            ("saturn", "planet", 0.5),
        ]
        
        for body_id, obj_type, default_mag in solar_system_bodies:
            name = body_id.capitalize()
            if name in used_objects:
                continue
            
            try:
                ra, dec, azimuth, altitude = get_skyfield_position(
                    body_id, observer_pos, observation_time
                )
                
                # Use calculated magnitude or default
                magnitude = default_mag
                
                body = CelestialObject(
                    name=name,
                    right_ascension=ra,
                    declination=dec,
                    magnitude=magnitude,
                    object_type=obj_type,  # type: ignore
                    azimuth=azimuth,
                    altitude=altitude,
                    is_visible=altitude > min_altitude
                )
                
                if body.is_visible:
                    visible_objects.append(body)
                    
            except Exception as e:
                # Skip bodies that can't be calculated
                continue
    
    return visible_objects


def get_object_position_at_location(
    celestial_obj: CelestialObject,
    observer_pos: Position,
    observation_time: Optional[datetime] = None
) -> Tuple[float, float]:
    """
    Get the current azimuth and altitude of a celestial object at a given location.
    
    Args:
        celestial_obj: The celestial object
        observer_pos: Observer's position
        observation_time: Time of observation (default: now)
        
    Returns:
        Tuple of (azimuth, altitude)
    """
    if observation_time is None:
        observation_time = datetime.utcnow()
    
    # For solar system bodies, use Skyfield for accuracy
    if EPHEMERIS_AVAILABLE and celestial_obj.object_type in ["planet", "moon", "sun"]:
        try:
            _, _, azimuth, altitude = get_skyfield_position(
                celestial_obj.name.lower(),
                observer_pos,
                observation_time
            )
            return azimuth, altitude
        except Exception:
            pass
    
    # For stars or fallback, use the calculation method
    return calculate_horizontal_coordinates(celestial_obj, observer_pos, observation_time)
