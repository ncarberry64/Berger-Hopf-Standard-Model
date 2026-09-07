import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

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
  title: 'BHSM Museum | Geometry and the Pattern of Matter',
  description:
    'Explore the scientific potential of the Berger–Hopf Standard Model through particle families, forces, mixing and openly labeled sandbox comparisons.',
  icons: {
    icon: './bhsm-symbol.svg',
  },
  alternates: {
    canonical: './',
  },
  openGraph: {
    title: 'BHSM Museum | Could Geometry Explain the Pattern of Matter?',
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
