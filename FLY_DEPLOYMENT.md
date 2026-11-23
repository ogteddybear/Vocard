# Fly.io deployment

Vocard runs as a Discord worker. It does not serve HTTP, so the bot and its backends have no public services or inbound ports. Run all three apps in the same Fly organization so the bot can use Fly's private DNS and 6PN network. The configured private hosts are `vocard-lavalink.internal:2333` and `vocard-mongodb.internal:27017`.

## Deploy three single-machine apps

Use the matching config file for each app and keep one machine in each app:

- Bot: root `fly.toml`, app `vocard-bot`, `shared-cpu-1x`, 512 MB.
- Lavalink: `lavalink/fly.toml`, app `vocard-lavalink`, `shared-cpu-1x`, 1 GB. It builds `lavalink/Dockerfile`, which copies the YouTube plugin configuration into the official Lavalink image.
- MongoDB: `mongodb/fly.toml`, app `vocard-mongodb`, `shared-cpu-1x`, 1 GB, with a 1 GB volume mounted at `/data/db`.

Deploy the database first, then Lavalink, then the bot. In Fly's dashboard, create one machine for each app and leave autoscaling disabled. These worker-only configs intentionally have no `services` or `http_service`; Fly's `min_machines_running` is only a service setting, and `fly.toml` does not set a machine count. The actual one-machine limit is maintained by keeping exactly one machine in each app.

If using `flyctl`, run the deploy command from the repository root with the corresponding config: `fly deploy --config mongodb/fly.toml`, then `fly deploy --config lavalink/fly.toml`, then `fly deploy --config fly.toml`. Confirm each app has exactly one machine after deployment.

## Secrets

Set secrets in the Fly dashboard under each app's Secrets page, or with `fly secrets set`. Never commit actual values to this repository.

Create a strong MongoDB root password and set it on `vocard-mongodb` as `MONGO_INITDB_ROOT_PASSWORD`. Set the same password in `vocard-bot` inside `MONGODB_URL` as a URL-encoded credential, for example:

```text
mongodb://vocard_admin:<URL-encoded-password>@vocard-mongodb.internal:27017/vocard?authSource=admin
```

Set one strong Lavalink password on both `vocard-lavalink` and `vocard-bot` as `LAVALINK_SERVER_PASSWORD`. Lavalink checks this password for WebSocket and REST connections.

Set the Discord bot token on `vocard-bot` as `DISCORD_TOKEN`. Optional: set `GENIUS_TOKEN` for Genius lyrics support. `MONGODB_NAME=vocard`, `LAVALINK_HOST`, `LAVALINK_PORT`, and `LAVALINK_SECURE` are non-secret defaults in the bot's `fly.toml`.

Example commands (replace placeholders locally; do not commit them):

```sh
fly secrets set -a vocard-mongodb MONGO_INITDB_ROOT_PASSWORD='<strong-mongodb-password>'
fly secrets set -a vocard-lavalink LAVALINK_SERVER_PASSWORD='<strong-lavalink-password>'
fly secrets set -a vocard-bot DISCORD_TOKEN='<discord-bot-token>' MONGODB_URL='mongodb://vocard_admin:<URL-encoded-password>@vocard-mongodb.internal:27017/vocard?authSource=admin' LAVALINK_SERVER_PASSWORD='<same-lavalink-password>'
```

Do not expose ports 2333 or 27017 publicly. Voice connections are initiated by the bot to Discord; they do not require an inbound HTTP port. Invite the bot using its Discord OAuth2 URL from the Developer Portal.
