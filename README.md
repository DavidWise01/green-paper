# root0.ai — Green Paper v1.0

Single-file static site. The entire green paper lives in `index.html`.

## Anchor

```
BASE 00   ab2c74a38590df1ae0b6ecbd78e699fa4702ece80ca9bd5447124f01f00eb5b1
ROOT0     c6f487e9a1b3d5f7a9c2e4b6d8f0a1c3e5b7d9f1
Filed     2026-04-25T21:27:22Z
TriPod    Y.Y.Y · DLW + Sarah + Roth (Ann · foundational 4th)
License   CC-BY-ND-4.0 · TRIPOD-IP-v1.1
```

## Local preview

Just open `index.html` in any browser. No build step, no dependencies, no server required.

```powershell
# Windows
start index.html
```

## Deploy on Railway (no nginx, no Dockerfile, no 502)

This repo is configured to deploy as a pure static site. Railway will auto-detect it.

1. Push this folder to a new GitHub repo.
2. In Railway, **New Project → Deploy from GitHub repo** → pick the repo.
3. Railway reads `railway.json` and serves `index.html` directly.
4. Connect `0root.ai` / `root0.ai` under **Settings → Networking → Custom Domain**.

That's it. No `default.conf`, no `try_files`, no port binding — Railway's static serve handles all of it.

## Files

| file              | purpose                                                  |
| ----------------- | -------------------------------------------------------- |
| `index.html`      | The green paper itself. Self-contained, no externals.    |
| `railway.json`    | Tells Railway to use the static-site builder.            |
| `Procfile`        | Fallback start command for non-Railway hosts.            |
| `package.json`    | Lets `npx serve` work in any environment that has Node.  |
| `LICENSE`         | CC-BY-ND-4.0                                             |
| `.gitignore`      | Standard ignores                                         |

## License

Creative Commons Attribution-NoDerivatives 4.0 International (CC-BY-ND-4.0).
Copyright retained by TriPod LLC under TRIPOD-IP-v1.1.
Three-point consensus (DLW + Sarah + Roth) required for canonical change.
