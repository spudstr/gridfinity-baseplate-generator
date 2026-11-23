# Security Policy

## Supported versions

This project has no numbered releases. Security fixes go to the `main`
branch only, so always use the latest `main`.

| Version | Supported |
|---|---|
| `main` (latest) | Yes |
| Older commits | No |

## What counts as a security issue

The generator is a small, offline Python script with no dependencies. It
reads only its command-line arguments and writes one STL file. Issues that
would be in scope include:

- The script writing outside the path you asked for, or overwriting files
  unexpectedly.
- Input that makes the script hang, crash in an unsafe way, or use unbounded
  memory or disk.
- Anything in the repository's GitHub Actions workflows that could leak
  secrets or let untrusted code run with write access.
- A committed STL or image file that is malicious or not what it claims to be.

Wrong dimensions, a bad fit, or a slicer warning are ordinary bugs. Please
open a normal issue for those.

## Reporting a vulnerability

**Please do not open a public issue for security problems.**

Report privately through GitHub's private vulnerability reporting: open the
repository's **Security** tab and choose **Report a vulnerability**.

Please include:

- what you found and why it matters
- steps or a command line to reproduce it
- your operating system and Python version

## What to expect

- An acknowledgement within 7 days.
- An initial assessment within 14 days.
- Credit in the fix commit or advisory if you want it.

This is a hobby project maintained by one person, so these are good-faith
targets, not guarantees.
