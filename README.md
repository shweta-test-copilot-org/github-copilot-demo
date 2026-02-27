# 🚀 AI Native Development Lab: Scaling GitHub Copilot in the Enterprise

> **From Vibe Coding to AI Native Development**: Learn to build structured AI workflows with VS Code and GitHub Copilot using the [PROSE Framework](https://danielmeppiel.github.io/awesome-ai-native/docs/concepts/).

[![VS Code](https://img.shields.io/badge/VS%20Code-1.108+-blue?logo=visualstudiocode)](https://code.visualstudio.com/)
[![GitHub Copilot](https://img.shields.io/badge/GitHub%20Copilot-Required-green?logo=github)](https://github.com/features/copilot)
[![Duration](https://img.shields.io/badge/Duration-90%20min-orange)]()

---

## 🤔 The Problem

You've seen Copilot work magic on small projects. But when you tried it on your enterprise codebase, something felt off:

- Copilot generated code that **ignored your team's patterns**
- It used libraries **you're not allowed to use** (security, compliance)
- The output was technically correct but **wrong for your context**
- Every developer got **different results** for the same task

**This is the "Vibe Coding Cliff"** — ad-hoc prompting works until it doesn't. Enterprise brownfield codebases have constraints, legacy patterns, and tribal knowledge that Copilot can't learn from a single prompt.

---

## 🎯 What You'll Build

By the end of this lab, you'll have a **working multi-agent pipeline** that generates documentation or tests following YOUR team's standards.

> 📚 **Theory**: This lab applies the [**PROSE Framework**](https://danielmeppiel.github.io/awesome-ai-native/docs/concepts/) for AI Native Development.

| Exercise | What You Create | PROSE Element |
|----------|-----------------|---------------|
| **1** | `.instructions.md` — Scoped context with `applyTo` | **E**ngineering (Context) |
| **2** | `.prompt.md` — Structured reusable tasks | **P**rompts |
| **3** | `.agent.md` pair — Analyzer hands off to Generator | **O**rchestration |
| **Scaling** | Skills demo — Agent discovers capabilities | **S**kills |

**→ The result?** **R**eliability — consistent, repeatable output across your team.

> *"Reliability isn't a technique you apply—it's the outcome of applying all other PROSE components systematically."*

---

## ⏱️ Session Flow (90 minutes)

| Section | Focus | Duration | Format |
|---------|-------|----------|--------|
| **Setup** | Verify environment, choose track | 5 min | Individual |
| **Exercise 1** | Create modular instructions | 15 min | Hands-on |
| **Exercise 2** | Build reusable prompts | 15 min | Hands-on |
| **Exercise 3** | Design agents with handoffs | 20 min | Hands-on |
| **Scaling** | Skills + Copilot CLI hands-on | 20 min | Demo + hands-on |
| **Wrap-Up** | Q&A + resources | 10 min | Discussion |

> 📖 Docs track and 🧪 Testing track run the **same exercises with different content**, then everyone converges for the Scaling section.

---

## ⚙️ Setup (5 min)

### 1. Verify Your Environment

- [ ] VS Code 1.108+ with GitHub Copilot extension
- [ ] GitHub Copilot Chat working (test: open chat, type "hello")
- [ ] This repo cloned: `git clone https://github.com/DevExpGbb/ai-native-dev-lab.git`

### 2. Choose Your Track

Pick **ONE** track based on your interest — both teach the same concepts with different content:

| Track | Best For | You'll Build |
|-------|----------|--------------|
| [📖 **Docs**](#-documentation-track-exercises-1-3) | Documenting legacy apps | Instructions → `/generate-docs` → Doc Analyzer + Writer |
| [🧪 **Tests**](#-testing-track-exercises-1-3) | Improving test coverage | Instructions → `/generate-tests` → Test Analyzer + Generator |

> After completing exercises 1-3 in your track, everyone converges for the [Scaling](#-scaling-across-the-enterprise-20-min) section.

### 3. Open Your Target Code

Navigate to the brownfield sample: [`sample-projects/contoso-orders-python/`](sample-projects/contoso-orders-python/)

> 🏗️ This is a realistic FastAPI app with legacy auth, "DO NOT MODIFY" constraints, and intentional test gaps

---

# 🛤️ Choose Your Track Below

> **Important:** Complete exercises 1-3 in your chosen track, then **everyone** proceeds to [Scaling Across the Enterprise](#-scaling-across-the-enterprise-20-min).

---

## 📖 Documentation Track (Exercises 1-3)

### Exercise 1: Modular Instructions (15 min)

#### 🔍 Discover the Problem

Before creating anything, let's see why instructions matter:

1. **Open** [`sample-projects/contoso-orders-python/src/services/order_service.py`](sample-projects/contoso-orders-python/src/services/order_service.py)

2. **Ask Copilot** (without any instructions):
   > "Add a docstring to the `create_order` method"

3. **Observe what happens:**
   - Does it use Google-style or NumPy-style docstrings?
   - Does it match the existing style in the file?
   - Does it include the `Raises` section for exceptions?

💡 **This inconsistency is the problem.** Every developer gets different results.

---

#### 🛠️ Build Your Solution

**Your task:** Create an instruction file that enforces YOUR documentation standards.

1. **Create the file:** `.github/instructions/documentation-standards.instructions.md`

2. **Start with this skeleton** (don't copy-paste the full solution!):

```yaml
---
applyTo: "**/*.py"
---
# Documentation Standards

## Docstring Format
<!-- What style? Google, NumPy, reStructuredText? -->

## Required Sections
<!-- What must every docstring include? Args? Returns? Raises? -->

## Examples
<!-- Should docstrings include usage examples? When? -->
```

1. **Fill in YOUR standards** based on what you observed in the codebase:
   - Look at existing docstrings in the project
   - What patterns should be consistent?
   - What's missing that should always be there?

---

#### ✅ Validate Your Work

1. **Reopen** `order_service.py`
2. **Ask the same question:** "Add a docstring to the `create_order` method"
3. **Compare:** Does Copilot now follow YOUR standards?

---

#### 📊 Compare with Golden Example

When you're done, compare your solution with our reference implementation:
→ [`golden-examples/documentation-track/.github/instructions/documentation-standards.instructions.md`](golden-examples/documentation-track/.github/instructions/documentation-standards.instructions.md)

**Reflection questions:**

- What did you include that we didn't?
- What did we include that you missed?
- Which version would work better for YOUR team?

---

#### 🏆 Challenge (if time permits)

Create a **second** instruction file for a different file type:

- Markdown style guide for `**/*.md` files
- API endpoint patterns for `**/api/**/*.py` files

---

### Exercise 2: Reusable Prompts (15 min)

#### 🔍 Discover the Problem

You've created great standards. But what if you want to generate docs for a whole file at once?

1. **Try asking Copilot:** "Generate documentation for all functions in this file"
2. **Notice:** You have to explain your requirements every time. That's tedious.

💡 **Prompt files solve this** — they're reusable commands you invoke with `/`.

---

#### 🛠️ Build Your Solution

**Your task:** Create a prompt file that generates documentation on demand.

1. **Create the file:** `.github/prompts/generate-docs.prompt.md`

2. **Start with the template:** [`starter-templates/prompt-template.prompt.md`](starter-templates/prompt-template.prompt.md)

3. **Customize it for documentation generation:**
   - What `tools` does the agent need? (`search`, `createFile`, `editFile`)
   - How should it reference your instructions file?
   - What variables will you use? (`${file}`, `${selection}`)

4. **Key insight:** Use `[text](path)` syntax to reference your instructions:

   ```markdown
   Follow the standards in [documentation-standards](../instructions/documentation-standards.instructions.md)
   ```

---

#### ✅ Validate Your Work

1. **Open** any Python file in the sample project
2. **Type in Copilot Chat:** `/generate-docs`
3. **Verify:** Does the command appear? Does it use your prompt?

---

#### 📊 Compare with Golden Example

→ [`golden-examples/documentation-track/.github/prompts/generate-docs.prompt.md`](golden-examples/documentation-track/.github/prompts/generate-docs.prompt.md)

---

### Exercise 3: Agents with Handoffs (20 min)

#### 🔍 Discover the Problem

Prompt files work great, but complex tasks need separation of concerns:

- **Analysis** should be thorough (read-only, no side effects)
- **Generation** should be focused (create/edit files)

Combining both in one prompt leads to:

- Analysis that's rushed to get to generation
- Generation that missed important context

💡 **Multi-agent handoffs solve this** — specialized agents that collaborate.

---

#### 🛠️ Build Your Solution

**Your task:** Create two agents that work together.

##### Agent 1: Doc Analyzer (read-only)

1. **Create:** `.github/agents/doc-analyzer.agent.md`

2. **Start with template:** [`starter-templates/agent-template.agent.md`](starter-templates/agent-template.agent.md)

3. **Customize for analysis:**
   - Give it read-only tools: `search`, `usages`, `fetch`
   - Define its persona: "You analyze code to identify documentation needs"
   - Add a **handoff** to the writer agent (this is the key!)

**Handoff syntax** (add to frontmatter):

```yaml
handoffs:
  - label: "📝 Write Documentation"
    agent: doc-writer
    prompt: "Based on my analysis, generate documentation."
    send: false
```

##### Agent 2: Doc Writer (creates files)

1. **Create:** `.github/agents/doc-writer.agent.md`

2. **Give it editing tools:** `createFile`, `editFile`, `search`

3. **Define its persona:** "You create documentation based on analysis"

4. **Reference your instruction file** in the body

---

#### ✅ Validate Your Work

1. **Open Copilot Chat**
2. **Select "Doc Analyzer"** from the Chat mode dropdown (click the mode selector at the top)
3. **Ask it to analyze** a file
4. **Look for the handoff button** — it should appear after analysis!
5. **Click the button** to hand off to Doc Writer

---

#### 📊 Compare with Golden Examples

- Analyzer: [`golden-examples/documentation-track/.github/agents/doc-analyzer.agent.md`](golden-examples/documentation-track/.github/agents/doc-analyzer.agent.md)
- Writer: [`golden-examples/documentation-track/.github/agents/doc-writer.agent.md`](golden-examples/documentation-track/.github/agents/doc-writer.agent.md)

---

#### 🏆 Challenge (if time permits)

**Option A: Add a third agent**

Add a "Doc Reviewer" that reviews generated documentation, suggests improvements, and has a handoff back to Doc Writer for revisions.

**Option B: Parallel subagents (Advanced)**

Modify your Analyzer to:

1. Break the project into **independent documentation tasks** (one per module)
2. Output a task list with dependencies
3. Have the Generator use `runSubagent` tool to spawn parallel workers per critical path

This demonstrates the PROSE Orchestration principle: *decompose big tasks into smaller, parallelizable units*.

> 💡 **Going Further**: This same pattern works with the **GitHub Coding Agent** in the cloud. Using the [GitHub MCP Server](https://github.com/github/github-mcp-server), your Generator can create GitHub Issues (`issue_write`) and assign Copilot Coding Agents on the cloud to work them asynchronously (`assign_copilot_to_issue`). *Watch the facilitator demo this in the Scaling section!*

---

> ✅ **Completed Exercises 1-3?** Continue to [Scaling Across the Enterprise](#-scaling-across-the-enterprise-20-min)

---

## 🧪 Testing Track (Exercises 1-3)

### Exercise 1: Modular Instructions (15 min)

#### 🔍 Discover the Problem

Before creating anything, let's see why instructions matter:

1. **Open** [`sample-projects/contoso-orders-python/src/services/order_service.py`](sample-projects/contoso-orders-python/src/services/order_service.py)

2. **Ask Copilot** (without any instructions):
   > "Write a unit test for the `create_order` method"

3. **Observe what happens:**
   - Does it use `pytest` or `unittest`?
   - Does it follow Arrange-Act-Assert pattern?
   - Does it mock the `LegacyAuthProvider` (which you MUST use)?
   - Does it use `structlog` for logging assertions?

💡 **This inconsistency is the problem.** Every developer gets different test patterns.

---

#### 🛠️ Build Your Solution

**Your task:** Create an instruction file that enforces YOUR testing standards.

1. **Create the file:** `.github/instructions/testing-standards.instructions.md`

2. **Start with this skeleton** (don't copy-paste the full solution!):

```yaml
---
applyTo: "**/test_*.py"
---
# Testing Standards

## Framework
<!-- pytest? unittest? What's the project using? -->

## Test Structure
<!-- What pattern? AAA? Given-When-Then? -->

## Naming Convention
<!-- How should tests be named? -->

## Mocking Rules
<!-- What MUST be mocked? What auth provider? -->
```

1. **Fill in YOUR standards** by analyzing the existing tests:
   - Look at [`sample-projects/contoso-orders-python/tests/`](sample-projects/contoso-orders-python/tests/)
   - What patterns are already established?
   - What constraints does the legacy auth impose?

---

#### ✅ Validate Your Work

1. **Reopen** `order_service.py`
2. **Ask the same question:** "Write a unit test for the `create_order` method"
3. **Compare:** Does Copilot now follow YOUR standards?

---

#### 📊 Compare with Golden Example

When you're done, compare your solution with our reference:
→ [`golden-examples/testing-track/.github/instructions/testing-standards.instructions.md`](golden-examples/testing-track/.github/instructions/testing-standards.instructions.md)

**Reflection questions:**

- Did you capture the `LegacyAuthProvider` constraint?
- How specific were your mocking rules?
- What edge cases did you think to include?

---

#### 🏆 Challenge (if time permits)

Create a **second** instruction file for integration tests:

- Different patterns for `**/integration_test_*.py`
- Database setup/teardown requirements

---

### Exercise 2: Reusable Prompts (15 min)

#### 🔍 Discover the Problem

You've created great testing standards. But generating tests one-by-one is tedious.

1. **Try asking Copilot:** "Generate tests for all untested methods in this file"
2. **Notice:** You have to explain the context every time. That's inefficient.

💡 **Prompt files solve this** — they're reusable commands you invoke with `/`.

---

#### 🛠️ Build Your Solution

**Your task:** Create a prompt file that generates tests on demand.

1. **Create the file:** `.github/prompts/generate-tests.prompt.md`

2. **Start with the template:** [`starter-templates/prompt-template.prompt.md`](starter-templates/prompt-template.prompt.md)

3. **Customize it for test generation:**
   - What `tools` does the agent need? (`search`, `createFile`, `editFile`)
   - How should it reference your instruction file?
   - What should it analyze: `${file}` or `${selection}`?

4. **Key insight:** Reference your instruction file:

   ```markdown
   Follow the standards in [testing-standards](../instructions/testing-standards.instructions.md)
   ```

---

#### ✅ Validate Your Work

1. **Open** any Python file in the sample project
2. **Type in Copilot Chat:** `/generate-tests`
3. **Verify:** Does the command appear? Does it use your testing standards?

---

#### 📊 Compare with Golden Example

→ [`golden-examples/testing-track/.github/prompts/generate-tests.prompt.md`](golden-examples/testing-track/.github/prompts/generate-tests.prompt.md)

---

### Exercise 3: Agents with Handoffs (20 min)

#### 🔍 Discover the Problem

Good tests require good analysis first:

- **What needs testing?** (public methods, edge cases, error paths)
- **What needs mocking?** (external services, legacy auth)
- **What's already covered?** (avoid duplicate tests)

A single prompt tries to do everything at once. That leads to:

- Shallow analysis
- Missed edge cases
- Redundant tests

💡 **Multi-agent handoffs solve this** — an Analyzer thinks, a Generator acts.

---

#### 🛠️ Build Your Solution

**Your task:** Create two agents that work together.

##### Agent 1: Test Analyzer (read-only)

1. **Create:** `.github/agents/test-analyzer.agent.md`

2. **Start with template:** [`starter-templates/agent-template.agent.md`](starter-templates/agent-template.agent.md)

3. **Customize for analysis:**
   - Read-only tools: `search`, `usages`, `fetch`
   - Persona: "You analyze code to identify what needs testing"
   - Output: List of test cases with edge cases and mocking requirements

4. **Add the handoff** (in frontmatter):

```yaml
handoffs:
  - label: "🧪 Generate Tests"
    agent: test-generator
    prompt: "Based on my analysis, generate comprehensive tests."
    send: false
```

##### Agent 2: Test Generator (creates files)

1. **Create:** `.github/agents/test-generator.agent.md`

2. **Editing tools:** `createFile`, `editFile`, `search`

3. **Persona:** "You implement tests based on the analysis provided"

4. **Reference your testing instruction file**

---

#### ✅ Validate Your Work

1. **Open Copilot Chat**
2. **Select "Test Analyzer"** from the Chat mode dropdown (click the mode selector at the top)
3. **Analyze a file** — look for thorough output (edge cases, mocking needs)
4. **Click the handoff button** when it appears
5. **Verify** the Test Generator creates proper test files

---

#### 📊 Compare with Golden Examples

- Analyzer: [`golden-examples/testing-track/.github/agents/test-analyzer.agent.md`](golden-examples/testing-track/.github/agents/test-analyzer.agent.md)
- Generator: [`golden-examples/testing-track/.github/agents/test-generator.agent.md`](golden-examples/testing-track/.github/agents/test-generator.agent.md)

---

#### 🏆 Challenge (if time permits)

**Option A: Add a third agent**

Add a "Test Runner" that runs generated tests, reports failures, and has a handoff to Test Generator for fixes.

**Option B: Parallel subagents (Advanced)**

Modify your Analyzer to:

1. Break the project into **independent test tasks** (one per untested module)
2. Output a task dependency tree
3. Have the Generator use `runSubagent` tool to spawn parallel test writers per critical path

This demonstrates the PROSE Orchestration principle: *decompose big tasks into smaller, parallelizable units*.

> 💡 **Going Further**: This same pattern works with the **GitHub Coding Agent** in the cloud. Using the [GitHub MCP Server](https://github.com/github/github-mcp-server), your Generator can create GitHub Issues (`issue_write`) and assign GitHub Copilot Coding Agents on the cloud to work them asynchronously (`assign_copilot_to_issue`). *Watch the facilitator demo this in the Scaling section!*

---

> ✅ **Completed Exercises 1-3?** Continue below!

---

# ⚡ Scaling Across the Enterprise (20 min)

> **Everyone converges here** — regardless of which track you chose.

*You've built modular VSCode primitives. Now let's learn about **Skills** — a different packaging format for sharing capabilities across teams and tools.*

---

## Two Packaging Models (3 min — facilitator explains)

| VSCode Primitives (Exercises 1-3) | Agent Skills |
|-----------------------------------|--------------|
| `.instructions.md`, `.prompt.md`, `.agent.md` | `SKILL.md` + reference files |
| Modular, separate files | Consolidated in one file |
| Invoked explicitly (`/command`, menu selection) | **Discovered** by agent based on intent |
| Lives in `.github/` | Lives in `.copilot/skills/` or installed globally |

**Key insight:** Skills aren't containers for VSCode primitives. The `SKILL.md` **is** the capability — it contains the guidance inline that agents discover and follow.

### Skill Structure

```
pdf-skill/
├── SKILL.md                    # Metadata + instructions (all inline)
├── reference.md                # Optional: detailed docs the skill references
├── forms.md                    # Optional: specialized guidance
└── scripts/                    # Optional: utility scripts
    ├── fill_fillable_fields.py
    └── convert_pdf_to_images.py
```

> 📚 **Standard**: [agentskills.io](https://agentskills.io) — the emerging specification for agent capabilities

---

## Exercise 4: Install a Skill with Copilot CLI (8 min)

Let's install the **skill-creator** skill — it will help you package your work from Exercises 1-3 into a shareable skill.

### Step 0: Launch Copilot CLI

In your terminal, run:

```bash
copilot
```

> **Codespaces**: If prompted "Would you like to install the GitHub Copilot CLI extension?", press **Y**.

This opens the Copilot CLI interactive interface. All following commands run **inside this TUI**.

### Step 1: Add the Anthropic Skills Marketplace

In the Copilot CLI, type:

```
/plugin marketplace add anthropics/skills
```

### Step 2: Install the Example Skills Plugin

```
/plugin install example-skills@anthropic-agent-skills
```

Then type `/exit` to leave the Copilot CLI.

### Step 3: Find Where It Landed

Back in your regular terminal:

```bash
ls ~/.copilot/installed-plugins/anthropic-agent-skills/example-skills/skills/
```

You should see folders including `skill-creator/`.

> 💡 **Notice:** The CLI installed skills into `~/.copilot/installed-plugins/...`. VSCode's default skill paths are `~/.copilot/skills`, `.github/skills`, etc. — so we need to add this new location.

### Step 4: Bridge CLI to VSCode

Add this to your `.vscode/settings.json`:

```json
"chat.agentSkillsLocations": {
   "~/.copilot/installed-plugins/anthropic-agent-skills/example-skills/skills": true
}
```

> ⚠️ **This is the key step.** You're telling VSCode where to discover CLI-installed skills - more precisely, the example-skills plugin you just installed.

### Step 5: Reload VSCode

Press `Cmd+Shift+P` → **Developer: Reload Window**

### ✅ Validate

Open a **new** Copilot Chat window and ask:

> "What skills do you have available?"

The skill-creator should appear.

---

## Exercise 5: Create Your Own Skill (6 min)

Now use skill-creator to package YOUR work from Exercises 1-3 into a reusable skill.

### Your Task

In Copilot Chat, ask:

**If you followed the 📖 Documentation track:**
> "Help me create a skill that packages my documentation workflow. I have a documentation-standards.instructions.md, a generate-docs.prompt.md, and doc-analyzer + doc-writer agents in .github/. Bundle these patterns into a skill that other teams can use."

**If you followed the 🧪 Testing track:**
> "Help me create a skill that packages my testing workflow. I have a testing-standards.instructions.md, a generate-tests.prompt.md, and test-analyzer + test-generator agents in .github/. Bundle these patterns into a skill that other teams can use."

### What the Skill-Creator Does

1. Analyzes your `.github/instructions/`, `.github/prompts/`, `.github/agents/`
2. Creates `SKILL.md` with proper frontmatter (name, description, globs)
3. Consolidates the guidance **inline** in the SKILL.md body
4. Places it in a skill folder in your repository

### ✅ Validate

After creation, start a **new** chat and ask:

> "Generate documentation for order_service.py" (or "Generate tests...")

The agent should **discover your skill** based on your intent — no explicit invocation needed.

---

## The Big Picture (3 min)

### What You Learned Today

| Primitive | How It's Used | Best For |
|-----------|---------------|----------|
| `.instructions.md` | Auto-applied by `applyTo` glob | Team standards (always on) |
| `.prompt.md` | Invoked with `/command` | Reusable tasks |
| `.agent.md` | Selected from Chat dropdown | Specialized personas |
| `SKILL.md` | **Discovered** by intent | Shareable capabilities |

### The Pioneer/Consumer Model

| Role | % | What They Do |
|------|---|--------------|
| **Pioneers** | 5% | Create skills from proven patterns |
| **Validators** | 20% | Test in real workflows |
| **Consumers** | 75% | Install and benefit — no authoring needed |

> *"Pioneers capture patterns once, everyone benefits forever."*

---

## 🎉 You Did It

Remember the **Vibe Coding Cliff** from the start? Copilot generating inconsistent code, ignoring team patterns, using forbidden libraries?

**That's solved now.**

You built a system where:

- **Instructions** enforce standards automatically — no one has to remember
- **Prompts** capture complex workflows — reusable with `/`
- **Agents** separate concerns and orchestrate work — one specialized agent hands off to another
- **Skills** package everything — shareable across your organization and automatically picked by GitHub Copilot when it makes sense

This isn't just better prompting. It's **AI Native Development** — treating AI guidance as engineered artifacts with the same rigor you apply to code.

### What's Next?

| If you want to... | Then... |
|-------------------|---------|
| Go deeper on theory | Read the [PROSE Framework](https://danielmeppiel.github.io/awesome-ai-native/docs/concepts/) |
| Share with your team | Create a skill from your work today |
| Scale across enterprise | Establish a skills marketplace for your org |
| Keep experimenting | Try the Challenge sections you skipped |

**The gap between "Copilot demo magic" and "enterprise-ready AI" is no longer a mystery. You just bridged it.**

---

## 🛟 Troubleshooting

| Issue | Solution |
|-------|----------|
| `copilot` command not found | In Codespaces: should auto-prompt to install. Otherwise: `gh extension install github/gh-copilot` |
| Marketplace add fails | Check: `gh auth status` — ensure you're authenticated |
| VSCode doesn't see skills | Verify path in settings matches actual folder structure |
| Still not working | Open a NEW chat window after reload |
| Skill-creator not helpful | Manual fallback: see [`golden-examples/skills-demo/`](golden-examples/skills-demo/) |

---

## 📁 What's in This Repository

| Folder | Purpose | When to Use |
|--------|---------|-------------|
| [`sample-projects/`](sample-projects/) | Brownfield code to practice on | Exercises 1-3 |
| [`golden-examples/`](golden-examples/) | Complete reference implementations | After each exercise to compare |
| [`starter-templates/`](starter-templates/) | Minimal scaffolds to start from | When building your own |
| [`.github/`](.github/) | Where YOU create your files | During exercises |

---

## 🔧 Quick Reference

### Files You'll Create

| File | Location | Purpose |
|------|----------|---------|
| Instructions | `.github/instructions/*.instructions.md` | Team standards that auto-apply |
| Prompts | `.github/prompts/*.prompt.md` | Reusable `/commands` |
| Agents | `.github/agents/*.agent.md` | Specialized AI personas |

### Key Frontmatter

**Instructions:**

```yaml
---
applyTo: "**/*.py"    # Glob pattern for auto-apply
---
```

**Prompts:**

```yaml
---
name: my-command
description: What it does
tools: ['search', 'editFile', 'createFile']
---
```

**Agents:**

```yaml
---
name: My Agent
description: What it does
tools: ['search', 'usages', 'runSubagent']
handoffs:
  - label: "Next Step"
    agent: other-agent
---
```

### Available Tools

| Tool | Purpose |
|------|---------|
| `search` | Search codebase |
| `usages` | Find references |
| `editFile` | Modify existing files |
| `createFile` | Create new files |
| `runSubagent` | Spawn parallel subagent for independent task |
| `fetch` | Fetch URLs |

### Variables for Prompts

| Variable | Description |
|----------|-------------|
| `${file}` | Current file path |
| `${selection}` | Selected text |
| `${input:name}` | User input prompt |

→ Full reference: [`cheatsheet.md`](cheatsheet.md)

---

## ✅ Success Criteria

By the end of the lab, you should have:

| Deliverable | How to Verify |
|-------------|---------------|
| 1+ Instruction files | Open matching file → Copilot follows your standards |
| 1 Prompt file | Type `/yourcommand` → it appears and works |
| 2 Agent files with handoff | Select agent from dropdown → handoff button appears |
| skill-creator installed | `ls ~/.copilot/installed-plugins/.../skill-creator/` shows SKILL.md |
| VSCode configured | `.vscode/settings.json` has `chat.agentSkillsLocations` with CLI path |
| Your skill created | `.copilot/skills/your-skill/SKILL.md` exists |

---

## 📖 Resources

| Topic | Link |
|-------|------|
| VS Code Customization | [code.visualstudio.com/docs/copilot/customization](https://code.visualstudio.com/docs/copilot/customization/overview) |
| AI-Native Development Guide | [danielmeppiel.github.io/awesome-ai-native](https://danielmeppiel.github.io/awesome-ai-native/) |
| PROSE Framework Concepts | [Awesome AI-Native: Concepts](https://danielmeppiel.github.io/awesome-ai-native/docs/concepts/) |

---

## 🙏 Acknowledgments

- VS Code and GitHub Copilot teams
- The AI-native development community

---

**Happy AI Native Development! 🎉**
