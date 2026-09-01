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
  title: 'BHSM Museum | Norman P. Carberry Research Archive',
  description:
    'Real CMS Open Data in motion, the integrated Berger–Hopf Standard Model record, and Norman P. Carberry’s artifact-backed research archive.',
  icons: {
    icon: './bhsm-symbol.svg',
  },
  openGraph: {
    title: 'BHSM Museum | CMS Open Data and the BHSM Record',
    description:
      'Explore real CMS dimuon data, animated BHSM calculations, integrated provenance, and the open physical-identification bridge.',
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
