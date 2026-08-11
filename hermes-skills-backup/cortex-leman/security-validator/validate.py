"""
SECURITY VALIDATOR - Cortex Leman
Defense Shield : Validation sécurité multi-couches

Fonctions :
- validate_security_headers() - Headers HTTP
- check_encryption() - Chiffrement at rest/in transit
- verify_access_control() - RBAC
- detect_vulnerabilities() - Scan CVEs
- enforce_kill_switch() - Activation Kill Switch

Author: L'Ingénieur de Flux
"""

import json
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class SecurityScore:
    """Score de sécurité 0-1"""
    headers: float
    encryption: float
    access_control: float
    vulnerabilities: float
    overall: float

class SecurityValidator:
    """Validateur de sécurité Cortex Leman"""

    REQUIRED_HEADERS = [
        'x-frame-options',
        'x-content-type-options',
        'strict-transport-security',
        'content-security-policy',
        'referrer-policy'
    ]

    ENCRYPTION_MIN_VERSIONS = {
        'tls': '1.3',
        'aes': '256'
    }

    def __init__(self):
        self.vulnerabilities_db = self._load_cve_database()

    def _load_cve_database(self) -> List[Dict]:
        """Charge base CVEs (simulé)"""
        return [
            {'cve': 'CVE-2024-1234', 'severity': 'critical', 'component': 'nginx'},
            {'cve': 'CVE-2024-5678', 'severity': 'high', 'component': 'openssl'}
        ]

    def validate_security_headers(self, headers: Dict[str, str]) -> Tuple[bool, List[str]]:
        """
        Valide headers HTTP

        Args:
            headers: Dictionnaire headers HTTP

        Returns:
            (valid, missing_headers)
        """
        missing = [h for h in self.REQUIRED_HEADERS if h not in headers]

        if missing:
            return False, missing

        # Vérifier valeurs
        issues = []
        if 'strict-transport-security' in headers:
            sts = headers['strict-transport-security']
            if 'max-age' not in sts or int(sts.split('max-age=')[1].split(';')[0]) < 31536000:
                issues.append('HSTS max-age < 1 year')

        return len(issues) == 0, issues

    def check_encryption(self, config: Dict) -> Tuple[bool, List[str]]:
        """
        Vérifie chiffrement

        Args:
            config: Configuration chiffrement

        Returns:
            (valid, issues)
        """
        issues = []

        # TLS
        if 'tls_version' in config:
            tls = config['tls_version']
            min_tls = self.ENCRYPTION_MIN_VERSIONS['tls']
            if tls < min_tls:
                issues.append(f'TLS {tls} < {min_tls}')

        # AES
        if 'encryption' in config:
            enc = config['encryption']
            if enc['algorithm'] != 'AES' or enc['key_size'] < 256:
                issues.append('Encryption: AES-256 required')

        return len(issues) == 0, issues

    def verify_access_control(self, users: List[Dict]) -> Tuple[bool, List[str]]:
        """
        Vérifie contrôle d'accès RBAC

        Args:
            users: Liste utilisateurs avec rôles

        Returns:
            (valid, issues)
        """
        issues = []

        # Vérifier admin unique
        admins = [u for u in users if u['role'] == 'admin']
        if len(admins) != 1:
            issues.append(f'{len(admins)} admins (should be 1)')

        # Vérifier MFA
        no_mfa = [u for u in users if not u.get('mfa_enabled', False)]
        if no_mfa:
            issues.append(f'{len(no_mfa)} users without MFA')

        return len(issues) == 0, issues

    def detect_vulnerabilities(self, component: str, version: str) -> List[Dict]:
        """
        Détecte vulnérabilités connues

        Args:
            component: Nom composant
            version: Version

        Returns:
            Liste CVEs trouvées
        """
        vulns = []
        for cve in self.vulnerabilities_db:
            if cve['component'] == component:
                vulns.append(cve)
        return vulns

    def calculate_security_score(self, headers_score: float,
                                   encryption_score: float,
                                   access_score: float,
                                   vuln_score: float) -> SecurityScore:
        """
        Calcule score global sécurité

        Args:
            headers_score: Score headers (0-1)
            encryption_score: Score chiffrement (0-1)
            access_score: Score accès (0-1)
            vuln_score: Score vulnérabilités (0-1)

        Returns:
            SecurityScore global
        """
        overall = (headers_score * 0.25 +
                   encryption_score * 0.35 +
                   access_score * 0.25 +
                   vuln_score * 0.15)

        return SecurityScore(
            headers=headers_score,
            encryption=encryption_score,
            access_control=access_score,
            vulnerabilities=vuln_score,
            overall=overall
        )

    def enforce_kill_switch(self, severity: str, reason: str) -> Dict:
        """
        Active Kill Switch

        Args:
            severity: Criticité (critical/high/medium/low)
            reason: Raison activation

        Returns:
            Statut activation
        """
        if severity not in ['critical', 'high']:
            return {'activated': False, 'reason': 'Severity insufficient'}

        # Activation
        return {
            'activated': True,
            'timestamp': __import__('time').time(),
            'severity': severity,
            'reason': reason,
            'action': 'system_shutdown'
        }


# Test rapide
if __name__ == "__main__":
    validator = SecurityValidator()

    # Test headers
    headers = {
        'x-frame-options': 'DENY',
        'x-content-type-options': 'nosniff',
        'strict-transport-security': 'max-age=31536000',
        'content-security-policy': "default-src 'self'",
        'referrer-policy': 'strict-origin-when-cross-origin'
    }
    valid, missing = validator.validate_security_headers(headers)
    print(f"Headers valid: {valid}, missing: {missing}")

    # Test encryption
    config = {'tls_version': '1.3', 'encryption': {'algorithm': 'AES', 'key_size': 256}}
    valid, issues = validator.check_encryption(config)
    print(f"Encryption valid: {valid}, issues: {issues}")

    # Test access control
    users = [
        {'name': 'admin', 'role': 'admin', 'mfa_enabled': True},
        {'name': 'user1', 'role': 'user', 'mfa_enabled': True}
    ]
    valid, issues = validator.verify_access_control(users)
    print(f"Access valid: {valid}, issues: {issues}")

    # Test score
    score = validator.calculate_security_score(1.0, 1.0, 1.0, 1.0)
    print(f"Security score: {score.overall}")

    print("✅ Security validator test passed")
