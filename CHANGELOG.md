# Changelog

## 0.3.0 — 2026-08-30

- Reject every backend redirect before it can change origin, forward a session
  cookie, downgrade HTTPS, or reach a private network through an RSS hop.
- Restrict authenticated requests to the exact Substack HTTPS origin and
  validate cookies before constructing request headers.
- Allowlist login-window navigation, deny web permissions, show the current
  origin, and prevent duplicate sign-in windows.
- Render remote feed and account content as plain text and restrict publication
  artwork to known Substack media origins.
- Preserve the last good feed until an unexpected empty subscription response
  is confirmed by a second sync.
- Move plugin IPC to the singleton service, add daemon restart backoff, and
  surface authentication-process errors in the panel.
- Keep the newest post scrolling in the bar after it has been read.
- Add security regression coverage, Python 3.13/3.14 CI, CodeQL, immutable
  Action pins, Dependabot, signed release support, and a marketplace preview.

## 0.2.1 — 2026-08-29

- Reserve explicit gutters for feed and settings scrollbars.
- Replace implicit footer layout with fixed anchors.
- Clarify that the headline toggle affects Substack, not Spotmarchy music.
- Verify headline-setting persistence through the running Omarchy shell.

## 0.2.0 — 2026-08-29

- Add a full in-panel settings and account surface.
- Add password-first, email-link, back, and reload authentication controls.
- Exclude publications administered by the reader by default.
- Replace generated initials with real Substack publication artwork.
- Add Last-Modified feed validation alongside ETag support.
- Support additional subscription endpoint response shapes.
- Make concurrent settings updates process-safe.
- Simplify feed status labels and correct narrow-panel alignment.

## 0.1.0 — 2026-08-29

- Initial authenticated subscription discovery, RSS polling, native
  notifications, unread tracking, and browser handoff.
