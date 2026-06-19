# -*- coding: utf-8 -*-
"""
Handlers globales (aplican en cualquier estado de la conversación):
  cmd_cancelar             → /cancelar  – interrumpe el flujo activo
  cmd_ayuda                → /ayuda, /help – muestra la guía de comandos
  mensaje_fuera_de_sesion  → responde a mensajes fuera de conversación activa
"""

import logging

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from .constantes import MAIN_MENU
from .teclados import kb_menu

logger = logging.getLogger(__name__)


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Descarta cualquier operación en curso y vuelve al menú principal.
    Si no hay sesión activa, indica que use /start.
    """
    for k in ("vac_inicio", "vac_fin", "vac_dias",
              "mod_id", "mod_inicio", "mod_fin", "mod_dias",
              "cancel_id"):
        context.user_data.pop(k, None)

    if context.user_data.get("empleado"):
        await update.effective_message.reply_text(
            "🔄 Operación cancelada. Volvés al menú principal.",
            reply_markup=kb_menu(),
        )
        return MAIN_MENU

    await update.effective_message.reply_text(
        "🔄 Escribí /start para iniciar sesión.",
    )
    return ConversationHandler.END


async def cmd_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ayuda y /help – Muestra todos los comandos y opciones disponibles."""
    await update.message.reply_text(
        "📖 *Ayuda — Sistema de Gestión de Vacaciones*\n\n"
        "*Comandos:*\n"
        "/start    – Iniciar o reiniciar sesión\n"
        "/cancelar – Cancelar la operación en curso\n"
        "/ayuda    – Mostrar esta ayuda\n\n"
        "*Opciones del menú:*\n"
        "📅 Solicitar Vacaciones  – Crear una nueva solicitud\n"
        "📋 Ver Solicitudes       – Listar todas tus solicitudes\n"
        "✏️ Modificar Solicitud   – Editar una solicitud PENDIENTE\n"
        "❌ Cancelar Solicitud    – Cancelar una solicitud activa\n"
        "💼 Días Disponibles      – Consultar tu saldo de días\n"
        "🚪 Salir                 – Cerrar sesión\n\n"
        "*Formatos aceptados:*\n"
        "• Fechas: DD/MM/AAAA  (ej: 15/07/2025)\n"
        "• Solo días hábiles (lunes a viernes) son contados.",
        parse_mode="Markdown",
    )


async def cmd_start_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para mensajes de texto recibidos fuera de una conversación activa
    (ConversationHandler.END). Redirige al /start sin reiniciar estados activos.
    """
    from .sesion import cmd_start
    await cmd_start(update, context)
