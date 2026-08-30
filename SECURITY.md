# Security policy

## Supported version

Security fixes are applied to the latest release. Upgrade with:

```bash
omarchy plugin update aaron.substack
```

## Reporting a vulnerability

Please use GitHub's **Report a vulnerability** form in the repository Security
tab. Do not open a public issue for session-cookie exposure, authentication
bypass, arbitrary command execution, or unintended network access.

Include the plugin version, Omarchy version, reproduction steps, and whether a
Substack session was connected. Never include a live session cookie or magic
link. Revoke the affected Substack session before sharing diagnostic material.

## Trust boundary

The plugin runs as the desktop user inside Omarchy's unsandboxed Quickshell
process and starts a local Python daemon. It stores only Substack session
cookies in the desktop Secret Service keyring. Feed metadata is stored with
user-only permissions under `~/.local/state/omarchy/substack/`.

Authenticated HTTP requests are restricted to `https://substack.com:443` and
never follow redirects. RSS requests are restricted to each publication's
canonical `https://<subdomain>.substack.com:443/feed` and never follow
redirects. Article links require HTTPS and are opened only after a user click.
