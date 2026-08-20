# IXPANSION Organism Console

A self-contained control panel that maps the whole hub to a living organism:

- **nervous** = agent workforce (cells)
- **skeletal** = config / repo integrity
- **respiratory** = LLM providers + API keys (breath)
- **circulatory** = cash flow (blood)
- **digestive** = recipes (behaviors)
- **immune** = red-team / safety scans
- **memory** = generated reports
- **reproductive** = experiment backlog
- **broadcast** = YouTube channels + ad campaigns
- **custom organs** — grow new organs from the console (registered in `ixpansion/content_output/console/organs.json`)

## Run

```bash
cd /root/Hub_spot
python3 ixpansion/organism-console/server.py --port 8890
```

Open http://127.0.0.1:8890

## API

- `GET /api/body` — full organism snapshot (score, organs, metabolism, atoms, provider, keys, cash flow, YouTube, pulses)
- `GET /api/pulses` — recent pulse ledger
- `GET /api/metabolism` — vital signs (heart rate, temperature, oxygen, blood pressure, immunity, stress, burn rate)
- `GET /api/heatmap` — per-organ activity heatmap over the last 7 days
- `GET /api/bus` — recent agent message-bus signals
- `POST /api/bus` — post a signal, e.g. `{"organ": "circulatory", "topic": "blood-flow", "severity": "info", "body": "..."}`
- `POST /api/consensus` — cross-agent vote on a proposal, e.g. `{"proposal": "schedule a daily pulse with a cost budget"}`
- `GET /api/organs` — list custom organs
- `POST /api/organs` — grow a custom organ, e.g. `{"id": "lymphatic", "label": "Lymphatic System", "source": "ixpansion/content_output/lymph"}`
- `POST /api/provider` — switch provider: `{"provider": "openai"}` or `{"provider": "xai"}`
- `POST /api/keys` — register an API key, e.g. `{"name": "Grok", "key_type": "xai", "key_value": "xai-..."}`
- `POST /api/pulse` — run an experiment, e.g. `{"input": "..." , "recipe": "summary", "mock": true}`

## Data

Console state lives in `ixpansion/content_output/console/`:

- `bus.json` — up to 200 recent organ signals (the message bus)
- `organs.json` — custom organs grown from the console

## Safety

- No third-party dependencies; stdlib only.
- Keys are returned masked from the console UI; the raw value lives in `ixpansion/content_output/api_keys.json` (same store as `APIKeyManager`).
- Provider switching rewrites `workforce.yaml`; `.env` remains the secret store.
