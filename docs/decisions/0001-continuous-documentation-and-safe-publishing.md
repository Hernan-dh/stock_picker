# Continuous documentation and safe publishing

Status: accepted

## Context

CrewAI projects generate outputs and can change quickly. Documentation, verification, and commit metadata need a repeatable workflow that does not expose credentials or publish generated artifacts.

## Decision

Keep architecture, operations, ADRs, deterministic changelog generation, centralized verification, a repository-managed pre-commit hook, CI verification, and a human-confirmed publishing command in each repository.

## Consequences

Durable changes include their documentation, local and CI checks share one implementation, and publication remains reviewable. Contributors must enable the hook per clone and maintain provider credentials locally.
