# Bot de Gestión de Vacaciones — Telegram

**TPI | Organización Empresarial | UTN FRSN — TUP a Distancia**

---

## Descripción

Chatbot de Telegram que automatiza el proceso de gestión de vacaciones dentro de una organización. Implementa un **CRUD completo** con persistencia en archivos CSV y una **Máquina de Estados** (`ConversationHandler`) que guía al empleado paso a paso por cada operación.

El sistema combina una interfaz de consola (selección de perfil de empleado al iniciar) con la interfaz conversacional de Telegram (botones inline para todas las acciones).

---

## Requisitos

- Python **3.10** o superior
- Acceso a internet (para conectarse a la API de Telegram)
- Un bot creado con **@BotFather** en Telegram

---

## Instalación

```bash
# 1. Clonar o descargar el repositorio
cd UTN-FRSN-OE-TPI-CHATBOT

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Instalar dependencias
pip install python-telegram-bot
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
python main.py
```

Al iniciarse, el sistema:

1. Inicializa los archivos CSV si no existen
2. Pide el token del bot y lo valida contra la API de Telegram
3. Muestra la lista de empleados en consola para seleccionar el perfil activo
4. Inicia el bot — abrí Telegram, buscá tu bot y enviá `/start`

```
=======================================================
  SISTEMA DE GESTIÓN DE VACACIONES — TELEGRAM BOT
  TPI | Organización Empresarial | UTN TUP
=======================================================

🔑 Ingresá el TOKEN del bot de Telegram: 123456:ABC-DEF...
✅ Token válido. Bot detectado: MiBot (@mi_bot)

👥 Seleccioná tu perfil de empleado:
  #    Nombre                 Depto            Anuales  Tomados  Programados  Disponibles
  ──────────────────────────────────────────────────────────────────────────────────────
  1    Juan Pérez             Sistemas              20        5            3           12
  ...
Ingresá el número de empleado: _
```

---

## Estructura del Proyecto

```
UTN-FRSN-OE-TPI-CHATBOT/
├── main.py                  ← Punto de entrada: configura y lanza el bot
├── README.md                ← Este archivo
├── flujo-chatbot-menu.bpmn  ← Modelo BPMN del flujo del sistema
│
├── data/
│   ├── usuarios.csv         ← Empleados de la organización
│   ├── vacaciones.csv       ← Solicitudes de vacaciones
│   └── solicitudes.csv      ← Tabla de relación usuario ↔ vacación
│
└── modulos/
    ├── __init__.py
    ├── constantes.py        ← Estados del ConversationHandler e íconos
    ├── persistencia.py      ← Lectura/escritura de CSVs, inicialización
    ├── negocio.py           ← Lógica de negocio: días hábiles, saldos, IDs
    ├── sesion.py            ← /start, selección de empleado en Telegram
    ├── menu.py              ← Distribuidor central del menú principal
    ├── vacaciones.py        ← Flujo solicitar vacaciones (CREATE)
    ├── modificar.py         ← Flujo modificar solicitud (UPDATE)
    ├── cancelar.py          ← Flujo cancelar solicitud (DELETE lógico)
    ├── consultas.py         ← Ver solicitudes y días disponibles (READ/QUERY)
    ├── globales.py          ← Comandos globales: /cancelar, /ayuda, /help
    └── teclados.py          ← Teclados inline reutilizables (menú, confirmar, volver)
```

---

## Diccionario de Datos

### `data/usuarios.csv`

Contiene los perfiles de los empleados de la organización. Estos datos son de solo lectura para el bot; se cargan al iniciar y se usan para calcular saldos.

| Campo          | Tipo    | Descripción                                        |
|----------------|---------|----------------------------------------------------|
| `id`           | entero  | Identificador único del empleado (PK)              |
| `nombre`       | texto   | Nombre del empleado                                |
| `apellido`     | texto   | Apellido del empleado                              |
| `dni`          | texto   | DNI del empleado                                   |
| `departamento` | texto   | Área o sector dentro de la empresa                 |
| `dias_anuales` | entero  | Total de días de vacaciones asignados por año      |

---

### `data/vacaciones.csv`

Contiene el registro de todas las solicitudes de vacaciones. Es el archivo principal de escritura del sistema.

| Campo             | Tipo    | Descripción                                                            |
|-------------------|---------|------------------------------------------------------------------------|
| `id`              | entero  | Identificador único de la solicitud (PK)                               |
| `id_empleado`     | entero  | FK → `usuarios.id`                                                     |
| `fecha_inicio`    | fecha   | Primer día de vacaciones (formato DD/MM/AAAA)                          |
| `fecha_fin`       | fecha   | Último día de vacaciones (formato DD/MM/AAAA)                          |
| `cantidad_dias`   | entero  | Cantidad de días hábiles (lunes a viernes) comprendidos en el período  |
| `estado`          | texto   | Estado de la solicitud: `pendiente` / `aprobada` / `rechazada` / `cancelada` |
| `fecha_solicitud` | fecha   | Fecha en que se registró o modificó la solicitud (DD/MM/AAAA)         |
| `observaciones`   | texto   | Notas adicionales opcionales (ej. motivo de cancelación)               |

> **Nota:** Los estados `aprobada` y `rechazada` se asignan manualmente en el CSV, simulando la acción de un supervisor de RRHH.

---

### `data/solicitudes.csv`

Tabla de relación entre empleados y sus solicitudes de vacaciones. Actúa como tabla intermedia (muchos a muchos entre `usuarios` y `vacaciones`).

| Campo          | Tipo    | Descripción                                  |
|----------------|---------|----------------------------------------------|
| `id_solicitud` | entero  | Identificador único del registro (PK)        |
| `id_usuario`   | entero  | FK → `usuarios.id`                           |
| `id_vacacion`  | entero  | FK → `vacaciones.id`                         |

---

## Funcionalidades

| Opción de Menú           | Operación | Descripción                                                        |
|--------------------------|-----------|--------------------------------------------------------------------|
| 📅 Solicitar Vacaciones   | CREATE    | Registra una nueva solicitud con validación completa de fechas     |
| 📋 Ver Solicitudes        | READ      | Lista todas las solicitudes del empleado con estado e íconos       |
| ✏️ Modificar Solicitud    | UPDATE    | Cambia las fechas de una solicitud en estado `pendiente`           |
| ❌ Cancelar Solicitud     | DELETE    | Cancela (lógicamente) una solicitud activa (`pendiente`/`aprobada`)|
| 💼 Días Disponibles       | QUERY     | Muestra el saldo: anuales − aprobados − pendientes                 |
| 🚪 Salir                  | —         | Cierra la sesión del empleado y limpia el contexto                 |

---

## Máquina de Estados

```
/start
  └─► SELECTING_USER
        ├─► [selección válida] ──► MAIN_MENU
        └─► [inválida] ──────────► SELECTING_USER (re-muestra lista)

MAIN_MENU
  ├─► "Solicitar Vacaciones" ──► VAC_START_DATE
  │       └─► VAC_END_DATE
  │               └─► VAC_CONFIRM ──► MAIN_MENU
  │
  ├─► "Ver Solicitudes" ────────► MAIN_MENU (muestra lista y vuelve)
  │
  ├─► "Modificar Solicitud" ───► MODIFY_SELECT
  │       └─► MODIFY_START
  │               └─► MODIFY_END
  │                       └─► MODIFY_CONFIRM ──► MAIN_MENU
  │
  ├─► "Cancelar Solicitud" ────► CANCEL_SELECT
  │       └─► CANCEL_CONFIRM ──► MAIN_MENU
  │
  ├─► "Días Disponibles" ───────► MAIN_MENU (muestra saldo y vuelve)
  └─► "Salir" ──────────────────► END

En cualquier estado:
  /cancelar ──► MAIN_MENU  (si hay sesión activa)
             └► END        (si no hay sesión)
```

---

## Comandos de Telegram

| Comando     | Descripción                                       |
|-------------|---------------------------------------------------|
| `/start`    | Iniciar sesión o reiniciar si ya estaba activa    |
| `/cancelar` | Cancelar la operación en curso y volver al menú   |
| `/ayuda`    | Mostrar ayuda con todos los comandos disponibles  |
| `/help`     | Alias de `/ayuda`                                 |

---

## Validaciones implementadas (Camino Infeliz)

| Situación                               | Respuesta del bot                                       |
|-----------------------------------------|---------------------------------------------------------|
| Empleado no seleccionado de la lista    | Muestra la lista nuevamente con aviso                   |
| Fecha con formato incorrecto            | Solicita reingreso indicando el formato correcto        |
| Fecha de inicio en el pasado            | Informa y pide una fecha igual o posterior a hoy        |
| Fecha de fin anterior al inicio         | Informa inconsistencia y pide corrección                |
| Rango sin días hábiles (ej. fin de semana) | Avisa que no hay días hábiles e invita a corregir    |
| Días solicitados > días disponibles     | Muestra el saldo disponible y pide reducir el período   |
| Respuesta libre donde se esperan botones| Pide usar los botones Sí/No o del menú                  |
| Opción inválida en el menú              | Avisa y re-muestra el menú                              |
| Sesión expirada (sin empleado en contexto) | Indica escribir `/start`                             |
| Sin solicitudes pendientes para modificar | Informa que solo se pueden editar solicitudes pendientes|
| Sin solicitudes activas para cancelar   | Informa que no hay solicitudes activas para cancelar    |

---

## Tecnologías utilizadas

| Tecnología                  | Versión   | Uso                                                        |
|-----------------------------|-----------|-------------------------------------------------------------|
| **Python**                  | 3.10+     | Lenguaje de desarrollo, async/await nativo                  |
| **python-telegram-bot**     | 20.x      | Framework asincrónico para la API de Telegram (PTB v20)     |
| **CSV** (stdlib)            | —         | Persistencia de datos (simulación de base de datos)         |
| **datetime** (stdlib)       | —         | Manejo y validación de fechas, cálculo de días hábiles      |
| **asyncio** (stdlib)        | —         | Validación del token en el inicio (llamada async en `main`) |

---

## Notas para la presentación

- Los **estados `aprobada`/`rechazada`** se asignan manualmente en `data/vacaciones.csv` para simular la aprobación por parte de un supervisor de RRHH. En un sistema real, existiría un panel web o un bot secundario para RRHH.
- El cálculo de **días hábiles** excluye sábados y domingos. No incluye feriados nacionales (extensión posible en versiones futuras).
- El bot usa **`context.user_data`** para mantener el estado de cada conversación de Telegram de forma independiente.
- Los archivos CSV se **auto-inicializan** al primer inicio con 5 empleados de ejemplo y 7 solicitudes de muestra en distintos estados.
