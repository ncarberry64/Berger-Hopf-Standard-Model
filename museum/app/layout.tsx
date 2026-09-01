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
  title: 'BHSM Museum | Reconstructed Scientific Record',
  description:
    'The public entrance to the integrated Berger–Hopf Standard Model record, its particle ontology, AE2 event dynamics, and open physical-enclosure bridge.',
  icons: {
    icon: './bhsm-symbol.svg',
  },
  openGraph: {
    title: 'BHSM Museum | Reconstructed Scientific Record',
    description:
      'Explore the integrated BHSM corpus, animated calculations, provenance, and the exact boundary of the open physical-enclosure bridge.',
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
