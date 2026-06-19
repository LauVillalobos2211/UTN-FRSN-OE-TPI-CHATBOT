# -*- coding: utf-8 -*-
"""
Handlers de inicio de sesión:
  /start            → muestra lista de empleados
  handle_selecting_user → procesa la elección del empleado
"""

import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from .constantes import SELECTING_USER, MAIN_MENU
from .persistencia import leer_usuarios
from .negocio import obtener_usuario, calcular_dias_disponibles, calcular_dias_tomados, solicitudes_empleado
from .teclados import kb_menu

logger = logging.getLogger(__name__)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Entrada al sistema.
    Si hay un empleado preseleccionado desde la consola (bot_data),
    lo asigna directamente y va al menú principal.
    En caso contrario muestra la lista de selección en Telegram (fallback).
    """
    context.user_data.clear()

    empleado = context.bot_data.get("empleado_consola")
    if empleado:
        context.user_data["empleado"] = empleado
        dias_anuales = int(empleado["dias_anuales"])
        tomados      = calcular_dias_tomados(empleado["id"])
        programados  = sum(
            int(v["cantidad_dias"])
            for v in solicitudes_empleado(empleado["id"])
            if v["estado"] == "pendiente"
        )
        disponibles  = dias_anuales - tomados - programados
        await update.message.reply_text(
            f"✅ *Sesión iniciada*\n\n"
            f"👤 {empleado['nombre']} {empleado['apellido']}\n"
            f"🏢 Departamento: {empleado['departamento']}\n\n"
            f"📊 *Días anuales asignados:* {dias_anuales}\n"
            f"✅ *Tomados/Aprobados:* {tomados}\n"
            f"⏳ *Programados/Pendientes:* {programados}\n"
            f"💚 *Disponibles:* {disponibles}\n\n"
            "¿Qué querés hacer?",
            parse_mode="Markdown",
            reply_markup=kb_menu(),
        )
        return MAIN_MENU

    # Fallback: sin empleado en consola → lista en Telegram
    usuarios = leer_usuarios()
    botones  = [
        [f"👤 {u['id']} – {u['nombre']} {u['apellido']} ({u['departamento']})"]
        for u in usuarios
    ]
    await update.message.reply_text(
        "🏢 *Sistema de Gestión de Vacaciones*\n\n"
        "Por favor, seleccioná tu nombre para iniciar sesión:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(botones, resize_keyboard=True, one_time_keyboard=True),
    )
    return SELECTING_USER


async def handle_selecting_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Procesa la selección del empleado.
    Camino infeliz: texto fuera de la lista → re-muestra la lista con aviso.
    """
    texto = update.message.text.strip()

    try:
        # Formato esperado: "👤 1 – Juan Pérez (Sistemas)"
        user_id = texto.split("–")[0].replace("👤", "").strip()
        usuario = obtener_usuario(user_id)
        if not usuario:
            raise ValueError("Empleado no encontrado")
    except Exception:
        usuarios = leer_usuarios()
        botones  = [
            [f"👤 {u['id']} – {u['nombre']} {u['apellido']} ({u['departamento']})"]
            for u in usuarios
        ]
        await update.message.reply_text(
            "⚠️ Opción no válida. Por favor, elegí un empleado de la lista:",
            reply_markup=ReplyKeyboardMarkup(botones, resize_keyboard=True, one_time_keyboard=True),
        )
        return SELECTING_USER

    context.user_data["empleado"] = usuario
    dias_anuales = int(usuario["dias_anuales"])
    tomados      = calcular_dias_tomados(usuario["id"])
    programados  = sum(
        int(v["cantidad_dias"])
        for v in solicitudes_empleado(usuario["id"])
        if v["estado"] == "pendiente"
    )
    disponibles  = dias_anuales - tomados - programados

    await update.message.reply_text(
        f"✅ *Sesión iniciada*\n\n"
        f"👤 {usuario['nombre']} {usuario['apellido']}\n"
        f"🏢 Departamento: {usuario['departamento']}\n\n"
        f"📊 *Días anuales asignados:* {dias_anuales}\n"
        f"✅ *Tomados/Aprobados:* {tomados}\n"
        f"⏳ *Programados/Pendientes:* {programados}\n"
        f"💚 *Disponibles:* {disponibles}\n\n"
        "¿Qué querés hacer?",
        parse_mode="Markdown",
        reply_markup=kb_menu(),
    )
    return MAIN_MENU
