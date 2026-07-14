# Offical MCP Server for Cisco Identity Services Engine (ISE)

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server that exposes Cisco ISE API operations as agent-callable tools over Streamable HTTP.

> **Beta (v0.1.0)** — This server is under active development. Tool names, input
> schemas, and response shapes may change between releases. It is intended for
> evaluation and supervised use; it is **not yet recommended for unsupervised
> production automation**. Feedback and issue reports are very welcome.

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
| `HOST` | Address the MCP server binds to | `0.0.0.0` | No |
| `PORT` | Port the MCP server listens on | `5000` | No |
| `ISE_CREDENTIAL_HEADER_NAME` | Inbound header carrying the per-user ISE credential | `X-ISE-Authorization` | No |
| `ISE_REQUIRE_PER_USER_CREDENTIAL` | Reject requests missing the credential header instead of using the service account | `false` | No |
| `ISE_CLIENT_CERT` | Path to the client certificate PEM (cert-based auth; see below) | — | No |
| `ISE_CLIENT_KEY` | Path to the client private-key PEM (required with `ISE_CLIENT_CERT`) | — | No |
| `ISE_CLIENT_KEY_PASSWORD` | Passphrase for an encrypted client key | — | No |
| `ISE_VERIFY_SERVER_CERT` | Verify the ISE server certificate | `true` | No |
| `ISE_VERIFY_HOSTNAME` | Verify the server hostname/SAN (must be `false` when `ISE_VERIFY_SERVER_CERT=false`) | `true` | No |
| `ISE_CA_BUNDLE` | Path to a CA / self-signed certificate to trust (replaces the system trust store when set) | — | No |

`API_USERNAME` / `API_PWD` are the service-account credentials used when a request
does not carry the per-user `X-ISE-Authorization` header or a client certificate.
They are required unless every client sends that header (see
[Authentication](#authentication)); with `ISE_REQUIRE_PER_USER_CREDENTIAL=true` or a
client certificate configured, they can be left empty.

See [Authentication](#authentication) for how these credentials, the client
certificate, and server-certificate verification fit together.

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
   `ISE_CLIENT_KEY_PASSWORD` only if the key is encrypted. This is the
   programmatic equivalent of:

   ```bash
   curl -X GET https://<ISE_IP>/ers/config/op/systemconfig/iseversion \
     --cert client.pem --key client.key -H "Accept: application/json"
   ```
3. **Service account** — the `API_USERNAME` / `API_PWD` credentials from `.env`
   are used when neither of the above applies.

Set `ISE_REQUIRE_PER_USER_CREDENTIAL=true` to reject any request that omits the
per-user header instead of using the service account (a configured client
certificate still satisfies the request).

**Server certificate verification** is **enabled by default**. To connect to ISE
nodes presenting self-signed or internal-CA certificates, configure trust via
`ISE_VERIFY_SERVER_CERT`, `ISE_VERIFY_HOSTNAME`, and `ISE_CA_BUNDLE` (see the
[Configuration](#configuration) table).

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

See [LICENSE.md](/LICENSE.md) file for details.
