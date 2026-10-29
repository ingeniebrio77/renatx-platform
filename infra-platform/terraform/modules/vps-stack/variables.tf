variable "environment" {
  description = "Entorno de despliegue (preprod o prod)"
  type        = string
  validation {
    condition     = contains(["preprod", "prod"], var.environment)
    error_message = "El entorno debe ser 'preprod' o 'prod'."
  }
}

variable "domain_name" {
  description = "Dominio raíz de marca personal"
  type        = string
  default     = "renatx.com"
}

variable "server_type" {
  description = "Tipo de servidor Hetzner (ej. cx22 para preprod, cx32/cpx21 para prod)"
  type        = string
  default     = "cx22"
}

variable "location" {
  description = "Datacenter en Alemania (fsn1 Falkenstein o nbg1 Nürnberg)"
  type        = string
  default     = "fsn1"
}

variable "ssh_public_key" {
  description = "Clave pública SSH del administrador"
  type        = string
}

variable "cloudflare_zone_id" {
  description = "Zone ID del dominio renatx.com en Cloudflare"
  type        = string
}
