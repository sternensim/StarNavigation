# StarNavigation Project Roadmap

## Overview
StarNavigation is a celestial navigation application that calculates routes using stars and celestial objects as waypoints. This roadmap documents completed features, known issues, and planned enhancements.

---

## Completed Features

### Backend (Python/FastAPI)
- [x] **Celestial Navigation Algorithm** - Core navigation logic using skyfield library
- [x] **Dynamic Target Reached Cutoff** - Cutoff calculated as `min(total_distance * 0.05, 5.0)` km
  - 50 km route → 2.5 km cutoff
  - 100+ km route → 5.0 km cutoff (capped)
- [x] **API Endpoints** - RESTful API for route calculation and celestial data
- [x] **GeoJSON Export** - Route export in GeoJSON format
- [x] **NumPy Compatibility Fix** - Pinned numpy<2.0 for skyfield compatibility
- [x] **Skyfield Update** - Updated to 1.54 to support NumPy 2.0 natively.

### Frontend (React/TypeScript/Leaflet)
- [x] **Interactive Map** - Leaflet-based map with OpenStreetMap tiles
- [x] **Route Visualization** - Colored polylines for each leg
  - Leg 1: Start → Waypoint 1 (Red)
  - Leg 2+: Waypoint n → Waypoint n+1 (cycling colors)
- [x] **Route Leg Legend** - Visual legend showing leg colors and descriptions
- [x] **Waypoint Markers** - Custom markers for start, target, and waypoints
- [x] **Location Input** - Form for entering start/target coordinates
- [x] **Route Information Panel** - Displays route details, statistics, and export options
- [x] **Dependency Updates** - Updated ESLint and TypeScript dependencies
- [x] **Dependency Vulnerabilities** - Resolved all vulnerabilities using npm overrides.
- [x] **Route Persistence** - Implemented localStorage persistence.
- [x] **Mobile Responsiveness** - Improved drawer and control behavior for mobile devices.

---

## Known Issues & Technical Debt

### Backend
- [x] **Skyfield Deprecation** - Updated `skyfield` to `1.54` and removed `numpy<2.0` pin. Skyfield 1.48+ officially supports NumPy 2.0.
- [ ] **No Persistent Storage** - Routes are calculated on-the-fly with no database
- [x] **Limited Error Handling** - Improved with global exception handlers and standardized responses.
- [ ] **No Authentication** - API is completely open

### Frontend
- [x] **Dependency Vulnerabilities** - Resolved all vulnerabilities (including `minimatch` ReDoS) by updating `vite`, `eslint`, and using `npm overrides`.
- [ ] **No Offline Support** - Map requires internet connection
- [x] **Limited Mobile Responsiveness** - Improved drawer behavior, responsive widths, and stackable controls.
- [x] **No Route Persistence** - Implemented `localStorage` persistence using `zustand/middleware`.
- [x] **UI Overlay Issue** - The "multibar" (AppBar) div is overlaying over the map and makes using it more difficult. We should make sure that there is no overlap.

---

## Known Issues Classification & Recommendations

The following table classifies all known issues by severity, category, and effort required to fix them. Issues are sorted by priority for addressing.

| # | Issue | Severity | Category | Effort | Recommendation |
|---|-------|----------|----------|--------|----------------|
| 1 | **UI Overlay Issue** | **High** | UI/UX | Quick Win (hours) | **Fixed** - Added a spacer Toolbar in `App.tsx` to handle the fixed AppBar height dynamically. |
| 2 | **Dependency Vulnerabilities** | **High** | Security | Quick Win (hours) | **Fixed** - Resolved all vulnerabilities (including `minimatch` ReDoS) by updating `vite`, `eslint`, and using `npm overrides`. |
| 3 | **No Route Persistence** | **Low** | Frontend | Quick Win (hours) | **Fixed** - Implemented `localStorage` persistence using `zustand/middleware`. |
| 4 | **Limited Mobile Responsiveness** | **Medium** | Frontend/UI | Short-term (days) | **Fixed** - Improved drawer behavior, responsive widths, and stackable controls. |
| 5 | **Skyfield Deprecation** | **Medium** | Backend | Short-term (days) | **Fixed** - Updated `skyfield` to `1.54` and removed `numpy<2.0` pin. |
| 6 | No Authentication | **Medium** | Backend/Security | Medium-term (weeks) | **Address soon** - Implement basic API key or JWT authentication if the API is to be exposed. |
| 7 | **Limited Error Handling** | **Low** | Backend | Short-term (days) | **Improved** - Added global exception handlers, Axios interceptors, and better user feedback. |
| 8 | No Persistent Storage | **Low** | Backend | Long-term (months) | **Nice to have** - Implement only if user accounts or route history features are prioritized. |
| 9 | No Offline Support | **Low** | Frontend | Long-term (months) | **Nice to have** - Would require service workers and map tile caching. |

### Priority Summary

**Quick Wins (Do First):**
- All quick wins completed.

**Short-term (Next Sprint):**
- All short-term tasks completed.

**Medium-term (Next Quarter):**
- Authentication - Implement basic auth for API protection.

**Long-term / Nice to Have:**
- Persistent Storage - Only if needed for user features.
- Offline Support - Major effort, evaluate need.

---

## Planned Enhancements

### High Priority
- [ ] **Route Simulation/Animation** - Visualize travel along the route with animated marker
- [ ] **Current Position Tracking** - Show user's current position relative to route
- [ ] **Progress Indicators** - Show distance traveled, distance remaining, ETA
- [ ] **Export Formats** - Support GPX, KML in addition to GeoJSON
- [ ] **Route History** - Save and load previous routes

### Medium Priority
- [ ] **Weather Integration** - Show weather conditions along route
- [ ] **Alternative Routes** - Calculate multiple route options
- [ ] **Route Optimization** - Optimize for shortest distance vs fewest waypoints
- [ ] **Print View** - Printable route summary with maps
- [ ] **Mobile App** - React Native or PWA version

### Low Priority / Nice to Have
- [ ] **3D Visualization** - Three.js globe view
- [ ] **Historical Routes** - Famous historical celestial navigation routes
- [ ] **Educational Mode** - Explain the celestial navigation concepts
- [ ] **Multi-language Support** - i18n for different languages
- [ ] **User Accounts** - Save personal routes and preferences
- [ ] **Social Features** - Share routes with others

---

## Architecture Ideas

### Potential Improvements
- [ ] **Microservices** - Split backend into navigation, celestial data, and user services
- [ ] **Caching Layer** - Redis for caching celestial calculations
- [ ] **WebSockets** - Real-time updates for route simulation
- [ ] **GraphQL** - Alternative to REST API
- [ ] **Containerization** - Docker setup for easy deployment

---

## Documentation Needs
- [ ] **API Documentation** - OpenAPI/Swagger specs
- [ ] **User Guide** - How to use the application
- [ ] **Developer Guide** - Setup and contribution guidelines
- [ ] **Algorithm Explanation** - Document the celestial navigation algorithm

---

## Testing & Quality
- [ ] **Unit Tests** - Backend test coverage
- [ ] **Integration Tests** - API endpoint tests
- [ ] **E2E Tests** - Frontend testing with Playwright/Cypress
- [ ] **Performance Testing** - Load testing for concurrent users
- [ ] **Code Quality** - Linting, formatting, type checking enforcement

---

## Last Updated
2026-02-24

## Notes
- Navigation core functionality is working
- Map visualization with colored legs is implemented
- Dynamic cutoff calculation is active
- Ready for next feature development
