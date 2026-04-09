---
name: app-surgeon
description: Reverse-engineer, customize, troubleshoot, and fix any installed application. Diagnoses crashes, patches code, injects UI, modifies configs, and adds functionality — with proactive web research and rollback safety.
trigger: /app-surgeon
---

# App Surgeon — Application Troubleshooting, Fixing & Customization Skill

## What This Does
Diagnoses and fixes application crashes, blank screens, and bugs. Also customizes any installed application (Electron, native macOS, web app, CLI tool) with targeted modifications: branding, UI changes, feature additions, behavior patches, and integrations — all with rollback safety and proactive research.

## When To Use
- **App is crashing, blank, frozen, or broken** — diagnose and fix
- **App has a bug** — find root cause and patch
- User wants to customize an app's look, feel, or behavior
- User wants to add features to an existing app
- User wants to rebrand or white-label an app
- User wants to integrate an app with other systems (FUTRON, MCP, APIs)
- User says: `/app-surgeon`, "fix this app", "app is crashing", "blank screen", "customize this app", "modify the UI", "add a feature to...", "rebrand...", "patch..."

---

## TROUBLESHOOTING & FIXING WORKFLOW (Use when app is broken)

### PRIME DIRECTIVE: PROACTIVE RESEARCH FIRST
**NEVER ask the user to google solutions. YOU are the researcher.** Search like a human would:

```
1. WebSearch for: "<app name> <error message> <OS version> fix"
2. WebSearch for: "<app name> <symptom> macOS <version> solution"
3. WebFetch official forum threads (look for [Solved] tags)
4. WebFetch GitHub issues (search repo issues for error text)
5. WebFetch Stack Overflow / Reddit threads
6. Check YouTube for video walkthroughs if text solutions unclear
7. Apply the MOST CONFIRMED fix first, then escalate
```

**Research cascade (search ALL of these before giving up):**
- Official app forum / community (e.g., forum.obsidian.md, discourse.*)
- GitHub Issues on the app's repo
- Stack Overflow
- Reddit (r/macOS, r/<AppName>, r/electronjs)
- X/Twitter (search `<app> crash <year>`)
- YouTube tutorials and fix videos
- Apple Developer Forums (for macOS-specific issues)
- Electron/Chromium bug tracker (for Electron apps)

### Fix Phase 1: SYMPTOM CAPTURE
```bash
# 1. What exactly is happening?
# Screenshot via CUA if possible, or user description

# 2. Crash logs (macOS)
ls -t ~/Library/Logs/DiagnosticReports/*<app>* | head -5

# 3. App's own log file
cat ~/Library/Application\ Support/<app>/*.log | tail -50

# 4. System console logs
log show --predicate 'process == "<app>"' --last 5m --style compact | tail -30

# 5. Process state
ps aux | grep -i "<app>"

# 6. Verbose launch (capture stderr)
/Applications/<App>.app/Contents/MacOS/<App> --enable-logging --v=1 2>&1 | head -50
```

### Fix Phase 2: DIAGNOSIS
Analyze crash reports and logs for root cause:

**Common patterns and their fixes:**

| Symptom | Likely Cause | Fix Approach |
|---------|-------------|--------------|
| Blank/black screen (Electron) | GPU renderer crash | `--disable-gpu`, Rosetta mode, or `user-flags.json` |
| Crash on indexing/loading | Corrupted cache or too many files | Clear caches, reduce scope, `.obsidianignore` equivalent |
| `EPIPE` / `SIGPIPE` errors | Broken pipe during file I/O | Remove problematic files/folders, fix permissions |
| `EXC_BREAKPOINT` / `SIGTRAP` | V8/Node crash, often plugin-related | Disable plugins, safe mode |
| `out of memory` / high RSS | Too many files or memory leak | Reduce file count, kill zombie processes |
| App closes immediately | Missing dependency or config corruption | Reinstall, reset config, check `otool -L` |
| Stale ASAR file (Electron) | Auto-update downloaded corrupt file | Delete `<app>-*.asar` from Application Support |
| macOS version incompatibility | ARM64 Metal/GPU bugs on new macOS | Rosetta mode (`arch -x86_64`), `LSArchitecturePriority` |

**Electron-specific diagnosis:**
```bash
# Check Electron/Chrome version
strings "/Applications/<App>.app/Contents/Frameworks/Electron Framework.framework/Versions/A/Electron Framework" | grep "Chrome/" | head -1

# Check for stale ASAR updates
ls ~/Library/Application\ Support/<app>/*.asar

# Check user flags
cat ~/Library/Application\ Support/<app>/user-flags.json

# Check if renderer process survives
ps aux | grep "<App> Helper (Renderer)"

# Force verbose launch
/Applications/<App>.app/Contents/MacOS/<App> --disable-gpu --enable-logging --v=1 2>&1
```

**macOS-specific diagnosis:**
```bash
# Check macOS version (new versions break apps)
sw_vers

# Check if app is running native ARM64 or Rosetta
arch  # shows current architecture
ps aux | grep <app>  # check process

# Check code signing
codesign -dv /Applications/<App>.app 2>&1

# Check if Metal GPU is the issue
# ARM64 Metal renderer bugs are common on macOS 26+
# Fix: force Rosetta mode
```

### Fix Phase 3: PROACTIVE WEB RESEARCH
**MANDATORY: Search for solutions BEFORE trying random fixes.**

```python
# Search pattern — do ALL of these:
WebSearch("<app name> <exact error text> fix <year>")
WebSearch("<app name> blank screen macOS <version>")
WebSearch("<app name> crash <error type> solution")
WebSearch("site:forum.<app>.com <symptom>")
WebSearch("site:github.com/<org>/<repo>/issues <error>")
```

**Rank solutions by confirmation count:**
1. Solutions marked [Solved] on official forums → try first
2. Solutions confirmed by 2+ users → try second
3. Official documentation fixes → try third
4. Single-user suggestions → try last

### Fix Phase 4: ESCALATING FIX CASCADE
Apply fixes from **least destructive to nuclear**, stopping when one works:

```
Level 1: CONFIG FIXES (zero risk)
├── Disable community plugins / extensions (safe mode)
├── Reset workspace/window state files
├── Set Electron flags (--disable-gpu, --no-sandbox)
├── Clear app caches (Cache/, GPUCache/, Code Cache/)
└── Check for and remove stale update files (.asar)

Level 2: ENVIRONMENT FIXES (low risk)
├── Force Rosetta mode (arch -x86_64) for ARM64 issues
├── Set LSArchitecturePriority in Info.plist
├── Update/downgrade the app version
├── Fix file permissions (chmod, xattr)
└── Remove symlinks that confuse the app

Level 3: DATA FIXES (moderate risk — backup first!)
├── Reduce data volume (.obsidianignore, proxy vault, etc.)
├── Move heavy folders out temporarily
├── Create lightweight proxy with symlinks to essential data
├── Remove corrupted data files identified in crash logs
└── Rebuild indexes/databases

Level 4: RESET (high risk — backup first!)
├── Rename/backup app config folder (e.g., .obsidian → .obsidian-backup)
├── Delete Application Support/<app>/ (preserves user data)
├── Fresh reinstall from official source or brew
└── Nuclear: delete ALL app data and reinstall clean

Level 5: WORKAROUNDS (when nothing else works)
├── Run under Rosetta permanently
├── Pin to older version that works
├── Create launcher script with special flags
├── Use alternative app for same purpose
└── File bug report with app maintainers
```

### Fix Phase 5: VERIFY & MAKE PERMANENT
```bash
# After finding a fix:
# 1. Verify app works (launch, test core features)
# 2. Make the fix PERMANENT (don't leave temporary workarounds):

# For Rosetta mode:
defaults write /Applications/<App>.app/Contents/Info.plist LSArchitecturePriority -array "x86_64"

# For Electron flags:
echo '["--disable-gpu"]' > ~/Library/Application\ Support/<app>/user-flags.json

# For launch scripts:
cat > ~/.openclaw/bin/<app> << 'EOF'
#!/usr/bin/env bash
arch -x86_64 /Applications/<App>.app/Contents/MacOS/<App> --disable-gpu "$@" &
disown
EOF
chmod +x ~/.openclaw/bin/<app>

# 3. Save the fix to memory so it's never rediscovered
```

### Fix Phase 6: DOCUMENT
Save fix to memory for future reference:
```markdown
# App Fix: <App Name>
## Date: YYYY-MM-DD
## Symptom: <what was broken>
## Root Cause: <why it was broken>
## Fix Applied: <what fixed it>
## Platform: <macOS version, architecture>
## Permanent: <how fix persists across restarts>
## What DIDN'T Work: <failed attempts, save time next time>
```

Save to: `memory/app-surgery-<appname>.md` AND `claude-mem`

## Known Fixes Database

| App | Issue | macOS | Fix |
|-----|-------|-------|-----|
| Obsidian 1.12.7 | Blank screen after indexing | 26.4 (ARM64) | Rosetta + `--disable-gpu` + proxy vault (reduce files) |
| Obsidian (any) | Crash during vault indexing | any | Reduce vault size via `.obsidianignore`, move Claude logs out |
| Obsidian (any) | Plugin causes crash | any | Disable plugins: `echo '[]' > .obsidian/community-plugins.json` |
| Electron apps (general) | Blank/black window | macOS 26+ | `--disable-gpu` in `user-flags.json` or Rosetta mode |
| Electron apps (general) | Stale update crash loop | any | Delete `<app>-*.asar` from `~/Library/Application Support/<app>/` |

---

## Workflow

### Phase 1: RECONNAISSANCE (mandatory first step)
Analyze the target app before ANY modifications:

```bash
# 1. Identify app type and structure
file /Applications/<App>.app/Contents/MacOS/*
ls /Applications/<App>.app/Contents/Resources/
defaults read /Applications/<App>.app/Contents/Info.plist CFBundleIdentifier

# 2. Detect technology stack
# Electron: Look for app.asar, .package/, package.json, main.js/main.cjs
# Native macOS: Look for Swift/ObjC binaries, .nib/.storyboard files
# Web wrapper: Look for index.html, webapp manifest
# Python: Look for .py files, __pycache__, venv/

# 3. Map customization points
# Config files: ~/.<app>/, ~/Library/Application Support/<app>/
# Compiled code: .js/.cjs bundles (Electron), .py (Python)
# UI resources: .html, .css, .svg, images
# Preload scripts: preload.js (Electron IPC bridge)
# Database: .sqlite, .json state files
```

**CRITICAL: Create backup before ANY modification**
```bash
cp <target-file> <target-file>.backup-$(date +%Y%m%d-%H%M%S)
```

### Phase 2: ANALYSIS
Understand the app's internals:

For **Electron apps** (most common for modern desktop apps):
- `package.json` → dependencies, entry points
- `main.cjs` or `main.js` → main process (IPC handlers, window creation, business logic)
- `renderer/dist/` → React/Vue/Svelte compiled UI (usually minified)
- `preload.js` → IPC bridge between main and renderer (security boundary)
- `~/.appname/config/` → user configuration files

**Key patterns to identify:**
- System prompt / personality text (for AI apps)
- IPC channel definitions (for adding new features)
- Window creation (`BrowserWindow`) → UI injection point
- Config loading functions → override points
- HTTP endpoints / API calls → proxy/intercept points

For **Python apps:**
- Entry point script → main logic
- Config files → override points
- HTTP servers → endpoint injection
- Templates → UI modification

### Phase 3: PLAN
Generate a modification plan:

1. **What changes are needed** (UI, behavior, branding, features)
2. **Which files to modify** (with exact line numbers/patterns)
3. **Backup strategy** (which files, where to store backups)
4. **Injection approach:**
   - **Config override**: Write config files the app reads (safest)
   - **Code patch**: String replacement in compiled code (moderate risk)
   - **UI injection**: `webContents.executeJavaScript` after page load (Electron)
   - **Preload modification**: Add IPC channels for new features
   - **Proxy layer**: HTTP proxy between app and services
   - **MCP server**: Add tools the app can call
5. **Rollback plan** (how to undo each change)

### Phase 4: EXECUTE
Apply modifications using these techniques:

#### A. Config Override (Safest)
```python
# Write config files the app reads at startup
import json
config = {"setting": "custom_value"}
with open("~/.appname/config/custom.json", "w") as f:
    json.dump(config, f, indent=2)
```

#### B. Compiled Code Patching (Electron .cjs/.js bundles)
```python
# String replacement in compiled JavaScript
with open("main.cjs", "r") as f:
    content = f.read()
content = content.replace("old_string", "new_string")
with open("main.cjs", "w") as f:
    f.write(content)
```

**Rules for code patching:**
- Always search for UNIQUE strings (avoid partial matches)
- Test replacements with `grep -c` before and after
- Verify file integrity (app still launches)
- Keep patches MINIMAL — smallest change that works

#### C. UI Injection (Electron webContents)
```javascript
// Inject after page loads via did-finish-load event
win.webContents.on("did-finish-load", () => {
    win.webContents.executeJavaScript(`
        // Add custom CSS
        const style = document.createElement("style");
        style.textContent = "...custom styles...";
        document.head.appendChild(style);
        
        // Add custom UI elements
        const widget = document.createElement("div");
        widget.id = "custom-widget";
        widget.innerHTML = "...";
        document.body.appendChild(widget);
    `);
});
```

#### D. IPC Channel Addition (Electron)
```javascript
// In main process (main.cjs)
require("electron").ipcMain.handle("custom:action", async (_, args) => {
    // Custom logic here
    return { result: "done" };
});

// In preload (preload.js) — add to contextBridge
// OR bypass via webContents.executeJavaScript with fetch to local HTTP server
```

#### E. HTTP Proxy/Intercept
```python
# Create a local proxy that intercepts and modifies app traffic
# Useful for: adding auth, modifying API responses, injecting data
```

#### F. MCP Server Integration
```python
# Create MCP servers that expose new capabilities
# App calls tools via MCP protocol (stdio or HTTP)
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("custom-tools")

@mcp.tool()
def custom_feature(args: str) -> str:
    """New feature description"""
    return "result"
```

### Phase 5: VERIFY
After every modification:
```bash
# 1. App still launches
open /Applications/<App>.app

# 2. Core functionality works
# Test main features manually or via automated checks

# 3. Custom features work
# Test each modification individually

# 4. No regressions
# Check console for errors
```

### Phase 6: DOCUMENT
Log all changes to memory:
```markdown
# App Surgery: <App Name>
## Date: YYYY-MM-DD
## Changes Applied:
1. [file] what was changed and why
2. [file] what was changed and why
## Backups:
- original.backup-YYYYMMDD-HHMMSS
## Rollback:
cp original.backup-YYYYMMDD-HHMMSS original
```

Save to: `memory/app-surgery-<appname>.md`

## Design Principles (for UI modifications)

Based on research, these produce the BEST results:

1. **Analyze code, not screenshots** — Understand what components DO, not how they look
2. **Principle-based, not prescriptive** — Describe the feel, not exact pixels
3. **Evocative framing** — "cyberpunk control panel" > "dark theme with neon accents"
4. **Force domain exploration** — Understand the app's purpose before designing
5. **Iterative refinement** — First pass 70%, second pass 90%
6. **Maintain functional parity** — Don't break existing features while adding new ones
7. **Config over code** — Prefer config file overrides over code patches when possible

## Rollback Commands
```bash
# List all backups for an app
ls /Applications/<App>.app/Contents/Resources/app/.package/dist/*.backup-*

# Restore a backup
cp <file>.backup-YYYYMMDD-HHMMSS <file>

# Nuclear rollback: reinstall from DMG/App Store
```

## Known App Architectures

| App Type | Key Files | Best Approach |
|----------|-----------|---------------|
| Electron (React) | main.cjs, renderer/dist/index-*.js | Config + code patch + UI injection |
| Electron (Vue) | main.js, renderer/dist/app-*.js | Same as React |
| Python (Flask/Django) | app.py, templates/ | Direct code edit |
| Python (CLI) | script.py | Direct code edit |
| Native macOS (Swift) | Binary in MacOS/ | Config override only (can't patch binary) |
| Web App (browser) | Chrome extension or userscript | CSS/JS injection via extension |

## Specialized Tools & Agents to Leverage

### Skills (invoke via Skill tool):
- **`gitnexus-exploring`** — Trace how code works, execution flows, architecture. USE THIS in Phase 1 & 2.
- **`gitnexus-refactoring`** — Safe rename, extract, split, restructure code. USE THIS in Phase 4.
- **`gitnexus-impact-analysis`** — "What will break if I change X?" USE THIS before patching.
- **`gitnexus-debugging`** — Trace errors after patches. USE THIS in Phase 5.
- **`frontend-design:frontend-design`** — Generate production-grade UI with high design quality. USE THIS for UI injection/redesign.
- **`graphify`** — Turn any code/docs into a knowledge graph. USE THIS to map complex apps.
- **`simplify`** — Review changed code for quality and efficiency. USE THIS after patching.
- **`feature-dev:feature-dev`** — Guided feature development with architecture focus. USE THIS for major additions.
- **`deep-research:deep-research`** — Research reports with citations. USE THIS for unfamiliar app stacks.

### Sub-Agents (136 specialized agents in ~/.claude/agents/):
Query `AGENT_INDEX.json` at `~/.openclaw/workspace/AVANI_SHARED_BRAIN/agents/` to find specialists:
- **react-specialist** — React component architecture, state flow, rendering
- **typescript-pro** — TypeScript types, interfaces, compiler fixes
- **electron-pro** — Electron main/renderer/preload, packaging, desktop runtime
- **frontend-developer** — UI implementation, CSS, responsive design
- **code-reviewer** / **code-reviewer-va** — Code health, maintainability, risky patterns
- **security-auditor** — Auth flows, secrets handling, input validation
- **refactoring-specialist** — Low-risk structural refactors preserving behavior
- **performance-engineer** — Hot paths, rendering regressions, bottlenecks
- **python-pro** — Python runtime, packaging, testing
- **javascript-pro** — JS runtime, browser/Node execution
- **debugger** — Deep bug isolation across code paths
- **ui-designer** — Interaction design, implementation-ready guidance
- **ui-fixer** — Smallest safe patch for UI issues
- **accessibility-tester** — Accessibility audit of UI changes

### MCP Tools:
- **Figma MCP** — `get_design_context`, `use_figma`, `search_design_system` — pull designs directly from Figma and generate code. See: figma.com/blog/introducing-claude-code-to-figma/
- **Claude Preview** — `preview_start`, `preview_screenshot`, `preview_inspect` — live preview of UI changes
- **Playwright** — `browser_snapshot`, `browser_click`, `browser_evaluate` — automated browser testing
- **Computer Use (CUA)** — `screenshot`, `left_click`, `type` — interact with native app GUIs directly
- **Context7** — `resolve-library-id`, `query-docs` — fetch current docs for any framework/library
- **Ludo AI** — `createImage`, `editImage`, `removeBackground` — generate game assets, icons, sprites

### DeepWiki:
- **deepwiki.com** — AI documentation for any GitHub repo. Use to understand open-source apps before surgery.

## Self-Evolving Learning System

App Surgeon gets smarter over time by learning from every fix and surgery it performs.

### How It Learns

**After EVERY fix or surgery, App Surgeon MUST:**

1. **Save the fix to the Known Fixes Database** (in this file's table above)
2. **Save detailed context to memory**: `memory/app-surgery-<appname>.md`
3. **Save to claude-mem** for cross-session persistence
4. **Update the app profile** in `~/.openclaw/app-profiles/`

### App Profiles (Proactive Learning)

App Surgeon should **proactively study** the user's installed applications to build context BEFORE issues arise. When idle or when asked to audit:

```bash
# Scan all installed apps and build profiles
/app-surgeon scan-apps
```

This creates `~/.openclaw/app-profiles/<app-name>.json` for each app with:
```json
{
  "name": "Obsidian",
  "bundleId": "md.obsidian",
  "version": "1.12.7",
  "type": "electron",
  "electronVersion": "Chrome/142",
  "configPaths": [
    "~/Library/Application Support/obsidian/",
    "~/.openclaw/workspace/AVANI_VAULT/.obsidian/"
  ],
  "logPaths": [
    "~/Library/Application Support/obsidian/obsidian.log",
    "~/Library/Logs/DiagnosticReports/Obsidian*"
  ],
  "knownIssues": [
    {
      "symptom": "Blank screen after indexing",
      "rootCause": "ARM64 Metal renderer crash on macOS 26.4",
      "fix": "Rosetta + --disable-gpu + proxy vault",
      "dateFixed": "2026-04-08"
    }
  ],
  "customizations": [],
  "flags": ["--disable-gpu"],
  "launchMode": "rosetta",
  "healthCheck": "curl -s http://localhost:... || ps aux | grep Obsidian"
}
```

### Learning From Fixes

Every time a fix is applied, the learning system:

1. **Records what failed** — saves failed attempts so they're never retried
2. **Records what worked** — adds to Known Fixes Database with confirmation
3. **Extracts patterns** — if the same fix works across multiple apps (e.g., `--disable-gpu` for Electron on macOS 26+), it becomes a **general rule** applied proactively
4. **Builds platform knowledge** — learns macOS version quirks, architecture issues, common Electron bugs
5. **Remembers user preferences** — which apps they use, how they prefer fixes (permanent vs. workaround)

### Proactive Behavior

App Surgeon should NOT wait for things to break. It should:

- **On first use with a new app:** Scan the app, build a profile, check for known issues with that version + macOS combo
- **After macOS updates:** Proactively check if any profiled apps have known compatibility issues with the new version
- **Periodically:** Review crash logs in `~/Library/Logs/DiagnosticReports/` for silent crashes the user hasn't noticed
- **When asked to customize:** First check the Known Fixes Database for any existing issues that should be resolved before modifications

### Memory Integration

```
App Surgeon Memory Stack:
├── SKILL.md Known Fixes Database    → quick lookup table (this file)
├── memory/app-surgery-*.md          → detailed fix/surgery logs
├── claude-mem observations          → cross-session persistence
├── ~/.openclaw/app-profiles/*.json  → structured app profiles
└── FUTRON brain.db knowledge_base   → searchable database
```

**Search order when diagnosing:**
1. Known Fixes Database in this file (instant)
2. App profiles in `~/.openclaw/app-profiles/` (local)
3. `memory/app-surgery-*.md` files (detailed)
4. `claude-mem` search (cross-session)
5. Web research (external — LAST resort, not first)

## Integration with FUTRON
- All app modifications are logged to `memory/app-surgery-*.md`
- MCP servers created for apps are registered in `.mcp.json`
- Backups can be synced to S3 via `futron-s3-critical-push`
- Changes tracked in `futron-brain.db` knowledge_base table
- Orpheus TTS (port 9103) available for voice-enabled UI additions
- AVANI shared brain provides context about past surgeries and preferences

## Examples of Past Surgeries
- **Rowboat → AVANI**: Replaced personality (3-layer enforcement), added TTS toggle widget (Orpheus/ElevenLabs/Off), injected agent notes (user.md, preferences.md, identity.md), patched voice routing (config-driven), fixed model template (raw → Gemma4 chat), created 8 MCP servers, wired bus agent
- **Template targets**: Cursor, VS Code, Obsidian, Discord, Slack, Spotify, VirtualDJ, Terminal apps, any Electron app

## Open Source Toolbox

### App Building & Cloning
- **Dyad** (github.com/dyad-sh/dyad) — Local AI app builder. Electron + React + BYOK. Can rapidly rebuild/clone app UIs locally. Apache 2.0. Install: download from dyad.sh
- **AI Website Cloner** (github.com/JCodesMore/ai-website-cloner-template) — 5-phase pipeline: Recon → Foundation → Component Specs → Parallel Construction (git worktrees) → Integration & Validation. Next.js 16 + Tailwind + shadcn. Works with Claude Code.
- **Gemini CLI** (`npm i -g @google/gemini-cli`) — Google's terminal AI. Query/edit large codebases, generate apps from images/PDFs. Free alternative to Claude Code for multi-model approach.

### Reverse Engineering
- **ReverserAI** (github.com/mrphrazer/reverser_ai) — AI-powered binary analysis using local LLMs (Mistral-7B or Mixtral-8x7B). Extracts semantic function names from decompiler output. Binary Ninja plugin. Runs offline. For native macOS app analysis.
- **Blackbox RE Methodology** (ThoughtWorks): When you can't access source code:
  1. Deploy AI agent to explore the UI (CUA screenshot + click)
  2. Capture screenshots, document all UI elements and flows
  3. Monitor network traffic (browser dev tools / mitmproxy)
  4. Monitor database changes (if accessible)
  5. Run multiple passes to discover all code paths
  6. Generate consolidated specification documents
  7. Feed specs into builder tools (Dyad, Claude Code, etc.)
  8. Build feature-parity tests comparing original vs. rebuilt
- **Ghidra** (ghidra-sre.org) — NSA's free reverse engineering framework. Decompile native binaries.
- **Hopper** — macOS disassembler for analyzing native app binaries.

### CLI Utilities (install via brew)
- **jq** — JSON query/transform: `cat config.json | jq '.settings.theme'`
- **httpie** — Human-friendly HTTP client: `http GET localhost:9103/health`
- **just** — Modern make-like task runner for automation scripts
- **mitmproxy** — Intercept HTTP/HTTPS traffic between app and services
- **asar** — Extract/pack Electron app archives: `asar extract app.asar ./extracted`
- **npx source-map-explorer** — Analyze webpack/vite bundles to understand code structure
- **prettier** — Format minified code for readability: `prettier --write main.cjs`

### Code Translation & Porting
- **aiTrans** (github.com/ortegaalfredo/aiTrans) — **BEST FIT: CLI source-to-source transpiler.** Pure Python, argparse, isolated API connector. Swap `openaiConnector.py` for Ollama to run 100% local. Supports C, C++, Python, Rust + most languages. Can even accept English descriptions as "source code." `python aiTrans.py -s input.py -l rust -a`
- **AWS Code Conversion Pipeline** (github.com/aws-samples/code-conversion-using-gen-ai) — 4-phase pipeline: analyze → convert → validate → generate tests. 15+ languages. Best architecture for production quality (confidence scoring, framework-specific tests). Heavy AWS coupling but core logic extractable.
- **AI Code Translator** (github.com/mckaywrigley/ai-code-translator) — Web UI for cross-language translation. Next.js + TypeScript. `git clone && npm i && npm run dev`
- **AI-Code-Converter** (github.com/Abhii-07/AI-Code-Converter) — React + Monaco Editor + Java Spring Boot. Web-only, OpenAI dependency.
- **Context7** (MCP tool) — Fetch current docs for any framework/library during translation
- **INTEGRATION PLAN:** Clone aiTrans → replace openaiConnector.py with Ollama connector → wrap as `futron-mcp-code-translate` MCP server → AVANI can translate any code locally at zero cost

### App-Specific Tools
- **electron-builder** — Package modified Electron apps
- **asar** — `npm i -g asar` — Extract/repack Electron app bundles
- **nw-builder** — Build NW.js apps
- **pyinstaller** — Package Python apps
- **create-dmg** — Create macOS DMG installers for modified apps

## Blackbox Reverse Engineering Pipeline

When you DON'T have source code (native apps, closed-source software):

```
Phase 1: OBSERVE
├── CUA screenshots of every screen/state
├── mitmproxy capture of all network traffic  
├── Accessibility tree dump (AX Scanner)
├── File system monitoring (fswatch on ~/Library/*)
└── Document: flows, states, API calls, data formats

Phase 2: SPECIFY
├── AI generates specs from observations
├── Component catalog with computed styles
├── API contract documentation
├── State machine diagrams (graphify)
└── Data model inference from traffic/files

Phase 3: REBUILD
├── Dyad or Claude Code generates new app from specs
├── AI Website Cloner for web-based apps
├── Parallel construction with git worktrees
├── MCP servers replace backend functionality
└── Progressive enhancement (start minimal, add features)

Phase 4: VALIDATE
├── Visual comparison (screenshot diff)
├── Functional parity testing
├── Performance benchmarking
├── User acceptance (Architect reviews)
└── Integration testing with FUTRON ecosystem
```

## Quick Start
```
/app-surgeon fix <app-name>       # Diagnose & fix crashes/bugs (NEW)
/app-surgeon <app-name>           # Full surgery workflow (customize/modify)
/app-surgeon analyze <app-name>   # Recon only
/app-surgeon clone <app-name>     # Blackbox clone/rebuild
/app-surgeon rollback <app-name>  # Restore from backup
/app-surgeon install-tools        # Install CLI toolbox
```

### Fix Mode Examples
```
/app-surgeon fix Obsidian          # "Obsidian shows blank screen"
/app-surgeon fix "VS Code"         # "VS Code won't start"
/app-surgeon fix Discord            # "Discord crashes on launch"
/app-surgeon fix Spotify            # "Spotify audio stuttering"
```

When invoked with `fix`, App Surgeon automatically:
1. Captures symptoms (crash logs, console, process state)
2. Searches web/forums/GitHub for confirmed solutions
3. Applies fixes in escalating order (config → env → data → reset)
4. Verifies the fix works
5. Makes it permanent
6. Documents everything to memory
