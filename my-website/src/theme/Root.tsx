import React from 'react';
import FloatingChat from '../components/FloatingChat';

// Root component that wraps the entire app
const Root: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      {children}
      <FloatingChat />
    </>
  );
};

export default Root;