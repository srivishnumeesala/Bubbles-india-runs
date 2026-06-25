---
name: phase-gate-checker
description: Validates that test suites pass before proceeding to subsequent project phases.
---
# Phase Gate Checker Skill

## Instructions
1. Before declaring any phase complete or moving to the next agent, run all tests corresponding to the modified modules using:
   `pytest tests/ -v` (or the specific test file paths).
2. Format and attach the full terminal output of the test run as a Verification Artifact.
3. If any test fails, STOP implementation, debug the failure, rerun the tests, and verify success before proceeding.
