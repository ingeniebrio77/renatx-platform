output "server_ipv4" {
  description = "Dirección IPv4 pública del nodo"
  value       = hcloud_server.node.ipv4_address
}

output "fqdn_web" {
  description = "Dominio web configurado"
  value       = local.fqdn_root
}

output "finops_tags" {
  description = "Etiquetas FinOps aplicadas para auditoría de costes"
  value       = local.finops_labels
}
