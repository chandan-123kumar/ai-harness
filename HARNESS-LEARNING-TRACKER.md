# Building My Own Coding Agent

A learning checklist and build-in-public journal for a Claude Code–style terminal agent powered by an open model.

**Starting status:** Basic live inference verified by user-provided CLI output; model/tool/model round trip pending.  
**Working schedule:** Eight weeks at approximately 6–8 hours per week; adjust as needed.  
**First release goal:** Given a bug in a small repository, the agent finds relevant code, edits it, runs checks, and presents a diff with an accurate verification report.

## Project decisions

### Personal website and daily blog — In progress

- **Website repository:** https://github.com/chandan-123kumar/chandan-123kumar.github.io
- **Goal:** Add a blog to the personal website and keep a dated record of daily learning and implementation progress.
- **Started:** 2026-10-07.
- **Prepared locally:** Website source snapshot in `personal-website/`; first daily post integrated with the existing blog and homepage, a daily-post helper, and a reusable entry template. Review notes and an apply-ready patch are in `website-blog/`.
- **Verified:** Post rendering and index ordering, matching article links and dates, menu-toggle behavior, and daily-entry creation/duplicate protection.
- **Pending:** Visual browser review and publishing through the website's actual hosting workflow.
- **Repository state:** Source downloaded from GitHub commit `07839c07b27a57a3d586c99946de081611b41a80`. Changes are local and prepared for review; no remote push or deployment has been made.
- **Cadence:** Update after each work session. Drafts are the initial workflow; scheduled automatic publishing has not been configured.

- [x] Choose Python or TypeScript. Selected Python.
- [x] Phase 1 inference route: call an existing model through Hugging Face Inference Providers.
- [ ] Revisit local inference or dedicated hosting after the first working agent loop, if useful.
- [ ] Select a model and verify its license and tool-calling support.
- [ ] Set a per-run time, token, and spending limit where applicable.
- [ ] Choose a small practice repository with deterministic tests.

Model: `Qwen/Qwen3-Coder-Next` · API: `Hugging Face Inference Providers` · Backend provider: `novita` · Language: `Python` · Repository URL: `TBD`

## Learning and build checklist

### Week 1 — Connect the model

Learn: messages, context windows, tokens, tool schemas, and tool results.

**Phase 1 decision:** Use an available hosted model through Hugging Face Inference Providers. The CLI and tools run locally; model inference runs remotely. Select a currently available model/provider combination that supports tool calling and meets the project's license requirements.

- [x] Create a Hugging Face token with Inference Providers permission and store it locally as `HF_TOKEN`, outside source control.
- [x] Check account credits/billing and the selected provider's pricing before requests.
- [x] Choose an available model/provider and keep both configurable in `config.json`.
- [x] Use the Hugging Face inference client to make a basic chat request (user-provided successful CLI output).
- [x] Create a minimal CLI and configuration file (`connect.py`, `config.json`).
- [ ] Send a task to the selected model.
- [ ] Define one read-only tool with validated arguments.
- [ ] Execute a model-requested tool call and return its result.
- [ ] Log requests, responses, tool results, and timing without secrets.
- [ ] Record the model ID, backend provider, inference settings, and model revision if exposed.

**Done when:** A saved trace shows a complete model → tool → model cycle.

### Week 2 — Build the agent loop

Learn: state transitions, dispatch, termination, and tool errors.

- [ ] Implement list-files, read-file, and search-text tools.
- [ ] Restrict file access to the intended workspace.
- [ ] Add tool dispatch and a bounded execution loop.
- [ ] Return structured errors for invalid arguments or missing files.
- [ ] Distinguish completion, failure, cancellation, and exhausted limits.

**Done when:** The agent locates and explains a function without being given its path.

### Week 3 — Edit and verify code

Learn: patches, subprocesses, exit codes, timeouts, and execution isolation.

- [ ] Prepare a disposable execution environment with only the practice repository mounted.
- [ ] Implement patch application with useful failure messages.
- [ ] Add command execution with timeouts and bounded output.
- [ ] Capture stdout, stderr, and exit codes.
- [ ] Run a bug-fix task from a clean snapshot.
- [ ] Present the resulting diff and actual test results.

**Done when:** The agent fixes a seeded bug and the relevant tests pass.

### Week 4 — Measure a baseline

Learn: evaluation design, reproducibility, traces, and failure classification.

- [ ] Create ten small tasks with clear acceptance criteria.
- [ ] Include code search, single-file fixes, and a multi-file change.
- [ ] Keep evaluator checks outside the agent's editable workspace.
- [ ] Reset the repository before each run.
- [ ] Record success, tool errors, elapsed time, tokens, and cost where available.
- [ ] Classify failures as model, context, tool, or environment failures.

**Done when:** A reproducible baseline report exists, including failed tasks.

### Week 5 — Improve context handling

Learn: selective retrieval, output truncation, context budgets, and summaries.

- [ ] Read files on demand instead of loading the entire repository.
- [ ] Add output limits and a way to retrieve omitted sections.
- [ ] Load concise repository instructions from a defined location.
- [ ] Preserve the task, decisions, changed files, and pending checks during summarization.
- [ ] Evaluate a task in a repository larger than the model's context window.

**Done when:** The agent completes the task without relying on the whole repository fitting in context.

### Week 6 — Recover from failures

Learn: bounded retries, repeated-action detection, and execution policy.

- [ ] Handle malformed tool calls and patch conflicts.
- [ ] Test command timeouts and model request failures.
- [ ] Avoid blindly retrying actions that may already have changed state.
- [ ] Stop repeated failing actions with a clear explanation.
- [ ] Treat repository content as data rather than permission to change execution policy.
- [ ] Verify that file tools reject workspace escape attempts.

**Done when:** Failure scenarios end in a bounded recovery or an explicit, accurate stop reason.

### Week 7 — Make sessions usable

Learn: persistence, cancellation, streaming, and change review.

- [ ] Save session state and execution events.
- [ ] Resume a session without repeating completed mutations.
- [ ] Show tool activity and current run status.
- [ ] Support cancellation and clean process shutdown.
- [ ] Show changed files, the final diff, and verification results.

**Done when:** Restarting the CLI preserves enough state to continue a task correctly.

### Week 8 — Compare and release

Learn: controlled experiments, held-out evaluation, and tradeoffs.

- [ ] Reserve additional tasks that were not used to tune the harness.
- [ ] Compare two models using the same tasks and harness.
- [ ] Compare two harness configurations with the model held fixed.
- [ ] Repeat runs where needed to expose variability.
- [ ] Document success rates, runtime, token usage, and limitations.
- [ ] Write setup instructions and record a short demonstration.
- [ ] Publish a retrospective with evidence for any improvement claims.

**Done when:** Someone else can run the project and understand what it does reliably and where it fails.

## Next session

- [x] Finalize Phase 1 inference route: Hugging Face Inference Providers.
- [x] Finalize the language and select an available model/provider.
- [x] Create the CLI skeleton.
- [x] Connect the model.
- [ ] Complete one read-file tool round trip.
- [ ] Save a trace and write a short learning note.

**Defer until the baseline works:** Multi-agent orchestration, vector databases, fine-tuning, and a polished UI.

## Progress log

Update this after each working session. Leave unknown values blank rather than estimating results.

| Date | Milestone / change | Evidence: commit, trace, or demo | Result | Next step |
|---|---|---|---|---|
| 2026-10-05 | Created learning plan and checklist | This document | Implementation pending | Choose stack and model |
| 2026-10-05 | Selected Hugging Face Inference Providers for Phase 1 | Phase 1 decision above | Route selected; no API integration tested yet | Select model/provider and make first request |
| 2026-10-05 | Selected Qwen3-Coder-Next via Novita; created bounded single-request Python CLI | `connect.py`, `config.json`; HF live provider mapping | Existing HF login found; request failed on local DNS resolution before inference; token permission and billing unverified | Run `python3 connect.py` in a network-enabled terminal, then implement read-file round trip |

| 2026-10-05 | Verified basic Qwen inference through Hugging Face / Novita | User-provided CLI output in conversation | 1.42 seconds; 9 input + 12 output = 21 tokens; finish reason `stop`. Original prompt not supplied; exact instruction following not assessed. | Implement one read-file tool round trip and save a trace |

## Experiment scorecard

Record the task-set version, model/settings, harness commit, and number of repeated runs alongside each report. Report raw counts with percentages; a small task set is a learning signal, not a broad capability claim.

| Run | Model + settings | Harness commit | Task set / attempts | Verified passes | Tool errors | Median runtime | Tokens / cost |
|---|---|---|---|---|---|---|---|
| Baseline | TBD | TBD | TBD | Not measured | Not measured | Not measured | Not measured |

## LinkedIn publishing plan

**Cadence:** One kickoff post, then one update per completed milestone or meaningful experiment. If a week produces only a useful failure, share that learning accurately. Posts are drafts for manual review and publishing.

For each update, collect:

- [ ] One concrete thing built or tested.
- [ ] One screenshot, short demo, trace excerpt, or diff that supports the claim.
- [ ] One lesson or unexpected failure.
- [ ] Actual numbers, if measured, with the task count and conditions.
- [ ] The next experiment.
- [ ] Remove credentials, private code, and personal data from shared material.
- [ ] Replace all draft placeholders and verify every claim.
- [ ] Publish manually and paste the post URL into the log below.

| Update | Topic | Evidence to capture | Published URL |
|---|---|---|---|
| Kickoff | Why I am building my own coding agent | Learning roadmap | |
| 1 | First model–tool round trip | CLI output or trace | |
| 2 | An agent that finds code | Repository navigation demo | |
| 3 | First verified bug fix | Diff and test output | |
| 4 | How often does it actually work? | Baseline results and failures | |
| 5 | Handling a repository that does not fit in context | Retrieval trace and comparison | |
| 6 | What happens when a tool fails? | Failure and recovery example | |
| 7 | Resume, cancel, and review | Session demo | |
| 8 | What improved the agent? | Controlled comparison and retrospective | |

### Kickoff post — ready to review

I'm starting a learning project: building my own Claude Code–style terminal coding agent using an open model.

My first target is small and concrete: give it a bug in a repository, let it inspect the code, make a change, run tests, and show me the diff.

I'll use the project to learn harness engineering—the tools, execution loop, context management, and feedback that make a model useful as an agent.

The plan is to build in stages:

• Connect a model and complete a tool call.
• Add code search, editing, and test execution.
• Measure performance on a fixed set of tasks.
• Improve context handling and failure recovery.
• Add resumable sessions and compare results.

I'm at the planning stage today. I'll share working demos, failed experiments, and measured progress as I go.

For Phase 1, I'll call an available model through Hugging Face Inference Providers and run the harness and tools locally.

First milestone: one complete model → tool → model loop.

#BuildInPublic #AIEngineering #CodingAgents

### Weekly progress post — reusable draft

Building my own coding agent — update [number].

This week I built [specific capability].

The agent can now [observable behavior]. I tested it on [task and conditions], and the result was [actual result].

The most useful lesson: [what the evidence taught you].

One thing that still fails: [specific limitation and example].

Next, I'll test [one focused change].

[Demo or repository link]

#BuildInPublic #AIEngineering #CodingAgents

### Experiment post — reusable draft

Does [specific harness change] improve my coding agent?

I compared [configuration A] with [configuration B], keeping [model, task set, and other controls] fixed.

Across [number] tasks and [number] attempts:

• Before: [verified passes / attempts], [runtime], [tokens or cost].
• After: [verified passes / attempts], [runtime], [tokens or cost].

What changed: [implementation detail that explains the experiment].

What I can conclude: [narrow conclusion supported by the results].

What I can't conclude yet: [sample-size limitation, variability, or untested scenario].

Next experiment: [specific follow-up].

[Evidence link]

#HarnessEngineering #AIEngineering #BuildInPublic

## Reference material

- [Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers/en/index) — access available hosted models through a Hugging Face token.
- [Hugging Face chat completion](https://huggingface.co/docs/inference-providers/tasks/chat-completion) — authentication and tool-call request/response fields; support depends on the model and provider.
- [mini-SWE-agent control flow](https://mini-swe-agent.com/latest/advanced/control_flow/) — study a compact model/tool execution loop.
- [Ollama tool calling](https://github.com/ollama/ollama/blob/main/docs/capabilities/tool-calling.mdx) — reference for local tool-call integration.
- [Qwen Agent quickstart](https://qwenlm.github.io/Qwen-Agent/en/guide/get_started/quickstart/) — model access and tool-parser setup considerations.

Choose the exact model after checking hardware fit, tool support, and license. Open weights and fully open-source models are not interchangeable terms.
