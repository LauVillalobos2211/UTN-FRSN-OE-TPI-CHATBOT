# -*- coding: utf-8 -*-
"""
Handlers de consulta (READ):
  mostrar_solicitudes      → lista todas las solicitudes del empleado
  mostrar_dias_disponibles → muestra el saldo de días anuales
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .constantes import MAIN_MENU, ESTADO_ICONO
from .negocio import solicitudes_empleado, calcular_dias_tomados, calcular_dias_disponibles
from .teclados import kb_menu

logger = logging.getLogger(__name__)


async def mostrar_solicitudes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Lista todas las solicitudes del empleado activo con estado e íconos.
    Camino infeliz: sin solicitudes → mensaje informativo.
    """
    empleado    = context.user_data["empleado"]
    solicitudes = solicitudes_empleado(empleado["id"])

    if not solicitudes:
        await update.effective_message.reply_text(
            "📋 No tenés solicitudes registradas aún.",
            reply_markup=kb_menu(),
        )
        return MAIN_MENU

    lineas = [f"📋 *Mis Solicitudes — {empleado['nombre']} {empleado['apellido']}*\n"]
    for s in solicitudes:
        icono = ESTADO_ICONO.get(s["estado"], "📌")
        lineas.append(
            f"{icono} *Solicitud #{s['id']}*\n"
            f"   📅 {s['fecha_inicio']} → {s['fecha_fin']}\n"
            f"   🗓️ {s['cantidad_dias']} días hábiles\n"
            f"   📌 Estado: *{s['estado'].upper()}*\n"
            f"   📆 Solicitada: {s['fecha_solicitud']}"
        )
        if s.get("observaciones"):
            lineas.append(f"   💬 {s['observaciones']}")
        lineas.append("")

    await update.effective_message.reply_text(
        "\n".join(lineas),
        parse_mode="Markdown",
        reply_markup=kb_menu(),
    )
    return MAIN_MENU


async def mostrar_dias_disponibles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Muestra el desglose completo del saldo de días del empleado."""
    empleado    = context.user_data["empleado"]
    tomados     = calcular_dias_tomados(empleado["id"])
    pendientes_dias = sum(
        int(v["cantidad_dias"])
        for v in solicitudes_empleado(empleado["id"])
        if v["estado"] == "pendiente"
    )
    disponibles = int(empleado["dias_anuales"]) - tomados - pendientes_dias

    await update.effective_message.reply_text(
        f"💼 *Saldo de Vacaciones*\n\n"
        f"👤 {empleado['nombre']} {empleado['apellido']}\n"
        f"🏢 {empleado['departamento']}\n\n"
        f"📊 Días anuales asignados:         *{empleado['dias_anuales']}*\n"
        f"✅ Días aprobados/tomados:          *{tomados}*\n"
        f"⏳ Días en solicitudes pendientes:  *{pendientes_dias}*\n"
        f"💚 Días actualmente disponibles:    *{disponibles}*",
        parse_mode="Markdown",
        reply_markup=kb_menu(),
    )
    return MAIN_MENU
