/**
 * Main App Component
 * Layout with sidebar for inputs and main area for the map
 */
import { useState, useCallback } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  CssBaseline,
  ThemeProvider,
  createTheme,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Navigation as NavigationIcon,
} from '@mui/icons-material';

import { useNavigationStore } from './store/navigationStore';
import { navigationApi } from './services/api';
import { Position } from './types';
import MapComponent from './components/Map/MapComponent';
import LocationInput from './components/LocationInput';
import RouteInfo from './components/RouteInfo';

const DRAWER_WIDTH = 400;

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [clickMode, setClickMode] = useState<'start' | 'target' | null>(null);
  const [error, setError] = useState<string | null>(null);

  const {
    startLocation,
    targetLocation,
    startLocationName,
    targetLocationName,
    route,
    isCalculating,
    setStartLocation,
    setTargetLocation,
    setRoute,
    setIsCalculating,
    setError: setStoreError,
    clearRoute,
    sidebarOpen,
    setSidebarOpen,
    setMapCenter,
  } = useNavigationStore();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
    setSidebarOpen(!sidebarOpen);
  };

  const handleMapClick = useCallback((position: Position) => {
    if (clickMode === 'start') {
      setStartLocation(position);
      setClickMode(null);
    } else if (clickMode === 'target') {
      setTargetLocation(position);
      setClickMode(null);
    }
  }, [clickMode, setStartLocation, setTargetLocation]);

  const handleCalculateRoute = async () => {
    if (!startLocation || !targetLocation) {
      setError('Please select both start and target locations');
      return;
    }

    setIsCalculating(true);
    clearRoute();

    try {
      const response = await navigationApi.calculateRoute({
        start: startLocation,
        target: targetLocation,
      });

      setRoute(response);

      // Center map on route
      if (response.waypoints.length > 0) {
        const midIndex = Math.floor(response.waypoints.length / 2);
        const midPoint = response.waypoints[midIndex].position;
        setMapCenter(midPoint);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to calculate route';
      setStoreError(errorMessage);
      setError(errorMessage);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleCloseError = () => {
    setError(null);
  };

  const drawerContent = (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <NavigationIcon />
        StarNavigation
      </Typography>

      <LocationInput
        startLocation={startLocation}
        targetLocation={targetLocation}
        startLocationName={startLocationName}
        targetLocationName={targetLocationName}
        onStartLocationChange={setStartLocation}
        onTargetLocationChange={setTargetLocation}
        onMapClickModeChange={setClickMode}
        clickMode={clickMode}
        onSwapLocations={() => {
          useNavigationStore.getState().swapLocations();
        }}
      />

      <RouteInfo
        route={route}
        isCalculating={isCalculating}
        onCalculate={handleCalculateRoute}
        waypoints={route?.waypoints || []}
      />
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh' }}>
        {/* App Bar */}
        <AppBar
          position="fixed"
          sx={{
            width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
            ml: { md: `${DRAWER_WIDTH}px` },
          }}
        >
          <Toolbar>
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { md: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div">
              Celestial Compass Navigation
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Sidebar Drawer */}
        <Box
          component="nav"
          sx={{ width: { md: DRAWER_WIDTH }, flexShrink: { md: 0 } }}
        >
          {/* Mobile drawer */}
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile
            }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: DRAWER_WIDTH,
              },
            }}
          >
            {drawerContent}
          </Drawer>

          {/* Desktop drawer */}
          <Drawer
            variant="permanent"
            sx={{
              display: { xs: 'none', md: 'block' },
              '& .MuiDrawer-paper': {
                boxSizing: 'border-box',
                width: DRAWER_WIDTH,
                position: 'relative',
                height: '100vh',
              },
            }}
            open
          >
            {drawerContent}
          </Drawer>
        </Box>

        {/* Main content - Map */}
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            width: { md: `calc(100% - ${DRAWER_WIDTH}px)` },
            height: '100vh',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Toolbar />
          <Box sx={{ flexGrow: 1, position: 'relative' }}>
            <MapComponent clickMode={clickMode} onMapClick={handleMapClick} />
          </Box>
        </Box>

        {/* Error Snackbar */}
        <Snackbar open={!!error} autoHideDuration={6000} onClose={handleCloseError}>
          <Alert onClose={handleCloseError} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;
