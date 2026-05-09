import type { Metadata } from "next";
import { ScrollToTop } from "@/components/ScrollToTop";
import { Outfit } from "next/font/google";
import "katex/dist/katex.min.css";
import "./globals.css";

const outfit = Outfit({ 
  subsets: ["latin"],
  variable: "--font-outfit",
});

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
    <html lang="pt-BR" className={`h-full antialiased ${outfit.variable}`}>
      <body className="min-h-full flex flex-col font-sans selection:bg-blue-500/30">
        <div className="fixed inset-0 bg-[#050507] -z-20" />
        <div className="fixed inset-0 bg-grid-pattern opacity-[0.03] -z-10 pointer-events-none" />
        <div className="fixed inset-0 bg-gradient-to-tr from-blue-600/5 via-transparent to-purple-600/5 -z-10 pointer-events-none" />
        
        {children}
        <ScrollToTop />
      </body>
    </html>
  );
}
