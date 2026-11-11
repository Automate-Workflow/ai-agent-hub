# Security Policy

## Supported Versions

Only the `main` branch is actively maintained and receives security attention.

| Branch | Supported |
|--------|-----------|
| main   | Yes       |
| others | No        |

## Scope

This repository is a knowledge base. Security concerns include:

- Malicious or compromised URLs in data files that could harm users who click them
- Phishing links embedded in any CSV, markdown, or documentation
- Leaked secrets or credentials in scripts or configuration files
- Vulnerabilities in scripts that run with elevated permissions
- Factual misinformation in data that could cause harm if acted upon

**Out of scope**: vulnerabilities in third-party tools, services, or websites that are linked from
this repository but are not maintained here.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security reports.**

Report privately via:

1. **GitHub Private Vulnerability Reporting**: Use the "Report a vulnerability" button on the
   Security tab of this repository. This creates a private draft security advisory visible only
   to maintainers.
2. **Email**: ayush_24a12res897@iitp.ac.in with subject: `[SECURITY] AI Agent Hub`

Please include:

- A clear description of the concern
- Affected file(s) and row ID(s) if applicable
- Potential impact on users
- Suggested remediation (if known)

## Response Targets

| Stage | Target |
|-------|--------|
| Acknowledgement | Within 3 business days |
| Triage and initial assessment | Within 7 business days |
| Resolution or status update | Within 30 days |

We will keep you informed of progress. If you have not heard back within the stated timeframe,
please follow up by email.

## Coordinated Disclosure

We follow a coordinated disclosure process. Please allow us time to assess and remediate before
public disclosure. We will credit reporters in the CHANGELOG unless they prefer anonymity.

## Safe Use Note

This repository links to many third-party resources. Always verify linked resources before executing
any code or following instructions from external sites. The maintainers are not responsible for
the content, security, or availability of external sites.

