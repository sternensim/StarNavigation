import { useEffect, useRef } from 'react';
import L from 'leaflet';
import { useNavigationStore } from '../store/navigationStore';
import { Position } from '../types';

export const useRouteSimulation = () => {
  const {
    route,
    startLocation,
    targetLocation,
    isSimulating,
    simulationProgress,
    simulationSpeed,
    setSimulationProgress,
    setCurrentSimulationPosition,
    setIsSimulating,
  } = useNavigationStore();

  const requestRef = useRef<number>();
  const lastTimeRef = useRef<number>();

  // Calculate total distance and segment distances
  const routePoints = useRef<Position[]>([]);
  const segmentDistances = useRef<number[]>([]);
  const totalDistance = useRef<number>(0);

  useEffect(() => {
    if (!route || !startLocation || !targetLocation) {
      routePoints.current = [];
      segmentDistances.current = [];
      totalDistance.current = 0;
      return;
    }

    const points: Position[] = [
      startLocation,
      ...route.waypoints.map((wp) => wp.position),
      targetLocation,
    ];
    routePoints.current = points;

    const distances: number[] = [];
    let total = 0;
    for (let i = 0; i < points.length - 1; i++) {
      const p1 = L.latLng(points[i].latitude, points[i].longitude);
      const p2 = L.latLng(points[i + 1].latitude, points[i + 1].longitude);
      const d = p1.distanceTo(p2);
      distances.push(d);
      total += d;
    }
    segmentDistances.current = distances;
    totalDistance.current = total;
  }, [route, startLocation, targetLocation]);

  const animate = (time: number) => {
    if (lastTimeRef.current !== undefined) {
      const deltaTime = time - lastTimeRef.current;
      
      // Base speed: entire route in 30 seconds at 1x
      const speedFactor = (simulationSpeed * deltaTime) / 30000;
      let newProgress = simulationProgress + speedFactor;

      if (newProgress >= 1) {
        newProgress = 1;
        setIsSimulating(false);
      }

      setSimulationProgress(newProgress);
    }
    lastTimeRef.current = time;
    requestRef.current = requestAnimationFrame(animate);
  };

  useEffect(() => {
    if (isSimulating) {
      lastTimeRef.current = undefined;
      requestRef.current = requestAnimationFrame(animate);
    } else {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    }
    return () => {
      if (requestRef.current) {
        cancelAnimationFrame(requestRef.current);
      }
    };
  }, [isSimulating, simulationProgress, simulationSpeed]);

  // Update position based on progress
  useEffect(() => {
    if (totalDistance.current === 0 || routePoints.current.length < 2) return;

    const targetDist = simulationProgress * totalDistance.current;
    let currentDist = 0;
    let segmentIndex = 0;

    for (let i = 0; i < segmentDistances.current.length; i++) {
      if (currentDist + segmentDistances.current[i] >= targetDist) {
        segmentIndex = i;
        break;
      }
      currentDist += segmentDistances.current[i];
      segmentIndex = i;
    }

    const p1 = routePoints.current[segmentIndex];
    const p2 = routePoints.current[segmentIndex + 1];
    const segmentProgress = segmentDistances.current[segmentIndex] === 0 
      ? 0 
      : (targetDist - currentDist) / segmentDistances.current[segmentIndex];

    // Geodesic interpolation (Spherical Linear Interpolation - Slerp)
    // Convert to radians
    const lat1 = (p1.latitude * Math.PI) / 180;
    const lon1 = (p1.longitude * Math.PI) / 180;
    const lat2 = (p2.latitude * Math.PI) / 180;
    const lon2 = (p2.longitude * Math.PI) / 180;

    // Angular distance between points
    const d =
      2 *
      Math.asin(
        Math.sqrt(
          Math.pow(Math.sin((lat1 - lat2) / 2), 2) +
            Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin((lon1 - lon2) / 2), 2)
        )
      );

    let interpolatedPos: Position;

    if (d === 0) {
      interpolatedPos = { latitude: p1.latitude, longitude: p1.longitude };
    } else {
      const A = Math.sin((1 - segmentProgress) * d) / Math.sin(d);
      const B = Math.sin(segmentProgress * d) / Math.sin(d);

      const x = A * Math.cos(lat1) * Math.cos(lon1) + B * Math.cos(lat2) * Math.cos(lon2);
      const y = A * Math.cos(lat1) * Math.sin(lon1) + B * Math.cos(lat2) * Math.sin(lon2);
      const z = A * Math.sin(lat1) + B * Math.sin(lat2);

      const lat = Math.atan2(z, Math.sqrt(Math.pow(x, 2) + Math.pow(y, 2)));
      const lon = Math.atan2(y, x);

      interpolatedPos = {
        latitude: (lat * 180) / Math.PI,
        longitude: (lon * 180) / Math.PI,
      };
    }

    setCurrentSimulationPosition(interpolatedPos);
  }, [simulationProgress]);

  return null;
};
