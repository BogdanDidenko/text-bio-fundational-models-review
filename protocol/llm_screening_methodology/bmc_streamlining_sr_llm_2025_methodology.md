# Streamlining Systematic Reviews With LLMs (Trad et al., 2025)

## Citation

Trad F, Yammine R, Charafeddine J, Chakhtoura M, Rahme M, El-Hajj Fuleihan G, Chehab A. *Streamlining systematic reviews with large language models using prompt engineering and retrieval augmented generation*. BMC Medical Research Methodology. 2025;25:130. doi: [10.1186/s12874-025-02583-5](https://doi.org/10.1186/s12874-025-02583-5)

## What the paper is about

Ця стаття порівнює ручний screening, Rayyan і власний GPT-4 pipeline на завершеному systematic review про vitamin D та falls. Головна методологічна ідея проста й сильна: не просити LLM винести один “загальний вердикт”, а подавати ті самі критерії screening у вигляді послідовності структурованих питань. Модель відповідає `yes` / `no` / `unsure`, а всі `unsure` переходять у manual review. Автори спершу застосовують це до title/abstract screening, а потім розширюють до full-text screening через RAG.

## Methodological takeaways

- Найсильніше рішення в paper: `question-by-question screening`. Модель не робить одну непрозору класифікацію, а проходить через ті самі критерії, якими користується людина.
- Дизайн явно `sensitivity-first`. Якщо модель не впевнена, запис не відкидається, а зберігається для ручного перегляду. Це знижує ризик false excludes.
- Structured outputs принципово важливі. Автори логують результат кожного питання в таблицю, що створює audit trail і дозволяє перевірити не лише фінальний label, а й шлях до нього.
- Налаштування порога виключення завжди є trade-off. Методологічний висновок не в тому, щоб “максимально автоматично відсіяти”, а в тому, щоб не втратити релевантні статті.
- Full-text RAG корисний як окремий другий етап, але його не треба змішувати з першою задачею. Для нашого репозиторію це радше майбутній модуль, а не причина ускладнювати title/abstract screening вже зараз.
- Результат сильно залежить від якості prompt design і retrieval, а не лише від назви моделі. Тобто paper радше валідовує pipeline pattern, ніж доводить універсальну продуктивність будь-якого LLM.

## Practical implications for our pipeline

- Наш title/abstract screening варто формулювати як послідовність перевірок по критеріях, а не як одну інструкцію “виріши include/exclude”.
- `UNCERTAIN` треба лишити окремим, навмисним станом. Це не шум і не збій пайплайну, а контрольований механізм збереження recall.
- Потрібно логувати відповіді по кожному критерію окремо, а не лише фінальне рішення. Це особливо важливо для нашої теми, де часто ламається межа між `text+bio`, `encoder-only`, `wrapper`, `benchmark` і `application`.
- Базовий policy має бути консервативним: якщо з abstract неясно, чи є generative architecture, чи є реальний text-bio bridge, чи paper справді про model paper, запис має йти в manual review.
- Якщо пізніше додавати full-text assistance, її треба оцінювати окремо від title/abstract screening і не змішувати з поточною задачею калібрування критеріїв.

## Recommended actions for this repo

- Перебудувати screening prompt у формат `criterion-by-criterion`, де кожен критерій має окрему відповідь і окреме коротке пояснення.
- Зберегти явний `UNCERTAIN` outcome та описати в protocol, що він автоматично означає escalation to manual review.
- Додати логування по кожному критерію: `ic1_bio_modality`, `ic2_text_component`, `ic3_generative`, `ic4_fm_evidence`, `paper_type`, `final_decision`, `decision_reason`.
- Додати правило консервативного fallback: невизначеність щодо modality, pretraining, foundation-model status або типу paper не повинна перетворюватися на автоматичний `EXCLUDE`.
- Якщо пізніше тестувати full-text RAG, робити це як окремий модуль з власним benchmark set і окремою оцінкою, а не як розширення безпосередньо поточного pilot screening.
