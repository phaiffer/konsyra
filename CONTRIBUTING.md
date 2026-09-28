# Contributing to Konsyra

Thank you for participating in the Konsyra project. As an open-source initiative under [PhaifferTech](https://github.com/phaiffertech), we follow clear and simple engineering standards to maintain high documentation and code quality.

---

## Branch Naming Conventions

All work must be performed on dedicated topic branches created from `main`. Use the following prefixes:

- `feat/` — New features or functionality
- `fix/` — Bug fixes
- `docs/` — Documentation updates, ADRs, or diagrams
- `refactor/` — Code refactoring without behavioral changes
- `test/` — Adding or updating test suites

*Example:* `docs/architecture-baseline` or `feat/solana-source-adapter`

---

## Commit Message Standard

We strictly enforce **Conventional Commits**. Commit messages must be concise, structured, and informative.

### Format
`<type>(<scope>): <short summary>`

### Allowed Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `refactor`: Code restructuring without bug fixes or features
- `test`: Adding missing tests or correcting existing tests
- `chore`: Maintenance tasks, dependency updates, configuration changes

### Example Commit Messages
```bash
docs(architecture): establish project baseline documentation
feat(engine): implement slot signature set reconciliation check
test(adapter): add mock response tests for solana RPC adapter
```

---

## Staging & Git Workflow Rules

1. **Explicit Staging Preferred:** Avoid using blanket commands like `git add .` or `git add -A`. Explicitly stage target files: `git add docs/architecture/ARCHITECTURE.md`.
2. **Never Commit Secrets:** Do not commit API keys, private keys, RPC tokens, or wallet credentials. Ensure `.env` is ignored. Always use `.env.example` for environment variable templates.
3. **Keep Branches Synchronized:** Rebase topic branches onto `main` before opening pull requests to keep history clean.
4. **No Direct Pushes to Main:** All changes must go through pull request review.

---

## Code & Documentation Alignment

- **Documentation Consistency:** When changing logic, interfaces, or domain contracts, update the corresponding documentation (`ARCHITECTURE.md`, `MVP.md`, or relevant ADR) in the same pull request.
- **Tests Required:** Any executable code submission must be accompanied by unit or integration tests verifying the contract.
- **Explicit Failure States:** Avoid silent exception handling or dummy fallbacks. System errors and quality failures must be handled explicitly.

---

## Security Policy

- Do not include real mainnet private keys or sensitive credentials in test fixtures.
- Test proofs must be anchored exclusively on **Solana Devnet**.
- Never log private keys or authorization headers.
