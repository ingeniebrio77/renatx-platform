# =============================================================================
# Entorno: PRODUCCIÓN (renatx.com)
# Instancia dedicada 24/7 con backups y mayor capacidad
# =============================================================================

variable "hcloud_token" { type = string }
variable "cloudflare_api_token" { type = string }
variable "cloudflare_zone_id" { type = string }
variable "ssh_public_key" { type = string }

provider "hcloud" {
  token = var.hcloud_token
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

module "prod_stack" {
  source             = "../../modules/vps-stack"
  environment        = "prod"
  domain_name        = "renatx.com"
  server_type        = "cx32" # 4 vCPU, 8 GB RAM (Holgado para varios micro-SaaS)
  location           = "fsn1" # Falkenstein, Alemania
  ssh_public_key     = var.ssh_public_key
  cloudflare_zone_id = var.cloudflare_zone_id
}

output "prod_ipv4" {
  value = module.prod_stack.server_ipv4
}
