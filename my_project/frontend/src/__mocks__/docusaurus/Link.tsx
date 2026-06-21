import React from 'react';
const Link: React.FC<{ to?: string; href?: string; children?: React.ReactNode; className?: string }> = ({ to, href, children, className }) => (
  <a href={to || href || '#'} className={className}>{children}</a>
);
export default Link;
