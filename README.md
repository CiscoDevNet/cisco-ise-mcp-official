# Offical MCP Server for Cisco Identity Services Engine (ISE)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes Cisco ISE API operations as agent-callable tools over Streamable HTTP.

## Overview

This server provides Cisco ISE tools for live session search, AAA failure
investigation, access policy inspection (policy sets, authentication and
authorization rules, authorization profiles, library conditions), certificate
lookups, and deployment/node health. MCP-compatible clients can discover the
tools, inspect their schemas, and call them from natural language prompts.

- **Protocol:** Streamable HTTP
- **Default URL:** `http://localhost:5000/mcp/`

## Pre-requisites

- Python 3.12
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (optional)
- Access to a Cisco ISE server

## Quick Start

### 1. Clone and Setup

Clone the repository to get the latest code from the default branch. For a
specific version, download the corresponding release from the
[Releases](https://github.com/CiscoDevNet/cisco-ise-mcp-official/releases) page.

```bash
# Latest code; see Releases for specific versions
git clone https://github.com/CiscoDevNet/cisco-ise-mcp-official.git
cd cisco-ise-mcp-official

# Copy environment template
cp .env.example .env
# Edit .env with your ISE credentials
```

See [Configuration](#configuration) for every setting, including the
authentication approaches and server-certificate verification.

### 2. Install Dependencies

```bash
uv sync
```

### 3. Run the Server

**Without Docker:**
```bash
uv run server.py
```

**With Docker:**
```bash
docker compose up
```

**Development mode with debug:**
```bash
DEV=true DEBUG=true docker compose up --build
```

The server will be available at `http://localhost:5000`

## Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ISE_IP` | ISE PAN host/IP | — | Yes |
| `API_PORT` | ISE PAN port | `443` | No |
| `API_USERNAME` | ISE service-account username | — | See below |
| `API_PWD` | ISE service-account password | — | See below |
| `ISE_CREDENTIAL_HEADER_NAME` | Inbound header carrying the per-user ISE credential | `X-ISE-Authorization` | No |
| `ISE_REQUIRE_PER_USER_CREDENTIAL` | Reject requests missing the credential header instead of using the service account | `false` | No |
| `ISE_CLIENT_CERT` | Path to the client certificate PEM (cert-based auth; see below) | — | No |
| `ISE_CLIENT_KEY` | Path to the client private-key PEM (required with `ISE_CLIENT_CERT`) | — | No |
| `ISE_CLIENT_KEY_PASSWORD` | Passphrase for an encrypted client key | — | No |
| `ISE_VERIFY_SERVER_CERT` | Verify the ISE server certificate | `true` | No |
| `ISE_VERIFY_HOSTNAME` | Verify the server hostname/SAN (must be `false` when `ISE_VERIFY_SERVER_CERT=false`) | `true` | No |
| `ISE_CA_BUNDLE` | Path to a CA / self-signed certificate to trust (replaces the system trust store when set) | — | No |
| `ISE_MNT_GATE_MAX_CONCURRENCY` | Max concurrent heavy MnT reads (AuthList downloads and deployment-diagnostics summary), 1–4 | `1` | No |
| `ISE_MNT_GATE_MIN_INTERVAL_S` | Min seconds between heavy MnT read starts (0 = off); raise to space large reads further apart on big deployments | `5.0` | No |
| `ISE_MNT_GATE_BACKOFF_BASE_S` | Circuit-breaker base backoff after MnT distress (502/503/504/timeout) | `5.0` | No |
| `ISE_MNT_GATE_BACKOFF_MAX_S` | Circuit-breaker max backoff | `300.0` | No |
| `ISE_LOG_DOWNLOAD_MAX_CONCURRENCY` | Max node-log (`.log.zip`) downloads in flight at once, 1–4 | `1` | No |
| `HOST` | Address the MCP server binds to | `0.0.0.0` | No |
| `PORT` | Port the MCP server listens on | `5000` | No |
| `DEBUG_MCP` | Set to `true` for DEBUG-level logs; otherwise INFO | `false` | No |

The server authenticates to ISE with one of three credential types: the
per-user `X-ISE-Authorization` header, a client certificate (`ISE_CLIENT_CERT` /
`ISE_CLIENT_KEY`), or the `API_USERNAME` / `API_PWD` service account. The service
account is the fallback and is required unless a client certificate is configured
or `ISE_REQUIRE_PER_USER_CREDENTIAL=true` forces the header — in either of those
cases it can be left empty. See [Authentication](#authentication) for how these
credentials and server-certificate verification fit together.

## API Endpoints

The server uses the MCP **streamable-HTTP** transport. With the default `HOST`/`PORT`
it listens on:

- `http://localhost:5000/mcp/` - MCP protocol endpoint (streamable-HTTP)

> The URL is derived from `HOST` and `PORT` in your `.env` (defaults `0.0.0.0` / `5000`).
> If you change them, update the URLs in the client configs below accordingly.

## Connecting MCP Clients

Because this is an HTTP MCP server, any client that supports the streamable-HTTP
transport can connect directly at the `/mcp/` endpoint. Start the server first
(`uv run server.py` or `docker compose up`), then configure your client.

### Claude Code

Add the server with the CLI (recommended):

```bash
claude mcp add --transport http cisco-ise-mcp http://localhost:5000/mcp/
```

To pass a per-user ISE credential header (optional — see [Authentication](#authentication)):

```bash
claude mcp add --transport http cisco-ise-mcp http://localhost:5000/mcp/ \
  --header "X-ISE-Authorization: Basic <base64(user:password)>"
```

Verify and inspect the connection:

```bash
claude mcp list
claude mcp get cisco-ise-mcp
```

Alternatively, commit an `.mcp.json` at the project root so the server is shared
with anyone who checks out the repo:

```json
{
  "mcpServers": {
    "cisco-ise-mcp": {
      "type": "http",
      "url": "http://localhost:5000/mcp/"
    }
  }
}
```

### Claude Desktop

Claude Desktop currently speaks stdio, so bridge to the HTTP server with
[`mcp-remote`](https://www.npmjs.com/package/mcp-remote). Edit
`claude_desktop_config.json` (Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "cisco-ise-mcp": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "http://localhost:5000/mcp/"]
    }
  }
}
```

Restart Claude Desktop after saving. To send the credential header, append
`--header "X-ISE-Authorization: Basic <base64>"` to the `args` array.

### Cursor / VS Code / other HTTP-capable clients

Most editors that support MCP accept the same shape as `.mcp.json`. For Cursor,
add to `~/.cursor/mcp.json` (or `.cursor/mcp.json` in the project):

```json
{
  "mcpServers": {
    "cisco-ise-mcp": {
      "url": "http://localhost:5000/mcp/"
    }
  }
}
```

### Authentication

The server can authenticate to ISE three ways. For each request it picks the
first that applies, in this order:

1. **Per-user credential header** — an inbound `X-ISE-Authorization` header
   carrying a pre-built `Basic <base64(username:password)>` credential is used
   verbatim. The header name is configurable via `ISE_CREDENTIAL_HEADER_NAME`.
2. **Client certificate** — when `ISE_CLIENT_CERT` and `ISE_CLIENT_KEY` are set
   (and no per-user header is present), the certificate is presented on the TLS
   connection and **no `Authorization` header is sent** — ISE identifies the API
   user from the certificate. Cert and key must be supplied together; add
   `ISE_CLIENT_KEY_PASSWORD` only if the key is encrypted. Requires **ISE 3.3 or
   later**; see
   [Certificate-based authentication](docs/SECURITY_BEST_PRACTICES.md#certificate-based-authentication)
   for key-strength and rotation guidance. For step-by-step setup on the ISE side,
   see
   [How to configure certificate-based authentication for Cisco ISE](https://community.cisco.com/t5/security-blogs/how-to-configure-certificate-based-authentication-for-cisco-ise/bc-p/5372752).

   > **Note:** Certificate auth covers the ISE Open APIs only — not the MnT API.
   > The ISE MnT API (`/admin/API/mnt/`) does **not** support certificate
   > authentication. The tools that use MnT — the session-search tools, the
   > AAA-failure investigator, and `ise_deployment_health` with
   > `diagnostics=true` — therefore fall back to the per-user header or the
   > service account (see below). **One of those must be available even when a
   > client certificate is configured**, or those tools will not work.

3. **Service account** — the `API_USERNAME` / `API_PWD` credentials from `.env`
   are used when neither of the above applies. In cert-auth mode they remain the
   MnT fallback, so leave them set (or forward the per-user header) if you use the
   session/AAA-failure tools.

Set `ISE_REQUIRE_PER_USER_CREDENTIAL=true` to reject any request that omits the
per-user header instead of using the service account (a configured client
certificate still satisfies the Open-API request; MnT tools still require the
header in that mode).

**Server certificate verification** is **enabled by default**. To connect to ISE
nodes presenting self-signed or internal-CA certificates, configure trust via
`ISE_VERIFY_SERVER_CERT`, `ISE_VERIFY_HOSTNAME`, and `ISE_CA_BUNDLE` (see the
[Configuration](#configuration) table).

## Security Best Practices

See [docs/SECURITY_BEST_PRACTICES.md](docs/SECURITY_BEST_PRACTICES.md) —
least-privilege ERS roles, certificate handling, and keeping secrets in the OS
keystore instead of a plaintext `.env`.

## Available Tools

See [MCP_TOOLS_CATALOG.md](docs/MCP_TOOLS_CATALOG.md) for a complete list of available MCP tools.

## Considerations

### Log downloads

Some tools enrich their results by reading ISE node logs — for example,
`ise_diagnose_certificate_issues` scans `ise-psc.log` on PSN nodes for
certificate/TLS error signals. Check [MCP_TOOLS_CATALOG.md](docs/MCP_TOOLS_CATALOG.md)
for which tools read logs and which log files they need. A few things to know:

- **A log must have been downloaded from the ISE UI at least once before.** Log
  data is retrieved through ISE's web server (the UI download mechanism), not a
  dedicated log API, so a given log file can only be fetched once it has been
  downloaded from the ISE admin UI at least once — under
  **Operations → Troubleshoot → Download Logs → *(ISE node)***. If that manual
  download was never performed, the log fetch will not succeed. This does **not**
  break the tool: it still returns its other results gracefully, and only the
  log-derived portion of the output is unavailable.
- **The account needs permission to download logs.** The credential used must
  have sufficient privileges on the ISE admin UI to access the Download Logs
  page for the target node.
- **Log downloads work with username/password auth only — not client
  certificates.** Because logs go through ISE's web server rather than the API,
  log fetching works with the service-account (`API_USERNAME` / `API_PWD`) or
  per-user `X-ISE-Authorization` credential flows, but **not** with
  client-certificate authentication. Other tool results are unaffected under
  cert auth.
- **Concurrency is bounded.** Concurrent node-log downloads are capped by
  `ISE_LOG_DOWNLOAD_MAX_CONCURRENCY` (see the [Configuration](#configuration)
  table).

### Load on MnT nodes

Several tools query the ISE Monitoring & Troubleshooting (MnT) APIs — the four
session-search tools (`active_sessions_search`,
`sessions_search_with_advanced_details`, `sessions_search_with_policy_details`,
`sessions_search_with_latency_details`), the AAA-failure investigator, and
`ise_deployment_health` with `diagnostics=true`. These are real work on the MnT
node.

The expensive path is the AuthList scan, which downloads every session in the
requested window, so larger `minutes`/`limit` values cost more. To keep that from
overloading MnT, these downloads are serialized by default; concurrent or
too-rapid calls receive a retryable `ISE_BUSY` error that clients should back off
and retry.

**The cheapest way to avoid that cost is to query one identifier at a time.**
Given a single identifier — username, MAC, NAS IP, endpoint IP, or
`audit_session_id`, with no other filter — the session tools call ISE's dedicated
per-identifier endpoint instead: one small GET, no download, and not gated. Each
result reports which path ran in `search_filters.lookup`. Combining filters is
more precise but forces the scan.

The `ISE_MNT_GATE_*` env vars in the [Configuration](#configuration) table tune
this backpressure. **The defaults are intentionally restrictive** (one heavy read
at a time, spaced at least 5 seconds apart). Raise the limits only with care and
with headroom on your MnT node — each concurrent call is genuine load on ISE, so
be mindful of the resource consumption you're adding.
`ise_investigate_aaa_failure` (bounded, no full
download) and `get_active_session_counts` (counters only) are also cheap.

## Development

### Development Setup

Follow [Quick Start](#quick-start) steps 1 (Clone and Setup) and 2 (Install
Dependencies) to get a working checkout. `uv sync` installs the `dev` dependency
group as well, so no extra step is needed for the tooling below.

### Running Tests

```bash
uv run pytest
```

### Creating a New Tool

See [docs/CREATING_TOOLS.md](docs/CREATING_TOOLS.md) — the layer conventions,
step-by-step walkthrough, and the OpenAPI client generation needed for a new ISE
API surface.

## Project Structure

```
.
├── api_client_config/    # API client configuration YAML files
├── api_specs/            # OpenAPI specifications (JSON)
├── clients/              # HTTP and database clients
├── docs/                 # Documentation (tool catalog, guides)
├── parsers/              # Response parsers
├── tools/                # MCP tool handlers
├── shared_libs/          # Shared utilities (timing, etc.)
├── tests/                # Test files
├── server.py             # Main server entry point
├── main.py               # Alternative entry point
└── docker-compose.yml    # Docker orchestration
```

## Support

For bugs, new tool requests, documentation problems, and usage questions, please
[open a GitHub issue](https://github.com/CiscoDevNet/cisco-ise-mcp-official/issues/new/choose)
and pick the matching template. See [CONTRIBUTING.md](/CONTRIBUTING.md) for more details.

**Cisco employees** can also join the internal Webex space for quicker questions
and design discussion: [Join the Webex space][webex-space].

[webex-space]: https://eurl.io/#meokmr05p

## License

Licensed under Apache 2.0.

See the [LICENSE](/LICENSE) file for details.
