/**
 * Route Info Component
 * Displays route statistics and provides calculate/export functionality
 */
import {
  Box,
  Button,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormControlLabel,
  Switch,
  Slider,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  ExpandMore as ExpandMoreIcon,
  Navigation as NavigationIcon,
  LocationOn as LocationIcon,
  Star as StarIcon,
} from '@mui/icons-material';

import { Waypoint, StopReason, RouteResult } from '../types';
import { navigationApi } from '../services/api';
import { useNavigationStore } from '../store/navigationStore';
import SimulationControls from './SimulationControls';

// Color palette matching MapComponent
const LEG_COLORS = [
  '#e53935', // Red
  '#1e88e5', // Blue
  '#43a047', // Green
  '#fb8c00', // Orange
  '#8e24aa', // Purple
  '#00acc1', // Cyan
  '#fdd835', // Yellow
  '#6d4c41', // Brown
  '#3949ab', // Indigo
  '#d81b60', // Pink
];

interface RouteInfoProps {
  routes: RouteResult[];
  isCalculating: boolean;
  onCalculate: () => void;
}

const getReasonColor = (reason: StopReason): 'success' | 'warning' | 'info' => {
  switch (reason) {
    case 'target_reached':
      return 'success';
    case 'object_lost':
      return 'warning';
    case 'closest_approach':
      return 'info';
    default:
      return 'info';
  }
};

const getReasonLabel = (reason: StopReason): string => {
  return reason.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase());
};

const RouteInfo: React.FC<RouteInfoProps> = ({
  routes,
  isCalculating,
  onCalculate,
}) => {
  const { 
    prioritizeMajor, 
    setPrioritizeMajor, 
    planetsOnly, 
    setPlanetsOnly,
    maxRoutes,
    setMaxRoutes,
    selectedRouteId,
    setSelectedRouteId
  } = useNavigationStore();

  const selectedRoute = routes.find(r => r.id === selectedRouteId) || (routes.length > 0 ? routes[0] : null);

  const handleExportGpx = async () => {
    if (!selectedRoute?.waypoints) return;

    try {
      const gpxContent = await navigationApi.exportGpx(selectedRoute.waypoints);
      const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `celestial_route_${selectedRoute.id}.gpx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export GPX file');
    }
  };

  const handleExportGeoJson = async () => {
    if (!selectedRoute?.waypoints) return;

    try {
      const geoJsonContent = await navigationApi.exportGeoJson(selectedRoute.waypoints);
      const blob = new Blob([JSON.stringify(geoJsonContent, null, 2)], {
        type: 'application/geo+json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `celestial_route_${selectedRoute.id}.geojson`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Failed to export GeoJSON file');
    }
  };

  const canCalculate = !isCalculating;

  return (
    <Box>
      {/* Calculate Button */}
      <Button
        variant="contained"
        fullWidth
        size="large"
        startIcon={isCalculating ? <CircularProgress size={20} color="inherit" /> : <PlayIcon />}
        onClick={onCalculate}
        disabled={!canCalculate}
        sx={{ mb: 2 }}
      >
        {isCalculating ? 'Calculating...' : 'Calculate Route'}
      </Button>

      {/* Settings */}
      <Paper sx={{ p: 1, mb: 2 }}>
        <FormControlLabel
          control={
            <Switch
              checked={prioritizeMajor}
              onChange={(e) => setPrioritizeMajor(e.target.checked)}
              color="primary"
            />
          }
          label={
            <Typography variant="body2">
              Prioritize Planets and Major Stars
            </Typography>
          }
          sx={{ ml: 0, display: 'block' }}
        />
        <FormControlLabel
          control={
            <Switch
              checked={planetsOnly}
              onChange={(e) => setPlanetsOnly(e.target.checked)}
              color="primary"
            />
          }
          label={
            <Typography variant="body2">
              Planets/Moon Only
            </Typography>
          }
          sx={{ ml: 0, display: 'block' }}
        />
        
        <Box sx={{ px: 1, mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Max Routes: {maxRoutes}
          </Typography>
          <Slider
            value={maxRoutes}
            min={1}
            max={5}
            step={1}
            marks
            onChange={(_, v) => setMaxRoutes(v as number)}
            size="small"
          />
        </Box>
      </Paper>

      {routes.length > 0 && (
        <>
          {/* Route Selector */}
          {routes.length > 1 && (
            <Box sx={{ mb: 2, display: 'flex', gap: 1, overflowX: 'auto', pb: 1 }}>
              {routes.map((r) => (
                <Chip
                  key={r.id}
                  label={r.label}
                  onClick={() => setSelectedRouteId(r.id)}
                  color={selectedRouteId === r.id ? 'primary' : 'default'}
                  variant={selectedRouteId === r.id ? 'filled' : 'outlined'}
                  sx={{ flexShrink: 0 }}
                />
              ))}
            </Box>
          )}

          {selectedRoute && (
            <>
              {/* Simulation Controls */}
              <SimulationControls />

              {/* Route Statistics */}
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {selectedRoute.label} Statistics
                </Typography>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">Total Distance:</Typography>
                  <Typography fontWeight="bold">{selectedRoute.total_distance.toFixed(2)} km</Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">Direct Distance:</Typography>
                  <Typography>{selectedRoute.direct_distance.toFixed(2)} km</Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">Waypoints:</Typography>
                  <Typography>{selectedRoute.waypoints.length}</Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">Iterations:</Typography>
                  <Typography>{selectedRoute.iterations}</Typography>
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography color="text.secondary">Celestial Objects Used:</Typography>
                  <Typography>{selectedRoute.used_objects.length}</Typography>
                </Box>

                {selectedRoute.used_objects.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Objects Used:
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selectedRoute.used_objects.map((obj, idx) => (
                        <Chip
                          key={idx}
                          icon={<StarIcon />}
                          label={obj}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>
                )}
              </Paper>

              {/* Route Legs Legend */}
              {selectedRoute.waypoints.length > 0 && (
                <Paper sx={{ p: 2, mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Route Legs
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    {/* Leg 1: Start to first waypoint */}
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 24,
                          height: 4,
                          borderRadius: 1,
                          backgroundColor: LEG_COLORS[0],
                        }}
                      />
                      <Typography variant="body2">
                        Leg 1: Start → Waypoint 1
                      </Typography>
                    </Box>
                    {/* Leg 2+: Between waypoints */}
                    {selectedRoute.waypoints.slice(0, -1).map((_, index) => (
                      <Box key={index + 1} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Box
                          sx={{
                            width: 24,
                            height: 4,
                            borderRadius: 1,
                            backgroundColor: LEG_COLORS[(index + 1) % LEG_COLORS.length],
                          }}
                        />
                        <Typography variant="body2">
                          Leg {index + 2}: Waypoint {index + 1} → {index + 2}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </Paper>
              )}

              {/* Export Buttons */}
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportGpx}
                  fullWidth
                >
                  GPX
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<DownloadIcon />}
                  onClick={handleExportGeoJson}
                  fullWidth
                >
                  GeoJSON
                </Button>
              </Box>

              {/* Waypoints List */}
              <Accordion defaultExpanded>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Waypoints ({selectedRoute.waypoints.length})</Typography>
                </AccordionSummary>
                <AccordionDetails sx={{ p: 0 }}>
                  <List dense>
                    {selectedRoute.waypoints.map((waypoint, index) => (
                      <ListItem key={index} divider={index < selectedRoute.waypoints.length - 1}>
                        <ListItemIcon>
                          {index === 0 ? (
                            <LocationIcon color="success" />
                          ) : index === selectedRoute.waypoints.length - 1 ? (
                            <LocationIcon color="error" />
                          ) : (
                            <NavigationIcon color="primary" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2">
                                {waypoint.position.latitude.toFixed(4)},{' '}
                                {waypoint.position.longitude.toFixed(4)}
                              </Typography>
                              <Chip
                                label={getReasonLabel(waypoint.reason)}
                                color={getReasonColor(waypoint.reason)}
                                size="small"
                              />
                            </Box>
                          }
                          secondary={
                            waypoint.reference_object && (
                              <Typography variant="caption" color="text.secondary">
                                via {waypoint.reference_object.name} ({waypoint.reference_object.object_type})
                              </Typography>
                            )
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            </>
          )}
        </>
      )}
    </Box>
  );
};

export default RouteInfo;
