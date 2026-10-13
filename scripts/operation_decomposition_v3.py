"""Protocol v3 for operation decomposition: per-step decisions, mechanically compiled.

v2 (atlas-anchored structure) still let the agent hand-write nodes, ports and edges, which produced
structural errors, and its keyword table left recurring choices open (library call vs unexpanded
boundary). v3 asks only for one decision per fixed atlas step: a closed category plus, for library
categories, the operation call(s) and stated parameter values. Nodes, ports and data flow are built by
compile_v3 from the atlas skeleton, so the published document format is unchanged.
"""

import json
import re

from scripts.operation_decomposition import EVIDENCE_KINDS, PHASES, _obj, _string_or_null
from scripts.operation_decomposition_v2 import atlas_skeleton as _atlas_skeleton_v2, route_signatures, validate_v2  # noqa: F401

PROTOCOL = "operation-decomposition-v3.2"

BOUNDARY_CATEGORIES = ["source_provenance", "external_generator", "learned_module", "fusion_unspecified",
                       "no_catalog_operation", "identity"]
CATEGORIES = ["library_operation"] + BOUNDARY_CATEGORIES


def extraction_schema_v3(catalog, skeleton):
    ev = _obj({"section_id": {"type": "string"}, "quote": {"type": "string"},
               "kind": {"type": "string", "enum": EVIDENCE_KINDS}})
    op_ids = [b["operation_id"] for b in catalog["blocks"]]
    params = sorted({p for b in catalog["blocks"] for p in b["parameters"]})
    call = _obj({"operation_id": {"type": "string", "enum": op_ids},
                 "parameters": {"type": "array", "items": _obj({"name": {"type": "string", "enum": params},
                                                                 "value": {"type": "string"}})}})
    step_ids = [s for cfg in skeleton for r in cfg["routes"] for s in r["expected_step_ids"]]
    decision = _obj({"step_id": {"type": "string", "enum": step_ids}, "chain_element": {"type": "string"},
                     "category": {"type": "string", "enum": CATEGORIES},
                     "calls": {"type": "array", "items": call},
                     "evidence": {"type": "array", "items": ev},
                     "rationale": {"type": "string"}, "uncertainty": _string_or_null()})
    proposal = _obj({"step_id": {"type": "string", "enum": step_ids}, "source_operation": {"type": "string"},
                     "why_no_existing_operation": {"type": "string"},
                     "compared_operation_ids": {"type": "array", "items": {"type": "string", "enum": op_ids}}})
    return _obj({"record_id": {"type": "string"}, "decisions": {"type": "array", "items": decision},
                 "operation_proposals": {"type": "array", "items": proposal}})


RULES_V3 = """Output contract v3 (enforced mechanically; violations are returned to you).

You return ONE decision per expected step of the atlas skeleton below, for every route of every
configuration, each step_id exactly once. You do not write nodes, ports or edges: they are compiled
from the skeleton (step k consumes step k-1's result; the last step yields the model-visible form).
A decision = step_id + chain_element (copied exactly from the skeleton for that step_id; it is checked)
+ category + calls + evidence + rationale (+ uncertainty). Write the decisions route by route, in chain
order, so that each decision is made for the element shown next to its step_id.
Identical chain elements in the same paper get identical decisions unless the paper states a different
computation for them.

Read each step as: route source_object_verbatim -> chain elements in order -> model_visible_form_verbatim.
Find what the PAPER TEXT says about that chain element (the atlas evidence_quote and section_heading
point to where it is described) and decide with the procedure below.

DECISION PROCEDURE (apply the rules in order; the first rule that applies decides).
General: decide each element by the computation its OWN wording applies to the data -- not by the
surrounding prompt, not by modules mentioned only as context, not by purpose clauses ("to form a
prompt", "for communication classification" are not operations).
P  a route with a fixed_decision in the skeleton (no chain recorded) is already decided: return exactly
   that category and operation_ids for its single step, with evidence; give stated parameter values.
R0 identity (calls empty): the element only NAMES a data object or representation -- the input itself
   ("single-cell RNA-seq profiles", "textual annotation") or a resulting state ("intermediate
   embedding c'", "soft prompts", "token-level embeddings", "Mistral-compatible embeddings") -- and
   does not name a computation; also an element that lists what content an input contains ("gene
   entity and its functions", "instruction and text", "protein entity, the phenotype and the
   relations"). Also: the model receives the data as they are.
   Not R0: embeddings whose element text itself names the producing model ("CellWhisperer-derived
   embeddings", "embeddings from the X encoder"; a bare "transcriptome embedding" stays R0) -> learned_module (R3); a text format produced from non-text data ("cell
   sentence", "prompt") -> serialize (R6).
R1 source_provenance (calls empty): the element names an ORIGIN or study set-up -- dataset, database,
   atlas, cohort, repository, download/retrieval (API, GEO, SRA, PubMed, CELLxGENE ...), manual curation
   or annotation by people, benchmark construction, an evaluation task, split or scenario -- and states
   no rule applied to the data. A statement of the task the model performs ("estimate the proportions
   of cell types", "predict expression of the target modality", "structured prediction of DEG
   outcomes", "clustering" as a downstream task) is also R1, and so is assigning items to training /
   validation / test splits or folds, also when the assignment rule is stated ("h <= 7 go to train",
   "randomly partitioned as an independent test set", "five-fold cross-validation"), and so is training on a corpus ("train on
   combined perturbation corpora"), merging datasets or corpora ("merged into OmniGene-SFT-v1",
   "merged into the SFT corpus"), labelling examples with classes ("labelled as Homologous /
   Non-Homologous"), balancing classes of a benchmark ("balanced labels") and a "0-shot setup". If the same element also states a filter or criterion ("downloaded from
   BioGRID and filtered for Homo sapiens"), it is select (R6), not R1.
R2 external_generator (calls empty): the content is written by another generative model (GPT-4, GPT-4o,
   Mixtral, Llama ... used to write, rewrite, summarise, condense, paraphrase, caption or generate
   conversations). Manual curation or annotation by people is R1, not R2.
   A prompt or prompting step whose purpose is to make such a generator write content ("LLM rewrite
   prompt", "zero-shot GPT-4 prompting", "prompt construction for conversation generation" when an
   external LLM writes the conversations) is also R2. A prompt, question or template given to the
   model under study itself ("prompt CellHermes to generate an explanation", where CellHermes is the
   model under study) is serialize (R6).
R3 named learned module -- take the first matching line:
   - the module that performs THIS element decides (in "the LLM-processed prompt projected into the
     latent space by a query connector" it is the connector -> project)
   - the receiving model or any pretrained LLM / decoder / backbone / foundation model (also "X decoder
     with LoRA on self-attention modules", also when its attention architecture is described, also
     "aligned to a Qwen LLM backbone": alignment to a model or embedding space is never align)
     ................................................................. learned_module (calls empty)
   - the CHAIN ELEMENT TEXT ITSELF names the module's layers or layer count ("2-layer MLP projection",
     "linear layer followed by LayerNorm") -> one call per layer / operation named in the element, in
     order, with the count taken from the element text (linear/MLP layer = project, batch/layer/L2
     normalisation = normalize; activations are the project activation parameter). A different count
     elsewhere in the paper is ignored for the call count and noted in uncertainty.
   - otherwise the module is ONE call (or one boundary) decided by its name with the lines below, even
     when the paper describes its internals elsewhere; record the stated architecture in the call's
     method parameter (e.g. method = "two-layer MLP with batch normalisation and leaky ReLU").
   - an element that names such a module together with conditioning wording ("adapter-mediated
     conditioning") is decided here by the module (adapter -> project), not by R4
   - Q-Former or Perceiver resampler: if the paper describes its layers as self-attention among the
     queries and cross-attention to the features -> self_attention, cross_attention (two calls);
     otherwise -> cross_attention (one call). The same holds for every occurrence in the paper
     ("Q-Former", "shared-weight Q-Former", "Q-Former initialized from BLIP-2").
   - the paper states cross-attention as the module's computation (also when the module is called
     a projector) ...................................................................... cross_attention
   - name contains projector, projection, linear, MLP, adapter, connector, or the module maps
     features into the language-model embedding space ................................ project
   - tokenizer of any kind (BPE, WordPiece, k-mer, VQ / RVQ / codebook tokenizer) ......... tokenize
   - embedding layer or embedding table; embedding of token / gene / value ids ........... lookup
   - taking a particular position or layer from a model's output (last token, [CLS], final layer,
     mean of the last layer is add) ........................................................ select
   - convolution layers (1D/2D convolution, GCN / graph convolution, message passing) named as the
     element ...................................................... no_catalog_operation (R7)
   - any other named learned network, framework or method (encoder, "encoded via the modality-specific
     encoders", RVQ encoder, decoder, backbone,
     transformer, GNN, ViT, LLM, foundation model, denoiser, "...framework"), and embeddings that a
     model generates or computes ("contextual gene embeddings generated by X"), positional encodings
     inside a model (RoPE, sinusoidal or learned position embeddings), and generation performed by the
     model under study (autoregressive generation of descriptions, protein outfilling, diffusion
     denoising, predicting outputs) ..................................... learned_module (calls empty)
R4 fusion or conditioning wording ("combined with", "paired with", "conditioned on", "conditioning",
   "integrated with", "fused"):
   - the paper states concatenation / appending / prepending / interleaving into one sequence -> concatenate
   - the paper states addition or summation ............................................ add
   - the paper states cross-attention ................................................. cross_attention
   - the data are written into a prompt or text ("incorporated X into the prompt", "merge the prompt
     with the specified cell type / metadata", "combine the prompt with the cell sentence",
     "attach metadata", "provide X and Y
     in the prompt") ............................................................... serialize
   - guidance wording (bias, guide, drive or steer generation or samples; constraints and penalties)
     ................................................................ fusion_unspecified (calls empty)
   - otherwise -- whatever is being conditioned on, however unusual -- fusion_unspecified (calls empty);
     never no_catalog_operation for conditioning wording
   "paired with" between two inputs that the model receives together ("paired with transcriptome-
   derived token embeddings") is fusion wording. Only building example pairs from data ("paired each
   question with the matched transcriptome embedding and randomly sampled mismatched ones") is R6
   sample/align.
R6 every other stated computation -> library_operation, one call per operation NAMED IN THE ELEMENT
   TEXT, in the stated order (do not add operations that the paper describes for the same data
   elsewhere: "tokenization" is one tokenize call even if the paper explains that tokenization
   normalises and ranks; the earlier chain elements carry those operations) (when several are stated in one sentence, use the order in which they are applied to the data),
   using this mapping:
   text from data by a template, prompt format, instruction template ("designed N template types"),
     cell sentence, field rendering, a fixed question asked to the model, data "presented / written /
     formatted as" a list or text, delimiter or special tokens marking structure inside one text/token
     stream; few-shot exemplars written into the prompt ("text-only 1-shot exemplar", "2-shot
     exemplar"); a dummy text placeholder put in the prompt instead of an image; providing, presenting,
     attaching, asking or instructing something IN THE PROMPT of the model under study ("provide gene
     expression profile and metadata", "ask for free-form cell type generation", "attach a predefined
     candidate label set", "present the candidate label set"); "prompt matches the
     SFT training prompt" .................................................................. serialize
   keep a subset by a stated criterion: filter, QC, top-k, "top N (most) highly expressed / top N gene
     sets", truncate or trim a list or conversation to its first / top N items ........... select
     (one select call; rank is NOT added for top-N selection, also when the element says "ranked":
     "the top-200 ranked genes" is select; "conversion to ranked Cell Sentences of topK = 200" is
     select, serialize); an element with rank / order wording and no N is rank; text cleaning that removes characters,
     symbols or records ("removed special characters using unidecode") is also select
   rank / sort by value or by stated keys where the order is kept in the output (rank-ordered gene
     list, "tokens ordered by flow, space, and then time") .................................. rank
   normalisation (library size, CP10K, TPM, z-score, LayerNorm, L2, min-max) ............... normalize
   log / log1p ....................................................................... log_transform
   discretise VALUES into intervals or coarser levels: each value or label is mapped to a level
     ("23 Carnegie stages grouped into four developmental bins", ages into age groups) ..... bin
   divide a sequence, genome, image or set into parts that are ALL kept (keeping one part and
     discarding the rest -- ROI extraction, cropping, centring a window on a region, extracting
     fields -- is select): windows, bins, patches, chunks, tiles, or groups
     by metadata or labels: a collection of ITEMS is divided ("segmentation into 200bp bins",
     "grouped the cells by metadata", neighbourhoods by a radius, sectors around a centre cell)
     ................................................................................... partition
   join two or more separately produced sequences end to end (only when every part already exists as
     its own token or embedding sequence; writing data into a prompt is serialize); stack channels or
     feature matrices
     ("stack channels 1, 2, 3 with channels 4, 5, 6") ....................................... concatenate
   sum, weighted sum, mean or weighted average of vectors; aggregation or pooling of profiles
     ("aggregate ... into pseudo-bulk samples"), also when sum vs mean is not stated ........ add
   explicit random draw of examples, negatives, noise or masks; random shuffling or permutation;
     random choice of a template ("question template selection" when the paper says it is random;
     otherwise select) ......................................................................... sample
   pair or match DATA items with each other (pair samples, map identifiers, register coordinates)
     ...................................................................................... align
     (never align: "align to natural language" or mapping into an embedding space -> project;
     centring or cropping around a region -> select; attaching metadata to text -> serialize)
   mask or overwrite values / nodes / tokens at positions; replace a placeholder token in the model
     input by an embedding ("replaces <omics> in the LLM input") ............................. update
   pad a sequence to a fixed length, or truncate it to a fixed length in tokens, characters or base
     pairs ("truncated to 3000 bp", "input truncated to 500 characters") ................... pad
     (truncating a LIST to its first / top N items is select)
   reshape, flatten, broadcast (values unchanged, only arranged differently) ............. reshape
   impute / fill missing ................................................................. impute
   clamp / clip .......................................................................... clamp
   augmentation (random perturbation used for training, including named noise methods such as
     NEFTune noise added to embeddings) ...................................................... augment
   stated self-attention ................................................................. self_attention
R7 a computation applied to the data is stated but no operation above represents it (e.g. computing
   clusters as an input to the model, physics-based energy terms, symmetry tessellation, resizing or
   resampling an image to a resolution ("resize to 224 x 224 x 3" is not reshape). Computing a
   score, distance (incl. optimal transport), loss, perplexity, probability or gradient is always R7, and
   so is a training objective ("contrastive learning alignment", "contrastive alignment with paired
   text embeddings" -- never align),
   also when the scores are then compared or ranked for evaluation -> no_catalog_operation (calls empty) and add an
   operation_proposals entry for the step.

calls is non-empty exactly when category is library_operation. Parameter values are only values the
paper states for this element; for every other declared parameter write exactly "unspecified" (you
may omit those -- they are filled mechanically). Never infer a value from convention.
evidence: 1-3 quotes copied VERBATIM (exact substring) from the cited section of the paper text that
show the element; the atlas evidence_quote may be reused when it is literally in that section.
rationale: one sentence naming the rule applied (e.g. "R3: Q-Former -> cross_attention").
"""

TEXT_FORM = re.compile(r"\b(prompts?|texts?|textual|sentences?|questions?|quer(y|ies)|descriptions?|captions?|"
                       r"instructions?|conversations?|dialogues?|answers?|narratives?|summar(y|ies))\b", re.I)


def atlas_skeleton(record_id, atlas=None):
    """v2 skeleton plus a mechanically fixed decision for routes without a recorded chain (rule P)."""
    skeleton = _atlas_skeleton_v2(record_id, atlas)
    for cfg in skeleton:
        for route in cfg["routes"]:
            if not route["chain_recorded"]:
                text = bool(TEXT_FORM.search(route["model_visible_form_verbatim"] or ""))
                route["fixed_decision"] = {"category": "library_operation" if text else "identity",
                                           "operation_ids": ["serialize"] if text else []}
    return skeleton


PRIMARY_PORT = {"lookup": "keys", "sample": "distribution", "cross_attention": "queries", "update": "state"}


def _node(node_id, rtype, info, role, evidence):
    return {"node_id": node_id, "representation_type": rtype, "symbolic_shape": None, "axis_semantics": None,
            "information_content": info, "contextual_role": role, "evidence": evidence, "uncertainty": None}


def check_decisions(dec_doc, record_id, skeleton, catalog):
    errors = []
    if dec_doc.get("record_id") != record_id:
        errors.append(f"record_id must be {record_id}")
    want = [s for cfg in skeleton for r in cfg["routes"] for s in r["expected_step_ids"]]
    got = [d["step_id"] for d in dec_doc.get("decisions", [])]
    if sorted(set(want) - set(got)):
        errors.append(f"missing decisions for steps {sorted(set(want) - set(got))}")
    dup = sorted({s for s in got if got.count(s) > 1})
    if dup:
        errors.append(f"steps decided more than once {dup}")
    blocks = {b["operation_id"]: b for b in catalog["blocks"]}
    element = {s: e for cfg in skeleton for r in cfg["routes"] for s, e in zip(r["expected_step_ids"], r["transformation_chain_verbatim"])}
    for d in dec_doc.get("decisions", []):
        if d["step_id"] in element and d.get("chain_element") != element[d["step_id"]]:
            errors.append(f"{d['step_id']}: chain_element must be exactly {element[d['step_id']]!r} (the element of THIS step); "
                          "check that the decision was written for this step and not for a neighbouring one")
        lib = d["category"] == "library_operation"
        if lib and not d["calls"]:
            errors.append(f"{d['step_id']}: category library_operation needs at least one call")
        if not lib and d["calls"]:
            errors.append(f"{d['step_id']}: category {d['category']} must have no calls")
        if not d["evidence"]:
            errors.append(f"{d['step_id']}: decision needs evidence")
        for c in d["calls"]:
            bad = [p["name"] for p in c["parameters"] if p["name"] not in blocks[c["operation_id"]]["parameters"]]
            if bad:
                errors.append(f"{d['step_id']} / {c['operation_id']}: parameters not declared for this operation {bad}")
    fixed = {r["expected_step_ids"][0]: r["fixed_decision"] for cfg in skeleton for r in cfg["routes"] if r.get("fixed_decision")}
    for d in dec_doc.get("decisions", []):
        f = fixed.get(d["step_id"])
        if f and (d["category"] != f["category"] or [c["operation_id"] for c in d["calls"]] != f["operation_ids"]):
            errors.append(f"{d['step_id']}: this step has a fixed_decision {f}; return exactly that")
    if not errors:
        proposed = {p["step_id"] for p in dec_doc.get("operation_proposals", [])}
        for d in dec_doc["decisions"]:
            if d["category"] == "no_catalog_operation" and d["step_id"] not in proposed:
                errors.append(f"{d['step_id']}: no_catalog_operation needs an operation_proposals entry")
    return errors


def compile_v3(dec_doc, record_id, skeleton, catalog):
    """Build the full (v1/v2 format) decomposition document from per-step decisions."""
    blocks = {b["operation_id"]: b for b in catalog["blocks"]}
    by_step = {d["step_id"]: d for d in dec_doc["decisions"]}
    trajectories = []
    for cfg in skeleton:
        nodes, steps, receipt, t_ev = [], [], [], []
        for route in cfg["routes"]:
            first = by_step[route["expected_step_ids"][0]]
            prev = f"{route['route_id']}__src"
            nodes.append(_node(prev, "source_object", route["source_object_verbatim"], "route source", first["evidence"]))
            n_steps = len(route["expected_step_ids"])
            for k, (sid, element) in enumerate(zip(route["expected_step_ids"], route["transformation_chain_verbatim"]), 1):
                d = by_step[sid]
                t_ev = t_ev or d["evidence"]
                out = f"{sid}__out"
                last = k == n_steps
                nodes.append(_node(out, "model_visible_form" if last else "intermediate",
                                   route["model_visible_form_verbatim"] if last else element,
                                   "model-visible form" if last else f"result of {element}", d["evidence"]))
                inter, calls = [], []
                if d["category"] != "library_operation":
                    calls = [{"operation_id": None, "inputs": [], "outputs": [], "parameters": [],
                              "condition": None, "uncertainty": f"{d['category']}: {d['rationale']}"}]
                else:
                    cur = prev
                    for j, c in enumerate(d["calls"], 1):
                        block = blocks[c["operation_id"]]
                        primary = PRIMARY_PORT.get(c["operation_id"], block["inputs"][0]["name"])
                        dst = out if j == len(d["calls"]) else f"{sid}__i{j}"
                        if dst != out:
                            inter.append({**_node(dst, "intermediate", f"result of {c['operation_id']} in {element}",
                                                  "within-step intermediate", d["evidence"]), "origin": "documented_intermediate"})
                        inputs = [{"port": primary, "node_ids": [cur]}]
                        for p in block["inputs"]:
                            if p["name"] != primary and not p["optional"]:
                                aux = f"{sid}__{j}_{p['name']}"
                                inter.append({**_node(aux, "implicit_parameter", f"{p['name']} of {c['operation_id']} ({p['meaning']})",
                                                      "operation operand not given as a route", d["evidence"]), "origin": "implicit_parameter"})
                                inputs.append({"port": p["name"], "node_ids": [aux]})
                        given = {p["name"]: p["value"] for p in c["parameters"]}
                        params = [{"name": n, "value": (given.get(n) or "").strip() or "unspecified"} for n in block["parameters"]]
                        calls.append({"operation_id": c["operation_id"], "inputs": inputs,
                                      "outputs": [{"port": block["outputs"][0]["name"], "node_ids": [dst]}],
                                      "parameters": params, "condition": None, "uncertainty": None})
                        cur = dst
                steps.append({"step_id": sid, "route_id": route["route_id"], "chain_element": element,
                              "component": d["category"], "operation_type": d["rationale"],
                              "inputs": [{"node_id": prev, "port_role": "input"}], "outputs": [out],
                              "evidence": d["evidence"], "uncertainty": d["uncertainty"],
                              "intermediate_nodes": inter, "decomposition": calls, "bypasses": []})
                prev = out
            receipt.append({"node_id": prev, "port_role": route["route_label"]})
        phase = cfg["lifecycle_phase"] if cfg["lifecycle_phase"] in PHASES else "unspecified"
        trajectories.append({"trajectory_id": cfg["configuration_id"], "model_variant": cfg["model_name"],
                             "task_configuration": cfg["task_or_configuration_verbatim"] or "unspecified",
                             "lifecycle_phase": phase, "model_role": "primary_model",
                             "recipient_component": cfg["model_name"], "nodes": nodes, "steps": steps,
                             "receipt_inputs": receipt, "evidence": t_ev, "open_questions": []})
    proposals = [{"source_operation": f"{p['step_id']}: {p['source_operation']}",
                  "why_no_existing_operation": p["why_no_existing_operation"],
                  "compared_operation_ids": p["compared_operation_ids"]} for p in dec_doc.get("operation_proposals", [])]
    return {"record_id": record_id, "trajectories": trajectories, "coverage_questions": [], "operation_proposals": proposals}


def decision_signatures(dec_doc):
    """Per step: category + ordered operation ids (for agreement diagnostics)."""
    return {d["step_id"]: (d["category"], tuple(c["operation_id"] for c in d["calls"])) for d in dec_doc["decisions"]}
