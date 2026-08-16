# Analyst review of the largest route-count changes

Date: 2026-08-17

## Scope

This review inspects the old and current route annotations for the 15 shared
records with the largest absolute count changes. It is separate from the
deterministic matcher and was written after examining model names, lifecycle
phases, source objects, carrier families/subtypes, tasks, and route labels. No
LLM was invoked for the migration run. These are migration diagnoses, not
changes to either canonical taxonomy output and not a substitute for checking
the cited full-document evidence in the cases marked substantive.

## Review

| Record | Delta | Dominant explanation | Assessment and required resolution |
|---|---:|---|---|
| `full_2026-07-06__rec_001617` Cell-o1 | +22 | Model-by-task decomposition | The current run expands four umbrella routes into evaluation routes for Cell-o1 and six comparator LLMs across cell-, batch-, open-ended-, and constrained-QA tasks. The carrier remains text-native throughout. This is not 22 new representation mechanisms. Review whether comparator LLMs are in-scope study models or evaluation baselines before retaining the extra models/routes. |
| `full_2026-07-06__rec_000090` C2S-Scale | -19 | Task aggregation | The old run separates many pretraining, spatial, perturbation, and evaluation tasks; the current run combines related tasks into 15 broader routes while preserving a text-native carrier. Because the classification unit includes task/input configuration, composite labels such as “spatial neighborhood prediction and related spatial tasks” require de-aggregation or an explicit equivalence rule. |
| `full_2026-07-06__rec_000086` ProCyon | +18 | Mixed task expansion and carrier recoding | The current run expands table/list entries and evaluation tasks, removes the PROCYON-BIND model label, reduces geometric routes from six to one, and introduces three dense routes. Case variants `PROCYON`/`ProCyon` normalize to one ID but remain inconsistent in display text. This is a substantive interface-boundary case, not a count-only migration; verify source object, actual model-visible carrier, lifecycle, and baseline status from full sections. |
| `full_2026-07-06__rec_001352` Med-PaLM M | +15 | Paired-route decomposition | All 14 old routes receive a plausible current link. The extra routes largely separate the textual question, indication, or clinical context from its paired image and distinguish datasets/tasks. Families remain text-native plus visual raster. This is consistent with route-level annotation, provided that repeated dataset variants are genuinely distinct permitted input configurations. |
| `full_2026-07-06__rec_003517` X-Cell | +15 | Evaluation expansion plus carrier recoding | The current run enumerates held-out cell types, donors, stimulation conditions, and evaluation datasets, while recoding old multi-track discrete control-cell routes as dense embeddings. Dense routes rise from 7 to 20 and discrete routes fall from 3 to 0. Verify the immediate model-visible representation of control cell sets and decide whether dataset/donor splits constitute distinct configurations. |
| `full_2026-07-06__rec_003394` OmniNA | +13 | Benchmark-task decomposition | Sixteen OmniNA-1.7B evaluation tasks are represented separately in the current run; the old run has one aggregate saturation-mutation evaluation route. The increase is primarily task granularity, not a new family: 19/21 current routes are native biological symbol streams. Establish a consistent policy for benchmark tasks that share the same model-visible nucleotide carrier. |
| `full_2026-07-06__rec_003323` TeamPath | -11 | Agent-role aggregation and model normalization | The old run separately records VQA, verifier, self-corrector, reason-corrector, caption, and router inputs. The current run normalizes TeamPath to TeamPath-7B and collapses verifier/corrector activity into broader visual and textual collaboration routes. Because outputs reused by downstream agents can be actual inputs, inspect the full workflow before treating the removed routes as duplicates. |
| `full_2026-07-06__rec_003434` Longevity-LLM | -9 | Lifecycle/model coverage loss | The current run retains nine fine-tuning routes but drops the old evaluation routes and the Qwen3-14B RFT entry. This is not explained solely by wording or aggregation. Verify whether evaluation inputs and the RFT model are valid in-scope configurations; otherwise record their explicit exclusion reasons. |
| `july_update_2026-07-06__rec_000060` CellTosg2Sequence | +9 | Lifecycle and dataset-split expansion | The same two principal carrier families remain, but the current run adds inference/evaluation routes and separate HCA train, validation, and test entries. Dataset partition alone is not necessarily a distinct model-visible route. Consolidate split-only duplicates unless the supplied input or model configuration changes. |
| `june_update_2026-06-10__rec_000148` SciCore-Omics | -8 | Text-route omission plus dense-subtype recoding | Current routes preserve visual and continuous biological inputs but remove all four text-native routes and recode connector-mediated expression embeddings as virtual-token prefixes. Since this corpus requires a text interface, omission of questions/class names/instructions is potentially substantive. Recheck both text inputs and the exact insertion topology. |
| `full_2026-07-06__rec_001830` OpticalDNA | -6 | Species-level consolidation | Twelve old routes are HG38/Rice versions of six tasks; the current run retains one route per task. The carrier and lifecycle are unchanged. This is a defensible consolidation if species is treated as a data variant, but not if organism-specific source objects define separate permitted configurations. The policy must be stated and applied consistently. |
| `full_2026-07-06__rec_001889` scMOBA | +6 | Task expansion plus carrier recoding | Four principal old inputs remain recognizable, but current evaluation/inference tasks are expanded and three old dense evaluation routes become native biological symbol streams. Verify whether expression and gene-activity values reach the model as tokens or projected continuous vectors; route counts should be revised only after that interface decision. |
| `full_2026-07-06__rec_003043` Geneverse | -6 | Model/configuration normalization | The old run treats LoRA, RAG, and full-tuning variants as 14 model names; the current run collapses them into eight base model names. Adaptation method belongs more naturally to configuration than model identity, but those configurations must remain represented rather than disappear. Confirm that LoRA/RAG/full variants survive in configuration-level fields. |
| `full_2026-07-06__rec_003629` GEMGen | +5 | Phase/task decomposition with a possible evaluator | The current run separates Phase I/II and several evaluation settings and adds a `compound-phenotype scoring model`. Check whether that scoring model consumes an in-scope route as part of the generative system or is only an output evaluator/baseline; the latter must not inflate the model or route denominator. |
| `june_update_2026-06-10__rec_000248` Cell2Text | -5 | Backbone/configuration collapse | The old run distinguishes Llama LoRA, Llama full, and Gemma variants and their biological/text routes; the current run retains two generic Cell2Text routes. The common route design is clear, but model/backbone and tuning configurations were lost. Preserve the two route mechanisms while restoring configuration-level distinctions if the paper permits those variants as usable models. |

## Synthesis

The net increase of 60 routes on the shared 52-record cohort is not evidence of
60 newly discovered input mechanisms. The largest movements combine four
different phenomena:

1. **Decomposition:** model, task, dataset, or paired-modality combinations are
   represented separately in the current run.
2. **Aggregation:** several task- or role-specific routes are represented by one
   umbrella route.
3. **Entity normalization:** backbone, tuning, RAG, agent-role, and case variants
   move between model and configuration levels.
4. **Substantive recoding:** the same biological object is assigned a different
   carrier family/subtype or lifecycle phase.

The first three require a frozen granularity and entity-normalization policy.
The fourth requires full-section evidence review. Highest-priority scientific
checks are ProCyon, X-Cell, SciCore-Omics, scMOBA, TeamPath, and Longevity-LLM.
Cell-o1 and GEMGen additionally require an explicit baseline/evaluator scope
decision. Until those resolutions are recorded, the 489- and 586-route totals
are valid within-version outputs but should not be interpreted as directly
comparable prevalence estimates.
