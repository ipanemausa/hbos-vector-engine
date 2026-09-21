# -*- coding: utf-8 -*-
import asyncio
import time
import json
import uuid
from winrt.windows.security.credentials.ui import (
    UserConsentVerifier,
    UserConsentVerificationResult,
    UserConsentVerifierAvailability
)

class HBOSAuthUI:
    def __init__(self, timeout_minutes: int = 30):
        self.available = False
        self.timeout = timeout_minutes * 60  # segundos
        self.cache = {}  # {scope: {'token': str, 'expires_at': timestamp}}
        self.log_file = 'auth_ui_audit.json'

    async def check_availability(self) -> bool:
        res = await UserConsentVerifier.check_availability_async()
        self.available = (res == UserConsentVerifierAvailability.AVAILABLE)
        return self.available

    def is_token_valid(self, scope: str) -> bool:
        if scope not in self.cache:
            return False
        entry = self.cache[scope]
        return time.time() < entry['expires_at']

    async def request_verification(self, message: str) -> bool:
        if not self.available:
            await self.check_availability()
        if not self.available:
            print('[HBOS AUTH UI] [FAIL] Windows Hello no disponible')
            return False
        res = await UserConsentVerifier.request_verification_async(message)
        return (res == UserConsentVerificationResult.VERIFIED)

    def authorize(self, scope: str, message: str, force: bool = False) -> bool:
        # Regla R37: Si el token está vigente para el scope y no se fuerza, autorización inmediata sin pedir huella
        if not force and self.is_token_valid(scope):
            print(f'[HBOS AUTH UI] [CACHE_HIT] Autorizacion vigente para scope: {scope}')
            return True

        print(f'[HBOS AUTH UI] Solicitando huella Windows Hello para scope: {scope}')
        result = asyncio.run(self.request_verification(message))
        if result:
            token = str(uuid.uuid4())
            expires_at = time.time() + self.timeout
            self.cache[scope] = {'token': token, 'expires_at': expires_at}
            self._audit(scope, message, 'VERIFIED', expires_at)
            print(f'[HBOS AUTH UI] [TOKEN_EMITIDO] Scope: {scope}, expira en {self.timeout // 60} min')
            return True
        else:
            self._audit(scope, message, 'DENIED', None)
            print(f'[HBOS AUTH UI] [FAIL] Autorizacion denegada para scope: {scope}')
            return False

    def _audit(self, scope: str, message: str, result: str, expires_at):
        entry = {
            'timestamp': time.asctime(),
            'scope': scope,
            'message': message,
            'result': result,
            'expires_at': expires_at
        }
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry) + '\n')

    def invalidate(self, scope: str = None):
        if scope:
            self.cache.pop(scope, None)
        else:
            self.cache.clear()

if __name__ == '__main__':
    auth = HBOSAuthUI(timeout_minutes=30)
    avail = asyncio.run(auth.check_availability())
    print(f'[OK] Windows Hello UserConsentVerifier disponible: {avail}')
