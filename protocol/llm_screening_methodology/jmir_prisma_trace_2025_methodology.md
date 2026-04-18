# PRISMA-trAIce (Holst et al., 2025)

## Citation

Holst D, Moenck K, Koch J, Schmedemann O, Schüppstuhl T. *Transparent Reporting of AI in Systematic Literature Reviews: Development of the PRISMA-trAIce Checklist*. JMIR AI. 2025;4:e80247. doi: [10.2196/80247](https://doi.org/10.2196/80247)

## What the paper is about

Це методологічна пропозиція для прозорого звітування про використання AI/LLM як інструменту в systematic literature reviews, а не як об’єкта дослідження. Автори пропонують PRISMA-trAIce як розширення PRISMA 2020: 14 пунктів, що покривають title/abstract, methods, results і discussion, плюс адаптовану flow diagram, яка окремо розводить рішення людини та AI під час screening.

## Methodological takeaways

- Ключовий принцип: AI-асистований review має бути відтворюваним і аудитованим так само, як класичний SLR.
- Потрібно явно декларувати, де саме використовувався AI, з якою метою і на якому етапі процесу.
- Необхідно документувати не лише модель, а й доступ до неї, версію, провайдера, інпут, формат виходу, промпти, параметри та post-processing.
- Окремий фокус автори роблять на human-AI interaction: скільки рев’юерів перевіряли output, чи працювали вони незалежно, як вирішувалися розбіжності, чи було калібрування.
- Для screening корисна ідея розділяти records/reports, відхилені AI, відхилені людиною, та випадки, де AI лише підсвічував ризик, а фінальне рішення лишалося за людиною.
- Сильна сторона роботи: вона добре формалізує transparency requirements, але сама лишається proposal без повної Delphi/consensus validation, тобто її варто трактувати як робочий стандарт, а не кінцевий догматичний guideline.

## Practical implications for our pipeline

- Для title/abstract screening нам потрібен не лише prompt, а повний screening trace: модель, версія, temperature/top-p, system prompt, user prompt, few-shot examples, дата прогону, ідентифікатори пакетів записів.
- Рішення LLM не мають бути “чорним ящиком”; кожен `INCLUDE`, `EXCLUDE`, `UNCERTAIN` має зберігати коротке обґрунтування та code/criterion, на якій базувалося рішення.
- `UNCERTAIN` треба тримати як окремий, навмисний стан для manual review, а не як дефолтну помилку моделі.
- Потрібно вміти окремо порахувати performance AI: хоча б agreement з human labels, кількість false excludes, кількість false includes і частку записів, де AI реально зменшив навантаження.
- Для нашої теми це особливо важливо, бо межа між text+bio FM і біо-тільки або encoder-only моделями тонка, а отже потрібні прозорі heuristics і задокументовані приклади.

## Recommended actions for this repo

- Додати до `screening_log` поля: `llm_model`, `llm_provider`, `model_version`, `prompt_version`, `prompt_hash`, `temperature`, `top_p`, `run_id`, `screening_stage`, `decision_source` (`ai`/`human`/`hybrid`), `reviewer_count`, `disagreement_resolved_by`, `ai_reason`, `human_final_reason`.
- Додати окремий prompt registry або prompt manifest з повним текстом промптів, few-shot прикладами, датою зміни, метою використання і посиланням на відповідний pipeline step.
- Додати structured audit trail для кожного прогону: вхідний batch, сирий output моделі, post-processed output, ручну верифікацію, кінцеве рішення, причину розбіжності.
- Окремо зафіксувати data governance: що саме передається в API/локальну модель, чи є full-text/abstract only, і як обробляються сторонні cloud-сервіси.
- Оновити `screening_prompt.md`, щоб він містив явний шаблон відповіді, правила для `UNCERTAIN`, і короткий протокол ескалації для спірних кейсів.
- Додати короткий evaluation note до методології: на яких labeled records перевіряємо prompt, які метрики вважаємо прийнятними, і коли змінюємо prompt або модель.
