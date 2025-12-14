# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A viewer for Claude Code session backups. Displays recorded sessions with expandable tool calls, collapsible "thinking" blocks for internal messages, skill prompt context, and user-added notes/comments.

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
3. `processConversation()` - merges streaming chunks by message ID, filters system messages, attaches skill context
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

### Message Types Handled

- `type: "assistant"` with `stop_reason: "end_turn"` = user-facing response
- `type: "assistant"` with `stop_reason: "tool_use"` = internal working (shown in thinking blocks)
- `type: "user"` with `isMeta: true` = injected skill prompts (attached to Skill tool call)
- `type: "user"` with `<command-message>` = skill invocation markers (filtered)
