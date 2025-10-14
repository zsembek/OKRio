# OKRio Frontend

This directory documents the plan for the React + TypeScript single-page application that powers the OKRio user experience.

## Technology stack

- React 18 with TypeScript and Vite as the build tool.
- Feature-Sliced Design (layers: `app`, `processes`, `pages`, `features`, `entities`, `shared`).
- Redux Toolkit with RTK Query for state management and data fetching.
- Chakra UI component library with custom theming (light/dark/brand palettes) and accessibility compliance (WCAG 2.1 AA).
- React Router for navigation, React-i18next for localisation (RU/EN baseline).
- Testing stack: Jest + React Testing Library for unit/component, Cypress for E2E, Storybook for UI documentation.
- PWA capabilities: service worker, offline cache, push notifications.

## Project structure

```
frontend/
├── README.md
├── package.json        # Defined in subsequent iterations when implementation begins
├── tsconfig.json       # Ditto
└── src/
    └── app/
        ├── providers/  # App-level contexts (store, theme, i18n)
        └── router/     # Route definitions and guards
```

Initial implementation will add reusable UI primitives (`shared`), entity slices (OKR, Objective, KeyResult, Workspace), feature-level widgets (alignment tree, check-in flow), and page compositions (dashboard, workspace OKR, settings, analytics).

## Key UX capabilities

- Alignment explorer with heatmap, drag-and-drop realignment, inline editing, and template selection.
- Workflow modals for OKR drafting, expert review, manager approval, and closure, backed by real-time collaboration via WebSocket updates.
- Check-in cadence management with reminders, 1:1 agenda builder, pulse surveys, and engagement scoring visualisations.
- Analytics dashboards with configurable widgets, drill-down, forecast visualisations, and exports.
- Notification centre with delivery preferences and quiet hours configuration.

## Next steps

1. Bootstrap Vite + React + TypeScript project with Chakra UI and Redux Toolkit.
2. Implement authentication flow against Azure AD (MSAL.js) and bootstrap user session management.
3. Establish RTK Query base API client (REST + WebSocket streaming) with optimistic updates and caching policies.
4. Build core pages (Home dashboard, Workspace OKR, Alignment map, Settings) and reusable components (data tables, tree explorer, forms).
5. Integrate localisation, accessibility testing, and performance budgets (bundle splitting, Suspense, list virtualisation).
