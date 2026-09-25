# Telegram: apuntes rápidos

## 1. Qué tenemos

Un bot de cuestionarios con FastAPI. Recibe mensajes de Telegram, valida respuestas según un YAML y contesta con la siguiente pregunta. No usa un modelo de IA ni implementa un login.

```text
Telegram → POST /webhook → WorkflowEngine → SQLite → sendMessage → Telegram
                                      ↘ notas de voz → data/telegram/audios/
```

El ejemplo funciona en chats privados y en español. Recorrido:

`/start → ES → nombre → animal → número 0–10 → día → momento → audio ≥20 s → despedida`

## 2. Qué archivo tocar

| Quiero cambiar… | Archivo | Qué tocar |
| --- | --- | --- |
| Preguntas, orden y límites | `chatbot_template/config/workflow.yml` | `PHASES`, textos y tipos de respuesta |
| Mensajes de error | `chatbot_template/config/errors.yml` | Texto de cada código bajo `ERRORS.es` |
| Validación o transiciones | `chatbot_template/utils/workflow.py` | `process_message()` |
| Añadir un código de error | `chatbot_template/utils/teacher/enums.py` | `WorkflowError` y su mensaje en el YAML |
| Conexión con Telegram, comandos o archivos | `scripts/telegram_hook.py` | `create_app()`, `telegram_call()` y `download_voice()` |
| Guardado local | `scripts/telegram_hook.py` | `ConversationStore` |
| Credenciales y carpeta de datos | `.env` | Variables de la sección siguiente |
| Comprobar que sigue funcionando | `tests/telegram/test_telegram.py` | Tests del motor y del webhook |

## 3. Arranque: una vez preparado el bot

Desde la raíz del proyecto:

```sh
uv sync
cp .env.template .env
```

Copia la plantilla solo si aún no tienes `.env`; si ya existe, añade las variables que falten. Edita `.env`:

```dotenv
TELEGRAM_BOT_TOKEN=tu_token_de_BotFather
TELEGRAM_WEBHOOK_SECRET=un_secreto_elegido_por_ti
TELEGRAM_DATA_DIR=data/telegram
```

El secreto admite 1–256 letras, números, `_` y `-`. Puedes generar uno con:

```sh
uv run python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

El token se obtiene administrando tu bot en [BotFather](https://t.me/BotFather). El README antiguo contenía uno: revócalo en BotFather si sigue activo y usa uno nuevo. Quitarlo del archivo no lo elimina del historial Git ni lo revoca.

Arranca el servidor:

```sh
uv run uvicorn scripts.telegram_hook:app --reload --port 8000
```

Alternativa sin recarga automática:

```sh
uv run python -m scripts.telegram_hook
```

Mantén **un solo proceso/worker**: el bloqueo que serializa las actualizaciones vive en ese proceso.

## 4. Conectar Telegram al servidor

Telegram necesita una URL HTTPS pública que llegue al puerto 8000. Para desarrollo puedes usar un túnel HTTPS; si ya tienes ngrok instalado:

```sh
ngrok http 8000
```

Con el servidor y el túnel abiertos, registra la URL desde otra terminal. Este ejemplo carga `.env` sin pegar el token en el comando:

```sh
uv run python - <<'PY'
import os
import httpx
from dotenv import load_dotenv

load_dotenv('.env')
url = input('URL HTTPS pública, sin /webhook: ').strip().rstrip('/')
if not url.startswith('https://'):
    raise SystemExit('La URL debe empezar por https://')
response = httpx.post(
    f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/setWebhook",
    json={
        'url': f'{url}/webhook',
        'secret_token': os.environ['TELEGRAM_WEBHOOK_SECRET'],
        'allowed_updates': ['message'],
        'max_connections': 1,
    },
    timeout=30,
)
print(response.json())
PY
```

Comprueba que devuelve `ok: true`. Abre tu bot en Telegram y escribe `/start`. Si cambia la URL del túnel, vuelve a registrar el webhook.

Referencia: [Telegram Bot API: setWebhook](https://core.telegram.org/bots/api#setwebhook). El servidor comprueba la cabecera `X-Telegram-Bot-Api-Secret-Token` enviada por Telegram.

## 5. Cambiar preguntas: receta

En `workflow.yml`, cada fase contiene una lista de preguntas. Las respuestas se validan por `type`:

```yaml
- question: "¿Cómo te llamas?"
  type: text  # Texto no vacío; también es el tipo por defecto.

- question: "¿Qué puntuación le das del 1 al 5?"
  type: number  # Número entero, límites incluidos.
  min: 1
  max: 5

- question: "Envía una nota de voz de al menos 10 segundos."
  type: audio
  min_duration: 10
```

Para añadir una pregunta, añade otro bloque a una fase. Para añadir una fase, crea su lista e incluye su nombre en `PHASES`. `presentation` debe ir primero y `conclusion` al final; ambas usan el primer texto de su lista. El resto se recorre en orden.

Los textos no generan respuestas inteligentes: preguntar por un día guarda lo que responde la persona, pero no consulta una agenda.

Al cambiar el flujo, reinicia el servidor y escribe `/start` para evitar continuar con un índice de la versión anterior.

## 6. Errores e idiomas

En `errors.yml`, conserva los marcadores que rellena el motor:

```yaml
INVALID_NUMBER: "Responde con un número entero entre {min} y {max}."
AUDIO_TOO_SHORT: "La nota de voz debe durar al menos {min_duration} segundos."
```

Para añadir catalán, crea `QUESTIONS.ca` con todas las fases, añade `ERRORS.ca` y actualiza la bienvenida y el error de idioma para anunciar `ES / CAT`. El motor ya reconoce `CAT` como `ca`; solo lo acepta cuando existe esa configuración.

## 7. Datos, reinicios y audios

- `data/telegram/conversations.sqlite3`: tabla `states` con el estado y las respuestas de la conversación actual por chat; tabla `updates` con respuestas preparadas y estado de envío.
- `data/telegram/audios/<update_id>.ogg`: notas de voz aceptadas, descargadas mediante [getFile](https://core.telegram.org/bots/api#getfile).
- Reiniciar el servidor conserva el progreso. `/start` o `/reset` reemplaza el cuestionario actual; no borra los archivos de audio ni el registro de actualizaciones.
- Las respuestas inválidas no avanzan ni se guardan como respuestas del cuestionario. Los audios demasiado cortos no se descargan.
- Los datos quedan excluidos de Git con la ruta por defecto. Si eliges otra carpeta, añádela a `.gitignore`.

Si Telegram repite una actualización, se reutiliza su respuesta pendiente sin volver a avanzar. Si el envío falla, se devuelve HTTP 502 para permitir el reintento. Un fallo justo después de enviar y antes de registrar el envío puede duplicar la respuesta visible; el procesamiento del cuestionario sigue deduplicado. Para varios workers o un despliegue más grande haría falta coordinación compartida y una cola de entregas.

## 8. Probar y localizar problemas

Tests sin token real, sin túnel y sin conexión con Telegram:

```sh
uv run pytest tests/telegram -o addopts='' -q
```

Simulación del cuestionario en la terminal:

```sh
uv run python -m scripts.trial_workflow
```

| Síntoma | Qué revisar |
| --- | --- |
| No arranca | `.env`: token y secreto obligatorios; YAML válido |
| HTTP 403 | El secreto registrado con `setWebhook` debe coincidir con `.env` |
| HTTP 422 | La petición no tiene el formato de una actualización de Telegram |
| HTTP 502 | Token, conectividad y disponibilidad de Telegram; el envío o la descarga han fallado |
| No llegan mensajes | Servidor y túnel activos; URL registrada terminada en `/webhook`; chat privado |
| Pregunta inesperada tras editar YAML | Reinicia servidor y conversación con `/start` |
| No acepta un idioma | Debe existir bajo `QUESTIONS` |

## 9. Qué se reparó

Rutas del paquete, importación y nombres de errores, carga del YAML de errores, preguntas y validaciones coherentes, arranque con servidor, plantilla `.env`, retirada del token del README, validación del secreto, tratamiento de errores de Telegram, estado persistente, descarga de audios y tests.

Se sustituyó el ejemplo incoherente de registro/login por un cuestionario sin contraseñas. La integración de WhatsApp solo recibió la corrección de la ruta del motor; requiere su propia revisión antes de usarla.
