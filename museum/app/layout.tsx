import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';
import './console.css';
import './museum-deck.css';
import './children-of-bhsm.css';
import './berger-hopf.css';
import './bhsm-transition.css';

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
    type: 'website',
    url: 'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/',
    siteName: 'BHSM Museum',
    title: 'BHSM Museum | Geometry, Matter and Interaction',
    description:
      'Explore interactive exhibits on matter, forces and cosmology. Geometry, evidence and open scientific questions in the Berger–Hopf Standard Model.',
    images: [
      {
        url: 'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/bhsm-museum-social-2026-09-27.png',
        width: 1200,
        height: 630,
        type: 'image/png',
        alt: 'BHSM Museum — Geometry, matter and interaction, with linked geometric fibers in amber, lavender and cyan.',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BHSM Museum | Geometry, Matter and Interaction',
    description:
      'Explore interactive exhibits on matter, forces and cosmology. Geometry, evidence and open questions.',
    images: [
      {
        url: 'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/bhsm-museum-social-2026-09-27.png',
        alt: 'BHSM Museum — Geometry, matter and interaction, with linked geometric fibers in amber, lavender and cyan.',
      },
    ],
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
