# OpenCode Epic Header Display Implementation Plan

**Epic Issue:** #21

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable OpenCode TUI header bar to display the current epic issue link when working in a project directory with a plan file.

**Architecture:** Create a context detection mechanism that reads plan files in the current working directory, extracts epic issue references, and exposes them via a plugin API that OpenCode's TUI can consume for header bar display.

**Tech Stack:** Node.js, OpenCode Plugin API, File System, Git

---

## Problem Analysis

**Investigation Results:**
- Commit 89779e3 in powerlevel repo mentions `lib/epic-detector.js` and `lib/session-title-updater.js`
- These files were documented in the commit message but **never actually added to the repository**
- The epic header display feature was planned but never implemented
- Current powerlevel plugin only handles epic syncing to GitHub, not context display

**Current State:**
- Plan files have `**Epic Issue:** #17` references (line 3 in people-presenter-agent plan)
- Powerlevel plugin exists but only syncs epics to GitHub  
- OpenCode TUI header bar has no mechanism to detect/display current epic context
- The implementation in commit 89779e3 exists in git history but was never applied

**Expected Behavior:**
- When working in `/var/home/jorge/src/casestudypilot`
- TUI header should show: "Epic #17: Add a skill for reports about individual presenters"
- Link should be clickable to open GitHub issue

**Root Cause:**
- No context provider for OpenCode to consume
- Powerlevel plugin doesn't expose current epic information
- No detection of "active" plan based on working directory

## Implementation Tasks

### Phase 1: Context Detection (Epic Discovery)

#### Task 1.1: Create Epic Context Detector Module

**Files:**
- Create: `~/.config/opencode/powerlevel/lib/context-detector.js`
- Test: `~/.config/opencode/powerlevel/test/context-detector.test.js`

**Step 1: Write the failing test**

```javascript
// test/context-detector.test.js
import { describe, it, expect } from 'vitest';
import { detectEpicContext } from '../lib/context-detector.js';
import { join } from 'path';

describe('detectEpicContext', () => {
  it('should extract epic number from plan file', () => {
    const testDir = join(__dirname, 'fixtures', 'project-with-epic');
    const context = detectEpicContext(testDir);
    
    expect(context).toEqual({
      epicNumber: 17,
      epicTitle: 'Add a skill for reports about individual presenters',
      planFile: 'docs/plans/2026-02-09-people-presenter-agent.md',
      repo: 'castrojo/casestudypilot'
    });
  });
  
  it('should return null when no plan files exist', () => {
    const testDir = join(__dirname, 'fixtures', 'empty-project');
    const context = detectEpicContext(testDir);
    
    expect(context).toBeNull();
  });
  
  it('should return null when plan has no epic reference', () => {
    const testDir = join(__dirname, 'fixtures', 'project-no-epic');
    const context = detectEpicContext(testDir);
    
    expect(context).toBeNull();
  });
});
```

**Step 2: Create test fixtures**

```bash
mkdir -p test/fixtures/project-with-epic/docs/plans
mkdir -p test/fixtures/empty-project
mkdir -p test/fixtures/project-no-epic/docs/plans
```

Create fixture file:
```markdown
# test/fixtures/project-with-epic/docs/plans/2026-02-09-people-presenter-agent.md
# People/Presenter Agent Implementation Plan

**Epic Issue:** #17  
**Date:** February 9, 2026
```

Create fixture without epic:
```markdown
# test/fixtures/project-no-epic/docs/plans/2026-02-09-feature.md
# Some Feature

**Date:** February 9, 2026
```

**Step 3: Run test to verify it fails**

```bash
cd ~/.config/opencode/powerlevel
npm test test/context-detector.test.js
```

Expected: FAIL with "detectEpicContext is not defined"

**Step 4: Implement context detector**

```javascript
// lib/context-detector.js
import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';
import { detectRepo } from './repo-detector.js';

/**
 * Detects epic context from plan files in the current directory
 * @param {string} cwd - Current working directory
 * @returns {Object|null} Epic context or null if not found
 */
export function detectEpicContext(cwd) {
  try {
    // Check for plans directory
    const plansDir = join(cwd, 'docs', 'plans');
    if (!existsSync(plansDir)) {
      return null;
    }
    
    // Get all plan files (most recent first)
    const planFiles = readdirSync(plansDir)
      .filter(f => f.endsWith('.md'))
      .sort()
      .reverse();
    
    if (planFiles.length === 0) {
      return null;
    }
    
    // Read most recent plan file
    const planFile = join(plansDir, planFiles[0]);
    const content = readFileSync(planFile, 'utf-8');
    
    // Extract epic reference (format: **Epic Issue:** #17)
    const epicMatch = content.match(/\*\*Epic Issue:\*\*\s+#(\d+)/);
    if (!epicMatch) {
      return null;
    }
    
    const epicNumber = parseInt(epicMatch[1], 10);
    
    // Extract title from first line
    const titleMatch = content.match(/^#\s+(.+)$/m);
    const planTitle = titleMatch ? titleMatch[1].replace(' Implementation Plan', '') : 'Unknown';
    
    // Detect repository
    const repoInfo = detectRepo(cwd);
    const repo = repoInfo ? `${repoInfo.owner}/${repoInfo.repo}` : null;
    
    return {
      epicNumber,
      epicTitle: planTitle,
      planFile: `docs/plans/${planFiles[0]}`,
      repo
    };
  } catch (error) {
    console.error(`Error detecting epic context: ${error.message}`);
    return null;
  }
}

/**
 * Formats epic context for display in UI
 * @param {Object} context - Epic context from detectEpicContext
 * @returns {string} Formatted string for display
 */
export function formatEpicDisplay(context) {
  if (!context) {
    return null;
  }
  
  return `Epic #${context.epicNumber}: ${context.epicTitle}`;
}

/**
 * Generates GitHub URL for epic issue
 * @param {Object} context - Epic context from detectEpicContext
 * @returns {string|null} GitHub issue URL
 */
export function getEpicUrl(context) {
  if (!context || !context.repo) {
    return null;
  }
  
  return `https://github.com/${context.repo}/issues/${context.epicNumber}`;
}
```

**Step 5: Run test to verify it passes**

```bash
npm test test/context-detector.test.js
```

Expected: PASS (all 3 tests)

**Step 6: Commit**

```bash
git add lib/context-detector.js test/context-detector.test.js test/fixtures/
git commit -m "feat: add epic context detector from plan files"
```

---

### Phase 2: Plugin API Integration

#### Task 2.1: Expose Context via Plugin API

**Files:**
- Modify: `~/.config/opencode/powerlevel/plugin.js`
- Create: `~/.config/opencode/powerlevel/lib/context-provider.js`

**Step 1: Write the test**

```javascript
// test/context-provider.test.js
import { describe, it, expect, beforeEach } from 'vitest';
import { ContextProvider } from '../lib/context-provider.js';

describe('ContextProvider', () => {
  let provider;
  
  beforeEach(() => {
    provider = new ContextProvider();
  });
  
  it('should cache context for performance', () => {
    const cwd = join(__dirname, 'fixtures', 'project-with-epic');
    
    const context1 = provider.getContext(cwd);
    const context2 = provider.getContext(cwd);
    
    expect(context1).toBe(context2); // Same object reference
  });
  
  it('should invalidate cache when plan files change', () => {
    const cwd = join(__dirname, 'fixtures', 'project-with-epic');
    
    const context1 = provider.getContext(cwd);
    provider.invalidateCache(cwd);
    const context2 = provider.getContext(cwd);
    
    expect(context1).not.toBe(context2); // Different object reference
  });
});
```

**Step 2: Run test to verify it fails**

```bash
npm test test/context-provider.test.js
```

Expected: FAIL with "ContextProvider is not defined"

**Step 3: Implement context provider**

```javascript
// lib/context-provider.js
import { detectEpicContext, formatEpicDisplay, getEpicUrl } from './context-detector.js';

/**
 * Provides cached context for OpenCode sessions
 */
export class ContextProvider {
  constructor() {
    this.cache = new Map();
  }
  
  /**
   * Gets epic context for a directory (with caching)
   * @param {string} cwd - Current working directory
   * @returns {Object|null} Epic context
   */
  getContext(cwd) {
    if (this.cache.has(cwd)) {
      return this.cache.get(cwd);
    }
    
    const context = detectEpicContext(cwd);
    this.cache.set(cwd, context);
    return context;
  }
  
  /**
   * Invalidates cache for a directory
   * @param {string} cwd - Current working directory
   */
  invalidateCache(cwd) {
    this.cache.delete(cwd);
  }
  
  /**
   * Clears all cached contexts
   */
  clearCache() {
    this.cache.clear();
  }
  
  /**
   * Gets formatted display string for header bar
   * @param {string} cwd - Current working directory
   * @returns {string|null} Formatted epic display
   */
  getDisplayString(cwd) {
    const context = this.getContext(cwd);
    return formatEpicDisplay(context);
  }
  
  /**
   * Gets GitHub URL for epic
   * @param {string} cwd - Current working directory
   * @returns {string|null} GitHub issue URL
   */
  getEpicUrl(cwd) {
    const context = this.getContext(cwd);
    return getEpicUrl(context);
  }
}
```

**Step 4: Run test to verify it passes**

```bash
npm test test/context-provider.test.js
```

Expected: PASS

**Step 5: Commit**

```bash
git add lib/context-provider.js test/context-provider.test.js
git commit -m "feat: add context provider with caching"
```

---

#### Task 2.2: Integrate with Plugin

**Files:**
- Modify: `~/.config/opencode/powerlevel/plugin.js`

**Step 1: Update plugin to expose context API**

```javascript
// plugin.js (add after imports)
import { ContextProvider } from './lib/context-provider.js';

// ... existing code ...

/**
 * Plugin initialization
 */
export async function PowerlevelPlugin({ session }) {
  console.log('Initializing Powerlevel plugin...');
  
  // ... existing verification code ...
  
  // Initialize context provider
  const contextProvider = new ContextProvider();
  
  // Expose context API to OpenCode
  if (session && session.context) {
    session.context.getEpic = () => {
      const cwd = session.cwd || process.cwd();
      return {
        display: contextProvider.getDisplayString(cwd),
        url: contextProvider.getEpicUrl(cwd),
        raw: contextProvider.getContext(cwd)
      };
    };
    
    console.log('✓ Epic context API exposed to session.context.getEpic()');
  }
  
  // Hook into file system watcher to invalidate cache
  if (session && session.on) {
    session.on('file:change', (event) => {
      if (event.path && event.path.includes('docs/plans/')) {
        contextProvider.invalidateCache(session.cwd || process.cwd());
        console.log('↻ Epic context cache invalidated (plan file changed)');
      }
    });
  }
  
  // ... existing hook code ...
  
  console.log('✓ Powerlevel plugin initialized successfully');
}
```

**Step 2: Test manually**

```bash
# In casestudypilot directory
cd /var/home/jorge/src/casestudypilot

# Open OpenCode and check in JavaScript console:
# session.context.getEpic()
# Should return:
# {
#   display: "Epic #17: People/Presenter Agent",
#   url: "https://github.com/castrojo/casestudypilot/issues/17",
#   raw: { epicNumber: 17, ... }
# }
```

**Step 3: Commit**

```bash
git add plugin.js
git commit -m "feat: expose epic context API to OpenCode sessions"
```

---

### Phase 3: OpenCode TUI Integration

#### Task 3.1: Create OpenCode TUI Context Consumer

**Note:** This task requires OpenCode source code access. If OpenCode is closed-source, we need to:
1. File a feature request with OpenCode team
2. Provide documentation on how our plugin API works
3. Request they consume `session.context.getEpic()` in their TUI header bar

**Alternative: Create OpenCode Plugin to Display Context**

If OpenCode supports header bar plugins, create a display plugin:

**Files:**
- Create: `.opencode/header-epic-display.js`

**Step 1: Create header display plugin**

```javascript
// .opencode/header-epic-display.js
/**
 * OpenCode Plugin: Epic Header Display
 * Displays current epic in TUI header bar
 */
export async function EpicHeaderDisplayPlugin({ session }) {
  // Check if powerlevel context API is available
  if (!session.context || !session.context.getEpic) {
    console.warn('Epic context API not available - is Powerlevel plugin loaded?');
    return;
  }
  
  // Get epic context
  const epic = session.context.getEpic();
  
  if (!epic || !epic.display) {
    console.log('No epic context found for current directory');
    return;
  }
  
  // Register header bar item
  if (session.ui && session.ui.header) {
    session.ui.header.addItem({
      id: 'epic-context',
      position: 'right',
      priority: 10,
      render: () => ({
        text: epic.display,
        url: epic.url,
        icon: '🎯',
        tooltip: 'Current Epic - Click to open in GitHub'
      })
    });
    
    console.log(`✓ Epic header display registered: ${epic.display}`);
  } else {
    console.warn('OpenCode UI API not available - header display not supported');
    console.log(`ℹ Current Epic: ${epic.display}`);
    console.log(`ℹ URL: ${epic.url}`);
  }
}

export default EpicHeaderDisplayPlugin;
```

**Step 2: Register plugin in OpenCode config**

```json
// .opencode/config.json
{
  "plugins": [
    "~/.config/opencode/powerlevel/plugin.js",
    "./.opencode/header-epic-display.js"
  ]
}
```

**Step 3: Test manually**

Restart OpenCode and verify:
1. Header bar shows "🎯 Epic #17: People/Presenter Agent"
2. Clicking the header opens GitHub issue
3. Changes to plan files update the display

**Step 4: Commit**

```bash
git add .opencode/header-epic-display.js .opencode/config.json
git commit -m "feat: add epic header display plugin for OpenCode TUI"
```

---

### Phase 4: Documentation & Testing

#### Task 4.1: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Create: `docs/EPIC-HEADER-DISPLAY.md`

**Step 1: Create feature documentation**

```markdown
# docs/EPIC-HEADER-DISPLAY.md

# Epic Header Display

OpenCode TUI integration that displays the current epic issue link in the header bar.

## How It Works

1. **Context Detection**: Powerlevel plugin scans `docs/plans/*.md` files for epic references
2. **Caching**: Detected context is cached for performance
3. **API Exposure**: Epic context exposed via `session.context.getEpic()`
4. **UI Integration**: Header display plugin consumes API and renders in TUI

## Setup

Epic header display is automatically enabled when:
- Powerlevel plugin is loaded (`.opencode/config.json`)
- Working directory contains `docs/plans/*.md` files
- Plan files have `**Epic Issue:** #N` references

## Manual Testing

```javascript
// In OpenCode JavaScript console:
session.context.getEpic()

// Expected output:
{
  display: "Epic #17: People/Presenter Agent",
  url: "https://github.com/castrojo/casestudypilot/issues/17",
  raw: {
    epicNumber: 17,
    epicTitle: "People/Presenter Agent",
    planFile: "docs/plans/2026-02-09-people-presenter-agent.md",
    repo: "castrojo/casestudypilot"
  }
}
```

## Troubleshooting

**Header doesn't show epic:**
- Verify plan file has epic reference: `grep "Epic Issue" docs/plans/*.md`
- Check plugin loaded: OpenCode console → `session.context.getEpic()`
- Restart OpenCode to reload plugins

**Epic shows wrong issue:**
- Cache invalidation issue - check file watcher is working
- Manually invalidate: Delete `.opencode/cache/epic-context.json` (if exists)

**Header shows stale epic:**
- Plan file changed but cache not invalidated
- Check file watcher event handler in plugin.js
- Restart OpenCode session
```

**Step 2: Update README.md**

Add section after "Integration":

```markdown
## Epic Header Display

When working on a project with implementation plans, OpenCode's TUI header bar displays the current epic issue link:

```
🎯 Epic #17: People/Presenter Agent
```

Clicking the epic opens the GitHub issue in your browser.

**Requirements:**
- Powerlevel plugin loaded
- Plan files in `docs/plans/` with `**Epic Issue:** #N` references

See [Epic Header Display Documentation](docs/EPIC-HEADER-DISPLAY.md) for details.
```

**Step 3: Update AGENTS.md**

Add to "Framework Extension Examples":

```markdown
### Epic Context Detection

Agents can access the current epic context programmatically:

```javascript
const epic = session.context.getEpic();
console.log(`Working on: ${epic.display}`);
console.log(`Issue URL: ${epic.url}`);
```

This enables agents to:
- Auto-comment progress on epic issues
- Update epic status based on task completion
- Reference epic in commit messages
- Link PRs to epics automatically
```

**Step 4: Commit**

```bash
git add README.md AGENTS.md docs/EPIC-HEADER-DISPLAY.md
git commit -m "docs: add epic header display documentation"
```

---

#### Task 4.2: Integration Testing

**Files:**
- Create: `test/integration/epic-header.test.js`

**Step 1: Write integration test**

```javascript
// test/integration/epic-header.test.js
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import { spawn } from 'child_process';
import { join } from 'path';
import { mkdirSync, writeFileSync, rmSync } from 'fs';

describe('Epic Header Integration', () => {
  const testDir = join(__dirname, 'tmp', 'test-project');
  
  beforeAll(() => {
    // Create test project structure
    mkdirSync(join(testDir, 'docs', 'plans'), { recursive: true });
    mkdirSync(join(testDir, '.opencode'), { recursive: true });
    
    // Create plan file with epic reference
    writeFileSync(
      join(testDir, 'docs', 'plans', '2026-02-10-test-feature.md'),
      `# Test Feature Implementation Plan\n\n**Epic Issue:** #42\n`
    );
    
    // Create OpenCode config
    writeFileSync(
      join(testDir, '.opencode', 'config.json'),
      JSON.stringify({
        plugins: ['~/.config/opencode/powerlevel/plugin.js']
      })
    );
  });
  
  afterAll(() => {
    // Cleanup
    rmSync(testDir, { recursive: true, force: true });
  });
  
  it('should detect epic context in test project', async () => {
    const { detectEpicContext } = await import('../../lib/context-detector.js');
    const context = detectEpicContext(testDir);
    
    expect(context).toMatchObject({
      epicNumber: 42,
      planFile: 'docs/plans/2026-02-10-test-feature.md'
    });
  });
  
  it('should format epic display correctly', async () => {
    const { ContextProvider } = await import('../../lib/context-provider.js');
    const provider = new ContextProvider();
    
    const display = provider.getDisplayString(testDir);
    expect(display).toBe('Epic #42: Test Feature');
  });
});
```

**Step 2: Run integration tests**

```bash
npm test test/integration/
```

Expected: PASS

**Step 3: Add to CI if exists**

```yaml
# .github/workflows/test.yml (if exists)
- name: Run integration tests
  run: npm test test/integration/
```

**Step 4: Commit**

```bash
git add test/integration/epic-header.test.js
git commit -m "test: add integration tests for epic header display"
```

---

## Verification Steps

After implementation, verify the feature works end-to-end:

### Verification 1: Context Detection

```bash
cd /var/home/jorge/src/casestudypilot
node -e "
  const { detectEpicContext } = require('~/.config/opencode/powerlevel/lib/context-detector.js');
  const context = detectEpicContext(process.cwd());
  console.log(JSON.stringify(context, null, 2));
"
```

Expected output:
```json
{
  "epicNumber": 17,
  "epicTitle": "People/Presenter Agent",
  "planFile": "docs/plans/2026-02-09-people-presenter-agent.md",
  "repo": "castrojo/casestudypilot"
}
```

### Verification 2: Plugin API

1. Open OpenCode in casestudypilot directory
2. Open JavaScript console
3. Run: `session.context.getEpic()`
4. Verify output matches expected structure

### Verification 3: Header Display

1. Open OpenCode in casestudypilot directory
2. Check TUI header bar for epic display
3. Click epic link → should open GitHub issue #17
4. Edit plan file → header should update (or after restart)

### Verification 4: Edge Cases

Test these scenarios:
- Directory with no `docs/plans/` → No header display
- Plan file without epic reference → No header display
- Multiple plan files → Uses most recent (alphabetically last)
- Invalid epic number → Graceful fallback (no crash)

---

## Success Criteria

✅ Epic context detector extracts epic number from plan files  
✅ Context provider caches results for performance  
✅ Powerlevel plugin exposes `session.context.getEpic()` API  
✅ OpenCode TUI header bar displays epic link (if supported)  
✅ Clicking epic link opens GitHub issue in browser  
✅ Plan file changes invalidate cache and update display  
✅ All tests pass (unit + integration)  
✅ Documentation complete (README, AGENTS, feature doc)  
✅ Manual verification passes for all scenarios  

---

## Alternative Implementations

If OpenCode doesn't support header bar plugins:

### Option A: Console Banner
Display epic context in OpenCode startup console:
```
┌─────────────────────────────────────────┐
│ 🎯 Epic #17: People/Presenter Agent    │
│ https://github.com/castrojo/case...    │
└─────────────────────────────────────────┘
```

### Option B: Slash Command
Create `/epic` command to show current epic:
```
User: /epic
OpenCode: 🎯 Epic #17: People/Presenter Agent
          https://github.com/castrojo/casestudypilot/issues/17
```

### Option C: Status Bar
If status bar is available instead of header:
```
[casestudypilot] Epic #17 | main | Python 3.11
```

---

## Notes

- **Caching is critical**: File I/O on every UI render would be slow
- **Plan file format**: Assumes `**Epic Issue:** #N` on line 3 (consistent with epic-creation skill)
- **Most recent plan**: Uses alphabetically last filename (YYYY-MM-DD format sorts correctly)
- **Repo detection**: Relies on existing `repo-detector.js` from Powerlevel
- **OpenCode API**: Implementation assumes session.context and session.ui APIs exist (may need adjustment based on actual OpenCode plugin API)

---

## Future Enhancements

After MVP is working:

1. **Multiple Plan Support**: Show dropdown if multiple active plans
2. **Epic Status Badge**: Show status color (🟡 In Progress, 🟢 Done, 🔴 Blocked)
3. **Task Progress**: Show "Task 3/10" in header
4. **Quick Actions**: Right-click epic → "Mark task complete", "Update status"
5. **Epic History**: Track recently worked epics for quick switching
