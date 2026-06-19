# UTN-FRSN-OE-TPI-CHATBOT

# Bot de Gestión de Vacaciones — Telegram

**TPI | Organización Empresarial | UTN TUP a Distancia**

---

## Descripción

Chatbot de Telegram que automatiza el proceso de gestión de vacaciones dentro de una organización. Implementa un CRUD completo con persistencia en archivos CSV y una **Máquina de Estados** que guía al usuario paso a paso por cada operación.

---

## Requisitos

- Python **3.10** o superior
- Acceso a internet (para conectar con la API de Telegram)
- Un bot creado con **@BotFather** en Telegram

---

## Instalación

```bash
# 1. Clonar o descargar el repositorio
cd "TPI"

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt
```

---

## Cómo crear el bot en Telegram

1. Abrí Telegram y buscá **@BotFather**
2. Enviá `/newbot`
3. Seguí las instrucciones (nombre y username del bot)
4. BotFather te dará un **TOKEN** — guardalo

---

## Ejecución

```bash
python bot.py
```

Al iniciarse, el sistema pedirá el token del bot:

```
=======================================================
  SISTEMA DE GESTIÓN DE VACACIONES — TELEGRAM BOT
  TPI | Organización Empresarial | UTN TUP
=======================================================

🔑 Ingresá el TOKEN del bot de Telegram: 123456:ABC-DEF...
```

Luego el bot queda escuchando. Abrí Telegram, buscá tu bot y enviá `/start`.

---

## Estructura de Archivos

```
TPI/
├── bot.py            ← Código fuente principal
├── requirements.txt  ← Dependencias Python
├── README.md         ← Este archivo
├── usuarios.csv      ← Base de datos de empleados
└── vacaciones.csv    ← Base de datos de solicitudes
```

---

## Diccionario de Datos

### `usuarios.csv`

| Campo         | Tipo   | Descripción                              |
|---------------|--------|------------------------------------------|
| id            | entero | Identificador único del empleado         |
| nombre        | texto  | Nombre del empleado                      |
| apellido      | texto  | Apellido del empleado                    |
| dni           | texto  | DNI del empleado                         |
| departamento  | texto  | Área o sector dentro de la empresa       |
| dias_anuales  | entero | Total de días de vacaciones por año      |

### `vacaciones.csv`

| Campo           | Tipo   | Descripción                                            |
|-----------------|--------|--------------------------------------------------------|
| id              | entero | Identificador único de la solicitud                    |
| id_empleado     | entero | FK → `usuarios.id`                                    |
| fecha_inicio    | fecha  | Primer día de vacaciones (DD/MM/AAAA)                  |
| fecha_fin       | fecha  | Último día de vacaciones (DD/MM/AAAA)                  |
| cantidad_dias   | entero | Días hábiles (lun–vie) del período                     |
| estado          | texto  | `pendiente` / `aprobada` / `rechazada` / `cancelada`   |
| fecha_solicitud | fecha  | Fecha en que se registró o modificó la solicitud       |
| observaciones   | texto  | Notas adicionales (ej. motivo de cancelación)          |

---

## Funcionalidades

| Opción de Menú          | Operación | Descripción                                              |
|-------------------------|-----------|----------------------------------------------------------|
| 📅 Solicitar Vacaciones  | CREATE    | Registra una nueva solicitud con fechas validadas        |
| 📋 Ver Solicitudes       | READ      | Lista todas las solicitudes del empleado con su estado   |
| ✏️ Modificar Solicitud   | UPDATE    | Cambia fechas de una solicitud en estado PENDIENTE       |
| ❌ Cancelar Solicitud    | DELETE    | Cancela una solicitud activa (pendiente o aprobada)      |
| 💼 Días Disponibles      | QUERY     | Muestra el saldo de días anuales disponibles             |
| 🚪 Salir                 | —         | Cierra la sesión del empleado                            |

---

## Máquina de Estados

```
/start
  └─► SELECTING_USER
        └─► [selección válida] ──► MAIN_MENU
        └─► [inválida] ──────────► SELECTING_USER (re-muestra lista)

MAIN_MENU
  ├─► "Solicitar Vacaciones" ──► VAC_START_DATE
  │       └─► VAC_END_DATE
  │               └─► VAC_CONFIRM ──► MAIN_MENU
  │
  ├─► "Ver Solicitudes" ────────► MAIN_MENU (muestra lista)
  │
  ├─► "Modificar Solicitud" ───► MODIFY_SELECT
  │       └─► MODIFY_START
  │               └─► MODIFY_END
  │                       └─► MODIFY_CONFIRM ──► MAIN_MENU
  │
  ├─► "Cancelar Solicitud" ────► CANCEL_SELECT
  │       └─► CANCEL_CONFIRM ──► MAIN_MENU
  │
  ├─► "Días Disponibles" ───────► MAIN_MENU (muestra saldo)
  └─► "Salir" ──────────────────► END

En cualquier estado: /cancelar ──► MAIN_MENU (o END si no hay sesión)
```

---

## Comandos de Telegram

| Comando    | Descripción                              |
|------------|------------------------------------------|
| `/start`   | Iniciar o reiniciar sesión               |
| `/cancelar`| Cancelar la operación en curso           |
| `/ayuda`   | Mostrar ayuda con todos los comandos     |
| `/help`    | Alias de `/ayuda`                        |

---

## Validaciones implementadas (Camino Infeliz)

| Situación                              | Respuesta del bot                                      |
|----------------------------------------|--------------------------------------------------------|
| Empleado no seleccionado de la lista   | Muestra la lista nuevamente con aviso                  |
| Fecha con formato incorrecto           | Solicita reingreso indicando el formato correcto       |
| Fecha de inicio en el pasado           | Informa y pide una fecha futura                        |
| Fecha de fin anterior al inicio        | Informa inconsistencia y pide corrección               |
| Rango sin días hábiles                 | Avisa que no hay días hábiles e invita a corregir      |
| Días solicitados > días disponibles    | Muestra el saldo y pide reducir el período             |
| Respuesta libre en confirmación        | Pide usar los botones Sí/No                            |
| Opción inválida en el menú             | Avisa y re-muestra el menú                             |
| Sesión expirada (sin empleado)         | Indica escribir `/start`                               |
| Sin solicitudes para modificar         | Informa que solo se pueden editar pendientes           |
| Sin solicitudes activas para cancelar  | Informa que no hay nada para cancelar                  |

---

## Tecnologías utilizadas

- **Python 3.10+** — lenguaje de desarrollo
- **python-telegram-bot 20.x** — librería asincrónica para la API de Telegram
- **CSV** — persistencia de datos (simulación de base de datos)
- **datetime** — manejo y validación de fechas, cálculo de días hábiles

---

## Notas para la presentación

- Los **estados aprobada/rechazada** son asignados manualmente en el CSV para simular la acción de un supervisor. En un sistema real, un panel de RRHH cambiaría el estado.  
- El cálculo de **días hábiles** excluye sábados y domingos (no incluye feriados, que podrían agregarse en una versión extendida).  
- El bot tiene **persistencia por conversación**: usa `context.user_data` para mantener el estado de cada usuario de Telegram de forma independiente.
