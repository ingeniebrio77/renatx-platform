# =============================================================================
# Entorno: PREPRODUCCIÓN (preprod.renatx.com)
# Pensado para ser efímero (encender bajo demanda y destruir al terminar)
# Coste estimado Hetzner CX22: ~0,007 €/hora (~4,51 €/mes si queda encendido)
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

module "preprod_stack" {
  source             = "../../modules/vps-stack"
  environment        = "preprod"
  domain_name        = "renatx.com"
  server_type        = "cx22" # 2 vCPU, 4 GB RAM (Mínimo coste para validación)
  location           = "fsn1" # Falkenstein, Alemania
  ssh_public_key     = var.ssh_public_key
  cloudflare_zone_id = var.cloudflare_zone_id
}

output "preprod_ipv4" {
  value = module.preprod_stack.server_ipv4
}
