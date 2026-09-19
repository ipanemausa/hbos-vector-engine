# PLAN ESTRATÉGICO DE RENOVACIÓN Y EJECUCIÓN (OCTUBRE 2026)
### Ecosistema: HBOS-Diamantino · Arquitectura Agéntica Soberana
### Trazabilidad: `operation_id = 79` · Ciclo Mensual de Cuotas Nube
### Fecha de Emisión: 2026-09-19

---

## 1. CALENDARIO Y VENTANA DE RENOVACIÓN DE CUOTAS NUBE

| Proveedor Nube | Tipo de Cuenta / Asignación | Fecha Estimada de Reseteo | Capacidad Esperada al Renovar |
|---|---|---|---|
| **ElevenLabs Cloud** | Free Tier (10,000 créditos/mes) | 1° de Octubre de 2026 (00:00 UTC) | 10,000 créditos (~20-25 minutos de habla en v2) |
| **Alibaba DashScope** | Free Tier Asignado (Wan 2.1 I2V) | 1° de Octubre de 2026 (00:00 UTC) | ~50-100 segundos de video generativo Wan 2.1 |
| **Google Gemini API** | Free Tier Pay-as-you-go | Diario (Activo continuamente) | Inferencia ilimitada dentro de rate limits |

---

## 2. CAPACIDAD DE PRODUCCIÓN CON CRÉDITOS RENOVADOS

### Con 10,000 créditos en ElevenLabs:
- **Ep04 (Voz Narrativa Única P-18):** Consumo estimado de **~1,800 créditos** (3 minutos de locución con Diamantino / Adam).
- **Margen restante para Ep05 y Ep06:** ~8,200 créditos suficientes para producir 4 episodios completos adicionales bajo el Patrón P-18.

### Con cuota renovada en DashScope (Wan 2.1):
- **Ep04 Planos Pendientes:** 8 clips de 5s base (escalados con cinemática continua P-14 a 20s).
- **Consumo total requerido:** 8 llamadas de inferencia a `wan2.1-i2v-turbo`.

---

## 3. PROTOCOLO DE EJECUCIÓN SECUENCIAL (DÍA DE RENOVACIÓN)

```
[DÍA 1 - HORA 00:05]
│
├── 1. Verificación automática de cuota HTTP 200 en ElevenLabs & DashScope
│
├── 2. Ejecución de `produce_ep04_final.py`:
│   ├── Fase A: Síntesis de la voz narrativa unificada (10 bloques, Adam/Diamantino)
│   ├── Fase B: Normalización acústica EBU R128 (-14 LUFS, TP -1.0 dBTP)
│   ├── Fase C: Despacho concurrente de Planos 02 a 09 en Wan 2.1 I2V Cloud
│   ├── Fase D: Descarga de videos raw y post-procesamiento a 1080p 30fps H.264
│   └── Fase E: Concatenación de los 10 clips + Voiceover + BGM (-14 LUFS, Ducking P-05)
│
├── 3. Generación de los 4 Formatos Responsive (16:9, 9:16, 1:1, 4:5)
│
└── 4. Replicación triple P-03 y publicación oficial
```

---

## 4. PREPARACIÓN ANTICIPADA
Todos los insumos creativos, composiciones 1080p, pistas BGM y scripts de orquestación ya se encuentran programados, probados y listos en local y Google Drive para ejecutarse sin demora en cuanto se detecte saldo en las APIs.
