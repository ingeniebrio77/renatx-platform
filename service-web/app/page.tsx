"use client";

/**
 * ============================================================================
 * WEB COMERCIAL BILINGÜE (ES / DE) — RENATX (renatx.com)
 * Autor: Franco Renato Palavecino (Ottensen, Hamburg, DE)
 * ============================================================================
 * Incluye:
 * 1. Conmutador instantáneo Español (ES) / Alemán (DE).
 * 2. Catálogo de Servicios 1-a-1 (Soporte Remoto S.O.S., Mentoría FISI/AWS/Network+,
 *    y Bono 5 sesiones DevOps) conectados a Stripe Checkout (/api/billing/checkout).
 * 3. Sala de Asistencia Remota Efímera con RustDesk (/api/support/status) +
 *    Panel de Control del Instructor (JWT) para encender/apagar el nodo por horas.
 * ============================================================================
 */

import React, { useEffect, useState } from "react";

type Lang = "es" | "de";

interface RustDeskStatus {
  active: boolean;
  status_label: string;
  id_server: string;
  relay_server: string;
  public_key: string;
  started_at_utc: string | null;
  elapsed_minutes: number;
  hourly_rate_eur: number;
  estimated_session_cost_eur: number;
  instructions_es: string;
  instructions_de: string;
}

const I18N = {
  es: {
    badge: "SOPORTE REMOTO LINUX/CLOUD & MENTORÍA 1-A-1 EN DIRECTO",
    heroTitle: "Resolución experta en tus servidores y formación práctica sin rodeos.",
    heroSubtitle:
      "Soy Franco Renato Palavecino, Administrador de Sistemas GNU/Linux y Docente IT en Hamburgo. Te ayudo en vivo mediante sesiones privadas (con servidor propio RustDesk cifrado punto a punto) a resolver incidencias críticas, desplegar infraestructura con Terraform/Ansible/Podman o aprobar tus certificaciones técnicas.",
    ctaCatalog: "Ver Servicios y Precios",
    ctaRustdesk: "Sala de Soporte Remoto (RustDesk)",
    servicesTitle: "Servicios 1-a-1 y Mentoría Técnica",
    servicesSub:
      "Reserva directa con precio cerrado. Todas las sesiones incluyen conexión remota segura o laboratorio compartido.",
    bookBtn: "Reservar y Pagar con Stripe",
    bookingMsg: "Procesando reserva...",
    services: [
      {
        id: "support_sos_1h",
        tag: "ASISTENCIA INMEDIATA · 60 MIN",
        title: "Soporte Remoto S.O.S. (Linux, Redes & Contenedores)",
        price: "65 €",
        unit: "/ sesión de 1 hora",
        desc: "Diagnóstico y solución en directo sobre tu servidor o estación de trabajo mediante nuestro nodo privado RustDesk.",
        features: [
          "Troubleshooting en Arch, Debian, Ubuntu y RHEL",
          "Arreglo de contenedores Podman / Docker y proxies Traefik / Nginx",
          "Diagnóstico de redes TCP/IP, cortafuegos UFW/iptables y SSH",
          "Servidor RustDesk dedicado en Alemania (100% privado, sin terceros)",
        ],
      },
      {
        id: "mentoring_1h",
        tag: "DOCENCIA IT & CERTIFICACIONES · 60 MIN",
        title: "Mentoría 1-a-1: Fachinformatiker / Network+ / AWS",
        price: "49 €",
        unit: "/ clase de 60 min",
        desc: "Tutoría individual adaptada a tu ritmo (en español o alemán) con un instructor experimentado en formación IT en Alemania (IAD).",
        features: [
          "Preparación práctica para exámenes IHK (Fachinformatiker FISI)",
          "Dominio de subredes, VLANs, routing y seguridad (CompTIA Network+ 1,0)",
          "Arquitectura en AWS (Solutions Architect SAA-C03) y Linux desde cero",
          "Material didáctico claro y resolución de ejercicios en vivo",
        ],
      },
      {
        id: "devops_pack_5h",
        tag: "PROGRAMA PRÁCTICO · BONO 5 HORAS",
        title: "Mentoría Hands-On: Tu Propia Plataforma DevOps",
        price: "220 €",
        unit: "/ bono 5 sesiones (ahorras 25 €)",
        desc: "Construimos juntos tu infraestructura soberana desde cero: dominio propio, VPS en Hetzner/Proxmox, Terraform, Ansible y Podman.",
        features: [
          "5 sesiones 1-a-1 de 60 minutos adaptadas a tu proyecto real",
          "Automatización completa con Terraform + Ansible paso a paso",
          "Despliegue seguro con Podman Rootless, Traefik v3 y TLS automático",
          "Control de costes Cloud (FinOps) entre preproducción y producción",
        ],
      },
    ],
    rustdeskSectionTitle: "Centro de Asistencia Remota Bajo Demanda (RustDesk)",
    rustdeskSectionSub:
      "Para garantizar máxima privacidad (DSGVO) y coste mínimo, mi servidor de soporte remoto en Alemania solo se enciende durante tu sesión programada.",
    clientBoxTitle: "Datos de Conexión para el Cliente / Alumno",
    adminBoxTitle: "Panel del Instructor (Control por Horas / Minutos)",
    adminBoxSub:
      "Autentícate con tu token JWT de administrador para encender o destruir la instancia de soporte remoto.",
    loginAdminBtn: "1. Autenticar Instructor (JWT)",
    startNodeBtn: "Encender Nodo RustDesk (0,007 €/h)",
    stopNodeBtn: "Apagar / Destruir Nodo (Volver a 0,00 €/h)",
    copyBtn: "Copiar",
  },
  de: {
    badge: "LINUX/CLOUD REMOTE-SUPPORT & 1:1 IT-MENTORING LIVE AUS HAMBURG",
    heroTitle: "Direkte Expertenhilfe für Ihre Server & praxisnahes IT-Mentoring.",
    heroSubtitle:
      "Ich bin Franco Renato Palavecino, GNU/Linux-Systemadministrator und IT-Trainer in Hamburg-Ottensen. Ich unterstütze Sie live über meinen eigenen, Ende-zu-Ende-verschlüsselten RustDesk-Server bei Server-Störungen, IaC-Deployments (Terraform, Ansible, Podman) oder Ihrer IHK-/Zertifizierungsprüfung.",
    ctaCatalog: "Leistungen & Preise ansehen",
    ctaRustdesk: "Remote-Support-Raum (RustDesk)",
    servicesTitle: "1:1 Remote-Services & IT-Mentoring",
    servicesSub:
      "Transparente Festpreise ohne versteckte Kosten. Alle Sitzungen finden auf Wunsch auf Deutsch oder Spanisch statt.",
    bookBtn: "Jetzt buchen & via Stripe zahlen",
    bookingMsg: "Buchung wird erstellt...",
    services: [
      {
        id: "support_sos_1h",
        tag: "SOFORTHILFE · 60 MINUTEN",
        title: "Remote-Support S.O.S. (Linux, Netzwerke & Container)",
        price: "65 €",
        unit: "/ 1 Stunde Live-Support",
        desc: "Gemeinsame Fehleranalyse und Behebung direkt auf Ihrem System über unseren dedizierten RustDesk-Server in Deutschland.",
        features: [
          "Troubleshooting für Debian, Ubuntu, RHEL und Arch Linux",
          "Podman Rootless / Docker, Traefik v3 Reverse Proxy & TLS-Zertifikate",
          "Netzwerk-Diagnose (TCP/IP, Routing, UFW/Firewall, SSH-Hardening)",
          "100 % DSGVO-konform über eigenen deutschen RustDesk-Knoten",
        ],
      },
      {
        id: "mentoring_1h",
        tag: "IT-TRAINING & PRÜFUNG · 60 MINUTEN",
        title: "1:1 Mentoring: Fachinformatiker (FISI) / Network+ / AWS",
        price: "49 €",
        unit: "/ 60 Min. Einzeltraining",
        desc: "Individueller Einzelunterricht für Auszubildende, Umschüler und IT-Einsteiger durch einen erfahrenen Dozenten (ehem. IAD).",
        features: [
          "Gezielte Vorbereitung auf die IHK-Abschlussprüfung (Fachinformatiker)",
          "Netzwerktechnik verstehen: Subnetting, VLANs, TCP/IP (Network+ Note 1,0)",
          "AWS Cloud-Architektur (SAA-C03) & Linux-Administration sicher beherrschen",
          "Geduldige, strukturierte Didaktik mit Live-Übungen",
        ],
      },
      {
        id: "devops_pack_5h",
        tag: "HANDS-ON INTENSIVPAKET · 5 STUNDEN",
        title: "Praxis-Begleitung: Ihre eigene Cloud- & DevOps-Plattform",
        price: "220 €",
        unit: "/ 5er-Paket (Sie sparen 25 €)",
        desc: "Wir bauen gemeinsam Ihre produktionsreife Infrastruktur auf: Eigene Domain, Hetzner/Proxmox, Terraform, Ansible & Podman.",
        features: [
          "5 persönliche 1:1-Sitzungen à 60 Minuten an Ihrem echten Projekt",
          "Infrastructure as Code (IaC) mit Terraform und Ansible Schritt für Schritt",
          "Sichere Container-Orchestrierung mit Podman Rootless & Traefik",
          "FinOps-Kostenkontrolle für Pre-Production und Production",
        ],
      },
    ],
    rustdeskSectionTitle: "On-Demand Remote-Support-Zentrum (RustDesk)",
    rustdeskSectionSub:
      "Für maximale Sicherheit (Null-Angriffsfläche im Ruhezustand) und minimale Kosten wird der RustDesk-Server nur für die Dauer unserer Sitzung gestartet.",
    clientBoxTitle: "Verbindungsdaten für Kunden & Teilnehmer",
    adminBoxTitle: "Dozenten-Steuerung (Abrechnung nach Stunden / Minuten)",
    adminBoxSub:
      "Mit Administrator-JWT anmelden, um die flüchtige RustDesk-Instanz für eine Sitzung zu starten oder zu beenden.",
    loginAdminBtn: "1. Als Dozent anmelden (JWT)",
    startNodeBtn: "RustDesk-Instanz starten (0,007 €/Std.)",
    stopNodeBtn: "Instanz stoppen / zerstören (0,00 €/Std.)",
    copyBtn: "Kopieren",
  },
};

export default function HomePage() {
  const [lang, setLang] = useState<Lang>("es");
  const t = I18N[lang];

  const [healthOk, setHealthOk] = useState<boolean>(false);
  const [rustdesk, setRustdesk] = useState<RustDeskStatus | null>(null);
  const [jwtToken, setJwtToken] = useState<string | null>(null);

  const [checkoutResult, setCheckoutResult] = useState<Record<string, unknown> | null>(null);
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null);
  const [supportLoading, setSupportLoading] = useState<boolean>(false);

  async function refreshStatus() {
    try {
      const [hRes, sRes] = await Promise.all([
        fetch("/api/health"),
        fetch("/api/support/status"),
      ]);
      if (hRes.ok) setHealthOk(true);
      if (sRes.ok) {
        const sData = await sRes.json();
        setRustdesk(sData);
      }
    } catch {
      setHealthOk(false);
    }
  }

  useEffect(() => {
    refreshStatus();
  }, []);

  async function handleBookService(planId: string) {
    setLoadingPlan(planId);
    try {
      const res = await fetch("/api/billing/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          plan_id: planId,
          customer_email: "cliente@renatx.com",
          language: lang,
        }),
      });
      const data = await res.json();
      setCheckoutResult(data);
    } finally {
      setLoadingPlan(null);
    }
  }

  async function handleAdminLogin() {
    setSupportLoading(true);
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: "renato@renatx.com",
          password: "linux-admin-demo",
        }),
      });
      const data = await res.json();
      setJwtToken(data.access_token || null);
    } finally {
      setSupportLoading(false);
    }
  }

  async function handleToggleRustdesk(action: "start" | "stop") {
    if (!jwtToken) return;
    setSupportLoading(true);
    try {
      const res = await fetch(`/api/support/${action}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwtToken}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        setRustdesk(data);
      }
    } finally {
      setSupportLoading(false);
    }
  }

  return (
    <>
      {/* BARRA SUPERIOR CON CONMUTADOR BILINGÜE ES / DE */}
      <nav className="navbar">
        <div className="navbar-inner">
          <div className="brand-logo">
            <span className="brand-mark">RX</span>
            <span>
              renatx<span style={{ color: "var(--accent-cyan)" }}>.com</span>
            </span>
            <span
              className="mono"
              style={{
                fontSize: "0.75rem",
                color: "var(--text-secondary)",
                marginLeft: "0.5rem",
                fontWeight: 400,
              }}
            >
              Franco Renato Palavecino · Hamburg
            </span>
          </div>

          <div className="nav-pills mono">
            <span className="pill">
              <span className={`dot ${healthOk ? "dot-online" : "dot-offline"}`} />
              {healthOk ? "SYSTEM ONLINE" : "CONNECTING..."}
            </span>

            <span className="pill">
              <span
                className={`dot ${rustdesk?.active ? "dot-online" : "dot-offline"}`}
              />
              RustDesk: {rustdesk?.active ? "ACTIVE" : "STANDBY (0 €/h)"}
            </span>

            <div style={{ display: "flex", gap: "0.35rem" }}>
              <button
                onClick={() => setLang("es")}
                className="btn"
                style={{
                  padding: "0.28rem 0.65rem",
                  fontSize: "0.75rem",
                  background: lang === "es" ? "var(--color-primary)" : "rgba(15,23,42,0.8)",
                  color: "var(--color-primary-foreground)",
                  border: "1px solid rgba(148,163,184,0.25)",
                }}
              >
                🇪🇸 ES
              </button>
              <button
                onClick={() => setLang("de")}
                className="btn"
                style={{
                  padding: "0.28rem 0.65rem",
                  fontSize: "0.75rem",
                  background: lang === "de" ? "var(--color-primary)" : "rgba(15,23,42,0.8)",
                  color: "var(--color-primary-foreground)",
                  border: "1px solid rgba(148,163,184,0.25)",
                }}
              >
                🇩🇪 DE
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="container">
        {/* HERO COMERCIAL */}
        <section className="hero">
          <div className="card">
            <div className="hero-badge mono">
              <span>●</span> {t.badge}
            </div>
            <h1 className="hero-title">{t.heroTitle}</h1>
            <p className="hero-subtitle">{t.heroSubtitle}</p>

            <div style={{ display: "flex", gap: "0.85rem", flexWrap: "wrap", marginBottom: "1.4rem" }}>
              <a href="#servicios" className="btn btn-primary" style={{ textDecoration: "none" }}>
                {t.ctaCatalog}
              </a>
              <a
                href="#rustdesk"
                className="btn"
                style={{
                  textDecoration: "none",
                  background: "rgba(30,41,59,0.8)",
                  color: "var(--bg-surface-hover)",
                  border: "1px solid rgba(148,163,184,0.25)",
                }}
              >
                {t.ctaRustdesk}
              </a>
            </div>

            <div className="tag-list mono">
              <span className="tag">GNU/Linux (Arch · Debian · RHEL)</span>
              <span className="tag">CompTIA Network+ (Note 1,0)</span>
              <span className="tag">AWS Solutions Architect (SAA-C03)</span>
              <span className="tag">Terraform · Ansible · Podman</span>
              <span className="tag">IT-Trainer (FISI / AEVO)</span>
            </div>
          </div>

          {/* TARJETA DE PERFIL Y GARANTÍA TÉCNICA */}
          <div className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div>
              <div className="mono" style={{ color: "var(--accent-cyan)", fontSize: "0.78rem", marginBottom: "0.4rem" }}>
                DIRECTO CON EL ESPECIALISTA · SIN INTERMEDIARIOS
              </div>
              <h2 style={{ margin: "0 0 0.5rem 0", fontSize: "1.35rem" }}>
                Franco Renato Palavecino
              </h2>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginTop: 0 }}>
                {lang === "es"
                  ? "Experiencia real combinando administración de centros de datos (Proxmox/KVM, Kubernetes, Linux en NMMN Hamburgo) y docencia oficial para futuros especialistas IT en Alemania (IAD)."
                  : "Praxiserfahrung aus Rechenzentrumsbetrieb (Proxmox/KVM, Kubernetes, Linux bei NMMN Hamburg) kombiniert mit fundierter Lehrtätigkeit für angehende Fachinformatiker (IAD)."}
              </p>
            </div>

            <div className="metrics-grid mono">
              <div className="metric-box">
                <div className="metric-label">Idiomas de Sesión</div>
                <div className="metric-value" style={{ color: "var(--accent-cyan)" }}>
                  Español / Deutsch
                </div>
              </div>
              <div className="metric-box">
                <div className="metric-label">Canal Remoto</div>
                <div className="metric-value" style={{ color: "var(--accent-emerald)" }}>
                  RustDesk Privado
                </div>
              </div>
              <div className="metric-box">
                <div className="metric-label">Ubicación</div>
                <div className="metric-value">Hamburg, DE</div>
              </div>
              <div className="metric-box">
                <div className="metric-label">CompTIA Network+</div>
                <div className="metric-value">1,0 (Sehr gut)</div>
              </div>
            </div>
          </div>
        </section>

        {/* SECCIÓN DE CATÁLOGO DE SERVICIOS 1-A-1 Y MENTORÍA */}
        <section id="servicios" style={{ marginBottom: "2.5rem" }}>
          <div style={{ marginBottom: "1.25rem" }}>
            <h2 style={{ fontSize: "1.65rem", margin: "0 0 0.35rem 0" }}>{t.servicesTitle}</h2>
            <p style={{ color: "var(--text-secondary)", margin: 0 }}>{t.servicesSub}</p>
          </div>

          <div className="grid-3">
            {t.services.map((srv) => (
              <div
                key={srv.id}
                className="card"
                style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}
              >
                <div>
                  <div
                    className="mono"
                    style={{
                      color: "var(--accent-cyan)",
                      fontSize: "0.75rem",
                      fontWeight: 700,
                      marginBottom: "0.5rem",
                    }}
                  >
                    {srv.tag}
                  </div>
                  <h3 style={{ margin: "0 0 0.6rem 0", fontSize: "1.2rem" }}>{srv.title}</h3>
                  <div style={{ marginBottom: "0.85rem" }}>
                    <span style={{ fontSize: "2rem", fontWeight: 800, color: "var(--bg-base)" }}>
                      {srv.price}
                    </span>{" "}
                    <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>{srv.unit}</span>
                  </div>
                  <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", marginBottom: "1rem" }}>
                    {srv.desc}
                  </p>
                  <ul
                    style={{
                      paddingLeft: "1.1rem",
                      margin: "0 0 1.5rem 0",
                      color: "var(--text-primary)",
                      fontSize: "0.86rem",
                    }}
                  >
                    {srv.features.map((f, idx) => (
                      <li key={idx} style={{ marginBottom: "0.45rem" }}>
                        {f}
                      </li>
                    ))}
                  </ul>
                </div>

                <button
                  onClick={() => handleBookService(srv.id)}
                  disabled={loadingPlan === srv.id}
                  className="btn btn-indigo"
                  style={{ width: "100%" }}
                >
                  {loadingPlan === srv.id ? t.bookingMsg : `${t.bookBtn} (${srv.price})`}
                </button>
              </div>
            ))}
          </div>

          {/* CONFIRMACIÓN DE RESERVA STRIPE */}
          {checkoutResult && (
            <div className="card" style={{ borderColor: "var(--accent-indigo)", marginTop: "1rem" }}>
              <div className="section-header">
                <h3 className="section-title" style={{ color: "var(--bg-surface)" }}>
                  ✅ {String(checkoutResult.service_title)} — {String(checkoutResult.amount_eur)} EUR
                </h3>
                <span className="tag mono">Stripe Session: {String(checkoutResult.session_id)}</span>
              </div>
              <p style={{ color: "var(--bg-surface-hover)", margin: "0 0 0.75rem 0", fontSize: "0.95rem" }}>
                {String(checkoutResult.message)}
              </p>
              <div className="mono" style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
                Checkout URL:{" "}
                <span style={{ color: "var(--accent-cyan)" }}>{String(checkoutResult.checkout_url)}</span>
              </div>
            </div>
          )}
        </section>

        {/* SECCIÓN DE SOPORTE REMOTO BAJO DEMANDA CON RUSTDESK */}
        <section id="rustdesk" style={{ marginBottom: "2rem" }}>
          <div style={{ marginBottom: "1.25rem" }}>
            <h2 style={{ fontSize: "1.65rem", margin: "0 0 0.35rem 0" }}>
              {t.rustdeskSectionTitle}
            </h2>
            <p style={{ color: "var(--text-secondary)", margin: 0 }}>{t.rustdeskSectionSub}</p>
          </div>

          <div className="grid-2">
            {/* PANEL PARA EL CLIENTE / ALUMNO */}
            <div className="card">
              <div className="section-header">
                <h3 className="section-title">🖥️ {t.clientBoxTitle}</h3>
                <span
                  className="pill mono"
                  style={{
                    borderColor: rustdesk?.active ? "var(--accent-emerald)" : "var(--text-muted)",
                    color: rustdesk?.active ? "var(--state-online-foreground)" : "var(--text-secondary)",
                  }}
                >
                  <span className={`dot ${rustdesk?.active ? "dot-online" : "dot-offline"}`} />
                  {rustdesk?.status_label || "STANDBY"}
                </span>
              </div>

              <div className="metrics-grid mono" style={{ marginBottom: "1rem" }}>
                <div className="metric-box">
                  <div className="metric-label">ID Server (hbbs)</div>
                  <div className="metric-value" style={{ fontSize: "0.9rem", color: "var(--accent-cyan)" }}>
                    {rustdesk?.id_server || "—"}
                  </div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Relay Server (hbbr)</div>
                  <div className="metric-value" style={{ fontSize: "0.9rem", color: "var(--accent-cyan)" }}>
                    {rustdesk?.relay_server || "—"}
                  </div>
                </div>
              </div>

              <div className="metric-box mono" style={{ marginBottom: "1rem" }}>
                <div className="metric-label">Public Key (Ed25519 Mandatory Encryption)</div>
                <div
                  className="metric-value"
                  style={{ fontSize: "0.82rem", wordBreak: "break-all", color: "var(--accent-emerald)" }}
                >
                  {rustdesk?.public_key || "—"}
                </div>
              </div>

              <p style={{ color: "var(--text-secondary)", fontSize: "0.86rem", margin: 0 }}>
                {lang === "de" ? rustdesk?.instructions_de : rustdesk?.instructions_es}
              </p>
            </div>

            {/* PANEL DE CONTROL DEL INSTRUCTOR (POR HORAS / MINUTOS) */}
            <div className="card">
              <div className="section-header">
                <h3 className="section-title">⚡ {t.adminBoxTitle}</h3>
                <span className="tag mono">Hetzner CX22 · 0,007 €/h</span>
              </div>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.88rem", marginTop: 0 }}>
                {t.adminBoxSub}
              </p>

              <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
                {!jwtToken ? (
                  <button
                    onClick={handleAdminLogin}
                    disabled={supportLoading}
                    className="btn btn-primary"
                  >
                    🔐 {t.loginAdminBtn}
                  </button>
                ) : !rustdesk?.active ? (
                  <button
                    onClick={() => handleToggleRustdesk("start")}
                    disabled={supportLoading}
                    className="btn btn-emerald"
                  >
                    ▶ {t.startNodeBtn}
                  </button>
                ) : (
                  <button
                    onClick={() => handleToggleRustdesk("stop")}
                    disabled={supportLoading}
                    className="btn"
                    style={{ background: "var(--state-error)", color: "var(--color-primary-foreground)" }}
                  >
                    ⏹ {t.stopNodeBtn}
                  </button>
                )}
              </div>

              <div className="metrics-grid mono">
                <div className="metric-box">
                  <div className="metric-label">Tiempo de Sesión Activa</div>
                  <div className="metric-value">
                    {rustdesk?.active ? `${rustdesk.elapsed_minutes} min` : "0 min (Apagado)"}
                  </div>
                </div>
                <div className="metric-box">
                  <div className="metric-label">Coste Acumulado Sesión</div>
                  <div className="metric-value" style={{ color: "var(--accent-emerald)" }}>
                    {rustdesk?.active
                      ? `${rustdesk.estimated_session_cost_eur.toFixed(4)} €`
                      : "0,0000 €"}
                  </div>
                </div>
              </div>

              <div className="terminal-window">
                <div className="terminal-bar mono">
                  <span>Comando de Infraestructura (Local / Cloud)</span>
                  <span>FinOps Efímero</span>
                </div>
                <pre className="terminal-body mono" style={{ maxHeight: "120px" }}>
                  {`# Levantar servidor RustDesk en local (Podman):
$ make rustdesk-local-up

# Levantar nodo efímero en Hetzner (0,007 €/h) y destruir al acabar:
$ make rustdesk-cloud-up
$ make rustdesk-cloud-down`}
                </pre>
              </div>
            </div>
          </div>
        </section>

        <footer className="footer mono">
          <div>
            <strong>RENATX.COM</strong> · Franco Renato Palavecino · Ottensen, Hamburg (DE)
          </div>
          <div>
            Email: <span style={{ color: "var(--accent-cyan)" }}>renatop@disroot.org</span> · LinkedIn:{" "}
            <span style={{ color: "var(--accent-cyan)" }}>linkedin.com/in/re-pal</span>
          </div>
        </footer>
      </div>
    </>
  );
}
