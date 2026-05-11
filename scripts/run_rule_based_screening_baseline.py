#!/usr/bin/env python3
"""Rule-based INCLUDE/EXCLUDE/UNCERTAIN baseline for text-bio model screening.

The baseline is intentionally simple and auditable.  It does not try to emulate
the LLM reviewers; it tests how far conservative lexical rules can go when the
target class is text/natural-language bridging with biological data and a
generative or foundation-model component.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


DECISIONS = ("INCLUDE", "UNCERTAIN", "EXCLUDE")


@dataclass(frozen=True)
class PatternGroup:
    name: str
    patterns: tuple[str, ...]

    def hits(self, text: str) -> list[str]:
        found: list[str] = []
        for pattern in self.patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(pattern)
        return found


BIO = PatternGroup(
    "bio",
    (
        r"\bbiomedical\b",
        r"\bbiology\b|\bbiological\b",
        r"\bgenom(?:e|ic|ics)\b|\bgene(?:s|tic)?\b",
        r"\bdna\b|\brna\b|\bnucleic acid\b",
        r"\bprotein(?:s)?\b|\bproteom(?:e|ic|ics)\b",
        r"\bcell(?:s|ular)?\b|\bsingle[- ]cell\b|\bscRNA[- ]seq\b|\bscATAC\b",
        r"\btranscriptom(?:e|ic|ics)\b|\bepigenom(?:e|ic|ics)\b",
        r"\bomics\b|\bmulti[- ]omics\b|\bspatial omics\b",
        r"\bhistolog(?:y|ical)\b|\bpatholog(?:y|ical)\b",
        r"\bclinical\b|\bpatient(?:s)?\b|\bdisease(?:s)?\b",
        r"\bdrug(?:s)?\b|\btherapeutic(?:s)?\b|\bphenotype(?:s)?\b",
        r"\bzellen\b|\bzell(?:e|en)\b",
    ),
)

NATURAL_LANGUAGE = PatternGroup(
    "natural_language",
    (
        r"\bnatural language\b",
        r"\bfree[- ]form\b",
        r"\btext(?:ual)?\b|\btext[- ]based\b",
        r"\bcaption(?:s|ing)?\b|\breport(?:s)?\b|\bdescription(?:s)?\b",
        r"\bquestion answering\b|\bqa\b|\bchat(?:bot|s|ting)?\b",
        r"\bconversation(?:al)?\b|\bdialog(?:ue|ue-based)?\b",
        r"\binstruction(?:s|[- ]following)?\b|\bprompt(?:s|ing)?\b",
        r"\blarge language model(?:s)?\b|\bLLM(?:s)?\b|\bGPT\b|\bChatGPT\b",
    ),
)

BRIDGE = PatternGroup(
    "text_bio_bridge",
    (
        r"\bmultimodal\b|\bmulti[- ]modal\b|\bany[- ]to[- ]any\b",
        r"\bcross[- ]modal\b|\bmodality alignment\b|\brepresentation alignment\b",
        r"\bvision[- ]language\b|\blanguage[- ]vision\b",
        r"\btext[- ]to[- ](?:image|protein|cell|omics|biology|bio)\b",
        r"\b(?:image|protein|cell|omics|bio|biology)[- ]to[- ]text\b",
        r"\btext[- ]condition(?:ed|ing)\b|\bcondition(?:ed|ing) on text\b",
        r"\bgenerat(?:e|es|ing|ion) (?:natural language |textual )?(?:description|caption|report|answer|text)s?\b",
        r"\b(?:natural language|text|prompt) (?:interface|query|queries|instruction|instructions)\b",
        r"\bchat(?:s|ting)? with (?:cell|cells|genes|genomes|data)\b",
        r"\bcell(?:s)? (?:chat|conversation|description|caption|report)s?\b",
    ),
)

EXPLICIT_TEXT_BIO_BRIDGE = PatternGroup(
    "explicit_text_bio_bridge",
    (
        r"\busing natural language prompts\b",
        r"\binstructed in natural language\b",
        r"\bnatural language (?:instructions|commands|queries|prompts|interface|interpretation|paradigms|chats)\b",
        r"\b(?:text|textual|free[- ]text) (?:instructions|queries|prompts|inputs|context|annotations)\b",
        r"\bbiological text\b|\bclinical language\b|\bclinical narratives\b",
        r"\btranscriptomes? and text\b",
        r"\bgenomic(?:s)? (?:and|with) (?:text|clinical narratives|natural language)\b",
        r"\b(?:single[- ]cell|scRNA[- ]seq|transcriptome|transcriptomic|gene|protein|genomic|nucleotide|pathology|histology|biomedical) (?:data|profiles?|sequences?|images?) and (?:text|natural language|clinical language)\b",
        r"\b(?:text|natural language|clinical language) and (?:single[- ]cell|scRNA[- ]seq|transcriptome|transcriptomic|gene|protein|genomic|nucleotide|pathology|histology|biomedical) (?:data|profiles?|sequences?|images?)\b",
        r"\bgenerat(?:e|es|ing) (?:candidate )?(?:free[- ]form,? )?(?:natural language |textual )?(?:descriptions?|captions?|reports?|answers?|summaries?|narratives?)\b",
        r"\bnatural language generation\b|\binterpretable natural language generation\b",
        r"\b(?:image|images|protein|proteins|cell|cells|omics|transcriptomes?|gene|genes|bio|biology)[- ]to[- ]text\b",
        r"\btext[- ]to[- ](?:image|images|protein|proteins|cell|cells|omics|transcriptomes?|gene|genes|bio|biology)\b",
        r"\bcondition(?:ed|ing) (?:the generative process )?(?:on|from) (?:text|textual|natural language|clinical language|reports?|captions?)\b",
        r"\b(?:textual inputs?|reports? from pathologists|GPT[- ]derived pathology report summaries|descriptive text captions)\b",
        r"\bchat[- ]based interrogation of transcriptome data\b|\banswers questions about cells and genes\b",
        r"\bchat(?:s|ting)? with (?:cell|cells|genes|genomes|data)\b",
        r"\bconversational (?:agent|single[- ]cell|multi[- ]omics|DNA|RNA|protein)\b",
        r"\bAI copilot\b|\bcopilot for single[- ]cell\b",
        r"\bquestion answering\b|\bQ&A capabilities\b|\bFeature[- ]Question[- ]Answer\b",
    ),
)

HIGH_PRECISION_TEXT_BIO = PatternGroup(
    "high_precision_text_bio",
    (
        r"\busing natural language prompts\b",
        r"\bnatural language (?:instructions|commands|queries|prompts|interpretation|chats)\b",
        r"\binstructed in natural language\b",
        r"\bnatural language as (?:a|the) medium\b",
        r"\bnatural language for generat(?:ing|e|es)\b",
        r"\bnatural language descriptions?\b",
        r"\bcross[- ]modal question answering\b|\bbiomedical question answering\b",
        r"\bfine[- ]tuned under natural language paradigms\b",
        r"\bgenerat(?:e|es|ing)[^.]{0,80}(?:single[- ]cell|cell|gene|protein|phenotypic|functional|clinical|pathology|histology)[^.]{0,80}(?:descriptions?|captions?|reports?|answers?|summaries?|narratives?)\b",
        r"\b(?:single[- ]cell|cell|gene|protein|phenotypic|functional|clinical|pathology|histology)[^.]{0,80}(?:descriptions?|captions?|reports?|answers?|summaries?|narratives?)[^.]{0,80}generat(?:e|es|ing)\b",
        r"\bnatural language generation\b|\binterpretable natural language generation\b",
        r"\b(?:image|images|protein|proteins|cell|cells|omics|transcriptomes?|gene|genes|bio|biology)[- ]to[- ]text\b",
        r"\btext[- ]to[- ](?:image|images|protein|proteins|cell|cells|omics|transcriptomes?|gene|genes|bio|biology)\b",
        r"\bcondition(?:ed|ing) (?:the generative process )?(?:on|from) (?:text|textual|natural language|reports?|captions?)\b",
        r"\btextual inputs?\b|\breports? from pathologists\b|\bGPT[- ]derived pathology report summaries\b|\bdescriptive text captions\b",
        r"\b(?:transcriptomes?|omics|single[- ]cell|scRNA[- ]seq|genomics?|proteins?) and text\b",
        r"\bbiological and textual inputs\b|\b(?:scRNA[- ]seq|single[- ]cell|omics|genomic|protein) data and biological text\b",
        r"\bchat[- ]based interrogation of transcriptome data\b|\banswers questions about cells and genes\b",
        r"\bQ&A capabilities grounded in biomedical knowledge\b|\bFeature[- ]Question[- ]Answer\b",
        r"\bconversational (?:agent|single[- ]cell|multi[- ]omics|DNA|RNA|protein)\b",
        r"\bAI copilot\b|\bcopilot for single[- ]cell\b",
        r"\bclinical language, imaging, and genomics\b",
        r"\bgenomic sequences or clinical narratives\b",
        r"\btextual context\b",
        r"\bnat[uü]rlicher sprache chatten\b|\bzellen chatten\b",
    ),
)

TITLE_LEVEL_EXCLUDE = PatternGroup(
    "title_level_exclude",
    (
        r"\breview\b|\boverview\b|\bprospects\b|\bprinciples and challenges\b",
        r"\bpromise of large language models\b|\binsights and implications\b",
        r"\bmethods, applications, and challenges\b|\bsymposium\b",
        r"\btutorial and code optimization\b|\bagricultural large language model\b",
        r"\bliteracy\b|\binformation extraction systems\b",
        r"\bcomparative analysis\b",
    ),
)

GEN_MODEL = PatternGroup(
    "generative_model",
    (
        r"\bgenerative\b|\bgenerat(?:e|es|ing|ion)\b",
        r"\bautoregressive\b|\bdecoder[- ]only\b|\bsequence[- ]to[- ]sequence\b",
        r"\bdiffusion\b|\bflow matching\b|\bvariational autoencoder\b|\bVAE\b|\bGAN\b",
        r"\blanguage model(?:s|ing)?\b|\blarge language model(?:s)?\b|\bLLM(?:s)?\b|\bGPT\b",
        r"\bsynthetic (?:data|image|images|sample|samples)\b",
    ),
)

FOUNDATION = PatternGroup(
    "foundation_model",
    (
        r"\bfoundation model(?:s)?\b",
        r"\bpre[- ]?train(?:ed|ing)?\b|\bself[- ]supervised\b",
        r"\blarge[- ]scale\b|\bgeneralist\b|\bzero[- ]shot\b|\bfew[- ]shot\b",
        r"\blarge language model(?:s)?\b|\bLLM(?:s)?\b|\bGPT\b|\btransformer(?:s)?\b",
    ),
)

REVIEW_OR_NONARTICLE = PatternGroup(
    "review_or_nonarticle",
    (
        r"\bsystematic review\b|\bscoping review\b|\bliterature review\b",
        r"\breview of\b|\bcomprehensive review\b|\bsurvey\b",
        r"\beditorial\b|\bcommentary\b|\bperspective\b|\bprotocol\b",
        r"\bcase report\b|\bcase series\b",
        r"\bbibliometric analysis\b|\bknowledge mapping\b",
        r"\bfundamentals, challenges, and perspectives\b",
    ),
)

WRAPPER_OR_RETRIEVAL_ONLY = PatternGroup(
    "wrapper_or_retrieval_only",
    (
        r"\bretrieval[- ]augmented\b|\bRAG\b",
        r"\bknowledge graph\b|\bdatabase utilit(?:y|ies)\b|\bweb APIs?\b|\bAPI calls?\b",
        r"\bexternal embeddings?\b|\bexternal labels?\b",
    ),
)

PREDICTIVE_ONLY = PatternGroup(
    "predictive_only",
    (
        r"\bclassification\b|\bclassifier\b|\bprediction\b|\bpredict(?:s|ing|ed)?\b",
        r"\bsurvival\b|\brisk\b|\bdiagnos(?:is|tic)\b|\bprognos(?:is|tic)\b",
        r"\bannotation\b|\bimputation\b|\bclustering\b|\bsegmentation\b",
        r"\bassessment\b|\bdetection\b|\binterpretation\b",
    ),
)

BIO_TOKEN_ONLY = PatternGroup(
    "biological_token_only",
    (
        r"\bgenes? as tokens\b|\bcells? as (?:tokens|sentences)\b",
        r"\bcell sentences\b|\bcell language model\b",
        r"\bDNA language model\b|\bgenomic language model\b|\bprotein language model\b",
        r"\bbiological sequence language model\b",
    ),
)


def norm(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value)


def evidence(text: str) -> dict[str, list[str]]:
    groups = [
        BIO,
        NATURAL_LANGUAGE,
        BRIDGE,
        GEN_MODEL,
        FOUNDATION,
        REVIEW_OR_NONARTICLE,
        WRAPPER_OR_RETRIEVAL_ONLY,
        PREDICTIVE_ONLY,
        BIO_TOKEN_ONLY,
        EXPLICIT_TEXT_BIO_BRIDGE,
        HIGH_PRECISION_TEXT_BIO,
        TITLE_LEVEL_EXCLUDE,
    ]
    return {group.name: group.hits(text) for group in groups}


def any_hits(ev: dict[str, list[str]], names: Iterable[str]) -> bool:
    return any(bool(ev[name]) for name in names)


def classify(text: str, version: str) -> tuple[str, str]:
    ev = evidence(text)
    bio = bool(ev["bio"])
    nl = bool(ev["natural_language"])
    bridge = bool(ev["text_bio_bridge"])
    gen = bool(ev["generative_model"])
    fm = bool(ev["foundation_model"])
    review = bool(ev["review_or_nonarticle"])
    wrapper = bool(ev["wrapper_or_retrieval_only"])
    predictive = bool(ev["predictive_only"])
    bio_token_only = bool(ev["biological_token_only"])
    explicit_bridge = bool(ev["explicit_text_bio_bridge"])
    high_precision = bool(ev["high_precision_text_bio"])
    title_exclude = bool(TITLE_LEVEL_EXCLUDE.hits(text.split("\n", 1)[0]))

    positives = sum([bio, nl, bridge, gen, fm])

    if version == "v0_broad_keywords":
        if review or not bio:
            return "EXCLUDE", "review_or_no_bio"
        if nl and (gen or fm):
            return "INCLUDE", "bio_nl_and_generative_or_foundation"
        if positives >= 2:
            return "UNCERTAIN", "partial_positive_keyword_match"
        return "EXCLUDE", "insufficient_positive_keywords"

    if version == "v1_bridge_required":
        if review or not bio:
            return "EXCLUDE", "review_or_no_bio"
        if bio and nl and bridge and (gen or fm):
            return "INCLUDE", "bio_nl_bridge_and_generative_or_foundation"
        if positives >= 3:
            return "UNCERTAIN", "near_scope_but_missing_decisive_bridge_or_model_signal"
        return "EXCLUDE", "insufficient_positive_keywords"

    if version == "v2_precision_guards":
        if review or not bio:
            return "EXCLUDE", "review_or_no_bio"
        if bio_token_only and not bridge:
            return "EXCLUDE", "biological_token_language_without_natural_language_bridge"
        if wrapper and not bridge:
            return "EXCLUDE", "application_or_retrieval_wrapper_without_text_bio_generation"
        if bio and nl and bridge and (gen or fm):
            if predictive and not gen:
                return "UNCERTAIN", "predictive_only_terms_with_foundation_language"
            return "INCLUDE", "bio_nl_bridge_and_generative_or_foundation"
        if positives >= 3:
            return "UNCERTAIN", "mixed_or_incomplete_scope_evidence"
        return "EXCLUDE", "insufficient_positive_keywords"

    if version == "v3_conservative_final":
        if review or not bio:
            return "EXCLUDE", "review_or_no_bio"
        if bio_token_only and not (nl and bridge):
            return "EXCLUDE", "biological_token_model_without_explicit_natural_language_bridge"
        if wrapper and not (bridge and gen):
            return "EXCLUDE", "tool_or_retrieval_wrapper_without_text_bio_generation"
        if bio and nl and bridge and gen:
            return "INCLUDE", "explicit_bio_text_bridge_with_generative_model"
        if bio and nl and bridge and fm:
            return "INCLUDE", "explicit_bio_text_bridge_with_foundation_model"
        if bio and nl and gen and positives >= 4:
            return "UNCERTAIN", "strong_text_bio_model_signals_but_bridge_not_explicit"
        if bio and bridge and (gen or fm):
            return "UNCERTAIN", "bio_bridge_model_signal_but_natural_language_not_explicit"
        if bio and nl and (gen or fm):
            return "UNCERTAIN", "bio_natural_language_model_signal_but_bridge_not_explicit"
        return "EXCLUDE", "insufficient_scope_evidence"

    if version == "v4_precision_text_bio_final":
        if review or not bio:
            return "EXCLUDE", "review_or_no_bio"
        if bio_token_only and not explicit_bridge:
            return "EXCLUDE", "biological_token_model_without_explicit_text_bio_bridge"
        if wrapper and not explicit_bridge:
            return "EXCLUDE", "tool_or_retrieval_wrapper_without_text_bio_generation"
        if explicit_bridge and (gen or fm):
            if predictive and not gen:
                return "UNCERTAIN", "explicit_text_bio_bridge_but_predictive_only_surface"
            return "INCLUDE", "explicit_text_bio_bridge_with_generative_or_foundation_model"
        if bio and nl and bridge and (gen or fm):
            return "UNCERTAIN", "broad_text_bio_signals_without_explicit_bridge_phrase"
        if bio and (nl or bridge) and (gen or fm):
            return "UNCERTAIN", "partial_text_bio_generative_signals"
        return "EXCLUDE", "insufficient_scope_evidence"

    if version == "v5_high_precision_final":
        if review or title_exclude or not bio:
            return "EXCLUDE", "review_title_or_no_bio"
        if bio_token_only and not high_precision:
            return "EXCLUDE", "biological_token_model_without_high_precision_text_bio_bridge"
        if wrapper and not high_precision:
            return "EXCLUDE", "tool_or_retrieval_wrapper_without_text_bio_generation"
        if high_precision and (gen or fm):
            return "INCLUDE", "high_precision_text_bio_bridge_with_generative_or_foundation_model"
        if explicit_bridge and (gen or fm):
            return "UNCERTAIN", "explicit_but_lower_precision_text_bio_bridge"
        if bio and nl and bridge and (gen or fm):
            return "UNCERTAIN", "broad_text_bio_signals_without_high_precision_bridge"
        if bio and (nl or bridge) and (gen or fm):
            return "UNCERTAIN", "partial_text_bio_generative_signals"
        return "EXCLUDE", "insufficient_scope_evidence"

    raise ValueError(f"Unknown rule version: {version}")


def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def load_llm_runs(paths: dict[str, Path]) -> pd.DataFrame:
    merged: pd.DataFrame | None = None
    for name, path in paths.items():
        df = pd.read_parquet(
            path,
            columns=["cluster_id", "pilot_final_decision"],
        ).rename(columns={"pilot_final_decision": f"{name}_decision"})
        merged = df if merged is None else merged.merge(df, on="cluster_id", how="outer")
    assert merged is not None
    decision_cols = [c for c in merged.columns if c.endswith("_decision")]
    for decision in DECISIONS:
        merged[f"llm_{decision.lower()}_votes"] = (merged[decision_cols] == decision).sum(axis=1)
    merged["llm_majority_decision"] = merged[
        [f"llm_{d.lower()}_votes" for d in DECISIONS]
    ].idxmax(axis=1).str.replace("llm_", "", regex=False).str.replace("_votes", "", regex=False).str.upper()
    merged["llm_stable_decision"] = None
    for decision in DECISIONS:
        merged.loc[(merged[decision_cols] == decision).all(axis=1), "llm_stable_decision"] = decision
    return merged


def summarize(version_df: pd.DataFrame, version: str) -> dict[str, object]:
    labels = version_df[f"{version}_decision"]
    majority = version_df["llm_majority_decision"]
    stable_include = set(version_df.loc[version_df["llm_stable_decision"] == "INCLUDE", "cluster_id"])
    stable_exclude = set(version_df.loc[version_df["llm_stable_decision"] == "EXCLUDE", "cluster_id"])
    llm_decision_cols = [
        c
        for c in version_df.columns
        if c.endswith("_decision")
        and c not in {"llm_majority_decision", "llm_stable_decision"}
        and not c.startswith("v")
    ]
    any_include = set(version_df.loc[version_df[llm_decision_cols].eq("INCLUDE").any(axis=1), "cluster_id"])
    pred_include = set(version_df.loc[labels == "INCLUDE", "cluster_id"])

    out: dict[str, object] = {
        "version": version,
        "n": int(len(version_df)),
        "counts": labels.value_counts().reindex(DECISIONS, fill_value=0).to_dict(),
        "agreement_with_llm_majority": float((labels == majority).mean()),
        "stable_include_recall": len(pred_include & stable_include) / len(stable_include) if stable_include else None,
        "any_llm_include_recall": len(pred_include & any_include) / len(any_include) if any_include else None,
        "include_precision_vs_any_llm_include": len(pred_include & any_include) / len(pred_include) if pred_include else None,
        "include_overlap_with_stable_exclude": len(pred_include & stable_exclude),
        "stable_exclude_specificity": float(
            (version_df.loc[version_df["llm_stable_decision"] == "EXCLUDE", f"{version}_decision"] == "EXCLUDE").mean()
        ),
    }
    for decision in DECISIONS:
        out[f"{decision.lower()}_jaccard_vs_llm_majority"] = jaccard(
            set(version_df.loc[labels == decision, "cluster_id"]),
            set(version_df.loc[majority == decision, "cluster_id"]),
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("runs/all_abstracts_input_4027.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("analysis/rule_based_screening_baseline"))
    parser.add_argument(
        "--llm-run",
        action="append",
        default=[],
        help="name=path to a completed LLM screening parquet. Can be repeated.",
    )
    args = parser.parse_args()

    llm_runs = {
        "ds1": Path("runs/deepseek_v4_review_pipeline_all4027_current_rep1_watchdog_20260510T013948Z/guideline_pilot_results_all_completed_dedup.parquet"),
        "ds2": Path("runs/deepseek_v4_review_pipeline_all4027_current_rep2_watchdog_20260510T013948Z/guideline_pilot_results_all_completed_dedup.parquet"),
        "gpt1": Path("runs/gpt_oss_120b_review_pipeline_all4027_current_watchdog_20260511T1116Z/guideline_pilot_results_all_completed_dedup.parquet"),
        "gpt2": Path("runs/gpt_oss_120b_review_pipeline_all4027_current_rep2_watchdog_20260511T1642Z/guideline_pilot_results_all_completed_dedup.parquet"),
        "nemo1": Path("runs/nemotron3_super_120b_fp8_review_pipeline_all4027_current_watchdog_20260511T1116Z/guideline_pilot_results_all_completed_dedup.parquet"),
    }
    for item in args.llm_run:
        name, raw_path = item.split("=", 1)
        llm_runs[name] = Path(raw_path)
    llm_runs = {name: path for name, path in llm_runs.items() if path.exists()}

    df = pd.read_csv(args.input)
    df["rule_text"] = (df["title"].map(norm) + "\n" + df["abstract"].map(norm)).str.lower()
    versions = [
        "v0_broad_keywords",
        "v1_bridge_required",
        "v2_precision_guards",
        "v3_conservative_final",
        "v4_precision_text_bio_final",
        "v5_high_precision_final",
    ]
    for version in versions:
        classified = df["rule_text"].map(lambda text: classify(text, version))
        df[f"{version}_decision"] = classified.map(lambda x: x[0])
        df[f"{version}_reason"] = classified.map(lambda x: x[1])

    ev_rows = df["rule_text"].map(evidence)
    for group in [
        "bio",
        "natural_language",
        "text_bio_bridge",
        "generative_model",
        "foundation_model",
        "review_or_nonarticle",
        "wrapper_or_retrieval_only",
        "predictive_only",
        "biological_token_only",
        "explicit_text_bio_bridge",
        "high_precision_text_bio",
        "title_level_exclude",
    ]:
        df[f"rule_hit_{group}"] = ev_rows.map(lambda ev, g=group: "; ".join(ev[g]))

    llm = load_llm_runs(llm_runs)
    out = df.merge(llm, on="cluster_id", how="left")

    summaries = [summarize(out, version) for version in versions]
    summary_df = pd.json_normalize(summaries)

    final_version = "v5_high_precision_final"
    mismatch_cols = [
        "cluster_id",
        "title",
        f"{final_version}_decision",
        f"{final_version}_reason",
        "llm_majority_decision",
        "llm_stable_decision",
        "llm_include_votes",
        "llm_uncertain_votes",
        "llm_exclude_votes",
        "rule_hit_bio",
        "rule_hit_natural_language",
        "rule_hit_text_bio_bridge",
        "rule_hit_generative_model",
        "rule_hit_foundation_model",
        "rule_hit_review_or_nonarticle",
        "rule_hit_wrapper_or_retrieval_only",
        "rule_hit_predictive_only",
        "rule_hit_biological_token_only",
        "rule_hit_explicit_text_bio_bridge",
        "rule_hit_high_precision_text_bio",
        "rule_hit_title_level_exclude",
    ]
    mismatches = out.loc[out[f"{final_version}_decision"] != out["llm_majority_decision"], mismatch_cols]

    args.outdir.mkdir(parents=True, exist_ok=True)
    out.drop(columns=["rule_text"]).to_csv(args.outdir / "rule_based_baseline_results.csv", index=False)
    out.drop(columns=["rule_text"]).to_parquet(args.outdir / "rule_based_baseline_results.parquet", index=False)
    summary_df.to_csv(args.outdir / "rule_based_baseline_iterations.csv", index=False)
    mismatches.to_csv(args.outdir / "v5_mismatches_vs_llm_majority.csv", index=False)
    with (args.outdir / "rule_based_baseline_summary.json").open("w") as fh:
        json.dump(
            {
                "input": str(args.input),
                "llm_runs": {k: str(v) for k, v in llm_runs.items()},
                "versions": versions,
                "summary": summaries,
            },
            fh,
            indent=2,
        )

    print(summary_df.to_string(index=False))
    print(f"\nWrote outputs to {args.outdir}")


if __name__ == "__main__":
    main()
