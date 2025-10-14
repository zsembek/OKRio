# OKRio Frontend

Enterprise-grade OKR management interface built with React 18, TypeScript and Vite. The project follows the Feature-Sliced Design methodology and includes localisation, drag-and-drop alignment tooling, analytics dashboards and Progressive Web App capabilities.

## Getting started

```bash
cd frontend
npm install
npm run dev
```

Key scripts:

- `npm run dev` — start the Vite development server with hot module replacement.
- `npm run build` — generate a production build.
- `npm run preview` — preview the production build locally.

## Architecture

The codebase is organised according to Feature-Sliced Design layers:

```
src/
├── app/            # Application shell, router and providers
├── entities/       # Domain entities (OKR tree, etc.)
├── features/       # User-facing features (alignment board, language switcher)
├── pages/          # Composed pages (dashboard, workspace, analytics)
├── processes/      # Cross-page processes (check-ins, workflows)
├── shared/         # Reusable configuration, UI primitives and helpers
└── widgets/        # Composite widgets (analytics dashboards)
```

### Internationalisation

Localisation is powered by `react-i18next` with automatic language detection (English/Russian). Strings live in `src/shared/config/i18n.ts` and can be extended per namespace.

### Drag-and-drop alignment

The alignment board leverages `@dnd-kit/core` to support rearranging objectives inside the OKR tree. Drops are persisted in Redux Toolkit state so the UI reflects hierarchy changes instantly.

### Analytics dashboards

Reusable dashboard widgets are provided in `src/widgets/analytics-dashboard` using Recharts. They visualise execution velocity, completion rates and engagement scores with Chakra UI theming.

### PWA support

`vite-plugin-pwa` delivers offline caching, manifest generation and automatic service worker updates. The entrypoint registers the service worker via `virtual:pwa-register`. To keep the repository text-only, the manifest ships an SVG icon (`public/favicon.svg`); replace it with PNG assets if your deployment requires bitmap icons.

## Tech stack

- React 18 + TypeScript + Vite
- Chakra UI design system
- Redux Toolkit for state management
- React Router v6
- `react-i18next` for localisation
- `@dnd-kit` for drag-and-drop interactions
- Recharts for analytical visualisations
- `vite-plugin-pwa` for Progressive Web App capabilities
