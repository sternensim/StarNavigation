/**
 * Map Component using Leaflet
 * Displays the navigation route, waypoints, and allows location selection
 */
import { useEffect, useCallback, useMemo } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Box } from '@mui/material';
import { useNavigationStore } from '../../store/navigationStore';
import { Position, Waypoint } from '../../types';

// Fix Leaflet default icon issue
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
  iconUrl: icon,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

// Custom icons
const createCustomIcon = (color: string) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="
      background-color: ${color};
      width: 24px;
      height: 24px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    "></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const startIcon = createCustomIcon('#4caf50'); // Green
const targetIcon = createCustomIcon('#f44336'); // Red
const waypointIcon = createCustomIcon('#2196f3'); // Blue

// Map click handler component
interface MapClickHandlerProps {
  onMapClick: (position: Position) => void;
  clickMode: 'start' | 'target' | null;
}

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onMapClick, clickMode }) => {
  useMapEvents({
    click: (e) => {
      if (clickMode) {
        onMapClick({
          latitude: e.latlng.lat,
          longitude: e.latlng.lng,
        });
      }
    },
  });
  return null;
};

// Map view controller
interface MapControllerProps {
  center: Position;
  zoom: number;
}

const MapController: React.FC<MapControllerProps> = ({ center, zoom }) => {
  const map = useMap();

  useEffect(() => {
    map.setView([center.latitude, center.longitude], zoom);
  }, [center, zoom, map]);

  return null;
};

// Waypoint popup content
const WaypointPopup: React.FC<{ waypoint: Waypoint; index: number }> = ({ waypoint, index }) => {
  return (
    <div>
      <h4>Waypoint {index + 1}</h4>
      <p>
        <strong>Position:</strong> {waypoint.position.latitude.toFixed(4)},{' '}
        {waypoint.position.longitude.toFixed(4)}
      </p>
      {waypoint.reference_object && (
        <p>
          <strong>Reference:</strong> {waypoint.reference_object.name} ({waypoint.reference_object.object_type})
        </p>
      )}
      <p>
        <strong>Reason:</strong> {waypoint.reason.replace('_', ' ')}
      </p>
      {waypoint.distance_to_target !== undefined && (
        <p>
          <strong>Distance to target:</strong> {waypoint.distance_to_target.toFixed(2)} km
        </p>
      )}
    </div>
  );
};

// Main Map Component
interface MapComponentProps {
  clickMode: 'start' | 'target' | null;
  onMapClick: (position: Position) => void;
}

const MapComponent: React.FC<MapComponentProps> = ({ clickMode, onMapClick }) => {
  const {
    startLocation,
    targetLocation,
    route,
    mapCenter,
    mapZoom,
    selectedWaypoint,
    setSelectedWaypoint,
  } = useNavigationStore();

  // Calculate route polyline positions
  const routePositions = useMemo(() => {
    if (!route?.waypoints) return [];
    return route.waypoints.map((wp) => [wp.position.latitude, wp.position.longitude] as L.LatLngExpression);
  }, [route]);

  // Calculate bounds to fit route
  const fitBounds = useCallback(() => {
    if (route?.waypoints && route.waypoints.length > 0) {
      const bounds = L.latLngBounds(
        route.waypoints.map((wp) => [wp.position.latitude, wp.position.longitude])
      );
      return bounds;
    }
    return null;
  }, [route]);

  return (
    <Box sx={{ height: '100%', width: '100%', position: 'relative' }}>
      <MapContainer
        center={[mapCenter.latitude, mapCenter.longitude]}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        <MapController center={mapCenter} zoom={mapZoom} />
        <MapClickHandler onMapClick={onMapClick} clickMode={clickMode} />

        {/* Start location marker */}
        {startLocation && (
          <Marker
            position={[startLocation.latitude, startLocation.longitude]}
            icon={startIcon}
          >
            <Popup>
              <div>
                <strong>Start Location</strong>
                <br />
                {startLocation.latitude.toFixed(4)}, {startLocation.longitude.toFixed(4)}
              </div>
            </Popup>
          </Marker>
        )}

        {/* Target location marker */}
        {targetLocation && (
          <Marker
            position={[targetLocation.latitude, targetLocation.longitude]}
            icon={targetIcon}
          >
            <Popup>
              <div>
                <strong>Target Location</strong>
                <br />
                {targetLocation.latitude.toFixed(4)}, {targetLocation.longitude.toFixed(4)}
              </div>
            </Popup>
          </Marker>
        )}

        {/* Route polyline */}
        {routePositions.length > 0 && (
          <Polyline
            positions={routePositions}
            color="#2196f3"
            weight={4}
            opacity={0.8}
          />
        )}

        {/* Waypoint markers */}
        {route?.waypoints.map((waypoint, index) => (
          <Marker
            key={index}
            position={[waypoint.position.latitude, waypoint.position.longitude]}
            icon={waypointIcon}
            eventHandlers={{
              click: () => setSelectedWaypoint(waypoint),
            }}
          >
            <Popup>
              <WaypointPopup waypoint={waypoint} index={index} />
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Click mode indicator */}
      {clickMode && (
        <Box
          sx={{
            position: 'absolute',
            top: 16,
            left: '50%',
            transform: 'translateX(-50%)',
            zIndex: 1000,
            backgroundColor: 'primary.main',
            color: 'white',
            px: 2,
            py: 1,
            borderRadius: 1,
            boxShadow: 2,
          }}
        >
          Click on the map to set {clickMode} location
        </Box>
      )}
    </Box>
  );
};

export default MapComponent;
