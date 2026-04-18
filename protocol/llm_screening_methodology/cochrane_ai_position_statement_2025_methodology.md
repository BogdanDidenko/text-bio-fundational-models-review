# Cochrane AI Position Statement (Flemyng et al., 2025)

## Citation

Flemyng E, Noel-Storr A, Macura B, Gartlehner G, Thomas J, Meerpohl JJ, Jordan Z, Minx J, Eisele-Metzger A, Hamel C, Jemioło P, Porritt K, Grainger M. *Position statement on artificial intelligence (AI) use in evidence synthesis across Cochrane, the Campbell Collaboration, JBI and the Collaboration for Environmental Evidence 2025*. Cochrane Database of Systematic Reviews. 2025;(11):ED000178. doi: [10.1002/14651858.ED000178](https://doi.org/10.1002/14651858.ED000178)

## What the paper is about

Це editorial/position statement, а не benchmark-study. Його цінність у тому, що він задає рамку допустимого використання AI в evidence synthesis для найконсервативніших гравців у полі: Cochrane, Campbell, JBI та CEE. Текст спирається на RAISE recommendations і формулює базовий принцип: AI можна використовувати, але відповідальність, обґрунтування, валідація і прозоре звітування залишаються на авторах review.

## Methodological takeaways

- Автори прямо фіксують, що evidence synthesists залишаються остаточно відповідальними за зміст, методи, висновки та рішення використовувати AI.
- AI допустимий лише тоді, коли його використання не підриває methodological rigour, trustworthiness і integrity review.
- Якщо AI робить або підказує judgment, це має бути повністю й прозоро задокументовано в manuscript або supplementary materials.
- Перед використанням AI потрібно критично оцінити, чи є в tool належні evaluation, validation і зрозумілі обмеження саме для цього контексту задачі.
- Автори наголошують не лише на технічних ризиках, а й на legal/ethical аспектах: copyright, provenance, confidentiality, privacy, licensing, jurisdiction.
- Важливий практичний принцип: use of AI є окремим methodological trade-off decision. Тобто ми маємо не просто “спробувати LLM”, а явно обґрунтувати, чому в нашому review цей trade-off прийнятний.

## Practical implications for our pipeline

- Для нашого screening pipeline недостатньо показати, що модель “працює технічно”. Потрібно окремо обґрунтувати, чому такий pipeline не створює неприйнятний ризик false excludes або систематичного bias.
- Ми маємо описувати не лише prompt і outputs, а й чому конкретна модель/інструмент взагалі придатні для цієї задачі: яка є validation evidence, які відомі failure modes і які є risk-mitigation steps.
- `UNCERTAIN -> manual review` добре узгоджується з логікою statement, бо зберігає human oversight над judgment-heavy decisions.
- Для нашої теми особливо критично обмежити scope AI-рішень: LLM може допомагати у title/abstract screening, але не має непомітно підміняти людське протокольне рішення там, де abstract неоднозначний.
- Нам потрібен явний policy, які стадії review дозволено автоматизувати, а які залишаються human-only або human-adjudicated.

## Recommended actions for this repo

- Додати короткий `AI use justification` note до protocol: чому ми використовуємо LLM у screening, які очікувані вигоди, які ризики і які safeguards застосовуємо.
- Для кожного screening run фіксувати не лише технічні параметри, а й `validation_basis`: на якому benchmark set або manual calibration set було підтверджено, що цей prompt/model прийнятні.
- Явно описати `human oversight policy`: які рішення модель може приймати самостійно, які автоматично переходять у manual review, хто робить adjudication.
- Додати `limitations and risk` section для AI-assisted screening: false exclusion risk, ambiguity in abstracts, model drift, prompt sensitivity, dependence on provider/runtime.
- Окремо задокументувати legal/data governance питання: що саме відправляється в API або локальний inference server, чи використовуємо лише bibliographic metadata та abstracts, і як забезпечується reproducibility.
- У майбутньому prompt/model revisions робити лише разом з коротким validation note, а не як “тиху” заміну інструмента в pipeline.
