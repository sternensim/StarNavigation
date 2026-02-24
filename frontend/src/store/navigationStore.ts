/**
 * Zustand store for navigation state management
 */
import { create } from 'zustand';
import { Position, NavigationResponse, Waypoint, CelestialObject } from '../types';

interface NavigationState {
  // Location state
  startLocation: Position | null;
  targetLocation: Position | null;
  startLocationName: string;
  targetLocationName: string;

  // Navigation result
  route: NavigationResponse | null;
  isCalculating: boolean;
  error: string | null;

  // UI state
  selectedWaypoint: Waypoint | null;
  sidebarOpen: boolean;
  mapCenter: Position;
  mapZoom: number;

  // Time selection (for future implementation)
  selectedTime: Date | null;
  useCurrentTime: boolean;

  // Actions
  setStartLocation: (location: Position | null, name?: string) => void;
  setTargetLocation: (location: Position | null, name?: string) => void;
  swapLocations: () => void;
  setRoute: (route: NavigationResponse | null) => void;
  setIsCalculating: (isCalculating: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedWaypoint: (waypoint: Waypoint | null) => void;
  setSidebarOpen: (open: boolean) => void;
  setMapCenter: (center: Position) => void;
  setMapZoom: (zoom: number) => void;
  setSelectedTime: (time: Date | null) => void;
  setUseCurrentTime: (useCurrent: boolean) => void;
  clearRoute: () => void;
  reset: () => void;
}

// Default center (Berlin)
const DEFAULT_CENTER: Position = { latitude: 52.52, longitude: 13.405 };

export const useNavigationStore = create<NavigationState>((set, get) => ({
  // Initial state
  startLocation: null,
  targetLocation: null,
  startLocationName: '',
  targetLocationName: '',
  route: null,
  isCalculating: false,
  error: null,
  selectedWaypoint: null,
  sidebarOpen: true,
  mapCenter: DEFAULT_CENTER,
  mapZoom: 5,
  selectedTime: null,
  useCurrentTime: true,

  // Actions
  setStartLocation: (location, name) => set({
    startLocation: location,
    startLocationName: name || (location ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}` : ''),
  }),

  setTargetLocation: (location, name) => set({
    targetLocation: location,
    targetLocationName: name || (location ? `${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}` : ''),
  }),

  swapLocations: () => {
    const { startLocation, targetLocation, startLocationName, targetLocationName } = get();
    set({
      startLocation: targetLocation,
      targetLocation: startLocation,
      startLocationName: targetLocationName,
      targetLocationName: startLocationName,
      route: null,
    });
  },

  setRoute: (route) => set({ route, error: null }),

  setIsCalculating: (isCalculating) => set({ isCalculating }),

  setError: (error) => set({ error, isCalculating: false }),

  setSelectedWaypoint: (waypoint) => set({ selectedWaypoint: waypoint }),

  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  setMapCenter: (center) => set({ mapCenter: center }),

  setMapZoom: (zoom) => set({ mapZoom: zoom }),

  setSelectedTime: (time) => set({ selectedTime: time }),

  setUseCurrentTime: (useCurrent) => set({
    useCurrentTime: useCurrent,
    selectedTime: useCurrent ? null : get().selectedTime,
  }),

  clearRoute: () => set({
    route: null,
    selectedWaypoint: null,
    error: null,
  }),

  reset: () => set({
    startLocation: null,
    targetLocation: null,
    startLocationName: '',
    targetLocationName: '',
    route: null,
    isCalculating: false,
    error: null,
    selectedWaypoint: null,
    mapCenter: DEFAULT_CENTER,
    mapZoom: 5,
    selectedTime: null,
    useCurrentTime: true,
  }),
}));
