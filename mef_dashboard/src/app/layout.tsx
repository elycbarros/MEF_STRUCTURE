import type { Metadata } from "next";
import { ScrollToTop } from "@/components/ScrollToTop";
import "katex/dist/katex.min.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "MEF STRUCTURAL SUITE",
  description: "Plataforma profissional de análise e dimensionamento estrutural via Elementos Finitos.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full antialiased">
      <body className="min-h-full flex flex-col">
        {children}
        <ScrollToTop />
      </body>
    </html>
  );
}
