import React from 'react';
import ChatKitWidget from '../components/ChatKitWidget';

// Root component that wraps the entire app
const Root: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <>
      {children}
      <ChatKitWidget />
    </>
  );
};

export default Root;