"""
Navigation API routes.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ...api.models import (
    Position, NavigationRequest, NavigationResponse,
    Waypoint, ExportRequest
)
from ...core.navigation import (
    calculate_navigation_route, NavigationError
)
from ...data.celestial import (
    get_celestial_objects_for_navigation,
    get_object_position_at_location
)


router = APIRouter(prefix="/navigation", tags=["navigation"])


@router.post("/calculate", response_model=NavigationResponse)
async def calculate_route(request: NavigationRequest):
    """
    Calculate a navigation route between two positions using celestial objects.
    
    The algorithm will:
    1. Calculate compass direction to target
    2. Find visible celestial objects
    3. Select the one closest to target direction
    4. Follow it until it sets or path diverges
    5. Repeat until target reached
    """
    try:
        # Use provided time or current time
        observation_time = request.observation_time or datetime.utcnow()
        
        # Define functions for the navigation algorithm
        def get_visible_objects(position: Position, time: datetime, used: set):
            return get_celestial_objects_for_navigation(
                position, time, used,
                min_altitude=0.0,
                max_magnitude=6.0
            )
        
        def get_object_position(obj, position: Position):
            return get_object_position_at_location(obj, position, observation_time)
        
        routes = []
        
        # Route 1: Shortest Path (Primary)
        try:
            shortest_route = calculate_navigation_route(
                start_position=request.start,
                target_position=request.target,
                get_visible_objects_func=get_visible_objects,
                get_object_position_func=get_object_position,
                observation_time=observation_time,
                step_size_km=request.step_size_km,
                max_iterations=request.max_iterations,
                prioritize_major=request.prioritize_major,
                planets_only=request.planets_only,
                optimize_for="shortest"
            )
            shortest_route.id = "shortest"
            shortest_route.label = "Shortest Path"
            routes.append(shortest_route)
        except NavigationError as e:
            # If we can't even find one route, re-raise
            if not routes:
                raise e
        
        # Route 2: Fewest Waypoints (Least Changes)
        if request.max_routes > 1:
            try:
                least_changes_route = calculate_navigation_route(
                    start_position=request.start,
                    target_position=request.target,
                    get_visible_objects_func=get_visible_objects,
                    get_object_position_func=get_object_position,
                    observation_time=observation_time,
                    step_size_km=request.step_size_km,
                    max_iterations=request.max_iterations,
                    prioritize_major=request.prioritize_major,
                    planets_only=request.planets_only,
                    optimize_for="least_changes"
                )
                least_changes_route.id = "least_changes"
                least_changes_route.label = "Fewest Waypoints"
                routes.append(least_changes_route)
            except NavigationError:
                # If alternative route fails, just continue with what we have
                pass
        
        # Route 3: Alternative (Exclude most used object from shortest)
        if request.max_routes > 2 and routes:
            # Try different exclusion strategies to ensure we get a 3rd route
            exclusion_strategies = []
            
            # Strategy 1: Exclude the first object of the shortest route
            if routes[0].used_objects:
                exclusion_strategies.append({routes[0].used_objects[0]})
            
            # Strategy 2: Exclude the first object of the second route (if different)
            if len(routes) > 1 and routes[1].used_objects:
                first_obj_r2 = routes[1].used_objects[0]
                if not exclusion_strategies or first_obj_r2 not in exclusion_strategies[0]:
                    exclusion_strategies.append({first_obj_r2})
            
            # Strategy 3: Exclude both first objects
            if len(exclusion_strategies) > 1:
                exclusion_strategies.append(exclusion_strategies[0] | exclusion_strategies[1])

            success = False
            for excluded in exclusion_strategies:
                try:
                    alt_route_3 = calculate_navigation_route(
                        start_position=request.start,
                        target_position=request.target,
                        get_visible_objects_func=get_visible_objects,
                        get_object_position_func=get_object_position,
                        observation_time=observation_time,
                        step_size_km=request.step_size_km,
                        max_iterations=request.max_iterations,
                        prioritize_major=request.prioritize_major,
                        planets_only=request.planets_only,
                        excluded_objects=excluded,
                        optimize_for="shortest"
                    )
                    
                    # Check if this route is actually different from existing ones
                    is_duplicate = False
                    for existing in routes:
                        if (len(existing.waypoints) == len(alt_route_3.waypoints) and
                            existing.used_objects == alt_route_3.used_objects):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        alt_route_3.id = "alternative"
                        alt_route_3.label = "Alternative Route"
                        routes.append(alt_route_3)
                        success = True
                        break
                except NavigationError:
                    continue
            
            # If still no 3rd route, try a different optimization or slightly different start
            if not success:
                try:
                    # Try with a different optimization if not already tried
                    alt_route_3 = calculate_navigation_route(
                        start_position=request.start,
                        target_position=request.target,
                        get_visible_objects_func=get_visible_objects,
                        get_object_position_func=get_object_position,
                        observation_time=observation_time,
                        step_size_km=request.step_size_km * 1.5, # Slightly different step size
                        max_iterations=request.max_iterations,
                        prioritize_major=not request.prioritize_major, # Flip prioritization
                        planets_only=request.planets_only,
                        optimize_for="shortest"
                    )
                    alt_route_3.id = "alternative"
                    alt_route_3.label = "Alternative Route"
                    routes.append(alt_route_3)
                except NavigationError:
                    pass
        
        # Sort routes by total distance to ensure "Shortest Path" is actually the shortest
        # and update labels accordingly
        if routes:
            # Sort by distance
            routes.sort(key=lambda r: r.total_distance)
            
            # Re-assign labels based on properties
            # The first one is now definitely the shortest
            routes[0].label = "Shortest Path"
            routes[0].id = "shortest"
            
            # If we have more, label them appropriately
            if len(routes) > 1:
                # Find the one with fewest waypoints (if it's not the shortest)
                # We use a stable sort or just find the one with min waypoints
                # that isn't already labeled as shortest
                fewest_wp_route = min(routes, key=lambda r: len(r.waypoints))
                
                for i, r in enumerate(routes):
                    if i == 0:
                        continue # Already labeled as shortest
                        
                    if r == fewest_wp_route:
                        r.label = "Fewest Waypoints"
                        r.id = "least_changes"
                    else:
                        r.label = f"Alternative Route {i}"
                        r.id = f"alternative_{i}"
                
        return NavigationResponse(routes=routes)
        
    except NavigationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Navigation calculation failed: {str(e)}")


@router.get("/direction")
async def get_compass_direction(
    from_lat: float = Query(..., ge=-90, le=90, description="Starting latitude"),
    from_lon: float = Query(..., ge=-180, le=180, description="Starting longitude"),
    to_lat: float = Query(..., ge=-90, le=90, description="Target latitude"),
    to_lon: float = Query(..., ge=-180, le=180, description="Target longitude")
):
    """Get the compass direction from one point to another."""
    from ...core.navigation import calculate_compass_direction
    
    from_pos = Position(latitude=from_lat, longitude=from_lon)
    to_pos = Position(latitude=to_lat, longitude=to_lon)
    
    bearing = calculate_compass_direction(from_pos, to_pos)
    
    # Convert bearing to cardinal direction
    cardinal_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    index = round(bearing / 45) % 8
    cardinal = cardinal_directions[index]
    
    return {
        "bearing": bearing,
        "cardinal_direction": cardinal
    }


@router.post("/export/gpx")
async def export_gpx(request: ExportRequest):
    """Export waypoints to GPX format."""
    gpx_content = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="StarNavigation" xmlns="http://www.topografix.com/GPX/1/1">
    <metadata>
        <name>{}</name>
        <time>{}</time>
    </metadata>
    <trk>
        <name>{}</name>
        <trkseg>
""".format(request.name, datetime.utcnow().isoformat(), request.name)
    
    for i, wp in enumerate(request.waypoints):
        obj_name = wp.reference_object.name if wp.reference_object else "Direct"
        gpx_content += """            <trkpt lat="{}" lon="{}">
                <name>Waypoint {}</name>
                <desc>Via: {} | Reason: {}</desc>
            </trkpt>
""".format(
            wp.position.latitude,
            wp.position.longitude,
            i + 1,
            obj_name,
            wp.reason
        )
    
    gpx_content += """        </trkseg>
    </trk>
</gpx>"""
    
    return {"format": "gpx", "content": gpx_content}


@router.post("/export/geojson")
async def export_geojson(request: ExportRequest):
    """Export waypoints to GeoJSON format."""
    features = []
    
    for i, wp in enumerate(request.waypoints):
        obj_name = wp.reference_object.name if wp.reference_object else "Direct"
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [wp.position.longitude, wp.position.latitude]
            },
            "properties": {
                "name": f"Waypoint {i + 1}",
                "reference_object": obj_name,
                "reason": wp.reason,
                "distance_to_target": wp.distance_to_target
            }
        })
    
    # Add LineString for the path
    if len(request.waypoints) > 1:
        coordinates = [
            [wp.position.longitude, wp.position.latitude]
            for wp in request.waypoints
        ]
        features.insert(0, {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": coordinates
            },
            "properties": {
                "name": request.name,
                "type": "route"
            }
        })
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return {"format": "geojson", "content": geojson}
