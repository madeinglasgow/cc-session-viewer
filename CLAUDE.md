# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A viewer for Claude Code session backups. Displays recorded sessions with expandable tool calls, collapsible "thinking" blocks for internal messages, skill prompt context, terminal-styled bash mode commands, and user-added notes/comments.

## Development

**Run the viewer locally:**
```bash
python server.py
# Open http://localhost:8000/viewer.html
```

No build step. The viewer is a single self-contained HTML file with embedded CSS and JavaScript.

## Architecture

### Files

**server.py** - Custom HTTP server that:
- Serves static files (HTML, JSON) on port 8000
- Handles `POST /save-comments` to persist notes to session JSON files
- Validates file paths to prevent directory traversal attacks

**viewer.html** - Single-file app with three main sections:
- CSS styles (lines 7-580) using CSS variables for theming
- HTML structure (lines 582-596) - minimal, just header and content container
- JavaScript (lines 598-end) - all rendering logic

### Key Data Flow

1. `discoverSessions()` - finds JSON files via directory listing
2. `loadSession(url)` - fetches and parses session JSON, loads existing comments
3. `processConversation()` - merges streaming chunks by message ID, filters system messages, attaches skill context, merges bash mode turns
4. `renderSession()` - groups internal turns into collapsible thinking blocks, renders timeline
5. `renderTurnRow()` - wraps turn + comment card in grid layout
6. `renderTurn()` / `renderThinkingBlock()` - generates HTML for individual turns

### Comment System

- `renderCommentCard()` / `renderCommentEditor()` - render note cards or inline editor
- `addComment()`, `editComment()`, `deleteComment()`, `saveComment()` - UI handlers
- `persistComments()` - POSTs to `/save-comments` endpoint

Comments are stored in session JSON under a `comments` key:
```json
{
  "metadata": { ... },
  "conversation": [ ... ],
  "comments": {
    "turn-0": "Note text here",
    "turn-5": "Another note"
  }
}
```

### Session Backup Format

From `~/.claude/session_backup.py`:
```json
{
  "metadata": { "topic", "backupDate", "cwd", ... },
  "summary": "auto-generated",
  "conversation": [ ...JSONL messages... ]
}
```

### Bash Mode Rendering

When users run shell commands via `!` in Claude Code, the session contains consecutive user turns with special tags:
- `<bash-input>command</bash-input>` - the command entered
- `<bash-stdout>output</bash-stdout>` - standard output
- `<bash-stderr>errors</bash-stderr>` - standard error (optional)

`processConversation()` merges these consecutive turns into a single turn with a `bashCommands` array. `renderBashSession()` then displays them in a terminal-styled card with:
- Dark background with macOS-style traffic light dots
- Green `$` prompt before commands
- Gray stdout, red stderr
- Cyan border and "Bash" label (instead of coral "User")

### Message Types Handled

- `type: "assistant"` with `stop_reason: "end_turn"` = user-facing response
- `type: "assistant"` with `stop_reason: "tool_use"` = internal working (shown in thinking blocks)
- `type: "user"` with `isMeta: true` = injected skill prompts (attached to Skill tool call)
- `type: "user"` with `<command-message>` = skill invocation markers (filtered)
- `type: "user"` with `<bash-input>` = bash mode commands (merged into terminal cards)
