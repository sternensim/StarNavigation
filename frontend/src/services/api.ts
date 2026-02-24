/**
 * API service for communicating with the backend
 */
import axios from 'axios';
import {
  Position,
  NavigationRequest,
  NavigationResponse,
  VisibleObjectsResponse,
  GeocodeResult,
  Waypoint,
  ExportFormat
} from '../types';

const API_BASE_URL = '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a response interceptor for global error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || 'An unexpected error occurred';
    // We can't use hooks here, but we can throw a formatted error
    const formattedError = new Error(message);
    (formattedError as any).status = error.response?.status;
    (formattedError as any).data = error.response?.data;
    return Promise.reject(formattedError);
  }
);

export const navigationApi = {
  /**
   * Calculate a navigation route between two positions
   */
  calculateRoute: async (request: NavigationRequest): Promise<NavigationResponse> => {
    const response = await api.post<NavigationResponse>('/navigation/calculate', request);
    return response.data;
  },

  /**
   * Get compass direction between two points
   */
  getDirection: async (from: Position, to: Position): Promise<{ bearing: number; cardinal_direction: string }> => {
    const response = await api.get('/navigation/direction', {
      params: {
        from_lat: from.latitude,
        from_lon: from.longitude,
        to_lat: to.latitude,
        to_lon: to.longitude,
      },
    });
    return response.data;
  },

  /**
   * Export waypoints to GPX format
   */
  exportGpx: async (waypoints: Waypoint[], name: string = 'celestial_route'): Promise<string> => {
    const response = await api.post('/navigation/export/gpx', {
      waypoints,
      format: 'gpx',
      name,
    });
    return response.data.content;
  },

  /**
   * Export waypoints to GeoJSON format
   */
  exportGeoJson: async (waypoints: Waypoint[], name: string = 'celestial_route'): Promise<unknown> => {
    const response = await api.post('/navigation/export/geojson', {
      waypoints,
      format: 'geojson',
      name,
    });
    return response.data.content;
  },
};

export const celestialApi = {
  /**
   * Get visible celestial objects at a location
   */
  getVisibleObjects: async (
    position: Position,
    date?: Date,
    minAltitude: number = 0,
    maxMagnitude: number = 6
  ): Promise<VisibleObjectsResponse> => {
    const params: Record<string, string | number> = {
      lat: position.latitude,
      lon: position.longitude,
      altitude: position.altitude || 0,
      min_altitude: minAltitude,
      max_magnitude: maxMagnitude,
    };

    if (date) {
      params.year = date.getUTCFullYear();
      params.month = date.getUTCMonth() + 1;
      params.day = date.getUTCDate();
      params.hour = date.getUTCHours();
      params.minute = date.getUTCMinutes();
    }

    const response = await api.get<VisibleObjectsResponse>('/celestial/objects', { params });
    return response.data;
  },

  /**
   * Get star catalog
   */
  getStarCatalog: async (): Promise<{ count: number; stars: Array<{ name: string; right_ascension: number; declination: number; magnitude: number }> }> => {
    const response = await api.get('/celestial/stars');
    return response.data;
  },

  /**
   * Get planet positions
   */
  getPlanetPositions: async (position: Position): Promise<unknown> => {
    const response = await api.get('/celestial/planets', {
      params: {
        lat: position.latitude,
        lon: position.longitude,
        altitude: position.altitude || 0,
      },
    });
    return response.data;
  },

  /**
   * Get sun position
   */
  getSunPosition: async (position: Position): Promise<unknown> => {
    const response = await api.get('/celestial/sun', {
      params: {
        lat: position.latitude,
        lon: position.longitude,
        altitude: position.altitude || 0,
      },
    });
    return response.data;
  },

  /**
   * Get moon position
   */
  getMoonPosition: async (position: Position): Promise<unknown> => {
    const response = await api.get('/celestial/moon', {
      params: {
        lat: position.latitude,
        lon: position.longitude,
        altitude: position.altitude || 0,
      },
    });
    return response.data;
  },
};

// Geocoding using OpenStreetMap Nominatim (free, no API key required for reasonable use)
export const geocodingApi = {
  /**
   * Search for a location by name
   */
  search: async (query: string): Promise<GeocodeResult[]> => {
    const response = await axios.get('https://nominatim.openstreetmap.org/search', {
      params: {
        q: query,
        format: 'json',
        limit: 5,
      },
      headers: {
        'User-Agent': 'StarNavigation/1.0',
      },
    });

    return response.data.map((item: { display_name: string; lat: string; lon: string; address?: { country?: string; state?: string } }) => ({
      name: item.display_name,
      latitude: parseFloat(item.lat),
      longitude: parseFloat(item.lon),
      country: item.address?.country,
      region: item.address?.state,
    }));
  },

  /**
   * Reverse geocode: get location name from coordinates
   */
  reverse: async (position: Position): Promise<GeocodeResult | null> => {
    const response = await axios.get('https://nominatim.openstreetmap.org/reverse', {
      params: {
        lat: position.latitude,
        lon: position.longitude,
        format: 'json',
      },
      headers: {
        'User-Agent': 'StarNavigation/1.0',
      },
    });

    if (!response.data) return null;

    return {
      name: response.data.display_name,
      latitude: position.latitude,
      longitude: position.longitude,
      country: response.data.address?.country,
      region: response.data.address?.state,
    };
  },
};

export default api;
