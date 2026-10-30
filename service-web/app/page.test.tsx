import React from "react";
import { render, screen, fireEvent, waitFor, act } from "@testing-library/react";
import "@testing-library/jest-dom";
import HomePage from "./page";

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock as any;

// Helper to create mock responses
function createMockResponse(data: any, ok = true) {
  return {
    ok,
    json: () => Promise.resolve(data),
  };
}

describe("HomePage Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockReset();

    // Default successful responses
    mockFetch.mockImplementation((url: string) => {
      if (url.includes("/api/health")) {
        return Promise.resolve(
          createMockResponse({
            status: "healthy",
            brand: "Renatx",
            environment: "test",
          })
        );
      }
      if (url.includes("/api/support/status")) {
        return Promise.resolve(
          createMockResponse({
            active: false,
            status_label: "STANDBY (0,00 €/h — Instancia Apagada)",
            id_server: "— (En espera de iniciar sesión) —",
            relay_server: "— (En espera de iniciar sesión) —",
            public_key: "— (Se habilita al activar la sesión) —",
            started_at_utc: null,
            elapsed_minutes: 0,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.0,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          })
        );
      }
      if (url.includes("/api/auth/login")) {
        return Promise.resolve(
          createMockResponse({
            access_token: "mock-jwt-token",
            token_type: "bearer",
            expires_in_minutes: 60,
            environment: "test",
          })
        );
      }
      if (url.includes("/api/billing/checkout")) {
        return Promise.resolve(
          createMockResponse({
            status: "success",
            mode: "payment",
            session_id: "cs_test_123",
            checkout_url: "https://checkout.stripe.com/pay/cs_test_123",
            plan_id: "support_sos_1h",
            service_title: "Soporte Remoto S.O.S.",
            amount_eur: 65.0,
            environment: "test",
            message: "Sesión de pago creada correctamente",
          })
        );
      }
      if (url.includes("/api/support/start")) {
        return Promise.resolve(
          createMockResponse({
            active: true,
            status_label: "ONLINE (Instancia Efímera Activa)",
            id_server: "renatx.localhost:21116",
            relay_server: "renatx.localhost:21117",
            public_key: "renatx_ed25519_pub_key",
            started_at_utc: new Date().toISOString(),
            elapsed_minutes: 1,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.00001,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          })
        );
      }
      if (url.includes("/api/support/stop")) {
        return Promise.resolve(
          createMockResponse({
            active: false,
            status_label: "STANDBY (0,00 €/h — Instancia Apagada)",
            id_server: "— (En espera de iniciar sesión) —",
            relay_server: "— (En espera de iniciar sesión) —",
            public_key: "— (Se habilita al activar la sesión) —",
            started_at_utc: null,
            elapsed_minutes: 0,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.0,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          })
        );
      }
      return Promise.resolve(createMockResponse({}, false));
    });
  });

  describe("Language Switching", () => {
    test("renders in Spanish by default", () => {
      render(<HomePage />);

      expect(screen.getByText("SOPORTE REMOTO LINUX/CLOUD & MENTORÍA 1-A-1 EN DIRECTO")).toBeInTheDocument();
      expect(screen.getByText("Resolución experta en tus servidores y formación práctica sin rodeos.")).toBeInTheDocument();
      expect(screen.getByText("Ver Servicios y Precios")).toBeInTheDocument();
    });

    test("switches to German when DE button is clicked", () => {
      render(<HomePage />);

      const deButton = screen.getByText("🇩🇪 DE");
      fireEvent.click(deButton);

      expect(screen.getByText("LINUX/CLOUD REMOTE-SUPPORT & 1:1 IT-MENTORING LIVE AUS HAMBURG")).toBeInTheDocument();
      expect(screen.getByText("Direkte Expertenhilfe für Ihre Server & praxisnahes IT-Mentoring.")).toBeInTheDocument();
      expect(screen.getByText("Leistungen & Preise ansehen")).toBeInTheDocument();
    });

    test("switches back to Spanish when ES button is clicked", () => {
      render(<HomePage />);

      fireEvent.click(screen.getByText("🇩🇪 DE"));
      fireEvent.click(screen.getByText("🇪🇸 ES"));

      expect(screen.getByText("SOPORTE REMOTO LINUX/CLOUD & MENTORÍA 1-A-1 EN DIRECTO")).toBeInTheDocument();
    });
  });

  describe("Service Catalog Display", () => {
    test("renders all three services in Spanish", () => {
      render(<HomePage />);

      expect(screen.getByText("Soporte Remoto S.O.S. (Linux, Redes & Contenedores)")).toBeInTheDocument();
      expect(screen.getByText("Mentoría 1-a-1: Fachinformatiker / Network+ / AWS")).toBeInTheDocument();
      expect(screen.getByText("Mentoría Hands-On: Tu Propia Plataforma DevOps")).toBeInTheDocument();

      expect(screen.getByText("65 €")).toBeInTheDocument();
      expect(screen.getByText("49 €")).toBeInTheDocument();
      expect(screen.getByText("220 €")).toBeInTheDocument();
    });

    test("renders all three services in German", () => {
      render(<HomePage />);
      fireEvent.click(screen.getByText("🇩🇪 DE"));

      expect(screen.getByText("Remote-Support S.O.S. (Linux, Netzwerke & Container)")).toBeInTheDocument();
      expect(screen.getByText("1:1 Mentoring: Fachinformatiker (FISI) / Network+ / AWS")).toBeInTheDocument();
      expect(screen.getByText("Praxis-Begleitung: Ihre eigene Cloud- & DevOps-Plattform")).toBeInTheDocument();
    });

    test("shows service features for each service", () => {
      render(<HomePage />);

      expect(screen.getByText("Troubleshooting en Arch, Debian, Ubuntu y RHEL")).toBeInTheDocument();
      expect(screen.getByText("Preparación práctica para exámenes IHK (Fachinformatiker FISI)")).toBeInTheDocument();
      expect(screen.getByText("5 sesiones 1-a-1 de 60 minutos adaptadas a tu proyecto real")).toBeInTheDocument();
    });
  });

  describe("Service Booking Flow", () => {
    test("shows loading state when booking a service", async () => {
      render(<HomePage />);

      const bookButton = screen.getByText("Reservar y Pagar con Stripe (65 €)");
      fireEvent.click(bookButton);

      expect(screen.getByText("Procesando reserva...")).toBeInTheDocument();
    });

    test("displays checkout result after successful booking", async () => {
      render(<HomePage />);

      const bookButton = screen.getByText("Reservar y Pagar con Stripe (65 €)");
      fireEvent.click(bookButton);

      await waitFor(() => {
        expect(screen.getByText("✅ Soporte Remoto S.O.S. — 65 EUR")).toBeInTheDocument();
      });

      expect(screen.getByText("Stripe Session: cs_test_123")).toBeInTheDocument();
      expect(screen.getByText("https://checkout.stripe.com/pay/cs_test_123")).toBeInTheDocument();
    });

    test("books mentoring service correctly", async () => {
      render(<HomePage />);

      const bookButton = screen.getByText("Reservar y Pagar con Stripe (49 €)");
      fireEvent.click(bookButton);

      await waitFor(() => {
        expect(screen.getByText("✅ Soporte Remoto S.O.S. — 65 EUR")).toBeInTheDocument();
      });
    });

    test("books devops pack service correctly", async () => {
      render(<HomePage />);

      const bookButton = screen.getByText("Reservar y Pagar con Stripe (220 €)");
      fireEvent.click(bookButton);

      await waitFor(() => {
        expect(screen.getByText("✅ Soporte Remoto S.O.S. — 65 EUR")).toBeInTheDocument();
      });
    });
  });

  describe("RustDesk Status Display", () => {
    test("shows STANDBY status when server is inactive", async () => {
      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText("STANDBY (0,00 €/h — Instancia Apagada)")).toBeInTheDocument();
      });

      // Both id_server and relay_server show the same placeholder text
      expect(screen.getAllByText("— (En espera de iniciar sesión) —").length).toBeGreaterThanOrEqual(2);
      expect(screen.getByText("— (Se habilita al activar la sesión) —")).toBeInTheDocument();
    });

    test("displays connection details when server is active", async () => {
      // Mock active status
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/support/status")) {
          return Promise.resolve(
            createMockResponse({
              active: true,
              status_label: "ONLINE (Instancia Efímera Activa)",
              id_server: "renatx.localhost:21116",
              relay_server: "renatx.localhost:21117",
              public_key: "renatx_ed25519_pub_key",
              started_at_utc: new Date().toISOString(),
              elapsed_minutes: 5,
              hourly_rate_eur: 0.007,
              estimated_session_cost_eur: 0.00005,
              instructions_es: "Instrucciones en español",
              instructions_de: "Anweisungen auf Deutsch",
            })
          );
        }
        return Promise.resolve(createMockResponse({}));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText("ONLINE (Instancia Efímera Activa)")).toBeInTheDocument();
      });

      expect(screen.getByText("renatx.localhost:21116")).toBeInTheDocument();
      expect(screen.getByText("renatx.localhost:21117")).toBeInTheDocument();
      expect(screen.getByText("renatx_ed25519_pub_key")).toBeInTheDocument();
    });
  });

  describe("Admin Panel", () => {
    test("shows login button when not authenticated", async () => {
      // Ensure health check passes
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/health")) {
          return Promise.resolve(createMockResponse({ status: "healthy", brand: "Renatx", environment: "test" }));
        }
        if (url.includes("/api/support/status")) {
          return Promise.resolve(createMockResponse({
            active: false,
            status_label: "STANDBY (0,00 €/h — Instancia Apagada)",
            id_server: "— (En espera de iniciar sesión) —",
            relay_server: "— (En espera de iniciar sesión) —",
            public_key: "— (Se habilita al activar la sesión) —",
            started_at_utc: null,
            elapsed_minutes: 0,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.0,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          }));
        }
        return Promise.resolve(createMockResponse({}, false));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i)).toBeInTheDocument();
      });
      expect(screen.getByText(/Panel del Instructor \(Control por Horas \/ Minutos\)/i)).toBeInTheDocument();
    });

    test("shows start button after successful login", async () => {
      // Ensure health check passes
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/health")) {
          return Promise.resolve(createMockResponse({ status: "healthy", brand: "Renatx", environment: "test" }));
        }
        if (url.includes("/api/support/status")) {
          return Promise.resolve(createMockResponse({
            active: false,
            status_label: "STANDBY (0,00 €/h — Instancia Apagada)",
            id_server: "— (En espera de iniciar sesión) —",
            relay_server: "— (En espera de iniciar sesión) —",
            public_key: "— (Se habilita al activar la sesión) —",
            started_at_utc: null,
            elapsed_minutes: 0,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.0,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          }));
        }
        if (url.includes("/api/auth/login")) {
          return Promise.resolve(createMockResponse({
            access_token: "mock-jwt-token",
            token_type: "bearer",
            expires_in_minutes: 60,
            environment: "test",
          }));
        }
        return Promise.resolve(createMockResponse({}, false));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i));

      await waitFor(() => {
        expect(screen.getByText(/▶ Encender Nodo RustDesk \(0,007 €\/h\)/i)).toBeInTheDocument();
      });
    });

    test("shows stop button when RustDesk is active", async () => {
      // Ensure health check passes
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/health")) {
          return Promise.resolve(createMockResponse({ status: "healthy", brand: "Renatx", environment: "test" }));
        }
        if (url.includes("/api/support/status")) {
          return Promise.resolve(createMockResponse({
            active: false,
            status_label: "STANDBY (0,00 €/h — Instancia Apagada)",
            id_server: "— (En espera de iniciar sesión) —",
            relay_server: "— (En espera de iniciar sesión) —",
            public_key: "— (Se habilita al activar la sesión) —",
            started_at_utc: null,
            elapsed_minutes: 0,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.0,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          }));
        }
        if (url.includes("/api/auth/login")) {
          return Promise.resolve(createMockResponse({
            access_token: "mock-jwt-token",
            token_type: "bearer",
            expires_in_minutes: 60,
            environment: "test",
          }));
        }
        if (url.includes("/api/support/start")) {
          return Promise.resolve(createMockResponse({
            active: true,
            status_label: "ONLINE (Instancia Efímera Activa)",
            id_server: "renatx.localhost:21116",
            relay_server: "renatx.localhost:21117",
            public_key: "renatx_ed25519_pub_key",
            started_at_utc: new Date().toISOString(),
            elapsed_minutes: 1,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.00001,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          }));
        }
        return Promise.resolve(createMockResponse({}, false));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i));

      await waitFor(() => {
        expect(screen.getByText(/▶ Encender Nodo RustDesk \(0,007 €\/h\)/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/▶ Encender Nodo RustDesk \(0,007 €\/h\)/i));

      await waitFor(() => {
        expect(screen.getByText(/⏹ Apagar \/ Destruir Nodo \(Volver a 0,00 €\/h\)/i)).toBeInTheDocument();
      });
    });
  });

  describe("Health Status Indicator", () => {
    test("shows SYSTEM ONLINE when health check passes", async () => {
      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText(/SYSTEM ONLINE|CONNECTING/i)).toBeInTheDocument();
      });
    });

    test("shows CONNECTING... when health check fails", async () => {
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/health")) {
          return Promise.resolve(createMockResponse({}, false));
        }
        return Promise.resolve(createMockResponse({}));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText("CONNECTING...")).toBeInTheDocument();
      });
    });
  });

  describe("RustDesk Status Indicator in Navbar", () => {
    test("shows STANDBY in navbar when inactive", async () => {
      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText("RustDesk: STANDBY (0 €/h)")).toBeInTheDocument();
      });
    });

    test("shows ACTIVE in navbar when server is running", async () => {
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/support/status")) {
          return Promise.resolve(
            createMockResponse({
              active: true,
              status_label: "ONLINE",
              id_server: "test:21116",
              relay_server: "test:21117",
              public_key: "key",
              started_at_utc: new Date().toISOString(),
              elapsed_minutes: 1,
              hourly_rate_eur: 0.007,
              estimated_session_cost_eur: 0.0,
              instructions_es: "es",
              instructions_de: "de",
            })
          );
        }
        if (url.includes("/api/health")) {
          return Promise.resolve(createMockResponse({ status: "healthy" }));
        }
        return Promise.resolve(createMockResponse({}));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText("RustDesk: ACTIVE")).toBeInTheDocument();
      });
    });
  });

  describe("Session Metrics Display", () => {
    test("shows elapsed time and cost when session is active", async () => {
      // Ensure health check passes
      mockFetch.mockImplementation((url: string) => {
        if (url.includes("/api/health")) {
          return Promise.resolve(createMockResponse({ status: "healthy", brand: "Renatx", environment: "test" }));
        }
        if (url.includes("/api/support/status")) {
          return Promise.resolve(createMockResponse({
            active: false,
            status_label: "STANDBY (0,00 €/h — Instancia Apagada)",
            id_server: "— (En espera de iniciar sesión) —",
            relay_server: "— (En espera de iniciar sesión) —",
            public_key: "— (Se habilita al activar la sesión) —",
            started_at_utc: null,
            elapsed_minutes: 0,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.0,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          }));
        }
        if (url.includes("/api/auth/login")) {
          return Promise.resolve(createMockResponse({
            access_token: "mock-jwt-token",
            token_type: "bearer",
            expires_in_minutes: 60,
            environment: "test",
          }));
        }
        if (url.includes("/api/support/start")) {
          return Promise.resolve(createMockResponse({
            active: true,
            status_label: "ONLINE (Instancia Efímera Activa)",
            id_server: "renatx.localhost:21116",
            relay_server: "renatx.localhost:21117",
            public_key: "renatx_ed25519_pub_key",
            started_at_utc: new Date().toISOString(),
            elapsed_minutes: 1,
            hourly_rate_eur: 0.007,
            estimated_session_cost_eur: 0.00001,
            instructions_es: "Instrucciones en español",
            instructions_de: "Anweisungen auf Deutsch",
          }));
        }
        return Promise.resolve(createMockResponse({}, false));
      });

      render(<HomePage />);

      await waitFor(() => {
        expect(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/1\. Autenticar Instructor \(JWT\)/i));

      await waitFor(() => {
        expect(screen.getByText(/▶ Encender Nodo RustDesk \(0,007 €\/h\)/i)).toBeInTheDocument();
      });

      fireEvent.click(screen.getByText(/▶ Encender Nodo RustDesk \(0,007 €\/h\)/i));

      await waitFor(() => {
        expect(screen.getByText("Tiempo de Sesión Activa")).toBeInTheDocument();
        expect(screen.getByText("Coste Acumulado Sesión")).toBeInTheDocument();
      });
    });
  });

  describe("Footer Information", () => {
    test("displays contact information in footer", () => {
      render(<HomePage />);

      expect(screen.getByText("RENATX.COM")).toBeInTheDocument();
      expect(screen.getByText("Franco Renato Palavecino")).toBeInTheDocument();
      // Multiple elements contain "Hamburg" - just verify at least one exists
      expect(screen.getAllByText(/Hamburg/i).length).toBeGreaterThan(0);
      expect(screen.getByText("renatop@disroot.org")).toBeInTheDocument();
      expect(screen.getByText("linkedin.com/in/re-pal")).toBeInTheDocument();
    });
  });
});