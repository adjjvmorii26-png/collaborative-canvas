# Free Hosting Paths

This repository is a Python multi-agent workforce/automation system. Its CLI is not itself an HTTP service, so deployment should preserve that distinction.

## Recommended architecture

- **Cloud Run**: package the HTTP-facing part in a container when an API entrypoint is needed.
- **GitHub Actions**: run scheduled/background jobs and tests without keeping a server alive.
- **Supabase/Postgres**: durable run metadata, messages, facts, and artifacts.
- **Cloudflare Pages**: static dashboard/docs if the dashboard is separated from the Python process.
- **Cloudflare Workers / Deno Deploy**: small HTTP control-plane endpoints only; keep long-running orchestration out of edge request handlers.

## Free/default domains

- Cloud Run: `<service>-<hash>.<region>.run.app`
- Cloudflare Pages: `<project>.pages.dev`
- Deno Deploy: `<app>.deno.net`
- GitHub Pages: `<user>.github.io/<repo>`

## Persistence warning

The application currently uses local runtime artifacts and SQLite-style state. Treat container filesystems as ephemeral in production. Move durable state to Postgres/object storage before relying on a serverless/container deployment for persistent runs.

## Safe migration order

1. Keep the CLI working locally.
2. Add an HTTP adapter for the specific API surface you want to expose.
3. Containerize that adapter.
4. Move durable state to Postgres/object storage.
5. Deploy to Cloud Run.
6. Put a static dashboard on Pages/Cloudflare Pages if desired.
