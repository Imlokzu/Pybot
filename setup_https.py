import os
import subprocess
import sys

def create_self_signed_cert():
    """Create self-signed certificate for HTTPS"""
    cert_dir = os.path.join(os.path.dirname(__file__), 'certs')
    os.makedirs(cert_dir, exist_ok=True)
    
    cert_file = os.path.join(cert_dir, 'cert.pem')
    key_file = os.path.join(cert_dir, 'key.pem')
    
    # Check if cert already exists
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"✅ Certificate already exists at {cert_file}")
        return cert_file, key_file
    
    # Try using openssl
    try:
        print("Creating self-signed certificate...")
        subprocess.run([
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', key_file, '-out', cert_file,
            '-days', '365', '-nodes',
            '-subj', '/CN=localhost'
        ], check=True)
        print(f"✅ Certificate created at {cert_file}")
        return cert_file, key_file
    except FileNotFoundError:
        print("❌ OpenSSL not found. Installing via Python...")
        
        # Use Python's ssl module to create cert
        try:
            import ssl
            import socket
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.backends import default_backend
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            import datetime
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
                backend=default_backend()
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.datetime.utcnow()
            ).not_valid_after(
                datetime.datetime.utcnow() + datetime.timedelta(days=365)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName(u"localhost"),
                    x509.DNSName(u"127.0.0.1"),
                ]),
                critical=False,
            ).sign(private_key, hashes.SHA256(), default_backend())
            
            # Write private key
            with open(key_file, "wb") as f:
                f.write(private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.TraditionalOpenSSL,
                    encryption_algorithm=serialization.NoEncryption()
                ))
            
            # Write certificate
            with open(cert_file, "wb") as f:
                f.write(cert.public_bytes(serialization.Encoding.PEM))
            
            print(f"✅ Certificate created at {cert_file}")
            return cert_file, key_file
            
        except ImportError:
            print("❌ Cryptography module not found. Installing...")
            subprocess.run([sys.executable, "-m", "pip", "install", "cryptography"], check=True)
            print("Please run this script again.")
            return None, None

if __name__ == '__main__':
    cert_file, key_file = create_self_signed_cert()
    if cert_file and key_file:
        print(f"\n✅ HTTPS Setup Complete!")
        print(f"Certificate: {cert_file}")
        print(f"Key: {key_file}")
    else:
        print("❌ Failed to create certificate")
        sys.exit(1)
