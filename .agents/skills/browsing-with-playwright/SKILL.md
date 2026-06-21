---
name: browsing-with-playwright
description: |
  Browser automation using Playwright MCP server. Navigate websites, fill forms, click elements,
  take screenshots, and extract data. This skill should be used for web browsing, form submission,
  web scraping, UI testing, or any task requiring browser interaction. NOT for static content
  (use curl/wget).
---

# Browser Automation

Automate browser interactions via Playwright MCP server.

## Before Implementation

Gather context to ensure successful automation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing test frameworks, browser automation setup, project dependencies |
| **Conversation** | Target URLs, expected interactions, data to extract, credentials if needed |
| **Skill References** | Playwright MCP tool documentation from `references/playwright-tools.md` |
| **User Guidelines** | Site-specific requirements, rate limits, authentication methods |

Ensure all required context is gathered before starting automation. Only ask user for THEIR specific targets and requirements.

## Required Clarifications

1. **Target URL(s)** — What website(s) need to be automated?
2. **Primary Action** — What should the browser do? (navigate, fill form, extract data, test UI, screenshot)
3. **Authentication Required** — Does the target require login? If so, what method? (form-based, OAuth, API key)

## Optional Clarifications

4. **Data to Extract** — What specific data should be collected? (only if data extraction is the goal)
5. **Output Format** — How should results be returned? (JSON, screenshot, console output, file)
6. **Page Interaction Complexity** — Is this a simple single-page action or multi-step workflow?
7. **Rate Limits / Politeness** — Any rate limits or throttling requirements to respect?

Note: Avoid asking too many questions in a single message. Start with Required, follow up with Optional as needed.

## Server Lifecycle

### Start Server
```bash
# Using helper script (recommended)
bash scripts/start-server.sh

# Or manually
npx @playwright/mcp@latest --port 8808 --shared-browser-context &
```

### Stop Server
```bash
# Using helper script (closes browser first)
bash scripts/stop-server.sh

# Or manually
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_close -p '{}'
pkill -f "@playwright/mcp"
```

### When to Stop
- **End of task**: Stop when browser work is complete
- **Long sessions**: Keep running if doing multiple browser tasks
- **Errors**: Stop and restart if browser becomes unresponsive

**Important:** The `--shared-browser-context` flag is required to maintain browser state across multiple mcp-client.py calls. Without it, each call gets a fresh browser context.

## Quick Reference

### Navigation

```bash
# Go to URL
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Go back
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_navigate_back -p '{}'
```

### Get Page State

```bash
# Accessibility snapshot (returns element refs for clicking/typing)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# Screenshot
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_take_screenshot \
  -p '{"type": "png", "fullPage": true}'
```

### Interact with Elements

Use `ref` from snapshot output to target elements:

```bash
# Click element
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'

# Type text
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_type \
  -p '{"element": "Search input", "ref": "e15", "text": "hello world", "submit": true}'

# Fill form (multiple fields)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_fill_form \
  -p '{"fields": [{"ref": "e10", "value": "john@example.com"}, {"ref": "e12", "value": "password123"}]}'

# Select dropdown
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_select_option \
  -p '{"element": "Country dropdown", "ref": "e20", "values": ["US"]}'
```

### Wait for Conditions

```bash
# Wait for text to appear
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_wait_for \
  -p '{"text": "Success"}'

# Wait for time (ms)
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_wait_for \
  -p '{"time": 2000}'
```

### Execute JavaScript

```bash
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_evaluate \
  -p '{"function": "return document.title"}'
```

### Multi-Step Playwright Code

For complex workflows, use `browser_run_code` to run multiple actions in one call:

```bash
python3 scripts/mcp-client.py call -u http://localhost:8808 -t browser_run_code \
  -p '{"code": "async (page) => { await page.goto(\"https://example.com\"); await page.click(\"text=Learn more\"); return await page.title(); }"}'
```

**Tip:** Use `browser_run_code` for complex multi-step operations that should be atomic (all-or-nothing).

## Workflow: Form Submission

1. Navigate to page
2. Get snapshot to find element refs
3. Fill form fields using refs
4. Click submit
5. Wait for confirmation
6. Screenshot result

## Workflow: Data Extraction

1. Navigate to page
2. Get snapshot (contains text content)
3. Use browser_evaluate for complex extraction
4. Process results

## Verification

Run: `python3 scripts/verify.py`

Expected: `✓ Playwright MCP server running`

## If Verification Fails

1. Run diagnostic: `pgrep -f "@playwright/mcp"`
2. Check: Server process running on port 8808
3. Try: `bash scripts/start-server.sh`
4. **Stop and report** if still failing - do not proceed with downstream steps

## Tool Reference

See [references/playwright-tools.md](references/playwright-tools.md) for complete tool documentation.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Element not found | Run browser_snapshot first to get current refs |
| Click fails | Try browser_hover first, then click |
| Form not submitting | Use `"submit": true` with browser_type |
| Page not loading | Increase wait time or use browser_wait_for |
| Server not responding | Stop and restart: `bash scripts/stop-server.sh && bash scripts/start-server.sh` |

## Anti-Patterns

- ❌ **Hardcoding element selectors** — Element refs change on page reload; always capture fresh snapshot
- ❌ **Mixed context usage** — Don't use `browser_navigate` results in a new server session; use `--shared-browser-context`
- ❌ **No error handling** — Always verify actions succeeded (wait for confirmation, check page state)
- ❌ **Blind typing without verification** — Always snapshot after form fill to verify field values
- ❌ **Excessive page loads** — Reuse page state where possible; don't navigate unnecessarily

## Output Specification

Deliver browser automation results as:

1. **Automation Script** — Sequence of Playwright MCP calls with proper error handling
2. **Results** — Extracted data, screenshots, or verification output as requested
3. **Summary** — Brief description of what was accomplished
4. **Cleanup** — Instructions to stop the server if it was started
