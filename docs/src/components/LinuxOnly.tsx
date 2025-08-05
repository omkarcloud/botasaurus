import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';

const isLinux = () => navigator.userAgent.indexOf("Linux")!=-1
interface Props {
  children: React.ReactNode;
}

export default function LinuxOnly({ children }: Props) {
  return (
    <BrowserOnly>
      {() => (isLinux() ? <>{children}</> : null)}
    </BrowserOnly>
  );
}