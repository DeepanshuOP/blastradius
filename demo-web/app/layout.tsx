import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BlastRadius demo",
  description: "Execution-grounded change impact prediction for CI: recorded pipeline runs.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  );
}
