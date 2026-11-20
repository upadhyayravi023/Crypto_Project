import "./globals.css";

export const metadata = {
  title: "DES IoT Security Console",
  description: "Encrypted virtual IoT telemetry and security monitoring dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
