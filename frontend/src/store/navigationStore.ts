/**
 * Zustand store for navigation state management
 */
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { Position, NavigationResponse, Waypoint, CelestialObject, RouteResult } from '../types';

interface NavigationState {
  // Location state
  startLocation: Position | null;
  targetLocation: Position | null;
  startLocationName: string;
  targetLocationName: string;

  // Navigation result
  routes: RouteResult[];
  selectedRouteId: string | null;
  isCalculating: boolean;
  error: string | null;

  // UI state
  selectedWaypoint: Waypoint | null;
  sidebarOpen: boolean;
  mapCenter: Position;
  mapZoom: number;

  // Simulation state
  isSimulating: boolean;
  simulationProgress: number; // 0 to 1
  simulationSpeed: number;
  currentSimulationPosition: Position | null;

  // Time selection (for future implementation)
  selectedTime: Date | null;
  useCurrentTime: boolean;

  // Navigation settings
  prioritizeMajor: boolean;
  planetsOnly: boolean;
  maxRoutes: number;

  // Actions
  setStartLocation: (location: Position | null, name?: string) => void;
  setTargetLocation: (location: Position | null, name?: string) => void;
  swapLocations: () => void;
  setRoutes: (routes: RouteResult[]) => void;
  setSelectedRouteId: (id: string | null) => void;
  setIsCalculating: (isCalculating: boolean) => void;
  setError: (error: string | null) => void;
  setSelectedWaypoint: (waypoint: Waypoint | null) => void;
  setSidebarOpen: (open: boolean) => void;
  setMapCenter: (center: Position) => void;
  setMapZoom: (zoom: number) => void;
  setSelectedTime: (time: Date | null) => void;
  setUseCurrentTime: (useCurrent: boolean) => void;
  setPrioritizeMajor: (prioritize: boolean) => void;
  setPlanetsOnly: (planetsOnly: boolean) => void;
  setMaxRoutes: (max: number) => void;

  // Simulation actions
  setIsSimulating: (isSimulating: boolean) => void;
  setSimulationProgress: (progress: number) => void;
  setSimulationSpeed: (speed: number) => void;
  setCurrentSimulationPosition: (position: Position | null) => void;
  resetSimulation: () => void;

  clearRoute: () => void;
  reset: () => void;
}

// Default center (Berlin)
const DEFAULT_CENTER: Position = { latitude: 52.52, longitude: 13.405 };

export const useNavigationStore = create<NavigationState>()(
  persist(
    (set, get) => ({
      // Initial state
      startLocation: null,
      targetLocation: null,
      startLocationName: '',
      targetLocationName: '',
      routes: [],
      selectedRouteId: null,
      isCalculating: false,
      error: null,
      selectedWaypoint: null,
      sidebarOpen: true,
      mapCenter: DEFAULT_CENTER,
      mapZoom: 5,
      selectedTime: null,
      useCurrentTime: true,
      prioritizeMajor: false,
      planetsOnly: false,
      maxRoutes: 1,
      isSimulating: false,
      simulationProgress: 0,
      simulationSpeed: 1,
      currentSimulationPosition: null,

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
          routes: [],
          selectedRouteId: null,
        });
      },

      setRoutes: (routes) => set({ 
        routes, 
        selectedRouteId: routes.length > 0 ? routes[0].id : null,
        error: null 
      }),

      setSelectedRouteId: (selectedRouteId) => set({ selectedRouteId }),

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

      setPrioritizeMajor: (prioritize) => set((state) => ({
        prioritizeMajor: prioritize,
        planetsOnly: prioritize ? false : state.planetsOnly,
      })),

      setPlanetsOnly: (planetsOnly) => set((state) => ({
        planetsOnly: planetsOnly,
        prioritizeMajor: planetsOnly ? false : state.prioritizeMajor,
      })),

      setMaxRoutes: (maxRoutes) => set({ maxRoutes }),

      setIsSimulating: (isSimulating) => set({ isSimulating }),
      setSimulationProgress: (simulationProgress) => set({ simulationProgress }),
      setSimulationSpeed: (simulationSpeed) => set({ simulationSpeed }),
      setCurrentSimulationPosition: (currentSimulationPosition) => set({ currentSimulationPosition }),
      resetSimulation: () => set({ 
        isSimulating: false, 
        simulationProgress: 0, 
        currentSimulationPosition: null 
      }),

      clearRoute: () => {
        get().resetSimulation();
        set({
          routes: [],
          selectedRouteId: null,
          selectedWaypoint: null,
          error: null,
        });
      },

      reset: () => set({
        startLocation: null,
        targetLocation: null,
        startLocationName: '',
        targetLocationName: '',
        routes: [],
        selectedRouteId: null,
        isCalculating: false,
        error: null,
        selectedWaypoint: null,
        mapCenter: DEFAULT_CENTER,
        mapZoom: 5,
        selectedTime: null,
        useCurrentTime: true,
        prioritizeMajor: false,
        planetsOnly: false,
        maxRoutes: 1,
        isSimulating: false,
        simulationProgress: 0,
        simulationSpeed: 1,
        currentSimulationPosition: null,
      }),
    }),
    {
      name: 'navigation-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        startLocation: state.startLocation,
        targetLocation: state.targetLocation,
        startLocationName: state.startLocationName,
        targetLocationName: state.targetLocationName,
        routes: state.routes,
        selectedRouteId: state.selectedRouteId,
        mapCenter: state.mapCenter,
        mapZoom: state.mapZoom,
        prioritizeMajor: state.prioritizeMajor,
        planetsOnly: state.planetsOnly,
        maxRoutes: state.maxRoutes,
      }),
    }
  )
);
