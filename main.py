#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║     Sistema de Gestión de Vacaciones — Telegram Bot      ║
║     TPI | Organización Empresarial | UTN TUP             ║
╠══════════════════════════════════════════════════════════╣
║  Punto de entrada: configura la Application de Telegram  ║
║  y registra todos los handlers importados desde modulos/ ║
╚══════════════════════════════════════════════════════════╝
"""

import logging
import warnings
import asyncio

from telegram import Bot, Update
from telegram.error import InvalidToken, TelegramError
from telegram.warnings import PTBUserWarning
warnings.filterwarnings("ignore", message=".*CallbackQueryHandler.*", category=PTBUserWarning)
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from modulos.persistencia import inicializar_csvs, leer_usuarios
from modulos.negocio import calcular_dias_tomados, solicitudes_empleado
from modulos.constantes import (
    SELECTING_USER,
    MAIN_MENU,
    VAC_START_DATE, VAC_END_DATE, VAC_CONFIRM,
    MODIFY_SELECT, MODIFY_START, MODIFY_END, MODIFY_CONFIRM,
    CANCEL_SELECT, CANCEL_CONFIRM,
)
from modulos.sesion     import cmd_start, handle_selecting_user
from modulos.menu       import handle_main_menu
from modulos.vacaciones import vac_fecha_inicio, vac_fecha_fin, vac_confirmar
from modulos.modificar  import (
    modificar_seleccionar, modificar_inicio,
    modificar_fin, modificar_confirmar,
)
from modulos.cancelar  import cancelar_seleccionar, cancelar_confirmar
from modulos.globales  import cmd_cancelar, cmd_ayuda, cmd_start_fallback

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


def validar_token_telegram(token: str) -> dict | None:
    """Valida el token contra la API de Telegram y devuelve metadata del bot."""
    try:
        bot = Bot(token=token)
        me = asyncio.run(bot.get_me())
        return {
            "id": me.id,
            "nombre": me.first_name,
            "username": me.username,
        }
    except InvalidToken:
        return None
    except TelegramError as exc:
        print(f"\n⚠️ No se pudo validar el token en Telegram: {exc}")
        return None


def main() -> None:
    inicializar_csvs()

    print("=" * 55)
    print("  SISTEMA DE GESTIÓN DE VACACIONES — TELEGRAM BOT")
    print("  TPI | Organización Empresarial | UTN TUP")
    print("=" * 55)
    print()

    token = None
    info_bot = None
    while not info_bot:
        token_ingresado = input("🔑 Ingresá el TOKEN del bot de Telegram: ").strip()

        if not token_ingresado:
            print("\n❌ Token vacío. El programa se cierra.")
            return

        info_bot = validar_token_telegram(token_ingresado)
        if not info_bot:
            print("\n❌ El token ingresado no es válido o no pudo verificarse. Intentá de nuevo.")
            continue

        token = token_ingresado
        print(
            f"\n✅ Token válido. Bot detectado: {info_bot['nombre']}"
            f" (@{info_bot['username']})"
        )

    # Selección de empleado desde la consola
    usuarios = leer_usuarios()
    print("\n👥 Seleccioná tu perfil de empleado:")
    print(f"  {'#':<4} {'Nombre':<22} {'Depto':<16} {'Anuales':>7} {'Tomados':>8} {'Programados':>12} {'Disponibles':>12}")
    print("  " + "-" * 87)
    for u in usuarios:
        tomados     = calcular_dias_tomados(u["id"])
        programados = sum(
            int(v["cantidad_dias"])
            for v in solicitudes_empleado(u["id"])
            if v["estado"] == "pendiente"
        )
        disponibles = int(u["dias_anuales"]) - tomados - programados
        print(f"  {u['id']:<4} {u['nombre'] + ' ' + u['apellido']:<22} {u['departamento']:<16} {u['dias_anuales']:>7} {tomados:>8} {programados:>12} {disponibles:>12}")

    empleado_consola = None
    while not empleado_consola:
        seleccion = input("\nIngresá el número de empleado: ").strip()
        empleado_consola = next((u for u in usuarios if u["id"] == seleccion), None)
        if not empleado_consola:
            print("⚠️  Opción inválida. Intentá de nuevo.")

    app = Application.builder().token(token).build()
    app.bot_data["empleado_consola"] = empleado_consola

    conv = ConversationHandler(
        entry_points=[
            CommandHandler("start", cmd_start),
            # Solo los callbacks del menú principal activan el entry point
            CallbackQueryHandler(handle_main_menu, pattern="^(solicitar|ver|modificar|cancelar_sol|dias|salir)$"),
        ],
        states={
            SELECTING_USER: [
                CallbackQueryHandler(handle_selecting_user, pattern="^user_"),
            ],
            MAIN_MENU: [
                CallbackQueryHandler(handle_main_menu),
            ],
            VAC_START_DATE: [
                CallbackQueryHandler(vac_fecha_inicio, pattern="^volver$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_fecha_inicio),
            ],
            VAC_END_DATE: [
                CallbackQueryHandler(vac_fecha_fin, pattern="^volver$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_fecha_fin),
            ],
            VAC_CONFIRM: [
                CallbackQueryHandler(vac_confirmar, pattern="^confirmar_"),
            ],
            MODIFY_SELECT: [
                CallbackQueryHandler(modificar_seleccionar),
            ],
            MODIFY_START: [
                CallbackQueryHandler(modificar_inicio, pattern="^volver$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, modificar_inicio),
            ],
            MODIFY_END: [
                CallbackQueryHandler(modificar_fin, pattern="^volver$"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, modificar_fin),
            ],
            MODIFY_CONFIRM: [
                CallbackQueryHandler(modificar_confirmar, pattern="^confirmar_"),
            ],
            CANCEL_SELECT: [
                CallbackQueryHandler(cancelar_seleccionar),
            ],
            CANCEL_CONFIRM: [
                CallbackQueryHandler(cancelar_confirmar, pattern="^confirmar_"),
            ],
        },
        fallbacks=[CommandHandler("cancelar", cmd_cancelar)],
        allow_reentry=True,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("ayuda", cmd_ayuda))
    app.add_handler(CommandHandler("help",  cmd_ayuda))
    # Mensajes fuera de conversación activa → muestra el menú directamente
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, cmd_start_fallback))

    print(f"\n✅ Sesión iniciada como {empleado_consola['nombre']} {empleado_consola['apellido']}. Bot escuchando (Ctrl+C para detener).\n")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
