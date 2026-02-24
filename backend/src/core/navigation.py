"""
Celestial Compass Navigation Algorithm Implementation

This module implements the pathfinding algorithm that navigates between
two points on Earth using celestial objects as reference points.
"""
import math
from datetime import datetime
from typing import List, Set, Tuple, Optional
from dataclasses import dataclass, field

from ..api.models import Position, CelestialObject, Waypoint, NavigationResponse
from ..data.celestial import NAVIGATIONAL_STARS


# Earth's radius in kilometers
EARTH_RADIUS_KM = 6371.0

# Maximum target reached cutoff in kilometers
MAX_TARGET_REACHED_CUTOFF_KM = 5.0

# Target reached cutoff as percentage of total route distance
TARGET_REACHED_CUTOFF_PERCENTAGE = 0.05


class NavigationError(Exception):
    """Exception raised for navigation errors."""
    pass


@dataclass
class NavigationState:
    """Internal state for navigation algorithm."""
    current_position: Position
    target_position: Position
    used_objects: Set[str] = field(default_factory=set)
    waypoints: List[Waypoint] = field(default_factory=list)
    iteration_count: int = 0


def to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    return degrees * math.pi / 180.0


def to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    return radians * 180.0 / math.pi


def calculate_compass_direction(from_pos: Position, to_pos: Position) -> float:
    """
    Calculate the compass bearing from 'from_pos' to 'to_pos'.
    
    Returns bearing in degrees (0-360), where:
    - 0 = North
    - 90 = East
    - 180 = South
    - 270 = West
    
    Uses the forward azimuth formula (great circle navigation).
    """
    lat1 = to_radians(from_pos.latitude)
    lat2 = to_radians(to_pos.latitude)
    delta_lon = to_radians(to_pos.longitude - from_pos.longitude)
    
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    
    bearing = to_degrees(math.atan2(x, y))
    return (bearing + 360) % 360  # Normalize to 0-360


def haversine_distance(pos1: Position, pos2: Position) -> float:
    """
    Calculate the great-circle distance between two positions in kilometers.
    
    Uses the haversine formula for accurate distance calculation on a sphere.
    """
    lat1, lon1 = to_radians(pos1.latitude), to_radians(pos1.longitude)
    lat2, lon2 = to_radians(pos2.latitude), to_radians(pos2.longitude)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_KM * c


def move_in_direction(position: Position, bearing_degrees: float, distance_km: float) -> Position:
    """
    Calculate new position after moving 'distance_km' in 'bearing_degrees' direction.
    
    Uses the direct geodesic problem solution (moving along a great circle).
    """
    lat1 = to_radians(position.latitude)
    lon1 = to_radians(position.longitude)
    bearing = to_radians(bearing_degrees)
    angular_distance = distance_km / EARTH_RADIUS_KM
    
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_distance) +
        math.cos(lat1) * math.sin(angular_distance) * math.cos(bearing)
    )
    
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_distance) * math.cos(lat1),
        math.cos(angular_distance) - math.sin(lat1) * math.sin(lat2)
    )
    
    return Position(
        latitude=to_degrees(lat2),
        longitude=to_degrees(lon2),
        altitude=position.altitude
    )


def circular_distance(angle1: float, angle2: float) -> float:
    """
    Calculate the shortest angular distance between two angles.
    
    Handles the 0/360 degree wraparound correctly.
    """
    diff = abs(angle1 - angle2)
    return min(diff, 360 - diff)


def select_best_celestial_object(
    target_bearing: float,
    visible_objects: List[CelestialObject],
    prioritize_major: bool = False
) -> Optional[CelestialObject]:
    """
    Select the visible celestial object whose azimuth is closest to the target bearing.
    
    Args:
        target_bearing: Desired compass direction in degrees
        visible_objects: List of visible celestial objects with azimuth calculated
        prioritize_major: If True, give a bonus to planets and navigational stars
        
    Returns:
        The best matching celestial object, or None if no objects available
    """
    if not visible_objects:
        return None
    
    best_object = None
    min_score = 360.0
    
    for obj in visible_objects:
        if obj.azimuth is None:
            continue
        
        angular_distance = circular_distance(obj.azimuth, target_bearing)
        score = angular_distance
        
        # Apply bonus for planets and navigational stars if prioritization is enabled
        if prioritize_major:
            is_planet = obj.object_type in ["planet", "moon", "sun"]
            is_nav_star = obj.name in NAVIGATIONAL_STARS
            
            if is_planet or is_nav_star:
                # Give a significant bonus (e.g., reduce score by 30 degrees)
                # This makes a major object 30 degrees "closer" to the target bearing than it actually is
                score = max(0, angular_distance - 30.0)
        
        if score < min_score:
            min_score = score
            best_object = obj
    
    return best_object


def positions_equal(pos1: Position, pos2: Position, tolerance_km: float = 0.1) -> bool:
    """Check if two positions are approximately equal within tolerance."""
    return haversine_distance(pos1, pos2) < tolerance_km


def calculate_target_reached_cutoff(total_route_distance_km: float) -> float:
    """
    Calculate the dynamic target reached cutoff distance.
    
    The cutoff is calculated as 5% of the total route distance,
    capped at a maximum of 5 km.
    
    Args:
        total_route_distance_km: The total direct distance of the route in km
        
    Returns:
        The cutoff distance in km
        
    Examples:
        - 50 km route -> 2.5 km cutoff
        - 100 km route -> 5.0 km cutoff
        - 1000 km route -> 5.0 km cutoff (capped)
    """
    return min(total_route_distance_km * TARGET_REACHED_CUTOFF_PERCENTAGE, MAX_TARGET_REACHED_CUTOFF_KM)


def follow_celestial_object(
    nav_state: NavigationState,
    reference_object: CelestialObject,
    get_object_position_func,
    step_size_km: float = 10.0,
    target_reached_cutoff_km: float = 1.0
) -> Tuple[Position, str, CelestialObject]:
    """
    Follow the reference celestial object until it sets or we reach closest approach.
    
    Args:
        nav_state: Current navigation state
        reference_object: The celestial object to follow
        get_object_position_func: Function to get updated object position (azimuth, altitude)
        step_size_km: Distance to move in each step
        target_reached_cutoff_km: Distance threshold for considering target reached
        
    Returns:
        Tuple of (final_position, reason_for_stopping, updated_reference_object)
    """
    current_pos = nav_state.current_position
    target_pos = nav_state.target_position
    
    # Track distance to target to detect when we start moving away
    previous_distance = haversine_distance(current_pos, target_pos)
    closest_point = current_pos
    closest_distance = previous_distance
    
    # Create a copy of the reference object to track its changing position
    updated_object = reference_object.model_copy()
    
    max_steps = 10000  # Safety limit to prevent infinite loops
    steps = 0
    
    while steps < max_steps:
        steps += 1
        
        # Move toward the reference object (follow its current azimuth)
        if updated_object.azimuth is None:
            break
        next_pos = move_in_direction(current_pos, updated_object.azimuth, step_size_km)
        
        # Update object position for new location and time
        azimuth, altitude = get_object_position_func(updated_object, next_pos)
        updated_object.azimuth = azimuth
        updated_object.altitude = altitude
        
        # Check 1: Is object still visible?
        if altitude <= 0:
            return current_pos, "object_lost", updated_object
        
        # Check 2: Calculate new distance to target
        current_distance = haversine_distance(next_pos, target_pos)
        
        # Check 3: Have we reached the closest point to target?
        if current_distance > previous_distance:
            # We're moving away from target - return the closest point
            return closest_point, "closest_approach", updated_object
        
        # Check 4: Have we reached the target?
        if current_distance < target_reached_cutoff_km:
            return next_pos, "target_reached", updated_object
        
        # Update tracking
        if current_distance < closest_distance:
            closest_distance = current_distance
            closest_point = next_pos
        
        previous_distance = current_distance
        current_pos = next_pos
    
    # Safety limit reached
    return closest_point, "closest_approach", updated_object


def calculate_navigation_route(
    start_position: Position,
    target_position: Position,
    get_visible_objects_func,
    get_object_position_func,
    observation_time: datetime,
    step_size_km: float = 10.0,
    max_iterations: int = 100,
    prioritize_major: bool = False
) -> NavigationResponse:
    """
    Main navigation algorithm using celestial objects as reference points.
    
    Args:
        start_position: Starting geographic position
        target_position: Target geographic position
        get_visible_objects_func: Function(position, time, used_objects) -> List[CelestialObject]
        get_object_position_func: Function(object, position) -> (azimuth, altitude)
        observation_time: Starting observation time
        step_size_km: Step size for following objects
        max_iterations: Maximum number of object switches
        prioritize_major: If True, give a bonus to planets and navigational stars
        
    Returns:
        NavigationResponse with waypoints and statistics
        
    Raises:
        NavigationError: If navigation fails (no visible objects, max iterations exceeded, etc.)
    """
    # Calculate the direct distance and dynamic cutoff
    direct_distance = haversine_distance(start_position, target_position)
    target_reached_cutoff = calculate_target_reached_cutoff(direct_distance)
    
    # Initialize navigation state
    nav_state = NavigationState(
        current_position=start_position,
        target_position=target_position,
        used_objects=set(),
        waypoints=[],
        iteration_count=0
    )
    
    total_distance_traveled = 0.0
    
    while nav_state.iteration_count < max_iterations:
        # Check if we've reached the target (using dynamic cutoff)
        if positions_equal(nav_state.current_position, target_position, target_reached_cutoff):
            final_waypoint = Waypoint(
                position=nav_state.current_position,
                reference_object=None,
                reason="target_reached",
                timestamp=observation_time,
                distance_to_target=0.0
            )
            nav_state.waypoints.append(final_waypoint)
            
            return NavigationResponse(
                waypoints=nav_state.waypoints,
                total_distance=total_distance_traveled,
                direct_distance=direct_distance,
                iterations=nav_state.iteration_count,
                used_objects=list(nav_state.used_objects),
                target_reached_cutoff=target_reached_cutoff
            )
        
        # Step 1: Calculate compass direction to target
        target_bearing = calculate_compass_direction(
            nav_state.current_position,
            nav_state.target_position
        )
        
        # Step 2: Get visible celestial objects
        visible_objects = get_visible_objects_func(
            nav_state.current_position,
            observation_time,
            nav_state.used_objects
        )
        
        if not visible_objects:
            raise NavigationError(
                f"No visible celestial objects available at position "
                f"({nav_state.current_position.latitude:.4f}, "
                f"{nav_state.current_position.longitude:.4f})"
            )
        
        # Step 3: Select best matching object
        best_object = select_best_celestial_object(target_bearing, visible_objects, prioritize_major)
        
        if not best_object:
            raise NavigationError("Could not find suitable celestial reference")
        
        # Step 4: Follow the celestial object
        start_of_leg = nav_state.current_position
        final_pos, reason, updated_object = follow_celestial_object(
            nav_state, best_object, get_object_position_func, step_size_km, target_reached_cutoff
        )
        
        # Calculate distance traveled this leg
        leg_distance = haversine_distance(start_of_leg, final_pos)
        total_distance_traveled += leg_distance
        
        # Calculate distance to target at this waypoint
        distance_to_target = haversine_distance(final_pos, nav_state.target_position)
        
        # Step 5: Record waypoint and update state
        waypoint = Waypoint(
            position=final_pos,
            reference_object=updated_object,
            reason=reason,  # type: ignore
            timestamp=observation_time,
            distance_to_target=distance_to_target
        )
        nav_state.waypoints.append(waypoint)
        
        # Mark object as used (don't use it again)
        nav_state.used_objects.add(best_object.name)
        
        # Update current position
        nav_state.current_position = final_pos
        nav_state.iteration_count += 1
        
        # If we reached the target, add final waypoint and return
        if reason == "target_reached":
            return NavigationResponse(
                waypoints=nav_state.waypoints,
                total_distance=total_distance_traveled,
                direct_distance=direct_distance,
                iterations=nav_state.iteration_count,
                used_objects=list(nav_state.used_objects),
                target_reached_cutoff=target_reached_cutoff
            )
    
    raise NavigationError(f"Exceeded maximum iterations ({max_iterations})")
