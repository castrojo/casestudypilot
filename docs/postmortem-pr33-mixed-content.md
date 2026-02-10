# Postmortem: PR #33 Mixed Content (Airbnb + Niantic)

## Date
2026-02-10

## Summary
PR #33 (Airbnb case study) incorrectly contained files from both Airbnb AND Niantic case studies, violating the atomic commit principle.

## Root Cause

The case-study-agent workflow did not explicitly instruct to checkout main branch before starting work. This led to:

1. Niantic case study created on branch `case-study-niantic-NbfyR_tNMXY` at 17:24
2. Agent immediately started Airbnb case study **without returning to main**
3. Airbnb branch created from Niantic branch, inheriting Niantic's commit
4. Result: PR #33 contained files for both case studies

## Fix

Added git branch validation to Step 0 (Pre-flight Validation):
- Verify agent is on main branch before starting
- Ensure working directory is clean
- Check sync status with origin/main

Updated Step 11 (Create Branch) to explicitly checkout main before branching.

## Prevention

All future case study generation must:
1. Start from clean main branch
2. Verify branch state in pre-flight checks
3. Never branch from feature branches

Related PRs: #32, #33
