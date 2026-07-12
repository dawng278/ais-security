# Security Console Design System

Phase 5 consolidates security console tokens in `frontend/src/app/globals.css`.

Token groups:

- surfaces: `--gg-bg`, `--gg-surface`, `--gg-surface-muted`
- text: `--gg-text`, `--gg-text-muted`
- borders: `--gg-border`, `--gg-border-strong`
- semantic: critical, high, medium, low, healthy, degraded, unavailable, demo
- radius and shadows: `--gg-radius*`, `--gg-shadow-card`
- container: `--gg-container`

Rules:

- Use semantic tokens and Tailwind utility composition.
- Use lucide-react only.
- Use visible focus rings.
- Respect reduced motion.
- Do not use color as the only severity signal.

