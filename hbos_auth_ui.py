# -*- coding: utf-8 -*-
import asyncio
import time
import json
from winrt.windows.security.credentials.ui import (
    UserConsentVerifier,
    UserConsentVerificationResult,
    UserConsentVerifierAvailability
)

class HBOSAuthUI:
    def __init__(self):
        self.available = False
        self.log_file = 'auth_ui_audit.json'

    async def check_availability(self) -> bool:
        res = await UserConsentVerifier.check_availability_async()
        self.available = (res == UserConsentVerifierAvailability.AVAILABLE)
        return self.available

    async def request_verification(self, message: str) -> bool:
        if not self.available:
            await self.check_availability()
        if not self.available:
            print('[HBOS AUTH UI] [FAIL] Windows Hello no disponible')
            return False
        res = await UserConsentVerifier.request_verification_async(message)
        success = (res == UserConsentVerificationResult.VERIFIED)
        audit_entry = {
            'timestamp': time.asctime(),
            'message': message,
            'result': res.name if hasattr(res, 'name') else str(res),
            'verified': success
        }
        with open(self.log_file, 'w', encoding='utf-8') as fi:
            json.dump(audit_entry, fi, indent=2)
        return success

    def authorize(self, message: str) -> bool:
        print('[HBOS AUTH UI] Solicitando autorizacion Windows Hello:', message)
        res = asyncio.run(self.request_verification(message))
        if res:
            print('[HBOS AUTH UI] [OK] Autorizacion concedida por huella')
        else:
            print('[HBOS AUTH UI] [FAIL] Autorizacion cancelada o denegada')
        return res

if __name__ == '__main__':
    a = HBOSAuthUI()
    avail = asyncio.run(a.check_availability())
    print('[OK] Windows Hello UserConsentVerifier disponible:', avail)
