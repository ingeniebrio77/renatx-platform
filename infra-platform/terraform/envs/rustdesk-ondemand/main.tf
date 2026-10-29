# =============================================================================
# Entorno Efímero Bajo Demanda: RUSTDESK REMOTE SUPPORT (support.renatx.com)
# Facturación por horas en Hetzner Cloud (~0,007 €/hora en CX22)
# Levantar antes de una sesión de soporte/mentoría y destruir al finalizar.
# =============================================================================

terraform {
  required_version = ">= 1.6.0"
  required_providers {
    hcloud = {
      source  = "hetznercloud/hcloud"
      version = "~> 1.48"
    }
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.40"
    }
  }
}

variable "hcloud_token" { type = string }
variable "cloudflare_api_token" { type = string }
variable "cloudflare_zone_id" { type = string }
variable "ssh_public_key" { type = string }
variable "domain_name" {
  type    = string
  default = "renatx.com"
}

provider "hcloud" {
  token = var.hcloud_token
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

locals {
  finops_labels = {
    env          = "ondemand"
    service      = "rustdesk-support"
    billing_mode = "hourly-ephemeral"
    owner        = "renatx"
    managed_by   = "terraform"
  }
}

resource "hcloud_firewall" "rustdesk_fw" {
  name   = "renatx-rustdesk-ondemand-fw"
  labels = local.finops_labels

  # SSH administrativo
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
  # Puertos TCP de RustDesk (hbbs + hbbr)
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "21115-21119"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
  # Puerto UDP de RustDesk (ID/Heartbeat/NAT punch)
  rule {
    direction  = "in"
    protocol   = "udp"
    port       = "21116"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}

resource "hcloud_server" "rustdesk_node" {
  name         = "renatx-rustdesk-ephemeral"
  image        = "debian-12"
  server_type  = "cx22" # 0,007 €/hora en Alemania (fsn1)
  location     = "fsn1"
  firewall_ids = [hcloud_firewall.rustdesk_fw.id]
  labels       = local.finops_labels

  user_data = <<-EOF
    #cloud-config
    package_update: true
    packages:
      - podman
    runcmd:
      - mkdir -p /opt/rustdesk
      - podman run -d --name hbbr -v /opt/rustdesk:/root:Z --net=host docker.io/rustdesk/rustdesk-server:latest hbbr -k _
      - podman run -d --name hbbs -v /opt/rustdesk:/root:Z --net=host docker.io/rustdesk/rustdesk-server:latest hbbs -r support.${var.domain_name}:21117 -k _
  EOF
}

# DNS con TTL de 60 segundos para propagación inmediata al encender la instancia
resource "cloudflare_record" "support_dns" {
  zone_id = var.cloudflare_zone_id
  name    = "support"
  content = hcloud_server.rustdesk_node.ipv4_address
  type    = "A"
  ttl     = 60
  proxied = false
}

output "rustdesk_server_ip" {
  description = "IP pública del nodo efímero de RustDesk"
  value       = hcloud_server.rustdesk_node.ipv4_address
}

output "rustdesk_fqdn" {
  description = "Servidor ID para configurar en el cliente RustDesk"
  value       = "support.${var.domain_name}"
}

output "hourly_cost_eur" {
  description = "Coste por hora del nodo efímero en Hetzner Cloud"
  value       = "0.007 EUR/h"
}
