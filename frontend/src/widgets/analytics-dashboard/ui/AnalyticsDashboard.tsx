import { Card, CardBody, Grid, GridItem, Heading, Stack, Text } from '@chakra-ui/react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  BarChart,
  Bar
} from 'recharts';
import { useTranslation } from 'react-i18next';

const velocityData = [
  { name: 'Q1', velocity: 62 },
  { name: 'Q2', velocity: 68 },
  { name: 'Q3', velocity: 74 },
  { name: 'Q4', velocity: 81 }
];

const completionData = [
  { name: 'Product', value: 72 },
  { name: 'Sales', value: 63 },
  { name: 'People', value: 58 },
  { name: 'Operations', value: 80 }
];

const engagementData = [
  { name: 'Jan', score: 54 },
  { name: 'Feb', score: 59 },
  { name: 'Mar', score: 61 },
  { name: 'Apr', score: 65 },
  { name: 'May', score: 69 }
];

export const AnalyticsDashboard = () => {
  const { t } = useTranslation();

  return (
    <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={6}>
      <GridItem colSpan={1}>
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>
              {t('analytics.velocity')}
            </Heading>
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={velocityData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="velocity" stroke="#319795" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </GridItem>
      <GridItem colSpan={1}>
        <Card>
          <CardBody>
            <Heading size="md" mb={4}>
              {t('analytics.completion')}
            </Heading>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={completionData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#2B6CB0" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </GridItem>
      <GridItem colSpan={{ base: 1, md: 2 }}>
        <Card>
          <CardBody>
            <Stack direction={{ base: 'column', md: 'row' }} justify="space-between" align="center" mb={4}>
              <Heading size="md">{t('analytics.engagement')}</Heading>
              <Text color="gray.500">+6 pts vs. last quarter</Text>
            </Stack>
            <ResponsiveContainer width="100%" height={240}>
              <AreaChart data={engagementData}>
                <defs>
                  <linearGradient id="colorEngagement" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#68D391" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#68D391" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Area type="monotone" dataKey="score" stroke="#38A169" fillOpacity={1} fill="url(#colorEngagement)" />
              </AreaChart>
            </ResponsiveContainer>
          </CardBody>
        </Card>
      </GridItem>
    </Grid>
  );
};
