# 🌟 StarNavigation

A web application that uses a celestial compass navigation algorithm to find paths between two locations on Earth using stars, planets, and other celestial objects as reference points.

## Overview

StarNavigation implements a unique pathfinding algorithm that navigates without GPS, magnetometers, or electronic signals. Instead, it uses the positions of celestial objects visible from Earth to create a series of waypoints leading from a start location to a target location.

## How It Works

1. **Calculate Compass Direction**: Determine the bearing from current position to target
2. **Query Visible Celestial Objects**: Find stars, planets, and the moon visible from the observer's position
3. **Select Best Reference**: Choose the celestial object whose position most closely aligns with the target direction
4. **Follow the Object**: Move toward the celestial object until it sets below the horizon or the path starts moving away from the target
5. **Repeat**: Select a new celestial object and continue until the target is reached

## Project Structure

```
StarNavigation/
├── frontend/          # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── hooks/        # Custom React hooks
│   │   ├── stores/       # Zustand state stores
│   │   ├── services/     # API clients
│   │   └── types/        # TypeScript interfaces
│   └── ...
├── backend/           # Python FastAPI backend
│   ├── src/
│   │   ├── api/          # API routes
│   │   ├── core/         # Navigation algorithm
│   │   └── data/         # Star catalogs & data
│   └── ...
├── docs/              # Documentation
└── shared/            # Shared types/contracts
```

## Quick Start

### Prerequisites

- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Docker Deployment

For a quick and easy setup using Docker, follow these steps:

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Build and Start

Run the following command in the project root directory:

```bash
docker-compose up --build
```

Once the containers are running, you can access the application at:
[http://localhost](http://localhost)

### Architecture

The Docker deployment consists of three main components:
- **FastAPI Backend**: Handles the celestial navigation logic and API requests.
- **Vite Frontend**: Provides the interactive user interface.
- **Nginx Proxy**: Acts as a reverse proxy, routing traffic to the frontend and backend services.

## Features

- 🗺️ Interactive map with Leaflet
- ⭐ Real-time celestial object positions
- 🧭 Celestial compass navigation algorithm
- 📍 Multiple location input methods (map click, search, coordinates, geolocation)
- ⏰ Time selection for past/future navigation
- 📊 Route statistics and waypoint details
- 📤 Export to GPX and GeoJSON formats
- 🎨 Material Design 3 UI

## Roadmap

- [x] Basic navigation algorithm
- [x] Map visualization
- [x] Location input methods
- [ ] Export features
- [ ] Time selection
- [ ] Simulation mode
- [ ] Mobile optimization
- [ ] User accounts and saved routes

## License

MIT License - see LICENSE file for details
