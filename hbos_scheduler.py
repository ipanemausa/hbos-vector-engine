# -*- coding: utf-8 -*-
"""
hbos_scheduler.py - PLANIFICADOR PERPETUO DE PUBLICACION
Ecosistema Soberano HBOS-Diamantino - Modo Experto ALEJAVI
"""
import time, os, subprocess, json

class HBOSScheduler:
    def __init__(self, interval_seconds=1800):
        self.interval = interval_seconds
        self.state_file = 'scheduler_state.json'

    def run_cycle(self):
        t = time.asctime()
        print(f'[SCHEDULER] Ciclo iniciado en {t}')
        r_start = subprocess.run(['python', 'hbos_daily_start.py'], capture_output=True, text=True)
        r_social = subprocess.run(['python', 'hbos_social_manager.py'], capture_output=True, text=True)
        r_mkt = subprocess.run(['python', 'hbos_marketing_agent.py'], capture_output=True, text=True)
        state = {
            'last_cycle': t,
            'daily_start_exit': r_start.returncode,
            'social_exit': r_social.returncode,
            'marketing_exit': r_mkt.returncode,
            'status': 'CYCLE_SUCCESS'
        }
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2)
        print('[SCHEDULER] Ciclo completado exitosamente.')
        return state

if __name__ == '__main__':
    s = HBOSScheduler()
    res = s.run_cycle()
    print('[OK] status:', res['status'])
