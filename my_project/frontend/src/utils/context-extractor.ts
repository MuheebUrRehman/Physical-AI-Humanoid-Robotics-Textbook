/**
 * Utility to extract relevant educational context from the current Docusaurus page.
 */
export interface PageContext {
  url: string;
  title: string;
  headings: string[];
}

export const getPageContext = (): PageContext => {
  if (typeof window === 'undefined') {
    return { url: '', title: '', headings: [] };
  }

  // Extract main headings (H1 and H2) to help the AI ground itself
  const headingElements = Array.from(document.querySelectorAll('h1, h2'));
  const headings = headingElements
    .map(h => h.textContent?.trim() || '')
    .filter(Boolean)
    .slice(0, 5); // Limit to top 5 headings for context efficiency

  const siteSeparator = ' | ';
  const titleParts = document.title.split(siteSeparator);
  const pageTitle = titleParts.length > 1 ? titleParts.slice(0, -1).join(siteSeparator).trim() : document.title;

  return {
    url: window.location.href,
    title: pageTitle,
    headings,
  };
};
