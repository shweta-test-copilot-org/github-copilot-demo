# 📋 AI Native Development Cheatsheet

Quick reference for VS Code Copilot customization primitives.

---

## 📁 File Locations

| Type | Location | Extension |
|------|----------|-----------|
| Instructions | `.github/instructions/` | `.instructions.md` |
| Prompts | `.github/prompts/` | `.prompt.md` |
| Agents | `.github/agents/` | `.agent.md` |
| Skills | `.github/skills/` | `SKILL.md` |
| Global Instructions | `.github/copilot-instructions.md` | (single file) |

---

## 📋 Instructions Frontmatter

```yaml
---
applyTo: "**/*.py"          # Glob pattern for auto-apply
---
```

### Common Glob Patterns

| Pattern | Matches |
|---------|---------|
| `**/*.py` | All Python files |
| `**/*.{js,ts}` | All JS and TS files |
| `**/*.test.*` | All test files |
| `src/**/*.tsx` | TSX files in src folder |
| `**/components/**` | Everything in components folders |

---

## 📝 Prompt Frontmatter

```yaml
---
name: my-prompt           # Required: Command name (use with /)
description: What it does # Required: Shown in command palette
agent: agent              # Optional: ask | edit | agent | custom-name
model: Claude Sonnet 4    # Optional: Specific model
tools:                    # Optional: Available tools
  - search
  - edit/editFiles
  - edit/createFile
---
```

### Available Tools

| Tool | Purpose |
|------|---------|
| `search` | Search codebase |
| `usages` | Find symbol usages |
| `fetch` | Fetch web content |
| `edit/editFiles` | Modify existing files |
| `edit/createFile` | Create new files |
| `githubRepo` | Access GitHub repos |
| `runTerminalCommand` | Run shell commands |

---

## 🤖 Agent Frontmatter

```yaml
---
name: My Agent            # Required: Display name
description: Purpose      # Required: Shown in dropdown
tools:                    # Optional: Restrict available tools
  - search
  - usages
model: Claude Sonnet 4    # Optional: Specific model
handoffs:                 # Optional: Agent transitions
  - label: "Button Text"  # Text on handoff button
    agent: target-agent   # Target agent identifier
    prompt: "Instructions"# Pre-filled prompt
    send: false           # Auto-submit? (true/false)
---
```

### Handoff Options

| Property | Type | Description |
|----------|------|-------------|
| `label` | string | Button text shown to user |
| `agent` | string | Target agent identifier |
| `prompt` | string | Pre-filled text for next agent |
| `send` | boolean | Auto-submit when clicked |

---

## ⚡ Skills Frontmatter (SKILL.md)

```yaml
---
name: My Skill                # Required: Skill name
description: What it enables and when to use it  # Required: Agent discovers and uses based on this
---
```

> **Key Difference**: Unlike prompts (explicit `/command`) or agents (manual selection), skills are **discovered autonomously** by the agent based on your intent.

### Skill Folder Structure

```
my-skill/
├── SKILL.md                 # Skill definition
├── instructions/            # Related instructions
├── prompts/                 # Related prompts
├── scripts/                 # Deterministic scripts
└── references/              # Reference documentation
```

---

## 📦 APM Commands

| Command | Purpose |
|---------|---------|
| `apm install <package>` | Install a skill or instruction package |
| `apm compile` | Generate nested AGENTS.md files |
| `apm compile --verbose` | Show what's being generated |
| `apm list` | List installed packages |
| `apm init` | Initialize apm.yml in current project |

### Progressive Disclosure

After `apm compile`, each folder gets context-appropriate instructions:

```
project/
├── AGENTS.md           # Root-level instructions
├── src/
│   ├── AGENTS.md       # src-level (inherits root)
│   ├── api/
│   │   └── AGENTS.md   # API-specific
│   └── database/
│       └── AGENTS.md   # Database-specific
```

---

## 🔤 Variables (Prompt Files)

| Variable | Description |
|----------|-------------|
| `${file}` | Full path of current file |
| `${fileBasename}` | Filename without path |
| `${fileDirname}` | Directory of current file |
| `${fileExtname}` | File extension |
| `${selection}` | Currently selected text |
| `${selectedText}` | Same as selection |
| `${workspaceFolder}` | Workspace root path |
| `${input:name}` | Prompt user for input |
| `${input:name:hint}` | With placeholder hint |

---

## 🔗 References

### Link to Other Files

```markdown
Follow [coding-standards](../instructions/coding-standards.instructions.md).
See [API docs](../../docs/API.md) for reference.
```

### Reference Tools in Body

```markdown
Use #tool:search to find related code.
Use #tool:githubRepo to fetch examples.
```

---

## ⚙️ VS Code Settings

```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "chat.promptFiles": true,
  "chat.instructionsFilesLocations": {
    ".github/instructions": true
  },
  "chat.promptFilesLocations": {
    ".github/prompts": true
  },
  "chat.agentFilesLocations": {
    ".github/agents": true
  }
}
```

---

## 🎯 Quick Patterns

### Read-Only Analyzer Agent

```yaml
---
name: Analyzer
description: Analyze code without making changes
tools: ['search', 'usages', 'fetch']
handoffs:
  - label: "Implement"
    agent: implementer
    prompt: "Implement based on analysis above."
    send: false
---
# You analyze code but DO NOT edit files.
```

### Implementation Agent

```yaml
---
name: Implementer
description: Implement changes to code
tools: ['search', 'editFile', 'createFile']
---
# You implement code changes based on requirements.
```

### Simple Prompt with Input

```yaml
---
name: create-component
description: Create a new component
agent: agent
tools: ['createFile']
---
Create a new component named ${input:componentName:Enter component name}.
```

---

## 🚫 Common Mistakes

| ❌ Wrong | ✅ Right |
|----------|----------|
| `apply-to:` | `applyTo:` |
| `prompt.md` | `*.prompt.md` |
| `tools: search` | `tools: ['search']` |
| `handoff:` | `handoffs:` (plural) |
| `send: "false"` | `send: false` (boolean) |

---

## 🔍 Debugging Tips

1. **Instructions not applying?**
   - Check `applyTo` pattern
   - Verify settings enabled
   - Restart VS Code

2. **Prompt not showing?**
   - Check file location
   - Verify YAML syntax
   - Check `name` property

3. **Agent not in dropdown?**
   - Check file location
   - Verify frontmatter
   - Check for syntax errors

4. **Handoff not appearing?**
   - Verify `handoffs` is array
   - Check target agent exists
   - Match agent name exactly

---

## 📚 Resources

### Official Documentation

- [Customization Overview](https://code.visualstudio.com/docs/copilot/customization/overview)
- [Custom Instructions](https://code.visualstudio.com/docs/copilot/customization/custom-instructions)
- [Prompt Files](https://code.visualstudio.com/docs/copilot/customization/prompt-files)
- [Custom Agents](https://code.visualstudio.com/docs/copilot/customization/custom-agents)

### AI-Native Development

- [PROSE Framework](https://danielmeppiel.github.io/awesome-ai-native/)
- [APM CLI Documentation](https://github.com/danielmeppiel/awd-cli)
