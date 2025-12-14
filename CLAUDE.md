# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A viewer for Claude Code session backups. Displays recorded sessions with expandable tool calls, collapsible "thinking" blocks for internal messages, and skill prompt context.

## Development

**Run the viewer locally:**
```bash
python server.py
# Open http://localhost:8000/viewer.html
```

The custom server enables the comment/note feature. Comments are saved directly to session JSON files.

No build step. The viewer is a single self-contained HTML file with embedded CSS and JavaScript.

## Architecture

**viewer.html** - Single-file app with three main sections:
- CSS styles (lines 7-390) using CSS variables for theming
- HTML structure (lines 391-392) - minimal, just header and content container
- JavaScript (lines 394-end) - all rendering logic

**Key data flow in JavaScript:**
1. `discoverSessions()` - finds JSON files via directory listing
2. `loadSession(url)` - fetches and parses session JSON
3. `processConversation()` - first pass merges streaming chunks by message ID, filters system messages, attaches skill context
4. `renderSession()` - groups internal turns into collapsible thinking blocks, renders timeline
5. `renderTurn()` / `renderThinkingBlock()` - generates HTML for individual turns

**Session backup format** (from `~/.claude/session_backup.py`):
```json
{
  "metadata": { "topic", "backupDate", "cwd", ... },
  "summary": "auto-generated",
  "conversation": [ ...JSONL messages... ]
}
```

**Message types handled:**
- `type: "assistant"` with `stop_reason: "end_turn"` = user-facing response
- `type: "assistant"` with `stop_reason: "tool_use"` = internal working (shown in thinking blocks)
- `type: "user"` with `isMeta: true` = injected skill prompts (attached to Skill tool call)
- `type: "user"` with `<command-message>` = skill invocation markers (filtered)
