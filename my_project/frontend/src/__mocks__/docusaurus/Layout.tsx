import React from 'react';
const Layout: React.FC<{ children?: React.ReactNode; title?: string; description?: string }> = ({ children }) => <div data-testid="layout">{children}</div>;
export default Layout;
