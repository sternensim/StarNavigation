/**
 * Location Input Component
 * Allows users to input start and target locations via various methods
 */
import { useState, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  IconButton,
  Typography,
  Divider,
  InputAdornment,
  Paper,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Search as SearchIcon,
  MyLocation as MyLocationIcon,
  SwapVert as SwapIcon,
  Map as MapIcon,
} from '@mui/icons-material';

import { Position, GeocodeResult } from '../types';
import { geocodingApi } from '../services/api';

interface LocationInputProps {
  startLocation: Position | null;
  targetLocation: Position | null;
  startLocationName: string;
  targetLocationName: string;
  onStartLocationChange: (location: Position | null, name?: string) => void;
  onTargetLocationChange: (location: Position | null, name?: string) => void;
  onMapClickModeChange: (mode: 'start' | 'target' | null) => void;
  clickMode: 'start' | 'target' | null;
  onSwapLocations: () => void;
}

const LocationInput: React.FC<LocationInputProps> = ({
  startLocation,
  targetLocation,
  startLocationName,
  targetLocationName,
  onStartLocationChange,
  onTargetLocationChange,
  onMapClickModeChange,
  clickMode,
  onSwapLocations,
}) => {
  const [startSearch, setStartSearch] = useState('');
  const [targetSearch, setTargetSearch] = useState('');
  const [searchResults, setSearchResults] = useState<GeocodeResult[]>([]);
  const [searchingFor, setSearchingFor] = useState<'start' | 'target' | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = useCallback(async (query: string, type: 'start' | 'target') => {
    if (!query.trim()) return;

    setIsSearching(true);
    setSearchingFor(type);

    try {
      const results = await geocodingApi.search(query);
      setSearchResults(results);
      if (results.length === 0) {
        // We could use a toast here if we had a global one
        console.log('No results found');
      }
    } catch (error) {
      console.error('Search failed:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  }, []);

  const handleSelectResult = (result: GeocodeResult, type: 'start' | 'target') => {
    const position: Position = {
      latitude: result.latitude,
      longitude: result.longitude,
    };

    if (type === 'start') {
      onStartLocationChange(position, result.name);
      setStartSearch('');
    } else {
      onTargetLocationChange(position, result.name);
      setTargetSearch('');
    }

    setSearchResults([]);
    setSearchingFor(null);
  };

  const handleUseCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const pos: Position = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          };
          onStartLocationChange(pos, 'Current Location');
        },
        (error) => {
          console.error('Geolocation error:', error);
          let msg = 'Could not get your location.';
          if (error.code === error.PERMISSION_DENIED) msg += ' Permission denied.';
          else if (error.code === error.POSITION_UNAVAILABLE) msg += ' Position unavailable.';
          else if (error.code === error.TIMEOUT) msg += ' Request timed out.';
          
          // Ideally this would use the global error state in App.tsx
          // For now, we'll keep the alert but make it more descriptive
          alert(msg);
        }
      );
    } else {
      alert('Geolocation is not supported by your browser');
    }
  };

  const handleCoordinateInput = (
    type: 'start' | 'target',
    latStr: string,
    lonStr: string
  ) => {
    const lat = parseFloat(latStr);
    const lon = parseFloat(lonStr);

    if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
      const position: Position = { latitude: lat, longitude: lon };
      if (type === 'start') {
        onStartLocationChange(position);
      } else {
        onTargetLocationChange(position);
      }
    }
  };

  return (
    <Box>
      <Typography variant="subtitle1" gutterBottom>
        Start Location
      </Typography>

      {/* Search input for start */}
      <TextField
        fullWidth
        size="small"
        placeholder="Search for a place..."
        value={startSearch}
        onChange={(e) => setStartSearch(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSearch(startSearch, 'start');
          }
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <LocationIcon color="success" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                size="small"
                onClick={() => handleSearch(startSearch, 'start')}
                disabled={isSearching}
              >
                {isSearching && searchingFor === 'start' ? (
                  <CircularProgress size={20} />
                ) : (
                  <SearchIcon />
                )}
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{ mb: 1 }}
      />

      {/* Coordinate input for start */}
      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <TextField
          size="small"
          label="Lat"
          type="number"
          value={startLocation?.latitude ?? ''}
          onChange={(e) =>
            handleCoordinateInput(
              'start',
              e.target.value,
              String(startLocation?.longitude ?? '')
            )
          }
          inputProps={{ step: 0.0001 }}
          sx={{ flex: 1 }}
        />
        <TextField
          size="small"
          label="Lon"
          type="number"
          value={startLocation?.longitude ?? ''}
          onChange={(e) =>
            handleCoordinateInput(
              'start',
              String(startLocation?.latitude ?? ''),
              e.target.value
            )
          }
          inputProps={{ step: 0.0001 }}
          sx={{ flex: 1 }}
        />
      </Box>

      {/* Action buttons for start */}
      <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 1, mb: 2 }}>
        <Button
          variant={clickMode === 'start' ? 'contained' : 'outlined'}
          size="small"
          startIcon={<MapIcon />}
          onClick={() =>
            onMapClickModeChange(clickMode === 'start' ? null : 'start')
          }
          fullWidth
        >
          {clickMode === 'start' ? 'Click on Map...' : 'Set on Map'}
        </Button>
        <Button
          variant="outlined"
          size="small"
          startIcon={<MyLocationIcon />}
          onClick={handleUseCurrentLocation}
          sx={{ width: { xs: '100%', sm: 'auto' } }}
        >
          Current
        </Button>
      </Box>

      {/* Display selected start location */}
      {startLocationName && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Selected: {startLocationName}
        </Typography>
      )}

      {/* Swap button */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
        <IconButton onClick={onSwapLocations} color="primary">
          <SwapIcon />
        </IconButton>
      </Box>

      <Typography variant="subtitle1" gutterBottom>
        Target Location
      </Typography>

      {/* Search input for target */}
      <TextField
        fullWidth
        size="small"
        placeholder="Search for a place..."
        value={targetSearch}
        onChange={(e) => setTargetSearch(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter') {
            handleSearch(targetSearch, 'target');
          }
        }}
        InputProps={{
          startAdornment: (
            <InputAdornment position="start">
              <LocationIcon color="error" />
            </InputAdornment>
          ),
          endAdornment: (
            <InputAdornment position="end">
              <IconButton
                size="small"
                onClick={() => handleSearch(targetSearch, 'target')}
                disabled={isSearching}
              >
                {isSearching && searchingFor === 'target' ? (
                  <CircularProgress size={20} />
                ) : (
                  <SearchIcon />
                )}
              </IconButton>
            </InputAdornment>
          ),
        }}
        sx={{ mb: 1 }}
      />

      {/* Coordinate input for target */}
      <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
        <TextField
          size="small"
          label="Lat"
          type="number"
          value={targetLocation?.latitude ?? ''}
          onChange={(e) =>
            handleCoordinateInput(
              'target',
              e.target.value,
              String(targetLocation?.longitude ?? '')
            )
          }
          inputProps={{ step: 0.0001 }}
          sx={{ flex: 1 }}
        />
        <TextField
          size="small"
          label="Lon"
          type="number"
          value={targetLocation?.longitude ?? ''}
          onChange={(e) =>
            handleCoordinateInput(
              'target',
              String(targetLocation?.latitude ?? ''),
              e.target.value
            )
          }
          inputProps={{ step: 0.0001 }}
          sx={{ flex: 1 }}
        />
      </Box>

      {/* Action buttons for target */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button
          variant={clickMode === 'target' ? 'contained' : 'outlined'}
          size="small"
          startIcon={<MapIcon />}
          onClick={() =>
            onMapClickModeChange(clickMode === 'target' ? null : 'target')
          }
          fullWidth
        >
          {clickMode === 'target' ? 'Click on Map...' : 'Set on Map'}
        </Button>
      </Box>

      {/* Display selected target location */}
      {targetLocationName && (
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Selected: {targetLocationName}
        </Typography>
      )}

      {/* Search results */}
      {searchResults.length > 0 && searchingFor && (
        <Paper sx={{ maxHeight: 200, overflow: 'auto', mb: 2 }}>
          <List dense>
            {searchResults.map((result, index) => (
              <ListItem
                key={index}
                button
                onClick={() => handleSelectResult(result, searchingFor)}
              >
                <ListItemText
                  primary={result.name}
                  secondary={`${result.latitude.toFixed(4)}, ${result.longitude.toFixed(4)}`}
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <Divider sx={{ my: 2 }} />
    </Box>
  );
};

export default LocationInput;
