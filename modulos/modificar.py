# -*- coding: utf-8 -*-
"""
Handlers para modificar solicitudes (UPDATE):
  inicio_modificar       → lista solicitudes PENDIENTES disponibles
  modificar_seleccionar  → procesa la elección de la solicitud
  modificar_inicio       → recibe la nueva fecha de inicio
  modificar_fin          → recibe la nueva fecha de fin + muestra resumen
  modificar_confirmar    → aplica o descarta la modificación
"""

import logging
from datetime import date

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from .constantes import (
    MAIN_MENU, MODIFY_SELECT, MODIFY_START, MODIFY_END, MODIFY_CONFIRM,
    DATE_EXAMPLE, DATE_FORMAT,
)
from .negocio import (
    solicitudes_empleado, solicitud_por_id,
    parsear_fecha,
    calcular_dias_disponibles, dias_habiles,
)
from .persistencia import leer_vacaciones, guardar_vacaciones
from .teclados import kb_menu, kb_confirmar, kb_volver

logger = logging.getLogger(__name__)


async def inicio_modificar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Lista las solicitudes en estado PENDIENTE para que el empleado elija.
    Camino infeliz: sin pendientes → informa y vuelve al menú.
    """
    empleado   = context.user_data["empleado"]
    pendientes = [
        v for v in solicitudes_empleado(empleado["id"])
        if v["estado"] == "pendiente"
    ]

    if not pendientes:
        await update.effective_message.reply_text(
            "ℹ️ No tenés solicitudes *pendientes* para modificar.\n"
            "Solo se pueden modificar solicitudes en estado PENDIENTE.",
            parse_mode="Markdown",
            reply_markup=kb_menu(),
        )
        return MAIN_MENU

    botones = [
        [InlineKeyboardButton(
            f"🔧 #{s['id']} | {s['fecha_inicio']} → {s['fecha_fin']} ({s['cantidad_dias']} días)",
            callback_data=f"mod_{s['id']}"
        )]
        for s in pendientes
    ]
    botones.append([InlineKeyboardButton("🔙 Volver al Menú", callback_data="volver")])

    await update.effective_message.reply_text(
        "✏️ *Modificar Solicitud*\n\n"
        "Seleccioná la solicitud que querés modificar:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(botones),
    )
    return MODIFY_SELECT


async def modificar_seleccionar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback: procesa la elección de la solicitud a modificar."""
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "volver":
        await update.effective_message.reply_text("🔙 Operación cancelada.", reply_markup=kb_menu())
        return MAIN_MENU

    id_sol    = data.replace("mod_", "")
    solicitud = solicitud_por_id(id_sol)

    if not solicitud or solicitud["estado"] != "pendiente":
        await update.effective_message.reply_text("⚠️ Solicitud inválida.", reply_markup=kb_menu())
        return MAIN_MENU

    context.user_data["mod_id"] = id_sol

    await update.effective_message.reply_text(
        f"✏️ *Modificando Solicitud #{id_sol}*\n"
        f"Período actual: {solicitud['fecha_inicio']} → {solicitud['fecha_fin']} "
        f"({solicitud['cantidad_dias']} días hábiles)\n\n"
        f"Ingresá la *nueva fecha de inicio* ({DATE_EXAMPLE}):",
        parse_mode="Markdown",
        reply_markup=kb_volver(),
    )
    return MODIFY_START


async def modificar_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Acepta callback \"volver\" o texto de nueva fecha de inicio."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🔙 Operación cancelada.", reply_markup=kb_menu())
        return MAIN_MENU

    fecha = parsear_fecha(update.message.text)

    if not fecha:
        await update.message.reply_text(
            f"⚠️ Formato inválido. Usá {DATE_EXAMPLE}:",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return MODIFY_START

    if fecha < date.today():
        await update.message.reply_text(
            f"⚠️ La fecha no puede ser en el pasado "
            f"(hoy: {date.today().strftime(DATE_FORMAT)}).\n"
            "Ingresá una fecha válida:",
            reply_markup=kb_volver(),
        )
        return MODIFY_START

    context.user_data["mod_inicio"] = fecha
    await update.message.reply_text(
        f"✅ Nueva fecha de inicio: *{fecha.strftime(DATE_FORMAT)}*\n\n"
        f"Ingresá la *nueva fecha de fin* ({DATE_EXAMPLE}):",
        parse_mode="Markdown",
        reply_markup=kb_volver(),
    )
    return MODIFY_END


async def modificar_fin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Acepta callback \"volver\" o texto de nueva fecha de fin."""
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🔙 Operación cancelada.", reply_markup=kb_menu())
        return MAIN_MENU

    empleado = context.user_data["empleado"]
    inicio   = context.user_data["mod_inicio"]
    fecha    = parsear_fecha(update.message.text)

    if not fecha:
        await update.message.reply_text(
            f"⚠️ Formato inválido. Usá {DATE_EXAMPLE}:",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return MODIFY_END

    if fecha < inicio:
        await update.message.reply_text(
            f"⚠️ La fecha de fin debe ser igual o posterior al inicio "
            f"({inicio.strftime(DATE_FORMAT)}).\nIngresá otra fecha:",
            reply_markup=kb_volver(),
        )
        return MODIFY_END

    cantidad = dias_habiles(inicio, fecha)

    if cantidad == 0:
        await update.message.reply_text(
            "⚠️ No hay días hábiles en ese rango. Ingresá otra fecha de fin:",
            reply_markup=kb_volver(),
        )
        return MODIFY_END

    disponibles = calcular_dias_disponibles(empleado)

    if cantidad > disponibles:
        await update.message.reply_text(
            f"⚠️ Días insuficientes.\n"
            f"Días solicitados: *{cantidad}* | Disponibles: *{disponibles}*\n"
            "Ingresá otra fecha de fin:",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return MODIFY_END

    context.user_data["mod_fin"]  = fecha
    context.user_data["mod_dias"] = cantidad
    id_sol = context.user_data["mod_id"]

    await update.message.reply_text(
        f"📋 *Resumen de la Modificación*\n\n"
        f"Solicitud #{id_sol}\n"
        f"📅 Nuevo inicio: *{inicio.strftime(DATE_FORMAT)}*\n"
        f"📅 Nuevo fin:    *{fecha.strftime(DATE_FORMAT)}*\n"
        f"🗓️ Días hábiles: *{cantidad}*\n\n"
        "¿Confirmás los cambios?",
        parse_mode="Markdown",
        reply_markup=kb_confirmar(),
    )
    return MODIFY_CONFIRM


async def modificar_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback: aplica los cambios al CSV con \"confirmar_si\" o los descarta con \"confirmar_no\"."""
    query = update.callback_query
    await query.answer()
    data  = query.data

    if data == "confirmar_si":
        id_sol = context.user_data["mod_id"]
        vacs   = leer_vacaciones()

        for v in vacs:
            if v["id"] == id_sol:
                v["fecha_inicio"]    = context.user_data["mod_inicio"].strftime(DATE_FORMAT)
                v["fecha_fin"]       = context.user_data["mod_fin"].strftime(DATE_FORMAT)
                v["cantidad_dias"]   = str(context.user_data["mod_dias"])
                v["fecha_solicitud"] = date.today().strftime(DATE_FORMAT)
                break

        guardar_vacaciones(vacs)

        await update.effective_message.reply_text(
            f"✅ *Solicitud #{id_sol} modificada exitosamente.*",
            parse_mode="Markdown",
            reply_markup=kb_menu(),
        )
    else:
        await update.effective_message.reply_text("🔙 Modificación cancelada.", reply_markup=kb_menu())

    for k in ("mod_id", "mod_inicio", "mod_fin", "mod_dias"):
        context.user_data.pop(k, None)

    return MAIN_MENU
