import { ReactNode } from 'react';
import {
  Box,
  Container,
  Flex,
  Heading,
  IconButton,
  Stack,
  useColorMode,
  Button
} from '@chakra-ui/react';
import { MoonIcon, SunIcon } from '@chakra-ui/icons';
import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { LanguageSwitcher } from '../../features/language-switcher';

interface MainLayoutProps {
  title: string;
  children: ReactNode;
}

const NAVIGATION_LINKS: Array<{ to: string; translationKey: string }> = [
  { to: '/', translationKey: 'navigation.dashboard' },
  { to: '/workspace', translationKey: 'navigation.workspace' },
  { to: '/analytics', translationKey: 'navigation.analytics' }
];

export const MainLayout = ({ title, children }: MainLayoutProps) => {
  const { colorMode, toggleColorMode } = useColorMode();
  const { t } = useTranslation();
  const location = useLocation();

  return (
    <Box minH="100vh" bgGradient="linear(to-br, gray.50, teal.50)" _dark={{ bg: 'gray.900' }}>
      <Box as="header" borderBottomWidth="1px" bg="white" _dark={{ bg: 'gray.800' }}>
        <Container maxW="7xl" py={4}>
          <Flex align="center" justify="space-between">
            <Stack direction="row" spacing={4} align="center">
              <Heading size="md">OKRio</Heading>
              <Stack direction="row" spacing={2}>
                {NAVIGATION_LINKS.map((link) => (
                  <Button
                    key={link.to}
                    as={Link}
                    to={link.to}
                    variant={location.pathname === link.to ? 'solid' : 'ghost'}
                    colorScheme="teal"
                    size="sm"
                  >
                    {t(link.translationKey)}
                  </Button>
                ))}
              </Stack>
            </Stack>
            <Stack direction="row" spacing={2} align="center">
              <LanguageSwitcher />
              <IconButton
                aria-label={t('actions.toggleTheme')}
                onClick={toggleColorMode}
                icon={colorMode === 'light' ? <MoonIcon /> : <SunIcon />}
                variant="ghost"
              />
            </Stack>
          </Flex>
        </Container>
      </Box>
      <Container as="main" maxW="7xl" py={10}>
        <Heading size="lg" mb={6}>
          {title}
        </Heading>
        {children}
      </Container>
    </Box>
  );
};
