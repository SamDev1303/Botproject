---
name: mcp-orchestrator
description: Coordinate and execute Model Context Protocol (MCP) server operations. Use when needing to integrate external tools, browse live web data (Google Maps/Search), or perform complex API interactions via mcporter.
---

# MCP Orchestrator

Use this skill to shift from standard REST API calls to MCP-driven operations for better tool integration and context handling.

## Core Tool: mcporter
Always use the full path for the binary: `/Users/hafsahnuzhat/.npm-global/bin/mcporter`

## Workflows

### 1. List Active Servers
Check which MCP servers are configured and reachable.
```bash
/Users/hafsahnuzhat/.npm-global/bin/mcporter list --output json
```

### 2. Add New Server
Add a new MCP server (stdio or HTTP).
```bash
/Users/hafsahnuzhat/.npm-global/bin/mcporter config add <name> --command "<cmd>"
```

### 3. Call MCP Tool
Execute a specific tool from an MCP server.
```bash
/Users/hafsahnuzhat/.npm-global/bin/mcporter call <server.tool> key=value
```

## Mandatory Logic
When a task can be performed via an active MCP server, prioritize it over standard Python scripts or manual API calls to ensure better context integration.
