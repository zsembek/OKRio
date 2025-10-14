import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './app';
import './shared/config/i18n';
import { registerSW } from 'virtual:pwa-register';

registerSW({ immediate: true });

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
