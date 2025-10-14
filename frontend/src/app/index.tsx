import { ChakraProvider, ColorModeScript } from '@chakra-ui/react';
import { Provider } from 'react-redux';
import { theme } from '../shared/config/theme';
import { store } from '../shared/config/store';
import { AppRouter } from './router';
import { AppProviders } from './providers';

export const App = () => (
  <Provider store={store}>
    <ChakraProvider theme={theme}>
      <ColorModeScript initialColorMode={theme.config.initialColorMode} />
      <AppProviders>
        <AppRouter />
      </AppProviders>
    </ChakraProvider>
  </Provider>
);
