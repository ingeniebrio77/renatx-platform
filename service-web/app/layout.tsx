import type { Metadata } from "next";
import React from "react";
import "./globals.css";

export const metadata: Metadata = {
  title: "Renatx Cloud & Systems | Franco Renato Palavecino (renatx.com)",
  description:
    "Ingeniería Cloud, Administración de Sistemas GNU/Linux, Redes e Infraestructura como Código (Terraform, Ansible, Podman) en Hamburgo, Alemania.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
