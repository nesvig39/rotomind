import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "Rotomind - Fantasy NBA Intelligence",
  description:
    "AI-powered assistant for Fantasy NBA 8-Cat Rotisserie leagues. Analyze trades, optimize lineups, and dominate your league.",
  keywords: [
    "fantasy basketball",
    "NBA",
    "rotisserie",
    "8-cat",
    "trade analyzer",
    "lineup optimizer",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-sans min-h-screen`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
