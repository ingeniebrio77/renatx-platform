---
name: Renatx IaC, FinOps & Ephemeral RustDesk
description: Use this skill when working on Terraform/OpenTofu, Ansible playbooks, Hetzner Cloud, Cloudflare DNS for renatx.com, FinOps cost tracking (preprod vs prod), or the on-demand RustDesk support server.
---

# Renatx IaC, FinOps & Ephemeral RustDesk (`renatx-iac-rustdesk`)

## 1. FinOps & Terraform Labeling Policy
Every resource in `infra-platform/terraform/` (Hetzner Cloud servers, firewalls, SSH keys, volumes) **must** carry FinOps labels:
- `owner = "renatx"`
- `env = "preprod" | "prod" | "ondemand"`
- `managed_by = "terraform"`

## 2. Environments (`infra-platform/terraform/envs/`)
- **`preprod` (`preprod.renatx.com`):** Hetzner `cx22` (`fsn1`, ~0.007 EUR/h). Designed to be spun up for validation and destroyed afterwards (`0.00 EUR/h` when off).
- **`prod` (`renatx.com`):** Hetzner `cx32` (`fsn1`, ~8.32 EUR/month) running 24/7.
- **`rustdesk-ondemand` (`support.renatx.com`):**
  - Ephemeral Hetzner `cx22` (~0.007 EUR/h) spun up only during live 1-on-1 remote support or mentoring sessions.
  - Firewall allows only `22/tcp`, `21115-21119/tcp`, and `21116/udp`.
  - Runs `rustdesk/rustdesk-server` (`hbbs` and `hbbr`) with `-k _` (mandatory Ed25519 public key encryption).
  - Cloudflare DNS record `support.renatx.com` uses `ttl = 60` for instant propagation when the node starts.

## 3. Ansible Host Provisioning (`infra-platform/ansible/playbook.yml`)
When modifying the Ansible playbook for Debian 12 / Ubuntu 24.04 LTS:
- Keep UFW strict (`deny incoming` default; allow `22/tcp`, `80/tcp`, `443/tcp`, `443/udp`).
- Configure Rootless Podman properly:
  - Set `net.ipv4.ip_unprivileged_port_start=80` via `sysctl`.
  - Enable systemd linger (`loginctl enable-linger renatx`) so containers survive SSH logout.
