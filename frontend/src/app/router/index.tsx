import { lazy } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigate, useRoutes } from 'react-router-dom';
import { MainLayout } from '../../shared/ui/MainLayout';

const DashboardPage = lazy(() => import('../../pages/dashboard'));
const WorkspacePage = lazy(() => import('../../pages/workspace'));
const AnalyticsPage = lazy(() => import('../../widgets/analytics-dashboard/pages/analytics-dashboard-page'));

export const AppRouter = () => {
  const { t } = useTranslation();

  return useRoutes([
    {
      path: '/',
      element: (
        <MainLayout title={t('navigation.dashboard')}>
          <DashboardPage />
        </MainLayout>
      )
    },
    {
      path: '/workspace',
      element: (
        <MainLayout title={t('navigation.workspace')}>
          <WorkspacePage />
        </MainLayout>
      )
    },
    {
      path: '/analytics',
      element: (
        <MainLayout title={t('navigation.analytics')}>
          <AnalyticsPage />
        </MainLayout>
      )
    },
    { path: '*', element: <Navigate to="/" replace /> }
  ]);
};
