# 🌐 Plataforma Comercial Renatx (`renatx.com`)
**Autor:** Franco Renato Palavecino — *Docente de TI & Administrador de Sistemas GNU/Linux | Especialista en Infraestructura Cloud y Redes (Ottensen, Hamburgo, Alemania)*

Plataforma comercial bilingüe (**Español 🇪🇸 / Alemán 🇩🇪**) para la venta de **Soporte Remoto 1-a-1 (vía RustDesk efímero por horas/minutos)** y **Mentoría Técnica (*Fachinformatiker FISI*, CompTIA Network+, AWS, Linux & DevOps)**.

---

## 🎯 1. Qué Hace esta Plataforma (Catálogo Comercial + RustDesk Efímero)

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

## 🛠️ 2. Guía Paso a Paso: Cómo Subir Todo a GitHub Hoy Mismo

He inicializado el repositorio Git local en `/home/renato/Projectos/Pagina` con el primer commit limpio (respetando `.gitignore` para que `.env` y las claves privadas jamás se suban).

Para publicarlo en tu cuenta de GitHub (`ingeniebrio77` o la cuenta que prefieras para tu marca `renatx`):

### Opción A: Usando la interfaz web de GitHub + SSH
1. Entra en [https://github.com/new](https://github.com/new) y crea un repositorio (privado o público) llamado **`renatx-platform`**, **sin** marcar "Add a README".
2. En tu terminal de Arch Linux, ejecuta:
   ```bash
   cd /home/renato/Projectos/Pagina
   git branch -M main
   git remote add origin git@github.com:TU_USUARIO_GITHUB/renatx-platform.git
   git push -u origin main
   ```

### Opción B: Usando GitHub CLI (`gh`) directamente desde tu terminal
```bash
cd /home/renato/Projectos/Pagina
gh repo create renatx-platform --private --source=. --remote=origin --push
```

---

## 🧪 3. Cómo Probar Todo en Local (Arch Linux + Podman)

### A. Levantar la Web Comercial y la API
```bash
cd /home/renato/Projectos/Pagina
make up
```
- Abre **`http://renatx.localhost:8080`** en tu navegador.
- Cambia entre **🇪🇸 ES** y **🇩🇪 DE** arriba a la derecha.
- Pulsa **"Reservar y Pagar con Stripe"** en cualquiera de tus 3 servicios.
- En la sección **RustDesk**, pulsa **"1. Autenticar Instructor (JWT)"** y luego **"Encender Nodo RustDesk"** para ver cómo se habilitan las credenciales `hbbs`/`hbbr` para el cliente.

### B. Levantar el Servidor RustDesk Real en tu Arch Linux Local
Si quieres probar la conexión con la aplicación de escritorio de RustDesk en tu propia red local:
```bash
# 1. Descarga y levanta hbbs y hbbr en Podman y muestra tu clave pública Ed25519:
make rustdesk-local-up

# 2. Para ver tu clave pública en cualquier momento:
make rustdesk-key

# 3. Para apagar el servidor RustDesk local cuando termines:
make rustdesk-local-down
```

---

## ☁️ 4. Guía Completa de Despliegue Real en Producción (`renatx.com`)

Cuando decidas lanzar la web a Internet, sigue exactamente este orden:

### Paso 1: Comprar `renatx.com` en Cloudflare
1. Entra en tu panel de **Cloudflare** -> *Domain Registration* -> *Register Domains*.
2. Busca **`renatx.com`** (~10,44 $/año a precio de coste) y regístralo.
3. En la página principal del dominio dentro de Cloudflare, copia el **Zone ID** (abajo a la derecha) y crea un **API Token** (*Edit zone DNS*).

### Paso 2: Crear cuenta y API Token en Hetzner Cloud (Alemania)
1. Entra en [https://console.hetzner.cloud](https://console.hetzner.cloud) y crea un proyecto llamado **`renatx-platform`**.
2. Ve a *Security* -> *API Tokens* y genera un token con permisos de *Read & Write*.
3. Instala OpenTofu (o Terraform) y Ansible en tu Arch Linux:
   ```bash
   sudo pacman -S opentofu ansible
   ```

### Paso 3: Desplegar el Servidor Web (`preprod` o `prod`) con Terraform/OpenTofu
1. Entra en `infra-platform/terraform/envs/prod` (o `preprod` para probar primero gastando menos de 1 céntimo la hora):
   ```bash
   cd /home/renato/Projectos/Pagina/infra-platform/terraform/envs/preprod
   tofu init
   tofu apply \
     -var="hcloud_token=TU_TOKEN_HETZNER" \
     -var="cloudflare_api_token=TU_TOKEN_CLOUDFLARE" \
     -var="cloudflare_zone_id=TU_ZONE_ID" \
     -var="ssh_public_key=$(cat ~/.ssh/id_ed25519.pub)"
   ```
2. OpenTofu creará el servidor Debian 12 en Falkenstein (`fsn1`), el firewall y apuntará los registros DNS de `renatx.com` automáticamente.

### Paso 4: Configurar el Servidor con Ansible (Podman Rootless + UFW)
```bash
cd /home/renato/Projectos/Pagina/infra-platform/ansible
cp inventory.ini.example inventory.ini
# Pon la IP que te devolvió OpenTofu en inventory.ini y ejecuta:
ansible-playbook -i inventory.ini playbook.yml
```
*(Esto deja el servidor endurecido con UFW, SSH solo por clave, Podman rootless autorizado para abrir el puerto 80/443 y `linger` activado).*

### Paso 5: Cómo Operar una Sesión de Soporte Remoto RustDesk por Horas/Minutos
Cuando un cliente te reserve una sesión de **Soporte S.O.S. (65 €)** o **Mentoría (49 €)**:

1. **5 minutos antes de la videollamada/sesión**, enciende el servidor efímero de RustDesk en Hetzner:
   ```bash
   make rustdesk-cloud-up
   ```
   *(En ~45 segundos tendrás `support.renatx.com` activo corriendo `hbbs` y `hbbr` en Podman).*
2. Al terminar la sesión de 1 o 2 horas, destrúyelo con un comando:
   ```bash
   make rustdesk-cloud-down
   ```
   **Resultado FinOps:** Habrás cobrado 49 € – 65 € por tu sesión y habrás pagado **~0,014 € (1,4 céntimos de euro)** de infraestructura Cloud, volviendo inmediatamente a **coste 0,00 €/h** y superficie de ataque cero.
