# Outline: AI Agents Knowledge Base (draft)

## A. Three lenses for agent types
1. Decision logic: simple reflex, model-based reflex, goal-based, utility-based, learning, hierarchical, multi-agent.
2. Job: conversational, workflow or task, voice, knowledge or RAG, vision or multimodal, research, coding, computer-use or browser, personal assistant, vertical or industry, data analysis, security monitoring, commerce.
3. Architecture: single LLM call, prompt chain, router, parallel, tool-calling loop, plan-and-execute, orchestrator and workers, evaluator loop, human-in-the-loop, swarm or peer-to-peer.

Rule of thumb to verify: start with the simplest pattern that works; add autonomy only when a fixed workflow cannot do the job.

## B. Anatomy of an agent
Model, instructions, tools, memory, knowledge (retrieval), planning, guardrails, observability, evaluation.

## C. Concept categories
foundations, reasoning, tools_and_actions, memory_and_knowledge, orchestration, protocols, safety_and_security, evaluation_and_ops, models, interfaces, business.

## D. How concepts connect (flow to verify)
Trigger -> context assembly (instructions, memory, retrieved documents) -> model reasoning -> tool call (via APIs or protocols such as MCP) -> result back to model -> loop until goal met, guardrail stops it, or a human approves -> logging, tracing and evals.
Multi-agent: orchestrator hands sub-tasks to specialists; inter-agent communication via protocols such as A2A or shared context.

## E. Learning paths
Foundations, Builder, Architect, Security and Governance, Team Lead.

## F. 2026 themes to research (do not treat as facts yet)
- Multi-agent orchestration moving from pilots to coordinated, supervised systems.
- Coding agents as collaborators across engineering and non-engineering roles.
- MCP and A2A as interoperability standards; debate about token overhead versus governance benefits.
- Governance: approval gates, permission scopes, audit logs.
- Verifiability as the limit for unattended agents.
- Forecasts (for example enterprise adoption by end of 2026) must be traced to a primary source, dated, and labeled as forecasts.

## G. Risk themes
Prompt injection (direct and indirect), data exfiltration, excessive permissions, runaway cost, hallucination, unsafe actions, privacy, legal and compliance, supply-chain risk in third-party tools.

## H. Evaluation themes
Task success, tool-use accuracy, groundedness and citation quality, safety tests, latency and cost, regression suites, LLM-as-judge limits, human review, benchmarks.
