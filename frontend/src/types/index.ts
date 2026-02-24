/**
 * TypeScript type definitions matching the backend API models
 */

export interface Position {
  latitude: number;
  longitude: number;
  altitude?: number;
}

export type ObjectType = 'star' | 'planet' | 'moon' | 'sun';
export type StopReason = 'target_reached' | 'object_lost' | 'closest_approach';

export interface CelestialObject {
  name: string;
  right_ascension: number;
  declination: number;
  magnitude: number;
  object_type: ObjectType;
  azimuth?: number;
  altitude?: number;
  is_visible?: boolean;
}

export interface Waypoint {
  position: Position;
  reference_object?: CelestialObject;
  reason: StopReason;
  timestamp: string;
  distance_to_target?: number;
}

export interface NavigationRequest {
  start: Position;
  target: Position;
  observation_time?: string;
  step_size_km?: number;
  max_iterations?: number;
  prioritize_major?: boolean;
  planets_only?: boolean;
}

export interface NavigationResponse {
  waypoints: Waypoint[];
  total_distance: number;
  direct_distance: number;
  iterations: number;
  used_objects: string[];
}

export interface VisibleObjectsResponse {
  objects: CelestialObject[];
  count: number;
  observation_time: string;
}

export interface GeocodeResult {
  name: string;
  latitude: number;
  longitude: number;
  country?: string;
  region?: string;
}

export type ExportFormat = 'gpx' | 'geojson';

export interface ExportRequest {
  waypoints: Waypoint[];
  format: ExportFormat;
  name: string;
}
