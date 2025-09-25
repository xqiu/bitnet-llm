docker network create bitnetnet
docker run -d --name bitnet --network bitnetnet -p 19000:8080 --restart=unless-stopped abstratium/python39-bitnet
docker run -d --name cf-tunnel --network bitnetnet --restart=unless-stopped cloudflare/cloudflared:1767-80b1634515ba tunnel --no-autoupdate run --token %1
