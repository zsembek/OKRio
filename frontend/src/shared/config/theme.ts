import { extendTheme, ThemeConfig } from '@chakra-ui/react';

const config: ThemeConfig = {
  initialColorMode: 'light',
  useSystemColorMode: false
};

export const theme = extendTheme({
  config,
  fonts: {
    heading: 'Inter, system-ui, sans-serif',
    body: 'Inter, system-ui, sans-serif'
  },
  colors: {
    brand: {
      50: '#E6F4FF',
      100: '#B8DEFF',
      200: '#8AC8FF',
      300: '#5BB2FF',
      400: '#2D9CFF',
      500: '#147FE6',
      600: '#0F62B4',
      700: '#094581',
      800: '#04294F',
      900: '#010E1F'
    }
  }
});
