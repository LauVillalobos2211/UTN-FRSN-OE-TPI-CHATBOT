# -*- coding: utf-8 -*-
"""
Constructores de teclados inline de Telegram (InlineKeyboardMarkup).
Los botones inline aparecen dentro de la burbuja del mensaje,
garantizando visibilidad en todos los clientes de Telegram.
"""

from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def kb_menu() -> InlineKeyboardMarkup:
    """Teclado del menú principal (6 opciones en grilla 2×3)."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📅 Solicitar Vacaciones", callback_data="solicitar"),
            InlineKeyboardButton("📋 Ver Solicitudes",      callback_data="ver"),
        ],
        [
            InlineKeyboardButton("✏️ Modificar Solicitud",  callback_data="modificar"),
            InlineKeyboardButton("❌ Cancelar Solicitud",   callback_data="cancelar_sol"),
        ],
        [
            InlineKeyboardButton("💼 Días Disponibles",     callback_data="dias"),
            InlineKeyboardButton("🚪 Salir",                callback_data="salir"),
        ],
    ])


def kb_confirmar() -> InlineKeyboardMarkup:
    """Teclado de confirmación Sí / No."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Sí, confirmar", callback_data="confirmar_si"),
            InlineKeyboardButton("🔙 No, volver",    callback_data="confirmar_no"),
        ],
    ])


def kb_volver() -> InlineKeyboardMarkup:
    """Botón único para cancelar el flujo activo y volver al menú."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Volver al Menú", callback_data="volver")],
    ])
