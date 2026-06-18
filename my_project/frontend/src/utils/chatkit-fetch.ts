import { getPageContext } from './context-extractor';

/**
 * Custom fetch interceptor for ChatKit to inject authentication and page metadata.
 * Handles the actual request types sent by the ChatKit SDK:
 *   - threads.create      (first message in a conversation)
 *   - threads.addUserMessage (subsequent messages)
 *   - threads.run         (legacy — kept for compatibility)
 */
export const createChatKitFetch = (studentId: string) => {
  return async (url: string, options: RequestInit) => {
    const pageContext = getPageContext();

    const headers = new Headers(options.headers);
    headers.set('X-User-ID', studentId);
    headers.set('Content-Type', 'application/json');

    let modifiedOptions = { ...options, headers };

    if (modifiedOptions.body && typeof modifiedOptions.body === 'string') {
      try {
        const parsed = JSON.parse(modifiedOptions.body);
        const msgType = parsed.type;

        if (
          msgType === 'threads.create' ||
          msgType === 'threads.addUserMessage' ||
          msgType === 'threads.run'
        ) {
          if (!parsed.params) parsed.params = {};
          if (!parsed.params.input) parsed.params.input = {};
          if (!parsed.params.input.metadata) parsed.params.input.metadata = {};

          parsed.params.input.metadata = {
            ...parsed.params.input.metadata,
            pageContext: pageContext,
          };
          modifiedOptions.body = JSON.stringify(parsed);
        }
      } catch (e) {
        console.error('Failed to inject metadata into ChatKit request', e);
      }
    }

    return fetch(url, modifiedOptions);
  };
};
