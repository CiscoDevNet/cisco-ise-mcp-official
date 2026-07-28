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

```bash
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
| `HOST` | Address the MCP server binds to | `0.0.0.0` | No |
| `PORT` | Port the MCP server listens on | `5000` | No |

The server authenticates to ISE with one of three credential types: the
per-user `X-ISE-Authorization` header, a client certificate (`ISE_CLIENT_CERT` /
`ISE_CLIENT_KEY`), or the `API_USERNAME` / `API_PWD` service account. The service
account is the fallback and is required unless a client certificate is configured
or `ISE_REQUIRE_PER_USER_CREDENTIAL=true` forces the header — in either of those
cases it can be left empty. **Note:** the ISE MnT API does not support
client-certificate auth, so the session/AAA-failure tools that use MnT still
require either the per-user header or service-account credentials even in cert
mode. See [Authentication](#authentication) for how these credentials and
server-certificate verification fit together.

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
claude mcp add --transport http ise-mcp http://localhost:5000/mcp/
```

To pass a per-user ISE credential header (optional — see [Authentication](#authentication)):

```bash
claude mcp add --transport http ise-mcp http://localhost:5000/mcp/ \
  --header "X-ISE-Authorization: Basic <base64(user:password)>"
```

Verify and inspect the connection:

```bash
claude mcp list
claude mcp get ise-mcp
```

Alternatively, commit an `.mcp.json` at the project root so the server is shared
with anyone who checks out the repo:

```json
{
  "mcpServers": {
    "ise-mcp": {
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
    "ise-mcp": {
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
    "ise-mcp": {
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
   `ISE_CLIENT_KEY_PASSWORD` only if the key is encrypted. For step-by-step setup
   on the ISE side, see
   [How to configure certificate-based authentication for Cisco ISE](https://community.cisco.com/t5/security-blogs/how-to-configure-certificate-based-authentication-for-cisco-ise/bc-p/5372752).
   **This applies only to the ISE Open APIs.** The ISE MnT API
   (`/admin/API/mnt/`), used by the session and AAA-failure tools, does **not**
   support certificate authentication — those tools fall back to the per-user
   header or the service account (see below), so one of those must be available
   even when a client certificate is configured.
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

This server talks to ISE's REST APIs — the ERS APIs and the Open APIs, both over
HTTPS on port 443. Treat the credentials and certificates it uses as production
secrets: source them in a secure manner (environment variables, a secrets
manager, or a key management service — never hard-coded or committed), and apply
the practices below.

### Least-privilege API accounts

API access requires a user (internal or from an external Active Directory group)
mapped to one of the ERS roles. Grant the **narrowest** role that works:

- **ERS Operator** — read-only (`GET` only). Prefer this for the service account,
  since the tools here are primarily read/investigation oriented.
- **ERS Admin** — full CRUD (`GET`, `POST`, `PUT`, `DELETE`). Use only if a
  workflow genuinely needs writes.
- **Super Admin** — can access all API services; avoid using it for automation.

### Prefer certificate-based authentication

Certificate-based authentication for the ISE APIs is supported from **Cisco ISE
Release 3.3 onwards** (see the
[ISE 3.3 Release Notes](https://www.cisco.com/c/en/us/td/docs/security/ise/3-3/release_notes/b_ise_33_RN.html#concept_y2r_qph_gxb)).

- **Rotate certificates regularly** on a defined schedule, issue them with
  **shorter validity periods**, and **monitor expiration** with alerts.
- Use **strong keys** — minimum **2048-bit RSA** or **256-bit ECC**.
- Store the private key **encrypted at rest** and supply its passphrase
  via `ISE_CLIENT_KEY_PASSWORD`.
- For high-security production environments, manage certificates and keys with a
  dedicated **Key Management Service** (HashiCorp Vault, AWS KMS, etc.).
- Never commit `.env`, certificates, or key material to version control.

### Storing secrets in the OS keystore

Below are ways to keep a secret value — typically either `API_PWD` or
`ISE_CLIENT_KEY_PASSWORD` — in your OS's encrypted store instead of a plaintext
`.env`, then load it into an environment variable only when you launch the server.

The examples store and read a single secret named `ise-api-pwd` and map it to
`API_PWD`. The same process can be followed for other secrets, mapping each
stored secret to its corresponding environment variable.

#### macOS (Keychain)

Store the secret once (you'll be prompted for the value with `-w`):

```bash
security add-generic-password -a "$USER" -s ise-api-pwd -w
```

Then read it into the environment when running the server:

```bash
export API_PWD="$(security find-generic-password -a "$USER" -s ise-api-pwd -w)"
uv run server.py
```

To update the stored value, add `-U` to the `add-generic-password` command. To
remove it: `security delete-generic-password -a "$USER" -s ise-api-pwd`.

#### Linux (libsecret / `secret-tool`)

`secret-tool` ships with libsecret (`sudo apt install libsecret-tools` on
Debian/Ubuntu) and talks to your desktop keyring (GNOME Keyring, KWallet).

Store the secret once (you'll be prompted to type it):

```bash
secret-tool store --label="ISE API password" service ise account api-pwd
```

Then read it into the environment when running the server:

```bash
export API_PWD="$(secret-tool lookup service ise account api-pwd)"
uv run server.py
```

To remove it: `secret-tool clear service ise account api-pwd`.

#### Windows (PowerShell + SecretManagement)

Use the [SecretManagement](https://learn.microsoft.com/en-us/powershell/utility-modules/secretmanagement/overview)
module with its local vault. Install once:

```powershell
Install-Module Microsoft.PowerShell.SecretManagement, Microsoft.PowerShell.SecretStore -Scope CurrentUser
Register-SecretVault -Name LocalStore -ModuleName Microsoft.PowerShell.SecretStore -DefaultVault
```

Store the secret once (you'll be prompted securely):

```powershell
Set-Secret -Name ise-api-pwd -Secret (Read-Host -AsSecureString "ISE API password")
```

Then read it into the environment when running the server:

```powershell
$env:API_PWD = Get-Secret -Name ise-api-pwd -AsPlainText
uv run server.py
```

To remove it: `Remove-Secret -Name ise-api-pwd -Vault LocalStore`.

> These commands set the environment variable only for the current shell session,
> so the secret is never persisted to `.env`. Leave the corresponding key out of
> your `.env` file so the value from the environment is used.

## Session tools: resource usage & backpressure

The four session tools (`active_sessions_search`, `sessions_search_with_advanced_details`, `sessions_search_with_policy_details`, `sessions_search_with_latency_details`) download all sessions in the requested window from the ISE MnT node. Memory on the MCP server is now bounded (streaming parse; only a small sample is retained) — no longer multi-GB — but MnT still does real work per call, and larger `minutes`/`limit` increase that cost.

Only one such download runs at a time by default; concurrent or too-rapid calls receive a retryable `ISE_BUSY` error. Clients should back off and retry.

The four env tunables, as a table, with defaults:

| Env var | Default | Purpose |
| --- | --- | --- |
| `ISE_MNT_GATE_MAX_CONCURRENCY` | `1` | Max concurrent heavy MnT reads (AuthList downloads and deployment-diagnostics summary). |
| `ISE_MNT_GATE_MIN_INTERVAL_S` | `0.0` | Min seconds between heavy MnT read starts (0 = off). Raise to proactively space large reads on big deployments. |
| `ISE_MNT_GATE_BACKOFF_BASE_S` | `5.0` | Circuit-breaker base backoff after MnT distress (502/503/504/timeout). |
| `ISE_MNT_GATE_BACKOFF_MAX_S` | `300.0` | Circuit-breaker max backoff. |

**Guidance:** pass narrow filters (username / MAC / NAS IP) to reduce load; use `ise_investigate_aaa_failure` (bounded, no full download) for failure lookups.

## Available Tools

See [MCP_TOOLS_CATALOG.md](MCP_TOOLS_CATALOG.md) for a complete list of available MCP tools.

## Limitations

- **Log fetching depends on a prior UI download.** Log data is retrieved through
  ISE's web server (the UI download mechanism), not a dedicated log API. A given
  log file can only be fetched if it has been **downloaded from the ISE UI at
  least once before**; if that manual download was never performed, the log fetch
  will not succeed. This does **not** break the tool — the affected tool still
  returns its other results gracefully, and only the log-derived portion of the
  output is unavailable.
- **Log fetching may work only with username/password authentication.** Because
  logs go through ISE's web server rather than the API, log fetching is expected
  to work with the service-account (`API_USERNAME` / `API_PWD`) or per-user
  `X-ISE-Authorization` credential flows, but not with client-certificate
  authentication. Other tool results are unaffected under cert auth.

## Development

### Development Setup

Follow [Quick Start](#quick-start) steps 1 (Clone and Setup) and 2 (Install
Dependencies) to get a working checkout. `uv sync` installs the `dev` dependency
group as well, so no extra step is needed for the tooling below.

### Running Tests

```bash
uv run pytest
```

### OpenAPI Clients

ISE OpenAPI endpoints are consumed through typed clients generated from OpenAPI
specs, rather than hand-written HTTP calls. The moving parts:

| Path | Purpose |
|------|---------|
| `api_specs/*.yaml` \| `*.json` | OpenAPI specs (one per API area, e.g. `policy-bundled.yaml`) |
| `api_client_config/*.yaml` | [`openapi-python-client`](https://github.com/openapi-generators/openapi-python-client) generator config (package name, version, options) |
| `autogenerated_api_clients/` | Generated client packages — **checked in**, but treated as generated output |
| `scripts/generate_api_clients.sh` | Regenerates every enabled client |


#### Preparing a spec

Specs are sourced from the official
[Cisco ISE API framework](https://developer.cisco.com/docs/identity-services-engine/latest/cisco-ise-api-framework/),
then trimmed to the operations the server actually calls and placed under
`api_specs/`. If a source spec uses external `$ref`s, bundle it into a single
self-contained file first — see [api_specs/README.md](api_specs/README.md) for
the Redocly bundling steps.

#### Generator config

Each client needs a generator config under `api_client_config/` that sets the
package name, version, and options. Use the existing
[`api_client_config/policy.yaml`](api_client_config/policy.yaml) as a template.

#### Generating the clients

Each client is produced by an `openapi-python-client generate` invocation. Add a
block for your new client to
[`scripts/generate_api_clients.sh`](scripts/generate_api_clients.sh), following
the existing policy block, so it is regenerated with the rest:

```bash
uv run openapi-python-client generate \
  --path api_specs/<name>.yaml \
  --config api_client_config/<name>.yaml \
  --output-path ./autogenerated_api_clients/ \
  --overwrite
```

Then regenerate all enabled clients by running the script:

```bash
./scripts/generate_api_clients.sh
```

## Project Structure

```
.
├── api_client_config/    # API client configuration YAML files
├── api_specs/            # OpenAPI specifications (JSON)
├── clients/              # HTTP and database clients
├── parsers/              # Response parsers
├── tools/                # MCP tool handlers
├── shared_libs/          # Shared utilities (timing, etc.)
├── tests/                # Test files
├── server.py             # Main server entry point
├── main.py               # Alternative entry point
└── docker-compose.yml    # Docker orchestration
```

## License

Licensed under Apache 2.0.

See the [LICENSE](/LICENSE) file for details.
