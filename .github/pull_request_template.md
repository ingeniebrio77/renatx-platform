## 📋 Descripción del Cambio
<!-- Explica brevemente qué añade o corrige este Pull Request -->

## 🎯 Entorno Afectado
- [ ] `local` (Podman + Traefik en `renatx.localhost`)
- [ ] `preprod` (`preprod.renatx.com`)
- [ ] `prod` (`renatx.com`)

## 🔒 Checklist de Seguridad (Renatx Platform)
- [ ] **Cero Secretos:** No se han subido archivos `.env`, `.tfvars` reales ni claves privadas.
- [ ] **Aislamiento de Red:** PostgreSQL (`5432`) sigue aislado en `db_net` (`internal: true`) sin `ports:` expuestos al host.
- [ ] **Podman Rootless:** Los contenedores funcionan sin privilegios de `root` innecesarios.
- [ ] **Trazabilidad FinOps:** Si se modificó Terraform, todos los recursos mantienen las etiquetas (`env`, `owner = "renatx"`, `cost_center`).
- [ ] **Verificación Local:** Se ha probado con `make up` y verificado `GET /api/health`.

## 🧪 Tests
- [ ] Backend: 191 tests pasando (`service-api/`)
- [ ] Frontend: 25 tests pasando (`service-web/`)
- [ ] Build: `npm run build` exitoso

## 📦 Cadena de Suministro
- [ ] `package-lock.json` actualizado
- [ ] `uv.lock` actualizado
- [ ] `.dockerignore` config
- [ ] Contenedores con usuario no-root (`USER` definido)

## 📝 Notas Adicionales
<!-- Cualquier información relevante para reviewers -->