# -*- coding: utf-8 -*-
"""
Constantes globales: rutas, estados de la máquina, formatos y configuración.
"""

import os

# ──────────────────────────────────────────────────────────────────────────────
# RUTAS DE ARCHIVOS CSV
# ──────────────────────────────────────────────────────────────────────────────
# BASE_DIR apunta a la raíz del proyecto (carpeta TPI/), independientemente
# de desde dónde se ejecute el script.
BASE_DIR        = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_CSV       = os.path.join(BASE_DIR, "data", "usuarios.csv")
VACATIONS_CSV   = os.path.join(BASE_DIR, "data", "vacaciones.csv")
SOLICITUDES_CSV = os.path.join(BASE_DIR, "data", "solicitudes.csv")

# ──────────────────────────────────────────────────────────────────────────────
# FORMATO DE FECHAS
# ──────────────────────────────────────────────────────────────────────────────
DATE_FORMAT  = "%d/%m/%Y"
DATE_EXAMPLE = "DD/MM/AAAA  (ej: 15/07/2025)"

# ──────────────────────────────────────────────────────────────────────────────
# ÍCONOS POR ESTADO DE SOLICITUD
# ──────────────────────────────────────────────────────────────────────────────
ESTADO_ICONO = {
    "pendiente": "⏳",
    "aprobada":  "✅",
    "rechazada": "❌",
    "cancelada": "🚫",
}

# ──────────────────────────────────────────────────────────────────────────────
# ESTADOS DE LA MÁQUINA DE ESTADOS (ConversationHandler)
# ──────────────────────────────────────────────────────────────────────────────
(
    SELECTING_USER,   # 0  – El empleado elige su perfil
    MAIN_MENU,        # 1  – Menú principal
    VAC_START_DATE,   # 2  – Ingreso de fecha de inicio (nueva solicitud)
    VAC_END_DATE,     # 3  – Ingreso de fecha de fin (nueva solicitud)
    VAC_CONFIRM,      # 4  – Confirmación de la nueva solicitud
    MODIFY_SELECT,    # 5  – Selección de solicitud a modificar
    MODIFY_START,     # 6  – Nueva fecha de inicio (modificación)
    MODIFY_END,       # 7  – Nueva fecha de fin (modificación)
    MODIFY_CONFIRM,   # 8  – Confirmación de modificación
    CANCEL_SELECT,    # 9  – Selección de solicitud a cancelar
    CANCEL_CONFIRM,   # 10 – Confirmación de cancelación
) = range(11)
