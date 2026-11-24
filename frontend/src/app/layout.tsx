import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/hooks/useAuth";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "PlacementIQ | Student Placement Analytics Platform",
  description:
    "AI-Powered Institutional Placement Intelligence, Live SSE Analytics, LangGraph Resume Parsing, and XGBoost Career Probability Engine.",
  keywords: [
    "Placement Analytics",
    "AI Resume Parser",
    "Campus Placements",
    "pgvector",
    "Next.js 14",
    "FastAPI",
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} min-h-full antialiased text-slate-800 dark:text-slate-100 bg-slate-50 dark:bg-slate-950`}>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
