#!/usr/bin/env python3
"""
hbos_anchor_vivo.py · Motor Canónico de Anchors Vivos (Regla R62)
Ecosistema Soberano HBOS-Diamantino · Modo Experto ALEJAVI

Implementa:
  - Movimiento humanizado continuo (420 micro-movimientos por ciclo: respiración, micro-sacadas, cabeza, hombros).
  - Interacción dinámica con el background y canvas molecular.
  - Explicación y orquestación por fases (fases 1 a 5).
  - Interacción y alternancia entre anchors (Diamantino, Anchor_Salud, Anchor_Farma, Álex).
"""

import os
import sys
import json
import math
import time
from typing import Dict, List, Any, Tuple

# Constante canónica R62
PASOS_HUMANIZADOS = 420

class AnchorProfile:
    """Perfil cinemático y escénico de cada personaje bajo R61/R62."""
    def __init__(self, name: str, role: str, base_pos: Tuple[int, int], scale: float = 1.0):
        self.name = name
        self.role = role
        self.base_pos = base_pos # (x, y)
        self.scale = scale

    def get_kinematic_pose(self, step: int, total_steps: int = PASOS_HUMANIZADOS) -> Dict[str, float]:
        """
        Calcula la traslación, respiración, inclinación y dilatación pupilar
        en el paso específico (0..419).
        """
        t = (step % total_steps) / float(total_steps)
        # Frecuencia respiratoria armónica (aprox. 15 respiraciones por minuto)
        breath = math.sin(t * 2.0 * math.pi * 3.0) * 0.012
        # Micro-inclinación craneal con fase desplazada
        head_tilt = math.sin(t * 2.0 * math.pi * 1.5 + 0.4) * 2.5 # grados
        # Micro-sacadas oculares y paneo de hombros
        shoulder_sway = math.cos(t * 2.0 * math.pi * 0.8) * 4.0 # píxeles en X
        gaze_x = math.sin(t * 2.0 * math.pi * 4.0) * 1.5
        gaze_y = math.cos(t * 2.0 * math.pi * 2.0) * 0.8

        return {
            "step": step,
            "x": self.base_pos[0] + shoulder_sway,
            "y": self.base_pos[1] - (breath * 100),
            "scale": round(self.scale + breath, 4),
            "head_tilt_deg": round(head_tilt, 2),
            "gaze_vector": (round(gaze_x, 2), round(gaze_y, 2)),
            "is_blinking": (step % 90) in (0, 1, 2)
        }

class AnchorVivoEngine:
    """Motor orquestador de Anchors Vivos y escenas R62."""

    def __init__(self, video_dir: str = "assets/videos/demis_hassabis_v2"):
        self.video_dir = video_dir
        self.fases_dir = os.path.join(video_dir, "fases")
        self.anchors = {
            "Diamantino": AnchorProfile("Diamantino", "Anchor Principal", (1420, 580), 1.0),
            "Anchor_Salud": AnchorProfile("Anchor_Salud", "Especialista Biología", (280, 620), 0.85),
            "Anchor_Farma": AnchorProfile("Anchor_Farma", "Especialista Farmacología", (320, 620), 0.85),
            "Alex": AnchorProfile("Alex", "Presentador Humano / Director", (960, 540), 1.0)
        }

    def cargar_fases(self) -> List[Dict[str, Any]]:
        """Carga en orden todas las especificaciones de fases existentes."""
        fases = []
        if not os.path.exists(self.fases_dir):
            return fases
        files = sorted([f for f in os.listdir(self.fases_dir) if f.startswith("fase_") and f.endswith(".json")])
        for fname in files:
            p = os.path.join(self.fases_dir, fname)
            with open(p, "r", encoding="utf-8") as f:
                fases.append(json.load(f))
        return fases

    def simular_movimientos_fase(self, fase_id: int) -> Dict[str, Any]:
        """
        Simula los 420 micro-movimientos para los anchors activos en la fase,
        incorporando interacciones con el background y turnos de voz.
        """
        fase_path = os.path.join(self.fases_dir, f"fase_{fase_id}.json")
        if not os.path.exists(fase_path):
            raise FileNotFoundError(f"No existe la definición de la fase {fase_id} en {fase_path}")

        with open(fase_path, "r", encoding="utf-8") as f:
            fase = json.load(f)

        principal = fase.get("anchor_principal", "Diamantino")
        secundario = fase.get("anchor_secundario")
        humano = fase.get("presentador_humano")

        timeline = []
        for step in range(PASOS_HUMANIZADOS):
            step_data = {
                "step": step,
                "timestamp_relativo": round(step / PASOS_HUMANIZADOS * fase["duracion_segundos"], 2),
                "principal": self.anchors[principal].get_kinematic_pose(step, PASOS_HUMANIZADOS)
            }
            if secundario and secundario in self.anchors:
                # Modulación de interacción: cuando el principal habla, el secundario asiente
                pose_sec = self.anchors[secundario].get_kinematic_pose(step + 30, PASOS_HUMANIZADOS)
                pose_sec["attentive_to_principal"] = True
                step_data["secundario"] = pose_sec

            if humano and "Alex" in self.anchors:
                step_data["director_humano"] = self.anchors["Alex"].get_kinematic_pose(step + 60, PASOS_HUMANIZADOS)

            # Sincronización con canvas de background
            bg_event = None
            if step == 0:
                bg_event = fase.get("interaccion_background", {}).get("evento_inicio")
            elif step == 210:
                bg_event = fase.get("interaccion_background", {}).get("evento_destacado")
            step_data["background_event"] = bg_event

            timeline.append(step_data)

        return {
            "fase_id": fase_id,
            "nombre": fase["nombre"],
            "duracion_segundos": fase["duracion_segundos"],
            "fuente_r58": fase.get("fuente_r58"),
            "dialogo": fase.get("dialogo"),
            "total_pasos_humanizados": len(timeline),
            "timeline": timeline
        }

    def compilar_manifiesto_cinematico(self) -> Dict[str, Any]:
        """Compila y valida la cinemática de las 5 fases completas."""
        fases = self.cargar_fases()
        resumen = []
        total_duracion = 0.0
        total_movimientos = 0

        for f in fases:
            fid = f["fase_id"]
            sim = self.simular_movimientos_fase(fid)
            total_duracion += sim["duracion_segundos"]
            total_movimientos += sim["total_pasos_humanizados"]
            resumen.append({
                "fase_id": fid,
                "nombre": sim["nombre"],
                "duracion_segundos": sim["duracion_segundos"],
                "pasos_humanizados": sim["total_pasos_humanizados"],
                "fuente_r58": sim["fuente_r58"]
            })

        manifiesto = {
            "engine": "HBOS-Anchor-Vivo-R62",
            "version": "1.0",
            "video_target": "demis_hassabis_v2",
            "reglas_activas": ["R58", "R61", "R62"],
            "total_fases": len(resumen),
            "duracion_total_segundos": round(total_duracion, 2),
            "total_movimientos_interpolados": total_movimientos,
            "fases": resumen
        }

        out_path = os.path.join(self.video_dir, "cinematica_r62.json")
        with open(out_path, "w", encoding="utf-8") as fp:
            json.dump(manifiesto, fp, indent=2, ensure_ascii=False)

        return manifiesto

def main():
    print("=" * 65)
    print(">>> MOTOR DE ANCHORS VIVOS HBOS (REGLA R62) <<<")
    print("=" * 65)
    engine = AnchorVivoEngine()
    print("[*] Verificando fases en:", engine.fases_dir)
    fases = engine.cargar_fases()
    print(f"[OK] Fases encontradas: {len(fases)}")

    print("[*] Compilando cinemática humanizada (420 movimientos por fase)...")
    manifest = engine.compilar_manifiesto_cinematico()
    print(f"[OK] Manifiesto R62 generado con éxito en assets/videos/demis_hassabis_v2/cinematica_r62.json")
    print(f"     • Duración total planificada: {manifest['duracion_total_segundos']}s")
    print(f"     • Movimientos interpolados:   {manifest['total_movimientos_interpolados']} pasos")
    for f in manifest["fases"]:
        print(f"     - Fase {f['fase_id']}: {f['nombre']} ({f['duracion_segundos']}s) | Ref: {f['fuente_r58'][:40]}...")
    print("=" * 65)

if __name__ == "__main__":
    main()
