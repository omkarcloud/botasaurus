import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

const isMac = () => navigator.platform.toUpperCase().indexOf("MAC") >=0;
  
export default function ShortCut() {
  return (
    <BrowserOnly>
      {() => (isMac() ? <>Cmd</> : <>Ctrl</>)}
    </BrowserOnly>
  );
}