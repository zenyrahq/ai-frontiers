# Git Conventions

> Read this file when: Creating branches, writing commits, or managing PRs

---

## 🔴 CRITICAL: No Direct Commits to Main

**Direct commits to `main` branch are STRICTLY FORBIDDEN!**

```bash
# ❌ NEVER DO THIS
git checkout main
git commit -m "feat: something"
git push origin main

# ❌ NEVER DO THIS
git push origin main:main  # from any branch
```

**Why?**
- Bypasses CodeRabbit review
- No peer review
- Risk of broken production
- Violates project workflow

**Correct approach:**
```bash
# ✅ ALWAYS create a branch and PR
git checkout -b feature/xxx
git commit -m "feat: something"
git push -u origin feature/xxx
gh pr create --title "feat: something" --body "..."
```

---

## Branch Naming

```
feature/xxx      # New feature
fix/xxx          # Bug fix
hotfix/xxx       # P0 urgent fix (from main)
refactor/xxx     # Refactoring
docs/xxx         # Documentation only
test/xxx         # Tests only
chore/xxx        # Build/tools/config
```

**Examples**:
```
feature/redis-cache-layer
fix/search-500-error
hotfix/security-vulnerability
refactor/database-service
```

---

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| docs | Documentation |
| style | Code format (no logic change) |
| refactor | Refactoring |
| test | Adding/updating tests |
| chore | Build, tools, dependencies |
| perf | Performance improvement |
| ci | CI/CD changes |

### Examples

```bash
# Feature
feat(api): add Redis cache layer for content queries

# Bug fix
fix(search): resolve 500 error on empty query

# Breaking change
feat(api)!: change response format for /v1/contents

BREAKING CHANGE: Response now uses 'items' instead of 'data'
```

---

## Branch Strategy

```
main (production)
  │
  └── develop (integration)
        │
        ├── feature/xxx
        ├── feature/yyy
        └── fix/zzz

# Hotfix workflow
main ─── hotfix/xxx ─── main
  │                      │
  └──────────────────────┘
```

---

## PR Guidelines

### PR Title
```
<type>: <description>

Example:
feat: Add Redis cache layer
fix: Resolve search 500 error
```

### PR Checklist
```markdown
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No new warnings
- [ ] Security considerations addressed
```

### Merge Requirements
- [ ] CI checks pass
- [ ] CodeRabbit review passed (automatic)
- [ ] No unresolved comments
- [ ] Branch up to date with target

### CodeRabbit Integration
- **Auto-review**: All PRs are automatically reviewed by CodeRabbit
- **Config**: `.coderabbit.yaml`
- **Manual review**: Only triggered when CodeRabbit fails critically
- **Notification**: Email sent automatically on critical failure

---

## Common Commands

```bash
# ============================================
# COMPLETE FEATURE DEVELOPMENT FLOW
# ============================================

# 1. Start from updated main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/xxx

# 3. Develop and commit
git add .
git commit -m "feat: implement xxx"

# 4. Push to remote
git push -u origin feature/xxx

# 5. Create Pull Request
gh pr create --title "feat: xxx" --body "$(cat <<'EOF'
## Summary
- What this PR does

## Test plan
- [ ] Test case 1
- [ ] Test case 2
EOF
)"

# 6. Wait for CodeRabbit review (automatic)

# 7. After approval, merge
gh pr merge --squash

# 8. Clean up
git checkout main
git pull
git branch -d feature/xxx

# ============================================
# OTHER USEFUL COMMANDS
# ============================================

# Interactive rebase (clean up commits)
git rebase -i HEAD~3

# Update branch with main
git fetch origin
git rebase origin/main

# Check PR status
gh pr view
gh pr checks

# View CodeRabbit review
gh pr comments
```
