# -*- coding: utf-8 -*-
"""
Handlers para cancelar solicitudes (DELETE lógico):
  inicio_cancelar      → lista solicitudes activas (pendiente / aprobada)
  cancelar_seleccionar → procesa la elección de la solicitud
  cancelar_confirmar   → cambia el estado a "cancelada" o aborta
"""

import logging
from datetime import date

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from .constantes import MAIN_MENU, CANCEL_SELECT, CANCEL_CONFIRM, DATE_FORMAT
from .negocio import solicitudes_empleado, solicitud_por_id
from .persistencia import leer_vacaciones, guardar_vacaciones
from .teclados import kb_menu, kb_confirmar

logger = logging.getLogger(__name__)


async def inicio_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Lista las solicitudes activas (pendiente o aprobada) cancelables.
    Camino infeliz: no hay activas → informa y vuelve al menú.
    """
    empleado = context.user_data["empleado"]
    activas  = [
        v for v in solicitudes_empleado(empleado["id"])
        if v["estado"] in ("pendiente", "aprobada")
    ]

    if not activas:
        await update.effective_message.reply_text(
            "ℹ️ No tenés solicitudes activas para cancelar.",
            reply_markup=kb_menu(),
        )
        return MAIN_MENU

    botones = [
        [InlineKeyboardButton(
            f"🗑️ #{s['id']} | {s['fecha_inicio']} → {s['fecha_fin']} [{s['estado'].upper()}]",
            callback_data=f"del_{s['id']}"
        )]
        for s in activas
    ]
    botones.append([InlineKeyboardButton("🔙 Volver al Menú", callback_data="volver")])

    await update.effective_message.reply_text(
        "❌ *Cancelar Solicitud*\n\n"
        "Seleccioná la solicitud que querés cancelar:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botones),
    )
    return CANCEL_SELECT


async def cancelar_seleccionar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback: procesa la elección de la solicitud a cancelar."""
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "volver":
        await update.effective_message.reply_text("🔙 Operación cancelada.", reply_markup=kb_menu())
        return MAIN_MENU

    id_sol    = data.replace("del_", "")
    solicitud = solicitud_por_id(id_sol)

    if not solicitud or solicitud["estado"] not in ("pendiente", "aprobada"):
        await update.effective_message.reply_text("⚠️ Solicitud inválida.", reply_markup=kb_menu())
        return MAIN_MENU

    context.user_data["cancel_id"] = id_sol

    await update.effective_message.reply_text(
        f"❌ *¿Cancelar Solicitud #{id_sol}?*\n\n"
        f"📅 {solicitud['fecha_inicio']} → {solicitud['fecha_fin']}\n"
        f"🗓️ {solicitud['cantidad_dias']} días hábiles\n"
        f"📌 Estado actual: *{solicitud['estado'].upper()}*\n\n"
        "⚠️ Esta acción no se puede deshacer. ¿Confirmás?",
        parse_mode="Markdown",
        reply_markup=kb_confirmar(),
    )
    return CANCEL_CONFIRM


async def cancelar_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback: marca la solicitud como 'cancelada' con \"confirmar_si\" o aborta."""
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "confirmar_si":
        id_sol = context.user_data["cancel_id"]
        vacs   = leer_vacaciones()

        for v in vacs:
            if v["id"] == id_sol:
                v["estado"]        = "cancelada"
                v["observaciones"] = (
                    f"Cancelada por el empleado el {date.today().strftime(DATE_FORMAT)}"
                )
                break

        guardar_vacaciones(vacs)

        await update.effective_message.reply_text(
            f"✅ *Solicitud #{id_sol} cancelada correctamente.*",
            parse_mode="Markdown",
            reply_markup=kb_menu(),
        )
    else:
        await update.effective_message.reply_text("🔙 Cancelación abortada.", reply_markup=kb_menu())

    context.user_data.pop("cancel_id", None)
    return MAIN_MENU
