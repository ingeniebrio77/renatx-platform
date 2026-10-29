# =============================================================================
# Módulo Base Terraform — Plataforma Renatx (Hetzner Cloud + Cloudflare DNS)
# Incluye etiquetado FinOps obligatorio para trazabilidad preprod vs prod
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

locals {
  # Etiquetas obligatorias para auditoría de costes (FinOps / Infracost)
  finops_labels = {
    env         = var.environment
    owner       = "renatx"
    author      = "franco-renato-palavecino"
    project     = "renatx-platform"
    cost_center = "saas-${var.environment}"
    managed_by  = "terraform"
  }

  fqdn_root = var.environment == "prod" ? var.domain_name : "${var.environment}.${var.domain_name}"
}

# 1. Clave SSH del administrador
resource "hcloud_ssh_key" "admin" {
  name       = "renatx-admin-${var.environment}"
  public_key = var.ssh_public_key
  labels     = local.finops_labels
}

# 2. Firewall Cloud en Hetzner (Defensa perimetral adicional a UFW)
resource "hcloud_firewall" "edge" {
  name   = "renatx-fw-${var.environment}"
  labels = local.finops_labels

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "80"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
  rule {
    direction  = "in"
    protocol   = "udp"
    port       = "443"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}

# 3. Instancia VPS (Debian 12 Bookworm)
resource "hcloud_server" "node" {
  name         = "renatx-${var.environment}-01"
  image        = "debian-12"
  server_type  = var.server_type
  location     = var.location
  ssh_keys     = [hcloud_ssh_key.admin.id]
  firewall_ids = [hcloud_firewall.edge.id]
  labels       = local.finops_labels

  public_net {
    ipv4_enabled = true
    ipv6_enabled = true
  }
}

# 4. Registros DNS en Cloudflare para renatx.com
resource "cloudflare_record" "web" {
  zone_id = var.cloudflare_zone_id
  name    = var.environment == "prod" ? "@" : var.environment
  content = hcloud_server.node.ipv4_address
  type    = "A"
  ttl     = 300
  proxied = false
}

resource "cloudflare_record" "api" {
  zone_id = var.cloudflare_zone_id
  name    = var.environment == "prod" ? "api" : "api.${var.environment}"
  content = hcloud_server.node.ipv4_address
  type    = "A"
  ttl     = 300
  proxied = false
}
