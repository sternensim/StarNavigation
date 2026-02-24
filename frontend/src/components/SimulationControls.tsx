import React from 'react';
import {
  Box,
  IconButton,
  Slider,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  RestartAlt as ResetIcon,
} from '@mui/icons-material';
import { useNavigationStore } from '../store/navigationStore';

const SimulationControls: React.FC = () => {
  const {
    isSimulating,
    simulationProgress,
    simulationSpeed,
    setIsSimulating,
    setSimulationProgress,
    setSimulationSpeed,
    resetSimulation,
    route,
  } = useNavigationStore();

  if (!route) return null;

  const handleTogglePlay = () => {
    if (simulationProgress >= 1) {
      setSimulationProgress(0);
    }
    setIsSimulating(!isSimulating);
  };

  const handleSliderChange = (_: Event, newValue: number | number[]) => {
    setSimulationProgress(newValue as number);
  };

  return (
    <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1, border: '1px solid', borderColor: 'grey.200' }}>
      <Typography variant="subtitle2" gutterBottom sx={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
        Route Simulation
      </Typography>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <Tooltip title={isSimulating ? 'Pause' : 'Play'}>
          <IconButton onClick={handleTogglePlay} color="primary" size="small">
            {isSimulating ? <PauseIcon /> : <PlayIcon />}
          </IconButton>
        </Tooltip>

        <Tooltip title="Reset">
          <IconButton onClick={resetSimulation} size="small">
            <ResetIcon />
          </IconButton>
        </Tooltip>

        <Box sx={{ flexGrow: 1, mx: 2 }}>
          <Slider
            value={simulationProgress}
            min={0}
            max={1}
            step={0.001}
            onChange={handleSliderChange}
            size="small"
            valueLabelDisplay="auto"
            valueLabelFormat={(v) => `${(v * 100).toFixed(1)}%`}
          />
        </Box>

        <FormControl size="small" sx={{ minWidth: 70 }}>
          <InputLabel id="speed-label">Speed</InputLabel>
          <Select
            labelId="speed-label"
            value={simulationSpeed}
            label="Speed"
            onChange={(e) => setSimulationSpeed(e.target.value as number)}
            sx={{ height: 32, fontSize: '0.8rem' }}
          >
            <MenuItem value={0.5}>0.5x</MenuItem>
            <MenuItem value={1}>1x</MenuItem>
            <MenuItem value={2}>2x</MenuItem>
            <MenuItem value={5}>5x</MenuItem>
            <MenuItem value={10}>10x</MenuItem>
          </Select>
        </FormControl>
      </Box>
      
      <Typography variant="caption" color="text.secondary" sx={{ display: 'block', textAlign: 'center' }}>
        {isSimulating ? 'Simulating travel...' : 'Simulation paused'}
      </Typography>
    </Box>
  );
};

export default SimulationControls;
