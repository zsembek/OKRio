import { ReactNode, Suspense } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { I18nextProvider } from 'react-i18next';
import { i18n } from '../../shared/config/i18n';

interface AppProvidersProps {
  children: ReactNode;
}

export const AppProviders = ({ children }: AppProvidersProps) => (
  <BrowserRouter>
    <I18nextProvider i18n={i18n}>
      <Suspense fallback={null}>{children}</Suspense>
    </I18nextProvider>
  </BrowserRouter>
);
