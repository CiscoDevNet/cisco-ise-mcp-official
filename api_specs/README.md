# API Specifications

## Creating Bundled YAML Files

To create bundled YAML files that resolve all `$ref` references into a single file, use the Redocly CLI:

### Example Command

```bash
redocly bundle jars/policy/openapiapps/policyapp/src/main/resources/Policy-v1.yaml -o policy-bundled.yaml
```

### General Pattern

```bash
redocly bundle <source-yaml-path> -o <output-bundled-yaml-path>
```

This command:
- Resolves all external `$ref` references
- Combines multiple YAML files into a single bundled file
- Outputs a self-contained OpenAPI specification

### Prerequisites

Install Redocly CLI if not already installed:

```bash
npm install -g @redocly/cli
```
