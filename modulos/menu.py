# -*- coding: utf-8 -*-
"""
Handler del menú principal: distribuye al módulo correspondiente
según la opción elegida (callback de botón inline).
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from .constantes import MAIN_MENU, VAC_START_DATE, DATE_EXAMPLE
from .teclados import kb_menu, kb_volver

logger = logging.getLogger(__name__)


async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Distribuidor central del menú. Recibe callbacks de los botones inline.
    Camino infeliz: sesión expirada → indica /start.
    """
    from .consultas import mostrar_solicitudes, mostrar_dias_disponibles
    from .modificar import inicio_modificar
    from .cancelar  import inicio_cancelar

    query    = update.callback_query
    await query.answer()
    data     = query.data
    empleado = context.user_data.get("empleado")

    if not empleado:
        await update.effective_message.reply_text(
            "⚠️ Tu sesión expiró. Escribí /start para iniciar nuevamente."
        )
        return ConversationHandler.END

    if data == "solicitar":
        await update.effective_message.reply_text(
            "📅 *Nueva Solicitud de Vacaciones*\n\n"
            f"Ingresá la *fecha de inicio* ({DATE_EXAMPLE}):",
            parse_mode="Markdown",
            reply_markup=kb_volver(),
        )
        return VAC_START_DATE

    elif data == "ver":
        return await mostrar_solicitudes(update, context)

    elif data == "modificar":
        return await inicio_modificar(update, context)

    elif data == "cancelar_sol":
        return await inicio_cancelar(update, context)

    elif data == "dias":
        return await mostrar_dias_disponibles(update, context)

    elif data == "salir":
        nombre = empleado["nombre"]
        context.user_data.clear()
        await update.effective_message.reply_text(
            f"👋 Hasta luego, *{nombre}*! Sesión cerrada.\n\n"
            "Escribí /start para iniciar nuevamente.",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    else:
        await update.effective_message.reply_text(
            "⚠️ Opción no reconocida. Por favor, usá los botones del menú.",
            reply_markup=kb_menu(),
        )
        return MAIN_MENU
