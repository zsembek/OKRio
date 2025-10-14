import { Grid, GridItem, Heading, Stack, Text, Card, CardBody } from '@chakra-ui/react';
import { AlignmentBoard } from '../../features/alignment-board';
import { AnalyticsDashboard } from '../../widgets/analytics-dashboard';
import { useTranslation } from 'react-i18next';

const healthSignals = [
  {
    id: 'checkins',
    label: 'Weekly check-ins',
    delta: '+12%',
    description: 'Teams reporting on time'
  },
  {
    id: 'pulse',
    label: 'Engagement pulse',
    delta: '+6',
    description: 'Score vs. last quarter'
  }
];

const DashboardPage = () => {
  const { t } = useTranslation();

  return (
    <Grid templateColumns={{ base: '1fr', xl: '2fr 1fr' }} gap={8}>
      <GridItem>
        <Stack spacing={6}>
          <Stack spacing={3}>
            <Heading size="md">{t('dashboard.alignmentTitle')}</Heading>
            <AlignmentBoard />
          </Stack>
          <Stack spacing={3}>
            <Heading size="md">{t('dashboard.analyticsTitle')}</Heading>
            <AnalyticsDashboard />
          </Stack>
        </Stack>
      </GridItem>
      <GridItem>
        <Stack spacing={4}>
          <Heading size="md">{t('dashboard.healthTitle')}</Heading>
          {healthSignals.map((signal) => (
            <Card key={signal.id} variant="elevated">
              <CardBody>
                <Stack spacing={1}>
                  <Heading size="sm">{signal.label}</Heading>
                  <Text color="teal.500" fontWeight="bold">
                    {signal.delta}
                  </Text>
                  <Text fontSize="sm" color="gray.500">
                    {signal.description}
                  </Text>
                </Stack>
              </CardBody>
            </Card>
          ))}
        </Stack>
      </GridItem>
    </Grid>
  );
};

export default DashboardPage;
