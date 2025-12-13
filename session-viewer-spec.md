# Claude Code Session Viewer

## Overview

A tool for recording and reviewing Claude Code sessions for research purposes. Consists of two components:

1. **Slash commands** for Claude Code that mark recording boundaries and export session data
2. **Viewer app** (single HTML file) that provides an interactive UI for walking through recorded sessions

## Use Case

Research and analysis of Claude Code interactions. The goal is to understand the play-by-play of coding sessions, including prompts, responses, tool usage, and planning artifacts. False starts and tangents are valuable data—no editing/curation needed.

---

## Component 1: Slash Commands

### `/record-start`

- Marks the beginning of a recording session
- Should store a marker/timestamp so we know where to begin extraction
- Prints confirmation to the user

### `/record-stop`

- Marks the end of a recording session
- Extracts all turns from the marked start point to now
- Writes a JSON file to the current working directory
- Filename format: `session-{timestamp}.json`
- Collects scratchpad files (final state only) and includes them in the export
- Prints confirmation with the output filename

### Scratchpad File Detection

Include the final contents of these files if they exist in the working directory:
- `CLAUDE.md`
- `PLANNING.md`
- `SCRATCHPAD.md`
- `TODO.md`

(Can be extended later)

---

## Component 2: Data Format

```json
{
  "id": "session-{uuid}",
  "recorded_at": "ISO8601 timestamp",
  "working_directory": "/absolute/path",
  "turns": [
    {
      "type": "user",
      "content": "The user's prompt text",
      "timestamp": "ISO8601"
    },
    {
      "type": "assistant", 
      "content": "The assistant's response text",
      "tool_calls": [
        {
          "tool": "read",
          "file": "relative/path.js"
        },
        {
          "tool": "edit",
          "file": "relative/path.js",
          "diff": "unified diff string or null"
        },
        {
          "tool": "bash",
          "command": "npm install foo"
        },
        {
          "tool": "write",
          "file": "new-file.js"
        }
      ],
      "timestamp": "ISO8601"
    }
  ],
  "scratchpad_files": {
    "CLAUDE.md": "full file contents",
    "PLANNING.md": "full file contents"
  }
}
```

### Tool Call Schema

Each tool call is a minimal record for display purposes:

| Tool Type | Fields |
|-----------|--------|
| `read` | `file` |
| `edit` | `file`, `diff` (optional) |
| `write` | `file` |
| `bash` | `command` |

We do NOT store full tool input/output blobs—just enough to render a meaningful one-liner.

---

## Component 3: Viewer App

A single self-contained HTML file with embedded CSS and JavaScript. No build step, no dependencies beyond what can be inlined or loaded from CDN.

### Launching

From the directory containing session JSON files:
```bash
python -m http.server 8000
# then open http://localhost:8000/viewer.html
```

Or we could include a small bash script that does this automatically.

### UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Session Viewer                            [Scratchpad ▼]   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ USER                                                 │   │
│  │ Add authentication to the API                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ ASSISTANT                                            │   │
│  │ I'll add JWT-based authentication to your Express   │   │
│  │ server. First, let me look at the current setup...  │   │
│  │                                                      │   │
│  │ [📖 read src/server.js] [📝 edit src/server.js]     │   │
│  │ [▶ npm install jsonwebtoken]                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ... more turns ...                                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### UI Behavior

1. **Timeline**: Vertical list of turns, scrollable
2. **User turns**: Full text, visually distinct (e.g., left-aligned, muted background)
3. **Assistant turns**: 
   - Full response text displayed
   - Tool calls rendered as compact chips/pills below the response
   - Chip format: `[icon] [tool type] [file/command summary]`
4. **Tool call expansion**: Clicking a chip toggles an inline expansion showing details (diff content for edits, full command for bash)
5. **Scratchpad panel**: Button in header toggles a slide-out drawer or modal showing the contents of scratchpad files, with tabs for each file

### Visual Design

- Clean, minimal, readable
- Monospace font for code/diffs
- Clear visual distinction between user and assistant turns
- Subtle borders/shadows to separate turns
- Syntax highlighting for diffs (nice to have, not required for v1)

### Session Selection

If multiple `session-*.json` files exist in the directory:
- Show a dropdown or list to select which session to view
- Default to most recent

---

## Out of Scope (for now)

- Editing/curation of sessions
- Sharing via hosted URLs
- Forking/continuing sessions
- Full tool input/output storage
- Snapshotting scratchpad files at each turn (only final state)
- Build tooling (React, bundlers, etc.)

---

## File Deliverables

1. `viewer.html` — The single-file viewer app
2. Documentation for slash command implementation (these will be implemented within Claude Code's extension system)
3. `example-session.json` — Mock data for testing the viewer

---

## Open Questions

1. How does Claude Code's slash command system work? (Need to investigate the extension API)
2. Where does Claude Code store session/conversation data that we'd extract from?
3. Should the viewer auto-reload when JSON files change, for live-ish viewing?
