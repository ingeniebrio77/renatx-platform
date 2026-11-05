# 🌐 Plataforma Comercial Renatx (`renatx.com`)
**Autor:** Franco Renato Palavecino — *Docente de TI & Administrador de Sistemas GNU/Linux | Especialista en Infraestructura Cloud y Redes (Ottensen, Hamburgo, Alemania)*

Plataforma comercial bilingüe (**Español 🇪🇸 / Alemán 🇩🇪**) para la venta de **Soporte Remoto 1-a-1 (vía RustDesk efímero por horas/minutos)** y **Mentoría Técnica (*Fachinformatiker FISI*, CompTIA Network+, AWS, Linux & DevOps)**.

---

## 🎯 1. Qué Hace esta Plataforma

1. **Web Comercial Bilingüe (`ES` / `DE`):**
   - Presenta tus 3 productos estrella con precios cerrados:
     - **Soporte Remoto S.O.S. (65 € / 1h):** Troubleshooting en directo de servidores Linux, redes, firewalls y contenedores.
     - **Mentoría 1-a-1 Certificaciones & FISI (49 € / 60 min):** Preparación práctica para exámenes IHK (*Fachinformatiker*), CompTIA Network+ y AWS.
     - **Bono 5 Sesiones Hands-On DevOps (220 € / 5h):** Construcción guiada de infraestructura con Terraform, Ansible, Podman y Traefik.
   - Conectada a `POST /api/billing/checkout` (FastAPI) para emitir la sesión de pago en Stripe en el idioma elegido por el cliente.

2. **Centro de Asistencia Remota RustDesk Bajo Demanda (`0,007 €/hora`):**
   - Muestra al cliente si tu nodo de soporte remoto (`support.renatx.com`) está en **STANDBY (0,00 €/h)** o **ACTIVO**.
   - Incluye un **Panel del Instructor** (protegido con tu token JWT) desde donde activas o apagas la sesión de soporte, mostrando el tiempo transcurrido en minutos y el coste acumulado en céntimos de euro.

---

## 🔒 2. Seguridad del Backend

| Protección | Descripción |
|------------|-------------|
| **JWT** | HMAC-SHA256, 60 min expiración, clave >= 32 caracteres |
| **Contraseña Admin** | PBKDF2-HMAC-SHA256 (260k iteraciones). Genera con `make password-hash` |
| **Rate Limiting** | 5 intentos / 5 minutos por IP en `/auth/login` |
| **Stripe Webhook** | Verificación HMAC con ventana anti-replay de 300s |
| **CORS** | Lista blanca en producción (Traefik sirve bajo mismo origen) |
| **Docs en Producción** | Deshabilitados por defecto (`ENABLE_DOCS` opcional) |
| **Health Check** | No expone credenciales ni datos internos |

---

## 🛠️ 3. Guía Paso a Paso: Cómo Preparar el Repositorio

El repositorio está listo para producción (F1 + F2 completados).

### Generar la contraseña del administrador
```bash
cd /home/renato/Projectos/Pagina
make password-hash
# Copia el output a .env como ADMIN_PASSWORD_HASH=...
```

### Verificar en local
```bash
make up           # Levanta web + API
make down         # Detiene todo
make db-backup    # Backup de PostgreSQL
```

---

## ☁️ 4. Guía Completa de Despliegue Real (`renatx.com`)

Cuando estés listo para lanzar la web a Internet, sigue exactamente este orden:

### Paso 1: Comprar `renatx.com` en Cloudflare
1. Entra en tu panel de **Cloudflare** -> *Domain Registration* -> *Register Domains*.
2. Busca **`renatx.com`** (~10,44 $/año) y regístralo.
3. Copia el **Zone ID** y crea un **API Token** (*Edit zone DNS*).

### Paso 2: Crear cuenta y API Token en Hetzner Cloud
1. Entra en [https://console.hetzner.cloud](https://console.hetzner.cloud) y crea un proyecto `renatx-platform`.
2. Ve a *Security* -> *API Tokens* y genera un token con permisos *Read & Write*.
3. Instala OpenTofu y Ansible:
   ```bash
   sudo pacman -S opentofu ansible
   ```

### Paso 3: Desplegar el Servidor Web (`prod` o `preprod`)
```bash
cd /home/renato/Projectos/Pagina/infra-platform/terraform/envs/prod
tofu init
tofu apply \
  -var="hcloud_token=TU_TOKEN_HETZNER" \
  -var="cloudflare_api_token=TU_TOKEN_CLOUDFLARE" \
  -var="cloudflare_zone_id=TU_ZONE_ID" \
  -var="ssh_public_key=$(cat ~/.ssh/id_ed25519.pub)"
```

### Paso 4: Configurar el Servidor con Ansible
```bash
cd /home/renato/Projectos/Pagina/infra-platform/ansible
cp inventory.ini.example inventory.ini
# Edita inventory.ini con la IP del servidor
ansible-playbook -i inventory.ini playbook.yml
```

---

## 🔐 5. Archivos Críticos (No Modificar Sin Confirmar)

| Archivo | Propósito | Precaución |
|---------|-----------|------------|
| `.env` | Variables de entorno | **Nunca subir a Git** |
| `~/.ssh/id_ed25519` | Clave SSH del servidor | Usar con Hetzner |
| `infra-platform/rustdesk/data/` | Claves RustDesk | Respaldar después de uso efímero |

---

## 🧪 6. Pruebas y Calidad

| Suite | Tests | Cobertura |
|-------|-------|-----------|
| Backend (service-api) | 191 | 100% |
| Frontend (service-web) | 25 | — |
| CI/CD (.github/workflows/ci.yml) | — | Trivy + ruff + mypy + jest |

---

## 📦 7. Dependencias Principales

| Componente | Versión | Nota |
|--------------|---------|------|
| FastAPI | >=0.115 | Async API |
| Next.js | 16.3.3 | App Router, Edge-ready |
| React | 19.0.0 | Con Suspense |
| Python | 3.12 | uv + uv.lock |
| Node.js | 24 | npm 10+ |
| PostgreSQL | 16 | En red interna db_net |
| Traefik | v3.1 | Reverse proxy + ACME |
| RustDesk | latest | hbbs/hbbr efímero |

---

## 📄 8. License

MIT License — Puedes usar, modificar y distribuir libremente. Ver archivo `LICENSE` para más detalles.