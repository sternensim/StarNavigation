import { Position } from '../types';

/**
 * Interpolates between two positions using Spherical Linear Interpolation (Slerp)
 * to follow a Great Circle path.
 * 
 * @param p1 Start position
 * @param p2 End position
 * @param fraction Fraction of the distance (0 to 1)
 * @returns Interpolated position
 */
export const interpolateGeodesic = (p1: Position, p2: Position, fraction: number): Position => {
  if (fraction <= 0) return { ...p1 };
  if (fraction >= 1) return { ...p2 };

  // Convert to radians
  const lat1 = (p1.latitude * Math.PI) / 180;
  const lon1 = (p1.longitude * Math.PI) / 180;
  const lat2 = (p2.latitude * Math.PI) / 180;
  const lon2 = (p2.longitude * Math.PI) / 180;

  // Angular distance between points (Haversine formula)
  const d =
    2 *
    Math.asin(
      Math.sqrt(
        Math.pow(Math.sin((lat1 - lat2) / 2), 2) +
          Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin((lon1 - lon2) / 2), 2)
      )
    );

  if (d === 0) {
    return { ...p1 };
  }

  const A = Math.sin((1 - fraction) * d) / Math.sin(d);
  const B = Math.sin(fraction * d) / Math.sin(d);

  const x = A * Math.cos(lat1) * Math.cos(lon1) + B * Math.cos(lat2) * Math.cos(lon2);
  const y = A * Math.cos(lat1) * Math.sin(lon1) + B * Math.cos(lat2) * Math.sin(lon2);
  const z = A * Math.sin(lat1) + B * Math.sin(lat2);

  const lat = Math.atan2(z, Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2)));
  const lon = Math.atan2(y, x);

  return {
    latitude: (lat * 180) / Math.PI,
    longitude: (lon * 180) / Math.PI,
  };
};

/**
 * Densifies a path by adding intermediate points along the Great Circle path.
 * 
 * @param p1 Start position
 * @param p2 End position
 * @param pointsPerDegree Number of points to add per degree of angular distance
 * @returns Array of positions including start and end
 */
export const densifyGeodesic = (p1: Position, p2: Position, pointsPerDegree: number = 1): Position[] => {
  const lat1 = (p1.latitude * Math.PI) / 180;
  const lon1 = (p1.longitude * Math.PI) / 180;
  const lat2 = (p2.latitude * Math.PI) / 180;
  const lon2 = (p2.longitude * Math.PI) / 180;

  const d =
    2 *
    Math.asin(
      Math.sqrt(
        Math.pow(Math.sin((lat1 - lat2) / 2), 2) +
          Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin((lon1 - lon2) / 2), 2)
      )
    );

  const dDegrees = (d * 180) / Math.PI;
  const numSegments = Math.max(1, Math.ceil(dDegrees * pointsPerDegree));
  
  if (numSegments <= 1) {
    return [p1, p2];
  }

  const points: Position[] = [];
  for (let i = 0; i <= numSegments; i++) {
    points.push(interpolateGeodesic(p1, p2, i / numSegments));
  }
  return points;
};
