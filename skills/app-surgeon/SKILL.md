---
name: app-surgeon
description: Reverse-engineer, customize, and add features to any installed application. Patches compiled code, injects custom UI, modifies configs, and adds functionality — all with rollback safety.
trigger: /app-surgeon
---

# App Surgeon — Application Customization & Feature Injection Skill

## When To Use
- Customize an app's look, feel, or behavior
- Add features to an existing app
- Rebrand or white-label an app
- Integrate an app with other systems
- Translate/port code between languages

## Workflow

### Phase 1: RECONNAISSANCE
```bash
# Identify app type
file /Applications/<App>.app/Contents/MacOS/*
ls /Applications/<App>.app/Contents/Resources/

# ALWAYS backup first
cp <target-file> <target-file>.backup-$(date +%Y%m%d-%H%M%S)
```

### Phase 2: ANALYSIS
- Electron: package.json, main.cjs, renderer/dist/, preload.js
- Python: entry point, config files, templates
- Native macOS: plists, config files (can't patch binaries)

### Phase 3: PLAN
Choose approach: Config override (safest) → Code patch (moderate) → UI injection (Electron) → MCP server (new features)

### Phase 4: EXECUTE
Apply modifications with automatic backups.

### Phase 5: VERIFY
Test app launches, core features work, custom features work.

### Phase 6: DOCUMENT
Log all changes for rollback and future reference.

## Techniques

### Config Override (Safest)
Write config files the app reads at startup.

### Code Patching (Electron)
String replacement in compiled JS bundles.

### UI Injection (Electron)
```javascript
win.webContents.on("did-finish-load", () => {
    win.webContents.executeJavaScript(`...custom code...`);
});
```

### MCP Server Integration
Create MCP servers that expose new capabilities to the app.

### Blackbox Reverse Engineering
OBSERVE (screenshots + traffic) → SPECIFY (AI generates specs) → REBUILD (new app from specs) → VALIDATE (visual diff)

## Code Translation
Use the included code-translate tool:
```bash
python tools/code-translate.py --cli -s input.py -l rust
```

## Quick Start
```
/app-surgeon <app-name>           # Full surgery workflow
/app-surgeon analyze <app-name>   # Recon only
/app-surgeon clone <app-name>     # Blackbox clone/rebuild
/app-surgeon rollback <app-name>  # Restore from backup
```
