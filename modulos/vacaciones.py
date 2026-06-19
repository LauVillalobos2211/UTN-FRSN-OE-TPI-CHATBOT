# -*- coding: utf-8 -*-
"""
Handlers para solicitar vacaciones (CREATE):
  vac_fecha_inicio → recibe y valida la fecha de inicio
  vac_fecha_fin    → recibe y valida la fecha de fin + muestra resumen
  vac_confirmar    → confirma o descarta la nueva solicitud
"""

import logging
from datetime import date

from telegram import Update
from telegram.ext import ContextTypes

from .constantes import VAC_START_DATE, VAC_END_DATE, VAC_CONFIRM, MAIN_MENU, DATE_EXAMPLE, DATE_FORMAT
from .negocio import parsear_fecha, calcular_dias_disponibles, dias_habiles, nuevo_id_vacacion, nuevo_id_solicitud
from .persistencia import leer_vacaciones, guardar_vacaciones, leer_solicitudes, guardar_solicitudes
from .teclados import kb_menu, kb_confirmar, kb_volver

logger = logging.getLogger(__name__)


async def vac_fecha_inicio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Valida la fecha de inicio. Acepta:
      - Callback "volver"     → regresa al menú.
      - Texto de fecha        → valida y avanza.
    """
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🔙 Operación cancelada.", reply_markup=kb_menu())
        return MAIN_MENU

    fecha = parsear_fecha(update.message.text)

    if not fecha:
        await update.message.reply_text(
            f"⚠️ *Formato inválido.*\n"
            f"Ingresá la fecha como {DATE_EXAMPLE}:",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return VAC_START_DATE

    if fecha < date.today():
        await update.message.reply_text(
            f"⚠️ La fecha de inicio no puede ser en el pasado.\n"
            f"Hoy es *{date.today().strftime(DATE_FORMAT)}*. "
            "Ingresá una fecha igual o posterior a hoy:",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return VAC_START_DATE

    context.user_data["vac_inicio"] = fecha
    await update.message.reply_text(
        f"✅ Fecha de inicio registrada: *{fecha.strftime(DATE_FORMAT)}*\n\n"
        f"Ahora ingresá la *fecha de fin* ({DATE_EXAMPLE}):",
        parse_mode="Markdown",
        reply_markup=kb_volver(),
    )
    return VAC_END_DATE


async def vac_fecha_fin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Valida la fecha de fin. Acepta callback "volver" o texto de fecha.
    """
    if update.callback_query:
        await update.callback_query.answer()
        await update.effective_message.reply_text("🔙 Operación cancelada.", reply_markup=kb_menu())
        return MAIN_MENU

    empleado = context.user_data["empleado"]
    inicio   = context.user_data["vac_inicio"]
    fecha    = parsear_fecha(update.message.text)

    if not fecha:
        await update.message.reply_text(
            f"⚠️ Formato inválido. Usá {DATE_EXAMPLE}:",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return VAC_END_DATE

    if fecha < inicio:
        await update.message.reply_text(
            f"⚠️ La fecha de fin ({fecha.strftime(DATE_FORMAT)}) debe ser igual o "
            f"posterior a la fecha de inicio ({inicio.strftime(DATE_FORMAT)}).\n"
            "Ingresá otra fecha de fin:",
            reply_markup=kb_volver(),
        )
        return VAC_END_DATE

    cantidad = dias_habiles(inicio, fecha)

    if cantidad == 0:
        await update.message.reply_text(
            "⚠️ El período seleccionado no contiene días hábiles (lunes a viernes).\n"
            "Seleccioná un rango que incluya al menos un día hábil:",
            reply_markup=kb_volver(),
        )
        return VAC_END_DATE

    disponibles = calcular_dias_disponibles(empleado)

    if cantidad > disponibles:
        await update.message.reply_text(
            f"⚠️ *Días insuficientes.*\n\n"
            f"📋 Días hábiles solicitados: *{cantidad}*\n"
            f"💼 Días disponibles:         *{disponibles}*\n\n"
            f"Por favor, seleccioná un período más corto "
            f"(máximo {disponibles} días hábiles):",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return VAC_END_DATE

    context.user_data["vac_fin"]  = fecha
    context.user_data["vac_dias"] = cantidad

    await update.message.reply_text(
        f"📋 *Resumen de la Solicitud*\n\n"
        f"👤 Empleado:               {empleado['nombre']} {empleado['apellido']}\n"
        f"📅 Desde:                  *{inicio.strftime(DATE_FORMAT)}*\n"
        f"📅 Hasta:                  *{fecha.strftime(DATE_FORMAT)}*\n"
        f"🗓️ Días hábiles:           *{cantidad}*\n"
        f"💚 Días restantes si se aprueba: *{disponibles - cantidad}*\n\n"
        "¿Confirmás la solicitud?",
        parse_mode="Markdown",
        reply_markup=kb_confirmar(),
    )
    return VAC_CONFIRM


async def vac_confirmar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Graba la solicitud en los CSV al recibir callback "confirmar_si" o la descarta con "confirmar_no".
    """
    query = update.callback_query
    await query.answer()
    data  = query.data  # "confirmar_si" | "confirmar_no"

    if data == "confirmar_si":
        empleado = context.user_data["empleado"]
        nid      = nuevo_id_vacacion()
        nueva    = {
            "id":              nid,
            "id_empleado":     empleado["id"],
            "fecha_inicio":    context.user_data["vac_inicio"].strftime(DATE_FORMAT),
            "fecha_fin":       context.user_data["vac_fin"].strftime(DATE_FORMAT),
            "cantidad_dias":   str(context.user_data["vac_dias"]),
            "estado":          "pendiente",
            "fecha_solicitud": date.today().strftime(DATE_FORMAT),
            "observaciones":   "",
        }
        vacs = leer_vacaciones()
        vacs.append(nueva)
        guardar_vacaciones(vacs)

        # Registrar la relación en solicitudes.csv
        id_sol = nuevo_id_solicitud()
        sols   = leer_solicitudes()
        sols.append({
            "id_solicitud": id_sol,
            "id_usuario":   empleado["id"],
            "id_vacacion":  nid,
        })
        guardar_solicitudes(sols)

        await update.effective_message.reply_text(
            f"✅ *¡Solicitud registrada exitosamente!*\n\n"
            f"🔢 Número de solicitud: *#{nid}*\n"
            f"📅 Período:             {nueva['fecha_inicio']} al {nueva['fecha_fin']}\n"
            f"🗓️ Días hábiles:        {nueva['cantidad_dias']}\n"
            f"📌 Estado:              *PENDIENTE de aprobación*",
            parse_mode="Markdown",
            reply_markup=kb_menu(),
        )
    else:
        await update.effective_message.reply_text(
            "🔙 Solicitud descartada. Volvés al menú principal.",
            reply_markup=kb_menu(),
        )

    for k in ("vac_inicio", "vac_fin", "vac_dias"):
        context.user_data.pop(k, None)

    return MAIN_MENU
