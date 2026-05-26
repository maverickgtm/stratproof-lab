# Hosted Public Demo

StratProof Lab includes a hardened public-demo mode for a public landing experience with interactive synthetic audits.

## What Visitors Can Do

- open the Evidence Command Center;
- choose or edit a formula;
- generate clearly labeled synthetic candles;
- run strict or relaxed research audits;
- read generated reports;
- download the complementary CSV evidence artifacts without a quota.

## What Hosted Mode Disables

- outbound public-market downloads initiated by visitors;
- saved-idea storage and retrieval;
- arbitrary repository file serving;
- direct generated-file browsing outside controlled report and CSV endpoints.

This boundary prevents a public demo from becoming a shared user-data store or an unbounded proxy to exchange endpoints. A cloned local Community installation continues to support public historical-data connectors.

## Start Locally

```bash
STRATPROOF_PUBLIC_DEMO=1 \
STRATPROOF_PUBLIC_RUNTIME_ROOT=/tmp/stratproof-public-demo \
STRATPROOF_WORKBENCH_PORT=8771 \
STRATPROOF_NO_BROWSER=1 \
python scripts/launch_local_workbench.py
```

Open `http://127.0.0.1:8771/`.

## Example Systemd Service

Run behind a reverse proxy, bound only to localhost:

```ini
[Unit]
Description=StratProof Lab Public Demo
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=/srv/stratproof-lab
Environment=STRATPROOF_PUBLIC_DEMO=1
Environment=STRATPROOF_PUBLIC_RUNTIME_ROOT=/tmp/stratproof-public-demo
Environment=STRATPROOF_WORKBENCH_PORT=8771
Environment=STRATPROOF_NO_BROWSER=1
Environment=PYTHONUNBUFFERED=1
ExecStart=/usr/bin/python3 scripts/launch_local_workbench.py
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=read-only

[Install]
WantedBy=multi-user.target
```

## Example Caddy Site

```caddyfile
stratproof-43-157-95-145.nip.io {
	encode zstd gzip

	header {
		Referrer-Policy "strict-origin-when-cross-origin"
		X-Content-Type-Options "nosniff"
		X-Frame-Options "SAMEORIGIN"
		-Server
	}

	reverse_proxy 127.0.0.1:8771
}
```

Use HTTPS through Caddy and keep port `8771` closed to the public firewall.
