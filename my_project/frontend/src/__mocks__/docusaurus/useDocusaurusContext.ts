const mockContext = {
  siteConfig: {
    title: 'Physical AI & Humanoid Robotics',
    tagline: 'A Comprehensive Guide to Embodied Intelligence',
    customFields: {
      apiBaseUrl: 'http://localhost:8000',
      chatkitDomainKey: 'physical-ai-textbook-local',
    },
  },
};

const useDocusaurusContext = () => mockContext;
export default useDocusaurusContext;
