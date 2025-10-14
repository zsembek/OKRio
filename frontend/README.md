# OKRio Frontend

React + TypeScript single-page application for the OKRio enterprise OKR platform. The project is scaffolded with Vite and implements the first slices of the workspace dashboard experience.

## Tech stack

- React 18 + TypeScript
- Vite build tool and dev server
- Redux Toolkit for state management
- Chakra UI for accessible UI components
- React-i18next for localisation (RU/EN)

## Available scripts

```bash
# install dependencies
npm install

# run development server on http://localhost:5173
npm run dev

# create production build in dist/
npm run build

# preview the production build
npm run preview
```

## Project structure

```
frontend/
├── index.html
├── package.json
├── public/
│   └── okrio.svg
├── src/
│   ├── App.tsx
│   ├── app/
│   │   ├── hooks.ts
│   │   └── store.ts
│   ├── components/
│   │   └── ObjectiveCard.tsx
│   ├── features/
│   │   └── dashboard/
│   │       ├── dashboardSlice.ts
│   │       └── selectors.ts
│   ├── locales/
│   │   ├── en/common.json
│   │   └── ru/common.json
│   ├── main.tsx
│   ├── shared/
│   │   └── i18n.ts
│   ├── styles.css
│   └── vite-env.d.ts
├── tsconfig.json
├── tsconfig.node.json
└── vite.config.ts
```

## Next steps

- Add routing and authenticated layouts.
- Wire Redux slices to RTK Query once backend endpoints are available.
- Expand dashboard widgets (alignment heatmap, confidence trends, hygiene score).
- Integrate Chakra theme overrides with brand palette and dark mode switcher.
- Set up automated testing (Jest, React Testing Library, Cypress) and Storybook docs.
