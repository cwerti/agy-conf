---
name: max-bot-design
description: Build or restyle chat bots for the MAX messenger (maxapi) with the unified design used in the ANK anti-drug bot — greeting main menu, step-by-step report flow, emoji+bold headers, home button always at the bottom, consistent short-message markers. Use when writing a new MAX/Telegram-style bot, adding a section/step to one, or bringing texts and keyboards to this style.
---

# MAX Bot Design Workflow

Reference implementation: `telegram_bot/app/max_bot/` (`texts.py`, `keyboards.py`, `bot_functions.py`, `handlers/handlers.py`, `state.py`).
Library: `maxapi` 0.9.x (Dispatcher, `MemoryContext` states, `ButtonsPayload`, `CallbackButton`, `LinkButton`, `RequestGeoLocationButton`).

## 1. Project layout

Keep these concerns separated — never inline user-facing strings in handlers:

| File | Contains |
|---|---|
| `texts.py` | All texts, limits (`MIN_DESCRIPTION_LENGTH`, `MAX_PHOTOS`), URLs, small text builders (`welcome(first_name)`) |
| `keyboards.py` | Payload constants (`"menu:report"`, `"report:send"`…) and all keyboards, built once with `.pack()` |
| `bot_functions.py` | UI helpers: `answer_html`, `edit_clicked`, `notify_clicked`, `edit_to_main_menu`, `send_main_menu` |
| `state.py` | `StatesGroup` with one state per step (`INTRO, DESCRIPTION, LOCATION, …, CONFIRM`) |
| `handlers/handlers.py` | Handlers only: validate → call service → switch state → render via helpers |

## 2. Navigation principles

- **One message per screen.** Callback buttons *edit the clicked message* (`bot.send_callback` with `MessageForCallback`), they don't spam new ones. New messages are sent only in reply to user input.
- **Popup, not message**, for transient info: outdated button, "report in progress", page hint, send error → `notify_clicked(callback, text)`.
- **Main menu = greeting.** The start screen, `/start`, `/menu`, any unknown message and the home button show the same menu: `Здравствуйте, {first_name}!` + menu text. After an action result (sent / cancelled / expired / service down) show `result + "\n\n" + MAIN_MENU` **without** the greeting.
- **🏠 В главное меню is always the last row** of every keyboard. On report steps it carries the cancel payload (cancels the backend draft, shows "↩️ Формирование сообщения отменено."); before the draft exists (intro/instruction) it just opens the menu.
- **No "Назад" buttons** inside a flow — only primary action(s) + home.
- **Paired actions in one row**, primary on the right: `[🔄 Заполнить заново | ✅ Отправить]`, `[📝 Направить сообщение | 📖 Инструкция]`.
- Handlers are matched first-wins: register state-specific handlers before generic ones, and finish with catch-alls (`callback_outdated` → popup, `message_default` → main menu).
- Guard menu callbacks while a flow is active (`state in REPORT_STATES[1:]` → popup `REPORT_IN_PROGRESS`).

## 3. Text style (HTML parse mode)

Big screens (menu, intro, steps, instruction, info sections):

```
{emoji} <b>Заголовок</b>

Основной текст с <b>акцентом</b> на ключевых словах.

<b>Подзаголовок списка:</b>
▪️ пункт;
▪️ пункт.

<i>Подсказка или пример — курсивом в конце.</i>
```

- Header: one emoji + bold title. Steps: `✏️ <b>Шаг 1 из 4. Описание</b>`, `📍 Шаг 2…`, `📷 Шаг 3…`, `📋 Шаг 4 из 4. Проверка`.
- Bullets: `▪️` (not ✔️). Numbered steps in instructions: `1️⃣ <b>Описание.</b> …`.
- Bold sparingly: 2–4 accents per screen (key phrase, phone numbers, field labels like `<b>Место:</b>`).
- Italic for examples (`<i>Например: «…»</i>`), hints and the closing line.
- Warnings: `⚠️ <b>…</b>`.
- Don't overdo it — no emoji on every line, no bold paragraphs.
- Escape all user data with `html.escape` before inserting into HTML texts.

Short messages and popups (plain text, no HTML — popups don't render it):

| Marker | Use |
|---|---|
| `✅` | accepted / done: "✅ Описание принято.", "✅ Геопозиция принята: {mo}." |
| `⚠️` | validation error / service down: "⚠️ Описание слишком короткое: 7 из 15 символов. …" |
| `↩️` | cancelled |
| `⏱` | expired |
| `🚀` | sent as a separate message right before the upload progress ("Выполняем загрузку: 1/3", edited in place) |

Validation messages always say what is wrong *and* how to fix it, with the actual numbers.

## 4. Keyboards

```python
_home_button = CallbackButton(text="🏠 В главное меню", payload=MENU_BACK)          # info sections
_cancel_button = CallbackButton(text="🏠 В главное меню", payload=REPORT_CANCEL)    # inside the flow
_begin_button = CallbackButton(text="📝 Направить сообщение", payload=REPORT_BEGIN, intent=Intent.POSITIVE)

report_intro_keyboard = ButtonsPayload(buttons=[
    [_begin_button, CallbackButton(text="📖 Инструкция", payload=MENU_INSTRUCTION)],
    [_cancel_button],
]).pack()

confirm_keyboard = ButtonsPayload(buttons=[
    [CallbackButton(text="🔄 Заполнить заново", payload=REPORT_RESTART),
     CallbackButton(text="✅ Отправить", payload=REPORT_SEND, intent=Intent.POSITIVE)],
    [_cancel_button],
]).pack()
```

- Main menu: one section per row, emoji first (`🚫`, `🌐`, `📚`, `🆘`), `Intent.POSITIVE` only on the main action. External resources → `LinkButton`.
- Short button labels (≤ ~30 chars; two-button rows even shorter). Truncate dynamic labels to 64 chars with `…`.
- Long lists (e.g. municipalities): 8 per page, row `◀ | 2 / 3 | ▶` (cyclic), home row last; the page-counter button answers with a popup hint.
- Age-gated content: question screen `[Да | Нет]` + home; "Нет" leads to an alternative resource, not a dead end.

## 5. Report flow pattern

`INTRO → DESCRIPTION → LOCATION (→ MUNICIPALITY → ADDRESS) → PHOTOS → CONFIRM → send`

- Intro screen: why it matters + `<b>Как сделать сообщение эффективным:</b>` bullets + italic call to action.
- Create the backend draft only on "Направить сообщение" (after `check_workability()`); in INTRO nothing to cancel.
- Each step: accept only the expected input; on anything else reply with a `⚠️` hint + the same step keyboard.
- Geolocation: `RequestGeoLocationButton` + "can't attach coordinates" → help screen → manual choice from a list + address text.
- Confirm screen: summary with bold labels, user text truncated (~300 chars) and escaped.
- "Заполнить заново": `start_new()` (cancels the draft), `context.clear()`, go to step 1 by editing the message.
- Send: wrap in try/except; on failure stay in CONFIRM and show a popup ("Попробуйте нажать «Отправить» ещё раз.").
- Handle `/help` mid-flow without resetting the step.

## 6. Verification

- Import check: `python -c "import max_bot.handlers.handlers"` with dummy tokens.
- Simulate the flow by feeding raw update dicts to the dispatcher (menu → intro → instruction → each step → restart → send → home) and print what the bot sends/edits; check every keyboard ends with the home row.
- Grep that no text still references renamed buttons (e.g. old «Прекратить формирование», «Отправить сообщение»).
