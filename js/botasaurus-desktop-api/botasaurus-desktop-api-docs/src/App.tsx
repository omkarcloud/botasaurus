import React from 'react';
import { EuiProvider } from '@elastic/eui/optimize/es/components/provider/provider';
import ApiIntegration from './app/pages/api-integration'

const App = () => (
  <EuiProvider colorMode="light">
    <ApiIntegration/>
  </EuiProvider>
);

export default App;
