# -*- coding: utf-8 -*-
"""
Capa de persistencia: lectura y escritura de los archivos CSV.
"""

import csv
import os
import logging

from .constantes import USERS_CSV, VACATIONS_CSV, SOLICITUDES_CSV

logger = logging.getLogger(__name__)

CAMPOS_USUARIOS    = ["id", "nombre", "apellido", "dni", "departamento", "dias_anuales"]
CAMPOS_VACACIONES  = [
    "id", "id_empleado", "fecha_inicio", "fecha_fin",
    "cantidad_dias", "estado", "fecha_solicitud", "observaciones",
]
CAMPOS_SOLICITUDES = ["id_solicitud", "id_usuario", "id_vacacion"]


def inicializar_csvs() -> None:
    """
    Crea la carpeta data/ y los archivos CSV si no existen.
    Los usuarios se pre-cargan con 5 empleados de ejemplo.
    """
    os.makedirs(os.path.dirname(USERS_CSV), exist_ok=True)

    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_USUARIOS)
            writer.writeheader()
            writer.writerows([
                {"id": "1", "nombre": "Juan",   "apellido": "Pérez",    "dni": "12345678", "departamento": "Sistemas",     "dias_anuales": "20"},
                {"id": "2", "nombre": "María",  "apellido": "García",   "dni": "23456789", "departamento": "RRHH",          "dias_anuales": "20"},
                {"id": "3", "nombre": "Carlos", "apellido": "López",    "dni": "34567890", "departamento": "Contabilidad",  "dias_anuales": "15"},
                {"id": "4", "nombre": "Ana",    "apellido": "Martínez", "dni": "45678901", "departamento": "Sistemas",      "dias_anuales": "20"},
                {"id": "5", "nombre": "Pedro",  "apellido": "Sánchez",  "dni": "56789012", "departamento": "Logística",     "dias_anuales": "10"},
            ])
        logger.info("Archivo %s creado con datos de ejemplo.", USERS_CSV)

    if not os.path.exists(VACATIONS_CSV):
        with open(VACATIONS_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_VACACIONES)
            writer.writeheader()
            writer.writerows([
                # Juan: 5 días aprobados + 3 pendientes → 12 disponibles de 20
                {"id": "1", "id_empleado": "1", "fecha_inicio": "01/07/2026", "fecha_fin": "07/07/2026", "cantidad_dias": "5", "estado": "aprobada",  "fecha_solicitud": "10/06/2026", "observaciones": ""},
                {"id": "2", "id_empleado": "1", "fecha_inicio": "10/08/2026", "fecha_fin": "12/08/2026", "cantidad_dias": "3", "estado": "pendiente", "fecha_solicitud": "15/06/2026", "observaciones": ""},
                # María: 13 días aprobados → 7 disponibles de 20
                {"id": "3", "id_empleado": "2", "fecha_inicio": "06/07/2026", "fecha_fin": "15/07/2026", "cantidad_dias": "8", "estado": "aprobada",  "fecha_solicitud": "01/06/2026", "observaciones": ""},
                {"id": "4", "id_empleado": "2", "fecha_inicio": "03/08/2026", "fecha_fin": "07/08/2026", "cantidad_dias": "5", "estado": "aprobada",  "fecha_solicitud": "20/06/2026", "observaciones": ""},
                # Carlos: 5 días aprobados + 3 cancelados → 10 disponibles de 15
                {"id": "5", "id_empleado": "3", "fecha_inicio": "14/07/2026", "fecha_fin": "18/07/2026", "cantidad_dias": "5", "estado": "aprobada",  "fecha_solicitud": "05/06/2026", "observaciones": ""},
                {"id": "6", "id_empleado": "3", "fecha_inicio": "25/08/2026", "fecha_fin": "27/08/2026", "cantidad_dias": "3", "estado": "cancelada", "fecha_solicitud": "08/06/2026", "observaciones": ""},
                # Ana: sin solicitudes → 20 disponibles de 20
                # Pedro: 5 días pendientes → 5 disponibles de 10
                {"id": "7", "id_empleado": "5", "fecha_inicio": "20/07/2026", "fecha_fin": "24/07/2026", "cantidad_dias": "5", "estado": "pendiente", "fecha_solicitud": "17/06/2026", "observaciones": ""},
            ])
        logger.info("Archivo %s creado con datos de ejemplo.", VACATIONS_CSV)

    if not os.path.exists(SOLICITUDES_CSV):
        with open(SOLICITUDES_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CAMPOS_SOLICITUDES)
            writer.writeheader()
            writer.writerows([
                {"id_solicitud": "1", "id_usuario": "1", "id_vacacion": "1"},
                {"id_solicitud": "2", "id_usuario": "1", "id_vacacion": "2"},
                {"id_solicitud": "3", "id_usuario": "2", "id_vacacion": "3"},
                {"id_solicitud": "4", "id_usuario": "2", "id_vacacion": "4"},
                {"id_solicitud": "5", "id_usuario": "3", "id_vacacion": "5"},
                {"id_solicitud": "6", "id_usuario": "3", "id_vacacion": "6"},
                {"id_solicitud": "7", "id_usuario": "5", "id_vacacion": "7"},
            ])
        logger.info("Archivo %s creado con datos de ejemplo.", SOLICITUDES_CSV)


def leer_usuarios() -> list:
    """Devuelve todos los empleados como lista de dicts."""
    with open(USERS_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def leer_vacaciones() -> list:
    """Devuelve todas las solicitudes de vacaciones como lista de dicts."""
    with open(VACATIONS_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def guardar_vacaciones(vacaciones: list) -> None:
    """Sobreescribe el CSV de vacaciones con la lista recibida."""
    with open(VACATIONS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_VACACIONES)
        writer.writeheader()
        writer.writerows(vacaciones)


def leer_solicitudes() -> list:
    """Devuelve todas las filas de la tabla de relación solicitudes."""
    with open(SOLICITUDES_CSV, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def guardar_solicitudes(solicitudes: list) -> None:
    """Sobreescribe el CSV de solicitudes con la lista recibida."""
    with open(SOLICITUDES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CAMPOS_SOLICITUDES)
        writer.writeheader()
        writer.writerows(solicitudes)
