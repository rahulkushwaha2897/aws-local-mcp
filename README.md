# aws-local-mcp

A zero-dependency Cursor MCP plugin that lets AI agents run any AWS CLI command on your local machine — with full SSO profile support across all your AWS accounts.

## Features

- **Run any `aws` CLI command** directly from Cursor AI agents
- **Full `--profile` support** — switch between all your AWS SSO accounts without restarting Cursor
- **Zero dependencies** — pure Python 3.9+, no pip installs needed
- **Safe** — only runs commands that start with `aws`

## Tools

| Tool | Description |
|---|---|
| `call_aws` | Execute any AWS CLI command. Include `--profile <name>` to target a specific account. |
| `list_profiles` | List all configured AWS SSO profiles. |

## Requirements

- Python 3.9+
- [AWS CLI v2](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed and configured
- AWS SSO profiles set up via `aws configure sso`

## Installation via Cursor Marketplace

Install directly from the Cursor Plugin Marketplace — search for **aws-local-mcp**.

## Manual Installation

Add the following to your `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "aws-local": {
      "command": "python3",
      "args": ["/path/to/aws_local_mcp.py"]
    }
  }
}
```

## Usage Examples

Ask your Cursor AI agent:

- *"List all S3 buckets in my prod account"* — it will run `aws s3 ls --profile prod`
- *"Show me all running EC2 instances in staging"* — `aws ec2 describe-instances --filters Name=instance-state-name,Values=running --profile staging`
- *"What AWS profiles do I have configured?"* — uses `list_profiles`

## License

MIT
