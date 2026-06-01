# TODO

- [x] Patch `launch_backend.ps1` to fail fast if `DATABASE_URL` is not set (prevents accidental SQLite fallback).
- [ ] Restart backend with correct `DATABASE_URL`.
- [ ] Re-test login flow.
- [ ] If still failing, verify JWT/auth works against the correct DB by calling `/api/auth/me` with the stored token.
