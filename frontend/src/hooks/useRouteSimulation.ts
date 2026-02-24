import { useEffect, useRef } from 'react';
import L from 'leaflet';
import { useNavigationStore } from '../store/navigationStore';
import { Position } from '../types';
import { interpolateGeodesic } from '../utils/geodesic';

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
    const interpolatedPos = interpolateGeodesic(p1, p2, segmentProgress);

    setCurrentSimulationPosition(interpolatedPos);
  }, [simulationProgress]);

  return null;
};
