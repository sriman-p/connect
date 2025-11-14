import type { Metadata } from "next";
import "./globals.css";
import Providers from "./providers";
import AppLayout from "@/components/navigation/app-layout";

export const metadata: Metadata = {
  title: "Connect | Enterprise Collaboration Platform",
  description: "Connect - Combining the best of Linear, Slack, and Google Workspace",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <Providers>
          <AppLayout>
            {children}
          </AppLayout>
        </Providers>
      </body>
    </html>
  );
}
