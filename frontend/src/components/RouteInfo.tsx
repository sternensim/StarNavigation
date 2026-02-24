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
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Download as DownloadIcon,
  ExpandMore as ExpandMoreIcon,
  Navigation as NavigationIcon,
  LocationOn as LocationIcon,
  Star as StarIcon,
} from '@mui/icons-material';

import { NavigationResponse, Waypoint, StopReason } from '../types';
import { navigationApi } from '../services/api';
import { useNavigationStore } from '../store/navigationStore';

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
  route: NavigationResponse | null;
  isCalculating: boolean;
  onCalculate: () => void;
  waypoints: Waypoint[];
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
  route,
  isCalculating,
  onCalculate,
  waypoints,
}) => {
  const { prioritizeMajor, setPrioritizeMajor } = useNavigationStore();

  const handleExportGpx = async () => {
    if (!route?.waypoints) return;

    try {
      const gpxContent = await navigationApi.exportGpx(route.waypoints);
      const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'celestial_route.gpx';
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
    if (!route?.waypoints) return;

    try {
      const geoJsonContent = await navigationApi.exportGeoJson(route.waypoints);
      const blob = new Blob([JSON.stringify(geoJsonContent, null, 2)], {
        type: 'application/geo+json',
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'celestial_route.geojson';
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
          sx={{ ml: 0 }}
        />
      </Paper>

      {route && (
        <>
          {/* Route Statistics */}
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="h6" gutterBottom>
              Route Statistics
            </Typography>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Total Distance:</Typography>
              <Typography fontWeight="bold">{route.total_distance.toFixed(2)} km</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Direct Distance:</Typography>
              <Typography>{route.direct_distance.toFixed(2)} km</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Waypoints:</Typography>
              <Typography>{route.waypoints.length}</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Iterations:</Typography>
              <Typography>{route.iterations}</Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography color="text.secondary">Celestial Objects Used:</Typography>
              <Typography>{route.used_objects.length}</Typography>
            </Box>

            {route.used_objects.length > 0 && (
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Objects Used:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {route.used_objects.map((obj, idx) => (
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
          {route.waypoints.length > 0 && (
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
                {route.waypoints.slice(0, -1).map((_, index) => (
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
              <Typography>Waypoints ({waypoints.length})</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ p: 0 }}>
              <List dense>
                {waypoints.map((waypoint, index) => (
                  <ListItem key={index} divider={index < waypoints.length - 1}>
                    <ListItemIcon>
                      {index === 0 ? (
                        <LocationIcon color="success" />
                      ) : index === waypoints.length - 1 ? (
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
    </Box>
  );
};

export default RouteInfo;
