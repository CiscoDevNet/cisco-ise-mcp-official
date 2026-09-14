# Security Best Practices

How to run this server safely against a production ISE deployment: scoping the
API account, handling certificates, and keeping secrets out of plaintext files.

## Overview

This server talks to ISE's REST APIs — the ERS APIs and the Open APIs, both over
HTTPS on port 443. Treat the credentials and certificates it uses as production
secrets: source them in a secure manner (environment variables, a secrets
manager, or a key management service — never hard-coded or committed), and apply
the practices below.

## Least-privilege API accounts

API access requires a user (internal or from an external Active Directory group)
mapped to one of the ERS roles. Grant the **narrowest** role that works:

- **ERS Operator** — read-only (`GET` only). Prefer this for the service account,
  since the tools here are primarily read/investigation oriented.
- **ERS Admin** — full CRUD (`GET`, `POST`, `PUT`, `DELETE`). Use only if a
  workflow genuinely needs writes.
- **Super Admin** — can access all API services; avoid using it for automation.

## Certificate-based authentication

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

## Storing secrets in the OS keystore

Below are ways to keep a secret value — typically either `API_PWD` or
`ISE_CLIENT_KEY_PASSWORD` — in your OS's encrypted store instead of a plaintext
`.env`, then load it into an environment variable only when you launch the server.

The examples store and read a single secret named `ise-api-pwd` and map it to
`API_PWD`. The same process can be followed for other secrets, mapping each
stored secret to its corresponding environment variable.

### macOS (Keychain)

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

### Linux (libsecret / `secret-tool`)

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

### Windows (PowerShell + SecretManagement)

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
