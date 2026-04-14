# Movibot v9 Deployment (Ubuntu 24.04)

This setup keeps the existing app logic intact (aiogram, SQLite, Docker, scheduler, scanner, queue, publish pipeline) and adds near-zero-touch operational scripts for Ubuntu 24.04.

## One-time server setup

Run from the server after SSH login:

```bash
sudo bash /opt/movibot/scripts/bootstrap.sh
```

If the repository is not already on the server, clone first:

```bash
sudo mkdir -p /opt/movibot
sudo git clone <YOUR_REPO_URL> /opt/movibot
cd /opt/movibot
sudo bash scripts/bootstrap.sh
```

## One-command bootstrap

`bootstrap.sh` performs all required first-time actions:

1. Installs `git`, `curl`, `ca-certificates`, `gnupg`
2. Installs Docker Engine + Docker Compose plugin
3. Creates `/opt/movibot`
4. Clones repo (if missing)
5. Creates `/opt/movibot/content`, `/opt/movibot/data`, `/opt/movibot/logs`
6. Copies `.env.example` to `.env` if `.env` is missing
7. Runs `docker compose up -d --build`

Environment overrides supported by bootstrap:

- `MOVIBOT_REPO_URL` (default: `https://github.com/your-org/movibot-v9.git`)
- `MOVIBOT_BRANCH` (default: `main`)

## .env minimal required fields

After bootstrap, edit `/opt/movibot/.env` and fill only:

- `BOT_TOKEN`
- `CHANNEL_ID`
- `ADMIN_IDS`

Everything else can remain at defaults from `.env.example` unless you need custom behavior.

## Operations scripts

All scripts live in `scripts/` and assume project root is `/opt/movibot`.

```bash
sudo bash scripts/deploy.sh   # git pull + rebuild/restart
sudo bash scripts/update.sh   # fetch/pull + image pull + recreate
sudo bash scripts/restart.sh  # restart services
sudo bash scripts/status.sh   # compose service status
sudo bash scripts/logs.sh     # tail all logs
sudo bash scripts/logs.sh bot # tail logs for one service
sudo bash scripts/backup.sh   # archive data/content/logs/.env
```

## Termius snippets

Suggested snippets for quick ops:

### 1) Bootstrap

```bash
cd /opt/movibot && sudo bash scripts/bootstrap.sh
```

### 2) Deploy latest

```bash
cd /opt/movibot && sudo bash scripts/deploy.sh
```

### 3) Update images + restart

```bash
cd /opt/movibot && sudo bash scripts/update.sh
```

### 4) Health check

```bash
cd /opt/movibot && sudo bash scripts/status.sh
```

### 5) Live logs

```bash
cd /opt/movibot && sudo bash scripts/logs.sh
```
