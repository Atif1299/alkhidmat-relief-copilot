# Alibaba ECS — create instance (user auth)

Open and complete in **your** browser (do not paste passwords into Cursor chat):

1. Sign in: https://www.alibabacloud.com/
2. Console → **Elastic Compute Service** → **Instances** → **Create Instance**
3. Settings:
   - Region: prefer **Singapore (ap-southeast-1)** or nearest with billing
   - Image: **Ubuntu 22.04 64-bit**
   - Instance: **2 vCPU / 4 GiB** (or similar)
   - Network: assign **public IPv4**
   - Security group inbound: **TCP 22**, **TCP 80** (add 443 later for HTTPS)
   - Key pair or password: keep private
4. After Running, copy **Public IP** and reply in the deploy chat:

```
Region: <region-id>
Public IP: <x.x.x.x>
SSH user: root
```

Then follow [DEPLOYMENT.md](../docs/DEPLOYMENT.md) bring-up commands (or ask the deploy agent to walk SSH steps).
