# OKRio Frontend

Enterprise-grade OKR management interface built with React 18, TypeScript and Vite. The implementation follows the Feature-Sliced Design methodology and already includes localisation, drag-and-drop alignment tooling, analytics dashboards and Progressive Web App capabilities present in the codebase.

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

## Architecture & features

The codebase is organised according to Feature-Sliced Design layers:

```
src/
├── app/            # Application shell, router and providers (Chakra UI, Redux, React Router)
├── entities/       # Domain entities (OKR tree data structures, analytics stubs)
├── features/       # User-facing features (alignment board, language switcher, theme toggle)
├── pages/          # Composed pages (dashboard, workspace, analytics)
├── processes/      # Cross-page processes (check-ins, workflows)
├── shared/         # Reusable configuration, API clients, i18n and store setup
└── widgets/        # Composite widgets (analytics dashboards)
```

### Internationalisation

Localisation is powered by `react-i18next` with automatic language detection (English/Russian). Strings live in `src/shared/config/i18n.ts` and can be extended per namespace. The provider is wired in `src/app/providers/I18nProvider.tsx` and initialised from `src/main.tsx`.

### Drag-and-drop alignment

The alignment board (`src/features/alignment-board/ui/AlignmentBoard.tsx`) leverages `@dnd-kit` to support rearranging objectives inside the OKR tree. Drops are persisted in Redux Toolkit state so the UI reflects hierarchy changes instantly.

### Analytics dashboards

Reusable dashboard widgets live in `src/widgets/analytics-dashboard` and use Recharts to visualise execution velocity, completion rates and engagement scores with Chakra UI theming.

### PWA support

`vite-plugin-pwa` delivers offline caching, manifest generation and automatic service worker updates. The entrypoint registers the service worker via `virtual:pwa-register` in `src/main.tsx`. To keep the repository text-only, the manifest ships an SVG icon (`public/favicon.svg`); replace it with PNG assets if your deployment requires bitmap icons.

### State management & theming

Global state is handled by Redux Toolkit (see `src/shared/config/store.ts`) with slices for alignment data and settings. Chakra UI supplies theming (light/dark) and layout primitives configured in `src/shared/config/theme.ts`.

## Tech stack

- React 18 + TypeScript + Vite
- Chakra UI design system
- Redux Toolkit for state management
- React Router v6
- `react-i18next` for localisation
- `@dnd-kit` for drag-and-drop interactions
- Recharts for analytical visualisations
- `vite-plugin-pwa` for Progressive Web App capabilities
