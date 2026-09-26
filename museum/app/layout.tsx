import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import './console.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/',
  ),
  title: 'BHSM Museum | Geometry, Evidence and Open Questions',
  description:
    'Explore the Berger–Hopf Standard Model: conditional structural results, historical screens, geometric interpretations and conventional reference data.',
  icons: {
    icon: './bhsm-symbol.svg',
  },
  alternates: {
    canonical: './',
  },
  openGraph: {
    title: 'BHSM Museum | The Scientific Record',
    description:
      'Particle families, shared interactions and testable differences: an accessible public collection with visible data provenance and open scientific limits.',
    images: ['./og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
