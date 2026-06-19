# -*- coding: utf-8 -*-
"""
Lógica de negocio: cálculos, consultas y validaciones de entrada.
"""

from datetime import datetime, date, timedelta

from .constantes import DATE_FORMAT
from .persistencia import leer_usuarios, leer_vacaciones, leer_solicitudes


# ──────────────────────────────────────────────────────────────────────────────
# CONSULTAS SOBRE EMPLEADOS
# ──────────────────────────────────────────────────────────────────────────────

def obtener_usuario(user_id: str) -> dict:
    """Devuelve el dict del empleado o None si no existe."""
    return next((u for u in leer_usuarios() if u["id"] == user_id), None)


# ──────────────────────────────────────────────────────────────────────────────
# CÁLCULO DE DÍAS
# ──────────────────────────────────────────────────────────────────────────────

def calcular_dias_tomados(id_empleado: str) -> int:
    """Suma los días de solicitudes APROBADAS del empleado."""
    return sum(
        int(v["cantidad_dias"])
        for v in leer_vacaciones()
        if v["id_empleado"] == id_empleado and v["estado"] == "aprobada"
    )


def calcular_dias_disponibles(usuario: dict) -> int:
    """Días anuales asignados menos los ya aprobados/tomados."""
    return int(usuario["dias_anuales"]) - calcular_dias_tomados(usuario["id"])


def dias_habiles(inicio: date, fin: date) -> int:
    """Cuenta días hábiles (lunes a viernes) en el rango [inicio, fin]."""
    total, cur = 0, inicio
    while cur <= fin:
        if cur.weekday() < 5:   # 0=lunes … 4=viernes
            total += 1
        cur += timedelta(days=1)
    return total


# ──────────────────────────────────────────────────────────────────────────────
# CONSULTAS SOBRE SOLICITUDES
# ──────────────────────────────────────────────────────────────────────────────

def solicitudes_empleado(id_empleado: str) -> list:
    """Devuelve todas las solicitudes del empleado indicado."""
    return [v for v in leer_vacaciones() if v["id_empleado"] == id_empleado]


def solicitud_por_id(id_sol: str) -> dict:
    """Devuelve la solicitud con ese id o None."""
    return next((v for v in leer_vacaciones() if v["id"] == id_sol), None)


def nuevo_id_vacacion() -> str:
    """Genera el próximo id correlativo para una vacación."""
    vacs = leer_vacaciones()
    return str(max((int(v["id"]) for v in vacs), default=0) + 1)


def nuevo_id_solicitud() -> str:
    """Genera el próximo id_solicitud correlativo para la tabla de relación."""
    sols = leer_solicitudes()
    return str(max((int(s["id_solicitud"]) for s in sols), default=0) + 1)


def solicitud_relacion_por_vacacion(id_vacacion: str) -> dict:
    """Devuelve la fila de solicitudes.csv que referencia a esa vacación, o None."""
    return next(
        (s for s in leer_solicitudes() if s["id_vacacion"] == id_vacacion),
        None,
    )


# ──────────────────────────────────────────────────────────────────────────────
# VALIDACIÓN DE ENTRADAS DEL USUARIO
# ──────────────────────────────────────────────────────────────────────────────

def parsear_fecha(texto: str) -> date:
    """
    Intenta parsear el texto como DD/MM/AAAA.
    Devuelve None si el formato es inválido (camino infeliz).
    """
    try:
        return datetime.strptime(texto.strip(), DATE_FORMAT).date()
    except ValueError:
        return None


def es_confirmacion(texto: str):
    """
    Interpreta la respuesta libre del usuario ante una confirmación.
    Devuelve: True = confirmó | False = rechazó | None = no reconocido.
    """
    t = texto.lower().strip()
    if "sí" in t or "si" in t or "confirmar" in t:
        return True
    if "no" in t or "volver" in t:
        return False
    return None
