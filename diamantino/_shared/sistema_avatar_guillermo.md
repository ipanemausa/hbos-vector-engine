# SISTEMA AVATAR — Guillermo (maestro, 12-oct-2026)
> **Ecosistema Soberano HBOS-Diamantino · Arquitectura de Canvas Espacial Muse**  
> **Fecha:** 2026-10-12 | **Estado:** ✅ IDENTIDAD BLOQUEADA Y PATRÓN CONSOLIDADO  
> **Documento único que consolida identidad, patrón de movimientos, protocolo de producción, límites anatómicos y caminos descartados/aprobados. Todo lo aceptado queda aquí; nada se re-deriva.**

---

## 1. IDENTIDAD BLOQUEADA
* **Imagen aprobada:** `media-generation-avatar-sheet-tres-cuartos-v6-0-7fb508c7-e9b7-41f0-845a-23b5e0fd94e0.webp` (veredicto Guillermo: *"Está bien"*).
* **Bloque verbatim (en cada prompt de pose):**
  > *mismo rostro, gafas, pelo corto gris, sonrisa sutil de labios cerrados (dientes apenas visibles, jamás sonrisa grande), piel con bronceado moderado natural en cara y más profundo parejo en cuello/brazos/manos (nada rosáceo), camiseta negra por fuera con logo amarillo pequeño HB.OS, jean, zapatos negros, muñecas sin reloj, 1.87 m, complexión delgada/atlética, sin barriga, hombros ANCHOS rectos y nivelados (más anchos que el torso, nunca caídos), cuerpo erguido, cuello liso sin arrugas exageradas, sin papada colgante, sin huecos en mejillas, marcas de edad sutiles, textura de piel natural como fotografía genuina.*
* **Descartado:** Perfiles totalmente de lado (el modelo inventaba rasgos, papada, hueco en mandíbula). Para giros usar tres-cuartos o cadena encadenada.

---

## 2. PATRÓN DE MOVIMIENTOS COMPLETOS (Dirección Guillermo)
* **Brazos/manos — rotación total:** Cada pose en palma arriba, palma abajo, dorso, palma de frente, palma de lado, mano girada.
* **Simetría obligatoria:** Todo gesto de una mano existe en versión derecha e izquierda.
* **Piernas/peso:** Peso izquierda, peso derecha, pies juntos, postura amplia, paso medio con cada pierna; cambios de lado (no de helado).
* **Torso:** Erguido, adelante, atrás, izquierda, derecha.
* **Cabeza:** Arriba, abajo, izquierda, derecha, inclinación lateral.
* **Giros:** 180° = perfiles y tres-cuartos (ambos lados); **360° = rotación del CUERPO (torno), la cabeza acompaña** — ver §4. Nuca/espalda anclada por pelo, hombros y ropa; generada en cadena encadenada (~15° por eslabón, cada uno referencia al anterior).
* **Movimientos acoplados:** Los brazos van con la cintura/torso (señalar-derecha rota torso a la derecha, etc.); cambios de peso con cadera compensando. Cada pose de brazos existe en versión neutra y acoplada.

---

## 3. PROTOCOLO DE PRODUCCIÓN (Sellado 12-oct)
* **Fondo croma verde puro `#00FF00`** en prompt $\rightarrow$ ffmpeg colorkey $\rightarrow$ PNG transparente.
* **Encuadre consistente:** Cuerpo entero centrado, pies abajo, cabeza arriba, misma escala.
* **Catálogo en `poses-catalogo.md`:** Pose $\rightarrow$ archivo $\rightarrow$ combinación del patrón $\rightarrow$ estado.
* **Contact sheet por lote + revisión visual:** Cero piezas defectuosas al usuario.

---

## 4. LÍMITES ANATÓMICOS (Verificados 12-oct)
* **Cabeza sobre dorso quieto:** 70-90° por lado, máximo; 180° hacia un lado = imposible.
* **Barrido total izq $\rightarrow$ der:** $\approx$ 140-180° (la suma, no por lado).
* **Regla estricta:** Cabeza sola $\le$ ~80°; más allá, el torso acompaña.

---

## 5. CAMINOS: DESCARTADO vs APROBADO
* **DESCARTADO:**
  * Image-to-video directo desde un still (desfigura: cambia pelo, cara, piel, cuerpo, expresión — veredicto Guillermo 12-oct).
  * Modelo 3D con mesh/rig (la industria usa imagen + referencia, no 3D).
* **APROBADO:**
  * (a) **Stills con identidad bloqueada $\rightarrow$ interpolación** (ffmpeg minterpolate, demo `demo-interpolacion.mp4`).
  * (b) **Primer/último frame** (técnica del diplomado — 2-3 imágenes $\rightarrow$ animación; Wan 2.1 / 2.2 la trae nativa).
  * (c) **Modelos guiados por pose** (MimicMotion: 1 imagen + secuencia de poses) o por audio (HunyuanVideo-Avatar: 1 imagen + voz).
  * (d) **Kling tier gratis** para clips sutiles (~6/día).
* **Veredicto paisaje 12-oct:** La biblioteca de 200 poses NO es estrictamente necesaria para animar (la vía automática es 1 referencia + modelo guiado); la biblioteca vale como banco de keyframes, endpoints de interpolación y seguro. No se bota.

---

## 6. ESTADO DEL ARCHIVO Y NODO DE CANVAS MUSE
* **20 poses base verificadas:** `poses-lote1.jpg`, `poses-lote2.jpg`, `poses-catalogo.md`.
* **Persistencia local-first & GDrive:** `_MAESTRO\_SISTEMA_AVATAR_GUILLERMO_MAESTRA.md`.
* **Entidad Muse (`HBOSCanvasNode`):**
  * `type`: `"avatar_system"`
  * `id`: `"guillermo_avatar_core_v1"`
  * `title`: `"Sistema Avatar Guillermo (Maestro)"`
  * `status`: `"LOCKED_APPROVED"`
  * `pipeline`: `"FREELLMAPI_TTS" + "WAN21_I2V" + "MIMICMOTION"`
