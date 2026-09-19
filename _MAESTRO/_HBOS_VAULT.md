# HBOS VAULT — AGENTE DE SEGURIDAD Y CUSTODIA DE SECRETOS
### Ecosistema: HBOS-Diamantino · Vector Engine
### Tipo: Agente Interno · Categoría: Seguridad Criptográfica
### Trazabilidad: operation_id = 148 | Estado: Pendiente

---

## 1. DESCRIPCIÓN
HBOS VAULT es el guardián criptográfico que aísla y resguarda todas las API keys y credenciales del ecosistema. Implementa cifrado simétrico AES-256-GCM en reposo y mecanismos de descifrado efímero en memoria RAM, garantizando cero exposición en código o repositorios (L-27).

## 2. FUNCIONES
- Cifrado y descifrado seguro de tokens bajo demanda efímera.
- Rotación automática de claves cuando una cuenta alcanza el límite de tasa (429).
- Emisión de tokens de sesión soberanos (`hbos-sec-...`) para herramientas cliente.
- Registro inmutable de auditoría de cada consumo en Qdrant (`boveda_secretos`).

## 3. CÓMO USARLO
```python
# Obtención efímera de credencial en memoria RAM
with vault.solicitar_credencial("ELEVENLABS_API_KEY") as key_efimera:
    audio = sintetizar_locucion(texto, key_efimera)
# La clave es destruida de RAM al salir del bloque
```

## 4. DEPENDENCIAS
- Criptografía estándar (`cryptography.hazmat`, AES-256-GCM).
- Qdrant Cloud (colección `boveda_secretos`).
- Archivos locales seguros (`.env.local` en workspace aislado).

## 5. ESTADO
- **Estado Actual:** Pendiente de migración a servicio daemon permanente.
