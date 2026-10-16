---
title: "Supplementary Information"
subtitle: "Translate or encode? Two design cultures for coupling language and omics data in generative foundation models: a scoping review."
---

Supplementary items are numbered by type in the order in which the article first cites them. Numbers
in square brackets refer to the article's reference list. Data files are listed at the end with their
column dictionary.

## Supplementary Notes

### Supplementary Note S1. Search strategies as executed

Every query string as executed, by round and source, with the execution date and the number of records
retained from each source. The strings are reproduced verbatim from the search configurations.

<!-- generated: include:search_strategies from analysis/prisma_search_audit_2026-10-14/search_strategies_as_executed.md -->

#### Round 1, baseline (protocol version 3.1): 2018-01-01 to 2026-02-28


##### PubMed (executed 2026-02-15; 631 records retained)

```
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "RNA seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR "multi omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract]) AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract]) AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract])) AND ("2018/01/01"[Date - Publication] : "2026/02/28"[Date - Publication]) AND "free full text"[sb] AND English[Language]
```

##### Scopus (executed 2026-02-15; 1,021 records retained)

```
TITLE-ABS-KEY(("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrain* OR "pre-train*" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")) AND PUBYEAR > 2017 AND OPENACCESS(1) AND LANGUAGE(English)
```

##### Semantic Scholar (executed 2026-02-15; 2,192 records retained)

```
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "RNA seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics" | "multi omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

##### arXiv (executed 2026-02-15; 187 records retained)

```
[primary] (ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"RNA seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics" OR abs:"multi omics") AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt) AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
[cell_language] abs:"foundation model" AND abs:"single cell" AND abs:"language model"
[model_names] (ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
[bio_llm] abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```

##### bioRxiv and medRxiv (Europe PMC preprints) (executed 2026-02-15; 669 records retained)

```
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "RNA seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR transcriptomics OR genomics OR proteomics OR epigenomics) AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning") AND (SRC:PPR) AND FIRST_PDATE:[2018-01-01 TO 2026-02-28]
```

##### Springer Nature (executed 2026-02-15; 272 records retained)

```
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
```

##### Google Scholar (executed 2026-02-15; 562 records retained)

```
"foundation model" "gene expression" "language model" single-cell
GPT "single cell" "gene expression" generative
"natural language" "single-cell" "cell type" foundation model
multimodal LLM genomics transcriptomics "foundation model"
scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent
"multi omics" "language model" "foundation model" transformer
"RNA seq" LLM "foundation model" generative single-cell
```

#### Round 2, April top-up: 2026-03-01 to 2026-04-14


##### PubMed (executed 2026-04-14; 46 records retained)

```
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "RNA seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR "multi omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract]) AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract]) AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract])) AND ("2026/03/01"[Date - Publication] : "2026/04/14"[Date - Publication]) AND "free full text"[sb] AND English[Language]
```

##### Scopus (executed 2026-04-14; 32 records retained)

```
TITLE-ABS-KEY(("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrain* OR "pre-train*" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")) AND PUBYEAR > 2025 AND OPENACCESS(1) AND LANGUAGE(English)
```

##### Semantic Scholar (executed 2026-04-14; 201 records retained)

```
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "RNA seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics" | "multi omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

##### arXiv (executed 2026-04-14; 14 records retained)

```
[primary] (ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"RNA seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics" OR abs:"multi omics") AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt) AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
[cell_language] abs:"foundation model" AND abs:"single cell" AND abs:"language model"
[model_names] (ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
[bio_llm] abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```

##### bioRxiv and medRxiv (Europe PMC preprints) (executed 2026-04-14; 5 records retained)

```
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "RNA seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR transcriptomics OR genomics OR proteomics OR epigenomics) AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning") AND (SRC:PPR) AND FIRST_PDATE:[2026-03-01 TO 2026-04-14]
```

##### Springer Nature (executed 2026-04-14; 33 records retained)

```
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
```

##### Google Scholar (executed 2026-04-14; 536 records retained)

```
"foundation model" "gene expression" "language model" single-cell
GPT "single cell" "gene expression" generative
"natural language" "single-cell" "cell type" foundation model
multimodal LLM genomics transcriptomics "foundation model"
scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent
"multi omics" "language model" "foundation model" transformer
"RNA seq" LLM "foundation model" generative single-cell
```

Notes logged with the round: Semantic Scholar API key expired (HTTP 403), used keyless access. Google Scholar rate-limited after query 5/7.

#### Round 3, June top-up: 2026-04-15 to 2026-06-10


##### PubMed (executed 2026-06-10; 68 records retained)

```
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "RNA seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR "multi omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract]) AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract]) AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract])) AND ("2026/04/15"[Date - Publication] : "2026/06/10"[Date - Publication]) AND "free full text"[sb] AND English[Language]
```

##### Scopus (executed 2026-06-10; 39 records retained)

```
TITLE-ABS-KEY(("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrain* OR "pre-train*" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")) AND PUBYEAR > 2025 AND OPENACCESS(1) AND LANGUAGE(English)
```

##### Semantic Scholar (executed 2026-06-10; 215 records retained)

```
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "RNA seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics" | "multi omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

##### arXiv (executed 2026-06-10; 21 records retained)

```
[primary] (ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"RNA seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics" OR abs:"multi omics") AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt) AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
[cell_language] abs:"foundation model" AND abs:"single cell" AND abs:"language model"
[model_names] (ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
[bio_llm] abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```

##### bioRxiv and medRxiv (Europe PMC preprints) (executed 2026-06-10; 33 records retained)

```
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "RNA seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR transcriptomics OR genomics OR proteomics OR epigenomics) AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning") AND (SRC:PPR) AND FIRST_PDATE:[2026-04-15 TO 2026-06-10]
```

##### Springer Nature (executed 2026-06-10; 27 records retained)

```
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
```

##### Google Scholar (executed 2026-06-10; 530 records retained)

```
"foundation model" "gene expression" "language model" single-cell
GPT "single cell" "gene expression" generative
"natural language" "single-cell" "cell type" foundation model
multimodal LLM genomics transcriptomics "foundation model"
scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent
"multi omics" "language model" "foundation model" transformer
"RNA seq" LLM "foundation model" generative single-cell
```

Notes logged with the round: Top-up search after 2026-04-14. PubMed ESearch required POST with retries after transient NCBI server errors (HTTP 500). Google Scholar rate-limited after query 5/7; queries 6-7 skipped.

#### Round 4, July top-up: 2026-06-11 to 2026-07-06


##### PubMed (executed 2026-07-06; 25 records retained)

```
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "RNA seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR "multi omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract]) AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract]) AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract])) AND ("2026/06/11"[Date - Publication] : "2026/07/06"[Date - Publication]) AND "free full text"[sb] AND English[Language]
```

##### Scopus (executed 2026-07-06; 12 records retained)

```
TITLE-ABS-KEY(("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrain* OR "pre-train*" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")) AND PUBYEAR > 2025 AND OPENACCESS(1) AND LANGUAGE(English)
```

##### Semantic Scholar (executed 2026-07-06; 118 records retained)

```
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "RNA seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics" | "multi omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

##### arXiv (executed 2026-07-06; 6 records retained)

```
[primary] (ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"RNA seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics" OR abs:"multi omics") AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt) AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
[cell_language] abs:"foundation model" AND abs:"single cell" AND abs:"language model"
[model_names] (ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
[bio_llm] abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```

##### bioRxiv and medRxiv (Europe PMC preprints) (executed 2026-07-06; 16 records retained)

```
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "RNA seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR transcriptomics OR genomics OR proteomics OR epigenomics) AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning") AND (SRC:PPR) AND FIRST_PDATE:[2026-06-11 TO 2026-07-06]
```

##### Springer Nature (executed 2026-07-06; 20 records retained)

```
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
```

##### Google Scholar (executed 2026-07-06; 0 records retained)

```
"foundation model" "gene expression" "language model" single-cell
GPT "single cell" "gene expression" generative
"natural language" "single-cell" "cell type" foundation model
multimodal LLM genomics transcriptomics "foundation model"
scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent
"multi omics" "language model" "foundation model" transformer
"RNA seq" LLM "foundation model" generative single-cell
```

#### Round 5, August living update (protocol version 3.3): 2026-07-07 to 2026-08-09


##### PubMed (executed 2026-08-10; 27 records retained)

```
(("single cell"[Title/Abstract] OR "single-cell"[Title/Abstract] OR scRNA-seq[Title/Abstract] OR "RNA-seq"[Title/Abstract] OR "RNA seq"[Title/Abstract] OR "gene expression"[Title/Abstract] OR scATAC-seq[Title/Abstract] OR "ATAC-seq"[Title/Abstract] OR "chromatin accessibility"[Title/Abstract] OR CITE-seq[Title/Abstract] OR "spatial transcriptomics"[Title/Abstract] OR "multi-omics"[Title/Abstract] OR "multi omics"[Title/Abstract] OR multiomics[Title/Abstract] OR transcriptomics[Title/Abstract] OR genomics[Title/Abstract] OR proteomics[Title/Abstract] OR epigenomics[Title/Abstract] OR "cell type"[Title/Abstract] OR "gene regulatory"[Title/Abstract]) AND ("language model"[Title/Abstract] OR LLM[Title/Abstract] OR "large language model"[Title/Abstract] OR "natural language"[Title/Abstract] OR GPT[Title/Abstract] OR CLIP[Title/Abstract] OR "cross-modal"[Title/Abstract] OR multimodal[Title/Abstract] OR "multi-modal"[Title/Abstract] OR tokenization[Title/Abstract] OR "gene token"[Title/Abstract] OR prompt[Title/Abstract] OR "text generation"[Title/Abstract] OR "cell-to-text"[Title/Abstract] OR "text-to-cell"[Title/Abstract] OR NLP[Title/Abstract]) AND ("foundation model"[Title/Abstract] OR pretrained[Title/Abstract] OR "pre-trained"[Title/Abstract] OR "self-supervised"[Title/Abstract] OR transformer[Title/Abstract] OR generative[Title/Abstract] OR decoder[Title/Abstract] OR autoregressive[Title/Abstract] OR "transfer learning"[Title/Abstract] OR "zero-shot"[Title/Abstract] OR "few-shot"[Title/Abstract] OR "masked modeling"[Title/Abstract] OR "attention mechanism"[Title/Abstract] OR "deep learning"[Title/Abstract])) AND ("2026/07/07"[Date - Publication] : "2026/08/09"[Date - Publication]) AND "free full text"[sb] AND English[Language]
```

##### Scopus (executed 2026-08-10; 16 records retained)

```
TITLE-ABS-KEY(("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrain* OR pre-train* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")) AND PUBYEAR > 2025 AND OPENACCESS(1) AND LANGUAGE(English)
```

##### OpenAlex (executed 2026-08-10; 100 records retained)

```
[main] (("single cell" OR "single-cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR "cell-to-text" OR "text-to-cell" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning"))
[model_names] (scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent OR PathOmCLIP)
```

##### Semantic Scholar (executed 2026-08-10; 183 records retained)

```
("single-cell" | "single cell" | "scRNA-seq" | "RNA-seq" | "RNA seq" | "gene expression" | transcriptomics | genomics | proteomics | epigenomics | "spatial transcriptomics" | "multi-omics" | "multi omics") + ("language model" | LLM | "large language model" | "natural language" | GPT | CLIP | multimodal | "multi-modal" | "cross-modal" | tokeniz* | prompt | NLP | "text generation") + ("foundation model" | pretrain* | "self-supervised" | transformer | generative | decoder | autoregressive | "transfer learning" | "zero-shot" | "deep learning")
```

##### arXiv (executed 2026-08-10; 14 records retained)

```
[primary] (ti:"single cell" OR ti:scRNA OR ti:"gene expression" OR ti:transcriptomics OR ti:genomics OR abs:"single-cell" OR abs:"RNA-seq" OR abs:"RNA seq" OR abs:"spatial transcriptomics" OR abs:"multi-omics" OR abs:"multi omics") AND (ti:"language model" OR ti:GPT OR ti:LLM OR ti:CLIP OR ti:multimodal OR abs:"language model" OR abs:"large language model" OR abs:"natural language" OR abs:"cross-modal" OR abs:"multi-modal" OR abs:tokeniz OR abs:prompt) AND (abs:"foundation model" OR abs:pretrain OR abs:"self-supervised" OR abs:transformer OR abs:generative OR abs:decoder OR abs:autoregressive OR abs:"transfer learning")
[cell_language] abs:"foundation model" AND abs:"single cell" AND abs:"language model"
[model_names] (ti:scGPT OR ti:tGPT OR ti:LangCell OR ti:ChatCell OR ti:GenePT OR ti:GeneGPT OR ti:CellPLM OR ti:Nicheformer OR ti:EpiAgent)
[bio_llm] abs:"gene expression" AND abs:LLM AND (abs:generative OR abs:decoder OR abs:autoregressive)
```

##### bioRxiv and medRxiv (Europe PMC preprints) (executed 2026-08-10; 20 records retained)

```
("single-cell" OR "single cell" OR "scRNA-seq" OR "RNA-seq" OR "RNA seq" OR "gene expression" OR "scATAC-seq" OR "ATAC-seq" OR "chromatin accessibility" OR "CITE-seq" OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR transcriptomics OR genomics OR proteomics OR epigenomics) AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokeniz* OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrain* OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "deep learning") AND (SRC:PPR) AND FIRST_PDATE:[2026-07-07 TO 2026-08-09]
```

##### Springer Nature (executed 2026-08-10; 27 records retained)

```
("single-cell" OR "single cell" OR scRNA-seq OR "RNA-seq" OR "RNA seq" OR "gene expression" OR scATAC-seq OR "ATAC-seq" OR "chromatin accessibility" OR CITE-seq OR "spatial transcriptomics" OR "multi-omics" OR "multi omics" OR multiomics OR transcriptomics OR genomics OR proteomics OR epigenomics OR "cell type" OR "gene regulatory") AND ("language model" OR LLM OR "large language model" OR "natural language" OR GPT OR CLIP OR "cross-modal" OR multimodal OR "multi-modal" OR tokenization OR "gene token" OR prompt OR "text generation" OR NLP) AND ("foundation model" OR pretrained OR "pre-trained" OR "self-supervised" OR transformer OR generative OR decoder OR autoregressive OR "transfer learning" OR "zero-shot" OR "few-shot" OR "masked modeling" OR "attention mechanism" OR "deep learning")
```

##### Google Scholar (executed 2026-08-10; 252 records retained)

```
("foundation model" "gene expression" "language model" single-cell) OR (GPT "single cell" "gene expression" generative) OR ("natural language" "single-cell" "cell type" foundation model) OR (multimodal LLM genomics transcriptomics "foundation model") OR (scGPT OR tGPT OR LangCell OR ChatCell OR CellWhisperer OR GenePT OR GeneGPT OR CellPLM OR Nicheformer OR EpiAgent) OR ("multi omics" "language model" "foundation model" transformer) OR ("RNA seq" LLM "foundation model" generative single-cell)
```

Date status of the retained records. PubMed: 27 within the window (database filter); Scopus: 16 within the window (exact-date check); OpenAlex: 100 within the window (database filter); Semantic Scholar: 144 within the window (exact-date check), 39 without a publication date (kept); arXiv: 14 within the window (database filter); bioRxiv and medRxiv (Europe PMC preprints): 20 within the window (database filter); Springer Nature: 27 within the window (database filter); Google Scholar: 252 with a publication year only (kept). Records removed as outside the window: 0.

<!-- end generated -->

### Supplementary Note S2. Search: rounds, dates and source-specific details

The five rounds retained 5,534, 867, 933, 197 and 639 records (8,170).

**Dates as executed.** PubMed, arXiv, Europe PMC, Springer Nature and OpenAlex were queried with exact
dates. Scopus and Semantic Scholar were queried by year, and records outside the window were then
removed by exact date. Records removed (Scopus/Semantic Scholar): 18/1 in the baseline, then 165/226,
292/462, 389/766 and 485/914 in the top-ups. In round 5, 39 Semantic Scholar records without a
publication date were kept. Google Scholar was queried by year only. The baseline ran on 2026-02-15, so
no date-bounded query covered records dated 2026-02-16 to 2026-02-28.

**Springer Nature.** The free API searches full text and cannot be restricted to title and abstract.
Retrieved records were therefore kept only if a term from each concept block appeared in the title or
abstract. Raw to validated, by round: 17,130 to 272, 1,185 to 33, 1,129 to 27, 510 to 20 and 691 to 27.
The flow counts the validated records.

**Google Scholar completeness.** The April and June rounds were rate-limited after 5 of 7 queries, and
the July round returned no records. The baseline completion log was overwritten by a later Springer
Nature-only rerun; the retained baseline records are preserved.

**Gap between search windows.** On 2026-10-14 the baseline queries of PubMed, arXiv, Europe PMC and
Semantic Scholar were re-run for the window 2026-02-16 to 2026-02-28. They returned 51 unique records.
17 had already been retrieved and 34 had not; none of the 34 met the eligibility criteria in an
indicative single-pass LLM title/abstract triage. Scopus and Springer Nature were not re-run.

### Supplementary Note S3. Operation-level decomposition: rules, runs and stability

**Library.** Each documented input path is reconstructed as a directed graph of calls to a library of
22 reusable operations (normalisation, log transform, binning, tokenisation, table lookup, projection,
concatenation, attention and others) with named ports and instance parameters, following the
operation guide and the catalog definitions of release 1.3.0. Steps whose internal computation the
paper does not state remain unexpanded boundaries. A four-paper pilot (ChatNT, InstructCell, X-Cell,
MUPAD; 47 trajectories, 509 operation calls) was curated by the authors.

**Agent decomposition.** The remaining 50 papers were decomposed by agents (Codex CLI, gpt-5.6-luna,
reasoning effort high; the earlier gpt-5.4-mini is no longer available through Codex) under version 3.2
of the decomposition protocol, which sharpens the boundaries between align, concatenate and serialize,
and between partition and select, after run-to-run disagreements under version 3.1. The structure is fixed by the charted
routes: one trajectory per charted configuration and one step per element of each route's verbatim
transformation chain. For each step the agent returns only a decision, a closed category plus the
library operation(s) named in the element text, with stated parameter values, verbatim evidence and
the echoed chain element. A predefined rule set decides the category (for example unexpanded learned
module, data provenance, external text generator, unspecified fusion). Routes without a recorded chain
get a mechanical decision. Nodes, ports and data flow are compiled from these decisions, and the
result is checked mechanically for verbatim evidence, catalog ports and declared parameters. The full
paper text is supplied without truncation. Each paper was decomposed in three independent runs (up to
four mechanical repairs each), and the published decision per step is the majority label. Steps
without a majority remain unresolved boundaries and are listed for the library steward, as are steps
decided 2 of 3.

**Parameter pass.** A separate parameter pass then read the whole paper again, with the operations
fixed. For every declared parameter of every library call (2,433 slots in 1.3.0, defined in the
operation parameter glossary) it decided whether the paper states the value for that data path, with
verbatim evidence checked mechanically. Values that only follow from convention, released code or
cited papers do not count. This pass also used three runs per paper and the majority status; its rules
were tuned on the ten development papers (two iterations) and then frozen. Before the first run we
fixed its gate: on ten held-out papers, consensus status agreement between runs 1-3 and 4-6 of at least
0.90. The result was library release 1.2.1. Under version 3.2, 39 of 1,468 steps changed operation; the
parameter pass was repeated for the 16 affected papers (three runs), and slots of unchanged calls were
carried over. The result is library release 1.3.0. No reviewer-agent pass was run on it.

**Development and stability.** The protocol was developed iteratively on ten length-stratified papers
and evaluated on held-out papers with the rules frozen. Stability was measured as agreement between
the consensus of runs 1-3 and of runs 4-6 against a predeclared gate. Of the 1,468 agent-decomposed
steps, 1,394 (95.0%) were decided identically in all three runs and 74 (5.0%) by two of three; every
step had a majority. Under version 3.1 with frozen rules, the consensus of runs 1–3 and of runs 4–6 on ten
unseen papers agreed on 95.6% of steps and 85.4% of complete routes. After the boundary fixes of version 3.2,
the same papers agree on 99.6% and 98.8%. That second figure is in-sample, because these papers
informed the fixes. Across the three production runs under version 3.2 on all 50 agent-decomposed papers, 90.9% of route ×
run-pair comparisons had identical operation sequences (gate: at least 90%) and the median paper-level
operation-set Jaccard was 1.0, but five papers fell below the predeclared minimum of 0.75 (lowest 0.0
for Chroma, where one run produced a disjoint set). The full-corpus gate was therefore not met;
release decisions use the per-step majority of the three runs. For the parameter pass, 88% of slot
decisions were unanimous across runs, and held-out consensus status agreement was 0.992. The withdrawn
OKR-Cell preprint is not included.

### Supplementary Note S4. Motifs, design axes and archetypes

**Model-level paths.** For each model configuration, the decomposed routes (agent-decomposed papers) or the
author-curated graphs (pilot papers, all root-to-model paths) were turned into paths of role-aware
operation tokens. Provenance and identity steps were dropped and repeated identical operations
collapsed. Each operation's role follows from its inputs: biological only, text only, or joining
biological and text inputs. Unexpanded learned modules were kept as typed tokens.

**Motifs.** Closed frequent sub-chains (contiguous and gapped) were mined at the operation and family
levels, with support counted in papers (at least 4 papers; no length limit). Supported, interpretable
sub-chains were named as motifs with templates, members, parameter reporting and evidence-quoted
examples (Supplementary Table S6). Stability: mining was repeated on each single
decomposition run.

**Design axes.** Each route was also coded on five axes along one canonical pipeline (source, curation,
value transformation, carrier formation, interface): carrier formation, interface to the language
model, transformation of measured values (order only, discretised, learned compression, verbatim; with
subset and normalisation modifiers), text role and transparency. Coding rules are deterministic over
the chains and the charted atlas labels (Supplementary Table S10). We tested coverage,
independence (normalised mutual information) and robustness to decomposition runs. Archetypes are
carrier x interface combinations; a model can carry several.

**Earlier analysis.** An earlier version of this analysis compared exact route chains and reported no
recurring recipes. That result was an artefact of chain construction (uneven wording granularity,
non-computational steps counted as operations, fragmentary routes) and is withdrawn.

### Supplementary Note S5. Use of AI tools, reported by PRISMA-trAIce item

**Tasks and tools.** LLMs were run through the Codex command-line agent (Codex CLI; the version of the
agent was not recorded with the runs). gpt-5.4-mini was used for title and abstract screening,
full-text screening and route charting; gpt-5.6-luna with reasoning effort high was used for the
operation-level decomposition, the parameter pass and the targeted charting pass, because the earlier
gpt-5.4-mini is no longer available through Codex. Full texts were converted with Docling (version
2.110.0), and Docling Graph (version 1.7.0) reconstructed the complete data-source and
input-representation sections that full-text screening used.

**Screening.** Title/abstract screening applied the eligibility decision tree with two role-separated
LLM reviewers (scope and architecture) and an adjudicator for conflicts; prompts and schemas were
hash-pinned. Full-text screening (baseline run on 2026-07-10) used Docling conversions; Docling Graph
provenance reconstructed the
complete data-source and input-representation sections, which were screened with the title and
abstract. Records still uncertain after adjudication were resolved by the review lead from the full
sections, keeping the automated decision alongside. The roles are prompts executed by the same model,
not independent human reviewers.

**Route charting.** Routes were extracted from the full text with three frozen direct runs plus
dense-coverage candidates. Agreement across the three runs on the 55-record corpus: route Jaccard
0.945–0.969; carrier-family exact agreement 0.929; Krippendorff's alpha 0.881 (acceptance thresholds
0.80, 0.90, 0.80). Dated author-led amendments are recorded in the atlas metadata.

**Decomposition and parameter pass.** Supplementary Note S3 gives the rules, runs and
stability.

**Targeted charting pass.** The pass followed a frozen protocol (design-culture charting, version 1.1).
Every item required verbatim evidence. Quotes were checked mechanically against the paper, with up to
three repairs per run; all 108 runs passed validation. One quote broken by PDF line numbers was
corrected by the steward. Run agreement was high for comparison presence (κ 0.92), LLM-generated text
(κ 0.96) and dependence tests (Jaccard 0.91), but lower for evaluation formats (0.57) and rationales
(0.60).

**Adjudication and human involvement.** The library steward is an agent-assisted role: an AI assistant,
directed by the review lead, applies written rules to the verbatim evidence and records each decision
with its reason. The steward adjudicated the rationale items, the single-run dependence tests and the
cross-representation comparison units, and assigned each work to a culture. The charting runs returned
217 comparison items, which adjudication merged into 31 comparison units in 20 works; three further
units were set aside as within-culture or not about representation form. A second human coder for the
31 comparison units and the culture assignment, with a recall audit of comparisons, is planned. The
review lead approved the targeted charting pass and resolved the records left uncertain by automated
full-text screening, and the authors curated the four pilot decompositions.

**Prompts, schemas and run records.** The prompts, output schemas, rule sets, run configurations and
run outputs of every step are in the project repository; the supplementary file index lists their
locations.

### Supplementary Note S6. Coverage of protein and nucleotide models

A coverage check found that 12 protein and biomolecular text–generative models (ProteinDT, BioT5,
BioT5+, NatureLM, Evolla, Galactica, InstructProtein, ProtLLM, Prot2Text, ProtT3, ProLLaMA, TxGemma)
were never retrieved. None has a term of the biological-data block in its title or abstract. In the
PubMed query for 2018-01-01 to 2026-08-09, a protein block in place of the biological-data block adds
1,140 records that the original block does not match (the original query returns 939), and a
nucleotide block adds 508. In Europe PMC preprints the additions are 1,130 and 633 (hit counts on
2026-10-15).


\newpage

## Supplementary Tables

### Supplementary Table S1. Deviations from the protocol

Amendments of the protocol after its first version under version control (version 3.0), and further
changes that the protocol did not foresee. "Made after results were seen" records whether the change
was decided after results of the review (or, where stated, after procedural results) were known.

<!-- generated: table:deviations from manuscript/supplementary/deviations_source.csv -->

| No. | Kind | Date or stage | Area | Change | After results seen | Dependent results and labelling |
|----:|---------------|-----------|-----------|-----------------------------------------|--------|---------------------------|
| 1 | Protocol amendment (version 3.1) | 15 February 2026 | Search | Space variants ('RNA seq', 'multi omics') were added to all queries and the search was re-run; this execution replaced the first one before screening. | No | All search results; reported as the baseline round. |
| 2 | Protocol amendment (version 3.2) | 14 April 2026 | Search and update | First top-up round across all sources; two models were added to the list of models that the search must find; short abstracts were enriched through Crossref title search. | No | Records of the April round. |
| 3 | Protocol amendment (version 4.0) | 25 April 2026 | Screening | Criterion-by-criterion screening with three prompt roles (scope reviewer, architecture reviewer, adjudicator) was adopted; the final decision is derived by fixed rules, not emitted by the model. | No | All screening decisions. |
| 4 | Protocol amendment (version 4.1) | 10 June 2026 | Search and update | Second top-up round with the same queries and only the date limits changed. | No | Records of the June round. |
| 5 | Protocol amendment (version 4.2) | 6 July 2026 | Search and update | Third top-up round with the same queries and only the date limits changed. | No | Records of the July round. |
| 6 | Protocol amendment (version 4.3) | 10 July 2026 | Screening | Full-text screening was done on the reconstructed data-source and input-representation sections of each paper, screened with the title and abstract. | No | Full-text screening decisions. |
| 7 | Protocol amendment (version 4.4) | 10 July 2026 | Screening | A human resolution layer was added: the review lead inspected the cited full sections of the records left uncertain by automated full-text screening; the automated decisions were kept alongside. | After the automated decisions | Inclusion decisions for the records left uncertain; the automated decisions are kept for audit. |
| 8 | Protocol amendment (version 4.5) | 9 August 2026 | Update procedure | A resumable procedure for living updates was added, from the dated search to publication of the updated atlas. | No | The fifth search round. |
| 9 | Protocol amendment (version 4.6) | 10 August 2026 | Search and update | Fifth round (living update): OpenAlex was added, and Google Scholar was queried with one combined query through a provider export. | No | Records of the August round. |
| 10 | Protocol amendment (version 4.7) | 10 August 2026 | Search and update | OpenAlex was added to abstract enrichment, so that no record of the August round is excluded for lack of an abstract. | No | Records of the August round. |
| 11 | Further change | After full-text screening | Data items | Input routes were charted as grounded routes from source object to carrier and classified in an input-representation taxonomy; the protocol's extraction plan did not foresee this. | No | All route-level results (Methods: data charting). |
| 12 | Further change | After route charting | Data items | Each input path was decomposed into calls to a library of reusable data operations, with a three-run consensus and a parameter pass that records whether each parameter is stated. | No | Operation reuse, unexpanded steps, unstated parameters, archetypes and opaque-step shares. |
| 13 | Further change | During the decomposition | Analysis | The decomposition rules were revised after run-to-run disagreement, sharpening the boundaries between align, concatenate and serialise, and between partition and select; the affected papers were decomposed and their parameter pass repeated. | Yes (stability results) | All decomposition results; the stability on the papers that informed the revision is reported as in-sample (Supplementary Note S3). |
| 14 | Further change | During the decomposition | Tool | The decomposition used gpt-5.6-luna instead of gpt-5.4-mini, which is no longer available through Codex. | No | Decomposition, parameter pass and targeted charting. |
| 15 | Further change | After the decomposition | Analysis | Motifs (recurring operation sub-chains) and five design axes with archetypes were defined after inspecting the decomposed data. | Yes | Motif and archetype results; the axes are described as not validated on an independent corpus (Limitations). |
| 16 | Further change | After the decomposition | Analysis | An earlier comparison of exact route chains, which reported no recurring recipes, was withdrawn as an artefact of chain construction and replaced by the motif analysis. | Yes | None; the earlier result is not reported. |
| 17 | Further change | After the decomposition | Analysis | The design-culture analysis and a targeted charting pass (rationales, supervision, dependence tests, cross-representation comparisons) were defined after exploring the decomposed corpus. | Yes | All culture-level results; described as exploratory (Methods, Results and figure legends), with contrasts not adjusted for multiple comparisons. |
| 18 | Further change | After screening | Correction | An error in the automated keyword check that precedes screening was corrected, which recovered one eligible record (XunZi); it was screened with the same frozen procedures. | Yes | Counted among the included records and shown in the flow diagram. |
| 19 | Further change | After the search | Search check | A 13-day gap between the baseline and first top-up windows was checked by re-running the baseline queries of four sources for the gap (2026-10-14); no eligible record was found. | Yes | None; reported in Limitations. |
| 20 | Further change | After the full-text screening | Screening check | An audit found that the abstract shown with the selected sections was cut for some records and that some reports were not screened at full text; the screening was not repeated. | Yes | None changed; reported in Limitations. |
| 21 | Further change | After the withdrawal of a preprint | Corpus | The withdrawn OKR-Cell preprint is still counted among the included records but was excluded from the decomposition and the culture-level analyses (author decision pending). | No | Record counts include it; work-level counts exclude it (Results). |
| 22 | Further change | At synthesis | Omission | Protocol objective 3 (datasets, downstream tasks, evaluation metrics) and the extraction fields for pretraining objective and code and data availability were not charted, except the evaluation formats and outputs of the targeted pass. | No | Not reported; listed in Limitations. |

<!-- end generated -->

### Supplementary Table S2. Search runs by round and source

Execution date, limits as executed, the number of hits reported by the source's interface and the
records retained, for each round and source; "not searched" marks a source that was not searched in a
round. The interface, the records fetched, the Springer Nature counts before validation and the export
file of each run are in the data file.

<!-- generated: table:search_runs from analysis/prisma_search_audit_2026-10-14/search_runs_by_database.csv -->

| Round | Source | Executed | Date limit as executed | Other limits as executed | Hits reported | Retained |
|-----------------|-----------------|-----------|---------------------------|---------------------------|--------:|--------:|
| 1 baseline (protocol version 3.1) | PubMed | 2026-02-15 | [Date - Publication] 2018/01/01 to 2026/02/28 | free full text[sb]; English[Language] | 631 | 631 |
| 1 baseline (protocol version 3.1) | Scopus | 2026-02-15 | PUBYEAR > 2017; exact-date post-filter none to 2026-02-28 | OPENACCESS(1); LANGUAGE(English) | 1,039 | 1,021 |
| 1 baseline (protocol version 3.1) | OpenAlex | not searched |  |  |  |  |
| 1 baseline (protocol version 3.1) | Semantic Scholar | 2026-02-15 | year=2018-2026; exact-date post-filter none to 2026-02-28 |  | 2,193 | 2,192 |
| 1 baseline (protocol version 3.1) | arXiv | 2026-02-15 | submittedDate:[20180101 TO 20260228] | arXiv categories cs.LG/cs.AI/cs.CL/q-bio.GN/q-bio.QM/stat.ML | 187 | 187 |
| 1 baseline (protocol version 3.1) | bioRxiv and medRxiv (Europe PMC preprints) | 2026-02-15 | FIRST_​PDATE:[2018-01-01 TO 2026-02-28] | SRC:PPR (preprints) | 669 | 669 |
| 1 baseline (protocol version 3.1) | Springer Nature | 2026-02-15 | datefrom:2018-01-01 dateto:2026-02-28 | three-block title/abstract validation after retrieval |  | 272 |
| 1 baseline (protocol version 3.1) | Google Scholar | 2026-02-15 | year range [2018, 2026] (year-level only) |  |  | 562 |
| 2 April top-up | PubMed | 2026-04-14 | [Date - Publication] 2026/03/01 to 2026/04/14 | free full text[sb]; English[Language] | 46 | 46 |
| 2 April top-up | Scopus | 2026-04-14 | PUBYEAR > 2025; exact-date post-filter 2026-03-01 to 2026-04-14 | OPENACCESS(1); LANGUAGE(English) | 197 | 32 |
| 2 April top-up | OpenAlex | not searched |  |  |  |  |
| 2 April top-up | Semantic Scholar | 2026-04-14 | year=2026-2026; exact-date post-filter 2026-03-01 to 2026-04-14 |  | 427 | 201 |
| 2 April top-up | arXiv | 2026-04-14 | submittedDate:[20260301 TO 20260414] | arXiv categories cs.LG/cs.AI/cs.CL/q-bio.GN/q-bio.QM/stat.ML | 14 | 14 |
| 2 April top-up | bioRxiv and medRxiv (Europe PMC preprints) | 2026-04-14 | FIRST_​PDATE:[2026-03-01 TO 2026-04-14] | SRC:PPR (preprints) | 5 | 5 |
| 2 April top-up | Springer Nature | 2026-04-14 | datefrom:2026-03-01 dateto:2026-04-14 | three-block title/abstract validation after retrieval |  | 33 |
| 2 April top-up | Google Scholar | 2026-04-14 | year range [2026, 2026] (year-level only) |  |  | 536 |
| 3 June top-up | PubMed | 2026-06-10 | [Date - Publication] 2026/04/15 to 2026/06/10 | free full text[sb]; English[Language] | 68 | 68 |
| 3 June top-up | Scopus | 2026-06-10 | PUBYEAR > 2025; exact-date post-filter 2026-04-15 to 2026-06-10 | OPENACCESS(1); LANGUAGE(English) | 331 | 39 |
| 3 June top-up | OpenAlex | not searched |  |  |  |  |
| 3 June top-up | Semantic Scholar | 2026-06-10 | year=2026-2026; exact-date post-filter 2026-04-15 to 2026-06-10 |  | 677 | 215 |
| 3 June top-up | arXiv | 2026-06-10 | submittedDate:[20260415 TO 20260610] | arXiv categories cs.LG/cs.AI/cs.CL/q-bio.GN/q-bio.QM/stat.ML | 21 | 21 |
| 3 June top-up | bioRxiv and medRxiv (Europe PMC preprints) | 2026-06-10 | FIRST_​PDATE:[2026-04-15 TO 2026-06-10] | SRC:PPR (preprints) | 33 | 33 |
| 3 June top-up | Springer Nature | 2026-06-10 | datefrom:2026-04-15 dateto:2026-06-10 | three-block title/abstract validation after retrieval |  | 27 |
| 3 June top-up | Google Scholar | 2026-06-10 | year range [2026, 2026] (year-level only) |  |  | 530 |
| 4 July top-up | PubMed | 2026-07-06 | [Date - Publication] 2026/06/11 to 2026/07/06 | free full text[sb]; English[Language] | 25 | 25 |
| 4 July top-up | Scopus | 2026-07-06 | PUBYEAR > 2025; exact-date post-filter 2026-06-11 to 2026-07-06 | OPENACCESS(1); LANGUAGE(English) | 401 | 12 |
| 4 July top-up | OpenAlex | not searched |  |  |  |  |
| 4 July top-up | Semantic Scholar | 2026-07-06 | year=2026-2026; exact-date post-filter 2026-06-11 to 2026-07-06 |  | 884 | 118 |
| 4 July top-up | arXiv | 2026-07-06 | submittedDate:[20260611 TO 20260706] | arXiv categories cs.LG/cs.AI/cs.CL/q-bio.GN/q-bio.QM/stat.ML | 6 | 6 |
| 4 July top-up | bioRxiv and medRxiv (Europe PMC preprints) | 2026-07-06 | FIRST_​PDATE:[2026-06-11 TO 2026-07-06] | SRC:PPR (preprints) | 16 | 16 |
| 4 July top-up | Springer Nature | 2026-07-06 | datefrom:2026-06-11 dateto:2026-07-06 | three-block title/abstract validation after retrieval |  | 20 |
| 4 July top-up | Google Scholar | 2026-07-06 | year range [2026, 2026] (year-level only) |  |  | 0 |
| 5 August living update (protocol version 3.3) | PubMed | 2026-08-10 | [Date - Publication] 2026/07/07 to 2026/08/09 | free full text[sb]; English[Language] | 27 | 27 |
| 5 August living update (protocol version 3.3) | Scopus | 2026-08-10 | PUBYEAR > 2025; exact-date post-filter 2026-07-07 to 2026-08-09 | OPENACCESS(1); LANGUAGE(English) | 501 | 16 |
| 5 August living update (protocol version 3.3) | OpenAlex | 2026-08-10 | from_​publication_​date:2026-07-07,to_​publication_​date:2026-08-09 | is_​oa:true; language:en |  | 100 |
| 5 August living update (protocol version 3.3) | Semantic Scholar | 2026-08-10 | year=2026-2026; exact-date post-filter 2026-07-07 to 2026-08-09 |  | 1,097 | 183 |
| 5 August living update (protocol version 3.3) | arXiv | 2026-08-10 | submittedDate:[20260707 TO 20260809] | arXiv categories cs.LG/cs.AI/cs.CL/q-bio.GN/q-bio.QM/stat.ML | 14 | 14 |
| 5 August living update (protocol version 3.3) | bioRxiv and medRxiv (Europe PMC preprints) | 2026-08-10 | FIRST_​PDATE:[2026-07-07 TO 2026-08-09] | SRC:PPR (preprints) | 20 | 20 |
| 5 August living update (protocol version 3.3) | Springer Nature | 2026-08-10 | datefrom:2026-07-07 dateto:2026-08-09 | three-block title/abstract validation after retrieval |  | 27 |
| 5 August living update (protocol version 3.3) | Google Scholar | 2026-08-10 | year range [2026, 2026] (year-level only) |  |  | 252 |

<!-- end generated -->

### Supplementary Table S3. Reports excluded at full text, with reasons

One main reason per report, as recorded at full-text screening.

<!-- generated: table:exclusions from analysis/prisma_flow_2026-10-07/PRISMA_FLOW.md, analysis/prisma_flow_2026-10-07/prisma_facts.json -->

| Reason | Reports |
|-------------------------------------------------------------|--------:|
| No natural-language text component | 131 |
| Application wrapper around an existing model | 23 |
| Not a generative model | 13 |
| Review or editorial | 5 |
| No biological data modality | 3 |
| Benchmark or resource without a new model | 2 |
| No foundation-model evidence | 1 |
| No substantive text-biology bridge | 1 |
| Total | 179 |

<!-- end generated -->

### Supplementary Table S4. Charted models

One row per charted model (<!-- generated: rows of charted_models.csv -->109<!-- end generated --> models): the record, paper title, DOI and year, the number of routes and
configurations, the input-carrier families, the primary carrier subtype, fusion topologies, text roles,
lifecycle phases and biological modalities. Data file only.

### Supplementary Table S5. Included works: design culture and charted variables

One row per independent work. Dependence test: whether the work reports any test of whether outputs
depend on the biological input (found by both charting runs, or by one run and confirmed at
adjudication). LLM-written text: whether text written by an LLM was used for training or evaluation.
Language-model adaptation: how the language model is trained, where both charting runs agree (LoRA,
low-rank adaptation; "none recorded" when no category was found by both runs). Cross-culture units:
comparison units between arms of different cultures. Opaque steps: median share of the work's
biological route steps that are learned modules left unexpanded. Unstated slots: share of the parameter
slots of the proposed and component models whose value the paper does not state. A dash marks a work
without a decomposed biological route or without parameter slots.

<!-- generated: table:works from analysis/design_culture_charting_2026-10-14/v11/work_level_table.csv, analysis/design_culture_charting_2026-10-14/roles.json, analysis/review_synthesis_2026-10-07/charting_table_models.csv -->

| Study | Proposed models | Culture | Dependence test | LLM-written text | Language-model adaptation | Cross-culture units | Opaque steps | Unstated slots |
|---------------------|-----------------------|--------------|------------|-----------|----------------|---------:|--------:|--------:|
| Shen and Li 2024 [14]; Shen et al. 2026 [15] | OmniNA; OmniNA-1.7B | token-native | yes | no | full fine-tuning | 0 | 0% | 35% |
| Rizvi et al. 2025 [24] | C2S-Scale; C2S-Scale perturbation model | token-native | yes | yes | full fine-tuning | 4 | 33% | 39% |
| Fang et al. 2025 [27] | Cell-o1 | token-native | yes | yes | LoRA or adapter | 0 | 0% | 50% |
| Gao et al. 2025 [28] | CellHermes | token-native | yes | yes | LoRA or adapter | 0 | 0% | 43% |
| Fang et al. 2024 [29] | CHATCELL | token-native | no | yes | none recorded | 0 | — | 44% |
| Jiang et al. 2026 [31] | compound-phenotype scoring model; GEMGen | token-native | yes | yes | full fine-tuning | 2 | 45% | 41% |
| Tang et al. 2025 [32] | DeepSeek; DeepSeek-R1-Distill (1.5B); DeepSeek-R1-Distill 70B; DeepSeek-R1-Distill series (14B, 32B, and 70B) | token-native | no | yes | none recorded | 1 | — | 89% |
| Liu et al. 2024 [33] | Gemma-7B; Geneverse; LLaMA2-13B; LLaMA2-7B; LLaMA3-8B; LLaMAPro-8B; LLaVA-7B (LoRA); Mistral-7B | token-native | no | yes | LoRA or adapter, full fine-tuning | 0 | 0% | 0% |
| Liang 2025 [34] | gene_​eng_​gpt2_​para_​seg; gene_​eng_​gpt2_​summary; gpt2-gene-eng; gpt2-gene-eng-ft | token-native | no | no | full fine-tuning, trained from scratch | 0 | 0% | 19% |
| Shen et al. 2026 [35] | GenNA | token-native | yes | no | trained from scratch | 0 | 50% | 26% |
| Lyu et al. 2024 [37] | GP-GPT | token-native | no | no | LoRA or adapter | 0 | — | 12% |
| Levine et al. 2023 [38] | GPT-2 Medium; GPT-2 Small | token-native | no | no | full fine-tuning, trained from scratch | 0 | 0% | 48% |
| Zhavoronkov et al. 2026 [42] | Longevity-LLM v0.1 | token-native | no | yes | full fine-tuning | 0 | 0% | 100% |
| Li et al. 2025 [47] | Omni-DNA | token-native | no | yes | full fine-tuning | 0 | 12% | 7% |
| Wang 2026 [48] | OmniGene-4; OmniGene-4 v3 | token-native | no | no | LoRA or adapter | 1 | 0% | 30% |
| Li et al. 2026 [52] | RVQ-Alpha | token-native | no | yes | full fine-tuning | 0 | 0% | 10% |
| Liu et al. 2025 [58] | TISSUENARRATOR | token-native | yes | no | LoRA or adapter | 2 | 25% | 4% |
| de Almeida et al. 2025 [5] | ChatNT | encoder-mediated | no | no | frozen | 0 | — | — |
| Fang et al. 2025 [6] | InstructCell | encoder-mediated | no | yes | full fine-tuning | 1 | — | — |
| Kharouiche et al. 2025 [10]; Markogiannakis 2026 [11] | Cell2Text-Gemma-4B; Cell2Text-Llama-1B; Cell2Text-Llama-1B-LoRA; Cell2Text | encoder-mediated | no | no | LoRA or adapter, full fine-tuning | 0 | 50% | 22% |
| Gupta et al. 2026 [19] | Bio-BLIP | encoder-mediated | yes | yes | frozen | 1 | 17% | 0% |
| Al-Kateb et al. 2025 [20] | BioGPT | encoder-mediated | yes | no | full fine-tuning | 0 | 0% | 57% |
| Luo et al. 2023 [21] | BioMedGPT-10B; BioMedGPT-LM-7B | encoder-mediated | no | no | frozen | 2 | 67% | 50% |
| Fallahpour et al. 2025 [22] | BIOREASON | encoder-mediated | no | yes | LoRA or adapter | 1 | 40% | 29% |
| He et al. 2024 [25] | CaLMFlow | encoder-mediated | no | no | none recorded | 0 | 0% | 41% |
| Danner et al. 2025 [36] | Genolator | encoder-mediated | no | yes | full fine-tuning | 1 | 50% | 22% |
| Shi et al. 2025 [41] | scMMGPT | encoder-mediated | no | no | LoRA or adapter | 1 | 25% | 33% |
| Tu et al. 2023 [43] | Med-PaLM M | encoder-mediated | no | no | full fine-tuning | 0 | 33% | 17% |
| Sypetkowski et al. 2026 [46] | OmicsLM | encoder-mediated | no | yes | full fine-tuning | 2 | 0% | 19% |
| Xiang et al. 2026 [49] | OpticalDNA | encoder-mediated | yes | no | LoRA or adapter | 1 | 40% | 22% |
| Fesser et al. 2026 [51] | Qwen3-1.7B; Qwen3-1.7B and Qwen3-4B; Qwen3-1.7B and Qwen3-4B-Thinking; Qwen3-1.7B, Qwen3-4B, and Gemma 4 E2B | encoder-mediated | no | yes | LoRA or adapter | 0 | 33% | 14% |
| Xiao et al. 2026 [54] | SciCore-Omics | encoder-mediated | yes | yes | full fine-tuning | 0 | 33% | 58% |
| Wei et al. 2025 [56] | scMOBA | encoder-mediated | no | yes | LoRA or adapter | 0 | 33% | 43% |
| Schaefer et al. 2024 [12]; Schaefer et al. 2025 [13] | Mistral 7B | hybrid | yes | yes | full fine-tuning | 2 | 50% | 42% |
| Huang et al. 2026 [17] | XunZi-M; XunZi-R | hybrid | no | yes | full fine-tuning | 1 | 50% | 38% |
| Tsou et al. 2025 [23] | BIOVERSE | hybrid | no | yes | LoRA or adapter | 2 | 33% | 29% |
| Galkin et al. 2024 [26] | P3GPT | hybrid | yes | no | none recorded | 0 | 17% | 21% |
| Liu et al. 2025 [44] | TeamPath-7B | hybrid | no | yes | full fine-tuning | 0 | 67% | 70% |
| Zhang et al. 2026 [45] | OCellus; OCellus-Agent; OCellus-GNN | hybrid | yes | yes | LoRA or adapter | 2 | 58% | 34% |
| Queen et al. 2024 [50] | PROCYON; PROCYON-SPLIT | hybrid | yes | yes | none recorded | 1 | 0% | 79% |
| Chen et al. 2026 [59] | CellTosg2Sequence | hybrid | yes | no | LoRA or adapter | 2 | 0% | 29% |
| Wang et al. 2026 [7] | X-Cell; X-Cell-Ultra | language-conditioned | yes | no | full fine-tuning | 1 | — | — |
| Xiang et al. 2026 [8] | MUPAD | language-conditioned | no | no | none recorded | 0 | — | — |
| Sun et al. 2025 [18] | ALTER | language-conditioned | yes | no | none recorded | 0 | 57% | 27% |
| Ingraham et al. 2023 [30] | Chroma | language-conditioned | yes | no | none recorded | 0 | 100% | 0% |
| Gu et al. 2026 [39] | H2O | language-conditioned | yes | no | none recorded | 0 | 100% | 21% |
| Liu et al. 2025 [40] | LEONINE; LEONINE-GPT-2 | language-conditioned | yes | no | full fine-tuning, trained from scratch | 0 | 0% | 17% |
| Tang et al. 2023 [53] | scDiff | language-conditioned | no | yes | none recorded | 0 | 0% | 14% |
| Zhang et al. 2025 [57] | Shusi | language-conditioned | yes | no | none recorded | 0 | 58% | 67% |
| Pang et al. 2025 [60] | TissueCraftAI | language-conditioned | no | no | none recorded | 0 | 67% | 67% |
| Shang et al. 2026 [55] | scMIR | alignment-only | no | no | none recorded | 0 | 67% | 36% |

<!-- end generated -->

### Supplementary Table S6. Motif library

Motifs are closed frequent sub-chains of role-aware operations supported by at least 4 papers.
Operations: library operations in order. Input: whether the operations act on biological input, on text
input, or join the two. Contiguous: whether the operations must be adjacent. Papers and models: support.
The reporting of each motif's parameters and an example with its verbatim evidence are in the data file.

<!-- generated: table:motifs from analysis/motif_library_2026-10-14/motifs.json -->

| Motif | Family | Operations | Input | Contiguous | Papers | Models | Description |
|-------------------|-------------|-----------------------|-------------|---------|------:|------:|-----------------------------------------|
| Subset then verbalise | carrier formation | select → serialise | biological input | no | 10 | 17 | Keep part of the biological record (top genes, fields, cells) and write it as text. |
| Ranked gene sentence | carrier formation | rank → serialise | biological input | no | 5 | 12 | Order features by value and write the ordered identifiers as text; magnitudes are dropped. |
| Expression normalisation | carrier formation | normalise → log transform | biological input | yes | 5 | 7 | Library-size or similar normalisation followed by a log transform of expression values. |
| Sample then verbalise | carrier formation | sample → serialise | biological input | no | 4 | 5 | Randomly draw cells, examples or negatives and write them into text. |
| Biological alphabet embedding | carrier formation | tokenise → table lookup | biological input | no | 5 | 5 | Tokenise a sequence in its own alphabet and look the tokens up in an embedding table. |
| Text token embedding | carrier formation | tokenise → table lookup | text input | no | 6 | 7 | Standard text channel: tokenise text and look the tokens up in the language model's embedding table. |
| Tile then encode | carrier formation | partition → learned module | biological input | no | 7 | 8 | Split an image, genome or sequence into patches/windows/chunks and encode them with a learned module. |
| Encoder then projector | encoding | learned module → learned projection | biological input | no | 18 | 23 | A learned (often pretrained, frozen) biological encoder followed by a projection into the receiving model's space. |
| Projector into the model | encoding | learned module → learned projection → learned module | biological input | no | 6 | 8 | Encoder output projected and then consumed by another learned module (typically the language model). |
| Stacked learned modules | encoding | learned module → learned module | biological input | no | 12 | 14 | Two or more unexpanded learned modules in sequence (e.g. frozen foundation model then trainable encoder). |
| Domain computation then encoder | encoding | computation outside the library → learned module | biological input | no | 10 | 10 | A computation outside the operation catalog (graph convolution, physics terms, clustering) before a learned encoder. |
| Verbalised biology read by a model | joining | serialise → learned module | biological input | no | 9 | 17 | Biology written as text and consumed by a learned language model. |
| Encode then join | joining | learned module → concatenate | biological input | no | 6 | 6 | Encoded biological representation concatenated with other inputs (text tokens, [CLS], other modalities). |
| Encode then add | joining | learned module → add | biological input | no | 5 | 5 | Encoded representation summed with another representation (positional, prior or other modality). |
| Text tokens into the model | joining | tokenise → learned module | text input | no | 7 | 9 | Tokenised text read by a learned module. |

<!-- end generated -->

### Supplementary Table S7. Gene and token budgets stated in the papers

Values as stated in the papers. (a) Genes or features kept per cell or object when a profile is written
as text or passed to an encoder; "not stated" marks a route whose number the paper does not give. (b)
Vectors, discrete codes or text tokens per object passed to the language model.

<!-- generated: table:budgets from analysis/discovery_2026-10-14/gene_budget_table.csv, analysis/discovery_2026-10-14/token_budget_table.csv -->

**(a) Genes or features kept per cell or object.**

| Study | Model and setting | Route | Genes kept | Values kept | Evidence |
|----------------|----------------|--------------|-------:|-------------|---------------------------------------------|
| Levine et al. 2023 [38] | Cell2Sentence (GPT-2) | text: proposed model input | 100 | no (rank order) | In order to limit computational costs, we truncate each cell sentence to only keep the 100 highest expressed (top 100 ranked) genes. |
| Rizvi et al. 2025 [24] | C2S-Scale | text: proposed model input | 1000 | no (rank order) | For predictive tasks such as cell type annotation on single cells, we find that K = 1000 often works well for cell annotation, achieving performance competitive or better than baseline models. |
| Gao et al. 2025 [28] | CellHermes | text: proposed model input | 100 | no (rank order) | Next, we ranked the gene expression values for each cell and truncated the top 100 genes for each cell , denoted as 𝑖 . |
| Fang et al. 2024 [29] | ChatCell | text: proposed model input | 100 | no (rank order) | To capture the most significant expression patterns, we prioritize the top 100 most expressed genes, since lower-ranked genes tend to have more consistent expression values. |
| Liu et al. 2025 [44] | TeamPath | text: proposed model input | 100 | no (rank order) | To transfer the information in gene expression space to text space, we first rank the genes of each spot based on their expression profiles and select the top 100 genes to formulate them in natural language. |
| Chen et al. 2026 [59] | CellTosg2Sequence | text: proposed model input | 200 | no (rank order) | For a cell with normalised expression X ∈ R G we sort genes by expression magnitude and keep the topK ( K =200 ) HGNC symbols: <!-- formula-not-decoded --> Rank correlates almost linearly with log-expression ( R 2 ≈ 0 . |
| Zhang et al. 2026 [45] | OCellus (cross-species task) | text: proposed model input | 250 | no (rank order) | We 5 probed cross-species reasoning with the cross-species cell-type task, in which OCellus is given a 6 mouse cell's top -ranked genes on the shared ortholog panel of approximately 250 genes and 7 asked to predict the canonical human-equivalent cell type. |
| Zhang et al. 2026 [45] | OCellus (EvenClock neighbours) | text: proposed model input | 5 | no (rank order) | Within each sector we sort neighboring cells by descending expression of their top-ranked genes and concatenate the top five marker genes per neighbor into a comma-separated string. |
| Schaefer et al. 2024 [12] | CellWhisperer (GPT-4/Mixtral conversation generation) | text: data-generation input | 50 | no (rank order) | For each transcriptome, we generated a chat-like conversation using one of two LLMs (GPT-4 or Mixtral) on the basis of the transcriptome's top 50 most highly expressed genes, the top 50 GSVA-derived gene sets, and the transcriptome's textual annotation. |
| Tsou et al. 2025 [23] | BIOVERSE baselines (open-domain LLMs) | text: comparator input | 128 | no (sorted by count) | ### 5.2 MAIN RESULTS #### 5.2.1 ZERO-SHOT GENERATIVE CELL TYPE ANNOTATION We evaluate BIOVERSE's against two baselines on the PBMC10K dataset as discussed in scvi-tools (Gayoso et al., 2022) under zero-shot generation: (1) random and majority baseline (2) open-domain LLMs given a list of the 128 most expressed genes (sorted by expression count) as input. |
| Sypetkowski et al. 2026 [46] | OmicsLM text-only baselines | text: comparator input | 50 | no (rank order) | Text-only baselines receive the 50 highest-expressed genes per sample, with sample identifiers replaced by dummy labels ( sample\_​1 , sample\_​2 , . |
| Sypetkowski et al. 2026 [46] | OmicsLM: C2S-Scale and Cell-o1 as comparators | text: comparator input | 1000 | no (rank order) | Candidate class labels are provided in text to OmicsLM, C2S-Scale-27B, and Cell-o1 during constrained likelihood scoring, matching the closed label set available to CLIP-like contrastive scoring; C2S-Scale and Cell-o1 receive the top-1000 expressed genes as text input. |
| Wang et al. 2026 [7] | X-Cell: C2S comparator | text: comparator input | 1000 | no (rank order) | We used the top 1,000 most highly expressed genes per cell ( top k genes=1000 ), providing substantially more gene coverage than the 200-gene default in the C2S tutorial. |
| Schaefer et al. 2024 [12] | CellWhisperer (Geneformer encoder) | embedding: proposed model input | 2048 | encoder (rank tokens) | Specifically, the transcriptomes were sorted by gene expression levels, and the top 2048 most highly expressed genes were tokenized with a dictionary of human gene symbols (Theodoris et al. |
| Shi et al. 2025 [41] | scMMGPT (scGPT encoder) | embedding: proposed model input | 2048 | encoder (values) | <!-- formula-not-decoded --> To mitigate data sparsity, we retain the top 2,048 most expressed genes per cell, which captures the majority of meaningful signals. |
| Fang et al. 2025 [6] | InstructCell | embedding: proposed model input | 3600 | encoder (values) | To standardize gene features across all datasets, we identify the top 3,600 highly variable genes for each dataset's cell-by-gene matrix using Seurat [87, 88]. |
| Jiang et al. 2026 [31] | GEMGen (signed DE lists) | text: proposed model input | 50 | no (rank order, sign as list) | Specifically, we selected the top 50/40/30 genes with the largest absolute CD values and then assigned each gene to the upregulated or downregulated category based on the sign of its value (positive or negative). |
| Fang et al. 2025 [27] | Cell-o1 | text: proposed model input | not stated | no (rank order) | Each cell c i serves as a proxy for a cluster centroid and is represented by a ranked list of its top M expressed genes g i = [ g i 1 , g i 2 , . |
| Sypetkowski et al. 2026 [46] | OmicsLM | embedding: proposed model input | 20541 | yes (vector) | For each sample, the default input vector concatenates four feature groups: a one-dimensional input-scale indicator, the normalized expression vector, a 512-dimensional Funomics T0 embedding [Powalski et al., 2026], and a 768-dimensional embedding from Geneformer-V2104M [Chen et al., 2026], yielding a 20,541-dimensional omics vector. |
| Xiang et al. 2026 [8] | MUPAD | embedding: proposed model input | 331 | yes (pathway scores) | Raw RNA-seq counts were normalized to TPM, filtered to remove housekeeping and mitochondrial genes, and compressed into 331 pathway-level enrichment scores using established pan-cancer gene signatures 61 , yielding biologically interpretable conditioning inputs. |
| Wang et al. 2026 [7] | X-Cell | embedding: proposed model input | 4000 | yes (values) | \| Parameter \| Mini (60M) \| X-Cell-Ultra Phase 1 \| X-Cell Ultra Phase 2 \| \|-------------------------\|------------------\|------------------------\|------------------------\| \| Dataset \| Replogle-Nadig \| Top 5% high-effect \| 100% all perturbations \| \| Nodes (GPUs) \| 1 (8) \| 12 (96) \| 16 (128) \| \| Set size S \| 64 \| 64 \| 64 \| \| Optimizer step size \| 64 \| 96 \| 128 \| \| Effective batch (cells) \| 4,096 \| 6,144 \| 8,192 \| \| Epochs \| 6 \| 10 \| 10 \| \| Optimizer \| AdamW \| AdamW \| AdamW (fresh) \| \| β 1 ,β 2 \| 0.9, 0.999 \| 0.9, 0.999 \| 0.9, 0.999 \| \| Peak LR \| 10 - 4 \| 3 × 10 - 4 \| 4 × 10 - 5 \| \| Weight decay \| 0.01 \| 0 \| 0 \| \| LR schedule \| Cosine + warmup \| Cosine + warmup \| Cosine + warmup \| \| Warmup \| 10% \| 10% \| 3% \| \| Grad clip norm \| 1.0 \| 1.0 \| 1.0 \| \| Context length G ′ \| Full ( ∼ 19k) \| 4,000 \| 4,000 \| \| Mixed precision \| bf16 \| bf16 \| bf16 \| \| FSDP strategy \| N/A \| Per-layer \| Per-layer \| \| Warmstart \| scGPT embeddings \| - \| Phase 1 epoch 9 \| #### Batch size scaling. |

**(b) Vectors, codes or text tokens per object.**

| Study | Model | What is counted | Number | Evidence |
|----------------|--------------|---------------------|-------:|---------------------------------------------------|
| Fang et al. 2025 [6] | InstructCell | Q-Former query tokens per cell | 8 | For the Q-Former module, L cell is set to 4, the number of query tokens k is 8, and the number of key-value pairs t is 6. |
| Shi et al. 2025 [41] | scMMGPT | Q-Former queries per cell | 32 | - The cell-to-text projector is implemented with a Query Transformer (Q-Former) [33] with 32 learnable queries, which maps high-dimensional cell embeddings from the scLLM into the token embedding space of the Text LLM. |
| Danner et al. 2025 [36] | Genolator | virtual tokens per modality embedding | 8 | For model input, each embedding modality was mapped to 8 virtual tokens of size 4096. |
| Gupta et al. 2026 [19] | Bio-BLIP | Q-Former query vectors (AlphaGenome / GenePT / ESM) | 32 | The Alphagenome Q-former has 32 query vectors, while the GenePT Q-former and ESM Q-former are trained with 8 query vectors each. |
| Shang et al. 2026 [55] | scMIR | Q-Former query embeddings per image | 32 | In our implementation, we use 32 learnable query embeddings, each with a hidden dimension of 768. |
| Li et al. 2026 [52] | RVQ-Alpha | discrete tokens per cell | 10 | We present RVQ-Alpha , an end-to-end framework that bridges this modality gap through three contributions: (i) a Residual Vector Quantization (RVQ) tokenizer that compresses each cell into a fixed 10-token sequence via eight residual codebooks embedded directly in the LLM vocabulary, requiring 3.4 × fewer tokens than prior discrete methods and enabling bidirectional unification of cell interpretation and generation; (ii) scCoT-Synth , a teacher-student engine that grounds newly added biological tokens through evidence-before-conclusion reasoning, using the language modeling objective as the cross-modal alignment signal without a separate projection network; and (iii) a Fact-Aware RLVR system combining an ontology-grounded answer judge with saliency-weighted verification of biological claims against actual expression data, under dynamic gating that conditions hallucination suppression on task competence. |
| Chen et al. 2026 [59] | CellTosg2Sequence | KG virtual tokens per cell (one per gene) | 200 | Each prompt has four blocks: (1) KG virtual tokens [KG\_​VT] : one virtual token per input gene (block length K =200 ), aligned one-to-one with the Cell Sentence; (2) Biological metadata [Meta] : short natural-language fields (tissue, compartment, disease, optional KG triples); (3) Cell Sentence [CellSentence] : the ranked gene list as HGNC symbols; (4) Task instruction [Task] : one short line specifying the output format. |
| Tsou et al. 2025 [23] | BIOVERSE | [BIO] embeddings per object (notation k=1) | 1 | Given a query q , bio embeddings ˜ z b injected at a 1 For notational simplicity, we assume k = 1 and omit the token index in most equations from here onward; the framework naturally extends to k &gt; 1 when multiple embeddings are injected [BIO] marker, and paired target text t b = ( t 1 , . |
| Levine et al. 2023 [38] | Cell2Sentence | text tokens: prompt + top-100 genes | 350 | On average, the number of tokens in the prompts and top 100 genes combined was around 350. |
| Li et al. 2026 [52] | RVQ-Alpha (critique of ranked lists) | text tokens for top-20 gene list | 80 | However, these approaches introduce a different fundamental trade-off: ranked gene lists discard quantitative expression precision and produce token-inefficient representations (40-80 tokens per cell for the top-20 genes), whereas structured descriptions scale poorly to population-level multi-cell reasoning [28]. |
| Wei et al. 2025 [56] | scMOBA | cross-attention learnable queries | 256 | To effectively summarize informative biological signals, 256 learnable queries are introduced to perform cross-attention with the GCN outputs, extracting the most relevant features for downstream textual reasoning while reducing the input length to the language model. |
| Xiao et al. 2026 [54] | SciCore-Omics | Q-Former query virtual tokens per profile | 32 | In the implementation used in this study, the gene branch follows <!-- formula-not-decoded --> where the gene encoder first maps the gene expression profile into molecular embeddings, the Q-Former compresses the molecular representation into 32 query virtual tokens, and the projector maps these virtual tokens into the language-model hidden space. |
| Sypetkowski et al. 2026 [46] | OmicsLM | projected vector per <omics> placeholder (one per profile) | 1 | Bottom: each placeholder is built by mapping a single-cell or bulk expression profile, including profiles from perturbation screens, to a continuous vector and projecting it into the LLM token-embedding space, allowing multiple profiles to be interleaved in one prompt for sample-level and comparative reasoning. |

<!-- end generated -->

### Supplementary Table S8. Text written by LLMs and used for training or evaluation

Works that train or evaluate on text written or rewritten by another LLM. What was written: training or
evaluation content, or instruction templates only. Human check: whether the paper reports a human check
of the generated text. Reasoning traces: whether the generated text includes reasoning traces. Used in
evaluation: whether LLM-written text enters the evaluation.

<!-- generated: table:synthetic from analysis/discovery_2026-10-14/synthetic_text_table.csv -->

| Study | Culture | What was written | Generators | Human check | Reasoning traces | Used in evaluation | Example |
|-----------------|------------|------------|-------------|--------|-----------|-----------|-------------------------------------|
| Rizvi et al. 2025 [24] | token-native | training or evaluation content | GPT-4o; GPT-4.5; GPT-3.5-Turbo | no | no | no | To create training data for this task, we use GPT-4o to generate natural language captions for cell clusters derived from annotated datasets (Methods Section 4.7). |
| Fang et al. 2025 [27] | token-native | training or evaluation content | OpenAI o1 | no | yes | no | We begin by performing reasoning distillation using OpenAI's o1 [22], a frontier LLM with strong multi-step reasoning capabilities, to construct a synthetic dataset of high-quality reasoning traces and predictions. |
| Gao et al. 2025 [28] | token-native | instruction templates only | ChatGPT-4o | no | no | no | To  increase  linguistic  diversity  and  robustness,  we used  ChatGPT-4o 39 to  augment  instruction  types  with  20  diverse  task  descriptions 48 (Methods). |
| Fang et al. 2024 [29] | token-native | instruction templates only | GPT-3.5-turbo | no | no | no | This description is then fed into GPT-3.5turbo, leveraging its capability to produce diverse renditions of the same concept. |
| Jiang et al. 2026 [31] | token-native | training or evaluation content | GPT-4o | yes | no | no | We curated descriptive annotations for all cell  types  used  in  this  study  by  combining  two  sources:  descriptions  retrieved from the ATCC cell catalog, and independently generated summaries by GPT-4o, which  were  manually  reviewed  to  ensure  biological  plausibility. |
| Tang et al. 2025 [32] | token-native | training or evaluation content | GPT-OSS-120B | no | no | no | We use the NCBI-derived biological dataset from GenePT [26]: biomedical corpus from NCBI is used as the knowledge source in EasyDataset [30], and GPT-OSS-120B [31] synthesizes instruction-response pairs covering broad biological knowledge. |
| Liu et al. 2024 [33] | token-native | training or evaluation content | GPT-3.5 | no | no | no | To generate LLMs for genomic and proteomic analysis, we incorporate the training datasets from rephrased descriptions for gene functions as well as synthetic descriptions from GPT 3.5. |
| Zhavoronkov et al. 2026 [42] | token-native | unclear | generator not stated | no | no | no | To  improve Longevity-LLM's  generalization  ability, prompt  collections feature semantic variation,  formatting  options,  synonym  rotation, and  automatically  generated  reasoning  traces. |
| Li et al. 2025 [47] | token-native | training or evaluation content | LLMAnnotator (model not named) | no | no | no | A LLMAnnotator is employed to extend and refine functional annotations. |
| Li et al. 2026 [52] | token-native | training or evaluation content | unspecified teacher LLM (replaceable backend) | no | yes | no | We present RVQ-Alpha , an end-to-end framework that bridges this modality gap through three contributions:  (i) a Residual Vector Quantization (RVQ) tokenizer that compresses each cell into a fixed 10-token sequence via eight residual codebooks embedded directly in the LLM vocabulary, requiring 3.4 × fewer tokens than prior discrete methods and enabling bidirectional unification of cell interpretation and generation;  (ii) scCoT-Synth , a teacher-student engine that grounds newly added biological tokens through evidence-before-conclusion reasoning, using the language modeling objective as the cross-modal alignment signal without a separate projection network;  and (iii) a Fact-Aware RLVR system combining an ontology-grounded answer judge with saliency-weighted verification of biological claims against actual expression data, under dynamic gating that conditions hallucination suppression on task competence. |
| Fang et al. 2025 [6] | encoder-mediated | instruction templates only | GPT-4o | no | no | no | Next, we prompt GPT-4o to generate a set number of instruction-response templates for each task. |
| Gupta et al. 2026 [19] | encoder-mediated | training or evaluation content | Claude Sonnet 4.6 | no | yes | no | We construct 5-step chain-of-thought reasoning traces linking GWAS variants from the Gold Standard Dataset to target genes and to the observed phenotype using Claude Sonnet 4.6 and ground-truth expert annotations from the available under a CC-BY 4.0 International license. |
| Fallahpour et al. 2025 [22] | encoder-mediated | training or evaluation content | Claude 3.7 Sonnet; GPT-4o | no | yes | no | These sequences have an average length of approximately 4,000 base pairs, with most variants differing by only 1-3 nucleotides from their reference sequences.  #### 4.1.2 Reasoning Path Construction and Curation  Adistinctive feature of this dataset is its inclusion of explicit causal reasoning paths connecting genetic variants to disease phenotypes via defined molecular mechanisms; these paths were constructed using the Claude 3.7 Sonnet model [2] and grounded with contextual disease information from the KEGG disease database [20]. |
| Danner et al. 2025 [36] | encoder-mediated | training or evaluation content | GPT-4.1 | yes | no | yes | For  each  GO  aspect 29 ,  we  engineered  specific  system  prompts  to  guide  a  GPT-4.1 37 model (hosted on Azure AI Foundry) in generating three confirmation QA samples per gene, leveraging the ontology annotations and at least six manually crafted few-shot examples from two or more unrelated genes per prompt. |
| Sypetkowski et al. 2026 [46] | encoder-mediated | training or evaluation content | unnamed LLM curation pipeline | no | no | no | We addressed this with an LLM-based curation pipeline that (i) generated free-text natural language descriptions for each sample, and (ii) extracted structured annotations including tissue, cell type, cell line, disease, and perturbation target. |
| Fesser et al. 2026 [51] | encoder-mediated | training or evaluation content | Claude 3.7 Sonnet (inherited BIOREASON traces) | no | yes | yes | In BIOREASON, these traces were produced using Claude 3.7 Sonnet and grounded with contextual disease information from the KEGG disease database [78, 79], then packaged into standardized question-answer pairs for training and evaluation [1]. |
| Xiao et al. 2026 [54] | encoder-mediated | training or evaluation content | unspecified LLM | no | no | no | Panels: - **a**: Schematic from a gene expression matrix to extracted biological features: top expressed/marker genes, pathway enrichment via ssGSEA, and tissue/metadata, which are converted into LLM-generated text. |
| Wei et al. 2025 [56] | encoder-mediated | training or evaluation content | unspecified LLM (LLM-assisted manual curation) | yes | no | no | To ensure the consistency of metadata from the large-scale and diverse high-dimensional datasets, we applied an LLMassisted manual curation procedure to align the cell type taxonomy, brain region origins, developmental stages and disease status from different datasets (Extended Data Fig. 1c and Supplementary Table 2). |
| Schaefer et al. 2024 [12]; Schaefer et al. 2025 [13] | hybrid | training or evaluation content | GPT-4; Mixtral 8x7b; GPT-4o | no | no | yes | Our method was created in three steps (Fig. 1a): (1) LLM-assisted curation of multimodal training data, resulting in 1,082,413 pairs of human RNA-seq profiles and matched textual annotations; (2) training of the CellWhisperer embedding model, which places the transcriptomes and their AI-curated textual descriptions into a joint embedding space for cell search and annotation; and (3) development of the CellWhisperer chat model for transcriptome-aware question answering and natural-language chats. |
| Huang et al. 2026 [17] | hybrid | training or evaluation content | GPT-4 | yes | yes | no | These entries were generated using structured prompts with GPT-4 to transform raw gene-disease associations from databases, including DisGeNET 10 and the Comparative Toxicogenomics Database (CTD) 13 , into detailed mechanistic interpretations based on literature evidence. |
| Tsou et al. 2025 [23] | hybrid | training or evaluation content | unspecified LLM (inherited dataset descriptions) | no | no | no | Following the dataset protocol, we use the CellxGene subset (Perkel, 2024), where pseudo-bulk RNA samples are generated by averaging single-cell profiles, and natural-language descriptions are produced from cell and tissue metadata using large language models. |
| Liu et al. 2025 [44] | hybrid | training or evaluation content | o4-mini | yes | yes | no | Reasoning data were constructed using COT templates generated based 94 on the advanced reasoning model o4-mini (25), with subsequent quality validation performed by 95 pathologists at Yale School of Medicine. |
| Zhang et al. 2026 [45] | hybrid | instruction templates only | GLM-5.2 | no | no | no | The Planner LoRA is fine-tuned on five thousand natural-language to directedacyclic-graph pairs synthesized via an Anthropic-compatible GLM-5.2 applicationprogramming-interface endpoint |
| Queen et al. 2024 [50] | hybrid | training or evaluation content | OpenAI GPT models | no | no | no | To increase the diversity of phenotypes, we rephrase the original descriptions using OpenAI's GPT models. |
| Tang et al. 2023 [53] | language-conditioned | training or evaluation content | GPT-4 | no | no | yes | For these two terms, we utilize GPT4 (OpenAI, 2023) to depict their descriptions given available definitions as query contexts. |

<!-- end generated -->

### Supplementary Table S9. Cross-culture comparison units

One row per comparison unit after adjudication: one comparison between arms of different cultures, per
work and task family. Design: a controlled ablation within one system, the same backbone given the data
as text, or different systems. Opponent arm: its culture and how it was obtained. Values reported: as
quoted in the charting; a dash marks a unit without values in the text. Image rendering is the
DNA-as-image arm of OpticalDNA.

<!-- generated: table:comparisons from analysis/design_culture_charting_2026-10-14/v11/comparison_units_adjudicated.csv -->

| Study | Task family | Task | Design | Proposed arm | Opponent arm (obtained as) | Winner | Values reported |
|--------------------|------------|-------------------------|--------------|-----------|------------------|-----------|------------------|
| Liu et al. 2025 [58] | spatial | spatial coordinates: numeric tokens vs learned positional embeddings | controlled ablation within one system | token-native | encoder-mediated (trained ablation) | token-native | qualitative only |
| Liu et al. 2025 [58] | quantitative generation | cell generation / ranked gene prediction vs Nicheformer | different systems | token-native | encoder-mediated (external frozen embedding) | token-native | NDCG, overlap (values not in text) |
| Queen et al. 2024 [50] | text generation | phenotype generation vs LLMs given gene symbol/UniProt ID/sequence | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | BERTScore F1; LLM judge |
| Rizvi et al. 2025 [24] | text generation | cluster captioning vs CellWhisperer | different systems | token-native | encoder-mediated (external pretrained model) | token-native | BioBERTScore |
| Rizvi et al. 2025 [24] | categorical | cell type annotation vs expression-only FMs | different systems | token-native | encoder-mediated (external frozen embedding) | token-native | >85% accuracy |
| Rizvi et al. 2025 [24] | embedding quality | cell embedding linear probe vs expression FMs | different systems | token-native | encoder-mediated (external frozen embedding) | token-native | — |
| Rizvi et al. 2025 [24] | categorical | spatial niche prediction vs averaged embeddings | different systems | token-native | encoder-mediated (external frozen embedding) | token-native | — |
| Schaefer et al. 2024 [12]; Schaefer et al. 2025 [13] | text generation | chat answers: embedding + top-50 gene list vs embedding only | controlled ablation within one system | hybrid | encoder-mediated (trained ablation) | hybrid | mild benefit (perplexity) |
| Schaefer et al. 2024 [12]; Schaefer et al. 2025 [13] | text generation | chat answers vs Mistral 7B / Llama 3.3 70B given top-50 genes | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | lowest perplexity |
| Fallahpour et al. 2025 [22] | sequence-level | KEGG reasoning, variant effect, chromatin: DNA encoder + Qwen3 vs Qwen3 reading DNA as text | same backbone given the data as text | encoder-mediated | token-native (trained baseline) | encoder-mediated | VEP coding acc 80.2 vs 49.0 |
| Fang et al. 2025 [6] | quantitative generation | pseudo-cell generation and drug sensitivity vs Cell2Sentence | different systems | encoder-mediated | token-native (trained baseline) | encoder-mediated | — |
| Shi et al. 2025 [41] | categorical | cell type annotation: expression values vs cell sentence | controlled ablation within one system | encoder-mediated | token-native (trained ablation) | encoder-mediated | error 0.76% vs 6.42% |
| Xiang et al. 2026 [49] | sequence-level | eQTL: DNA rendered as image vs 1D tokens at matched budget | controlled ablation within one system | image rendering | token-native (trained ablation) | image rendering | AUROC 0.626 vs 0.558 |
| Tsou et al. 2025 [23] | categorical | zero-shot PBMC annotation vs LLMs given 128-gene list | different systems | hybrid | token-native (prompted general LLM) | mixed | acc 0.614 vs GPT-OSS-120B 0.779, Granite-8B 0.369 |
| Tsou et al. 2025 [23] | text generation | molecule/protein description vs LLMs given raw SMILES/sequence | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | LLM-judge 0.17 vs 0.02 |
| Danner et al. 2025 [36] | categorical | GO confirmation/denial vs GPT-4.1 given sequences as text | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | MCC 0.955 vs 0.18 |
| Tang et al. 2025 [32] | embedding quality | LLM-written gene profiles + text embedding vs scGPT | different systems | token-native | encoder-mediated (external frozen embedding) | token-native | gene-level AUC mostly higher |
| Luo et al. 2023 [21] | text generation | protein QA: aligned encoder features vs raw sequence into the same Llama2-7B-Chat | controlled ablation within one system | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | BLEU-2 0.344 vs 0.019 |
| Luo et al. 2023 [21] | text generation | molecule QA vs ChatGPT/Llama2 given SMILES | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | BLEU-2 0.234 vs 0.103 |
| Wang et al. 2026 [7] | quantitative generation | perturbation response vs C2S-2B cell sentences | different systems | encoder-mediated | token-native (trained baseline) | encoder-mediated | Pearson delta 0.51 vs -0.03 (iPSC-200) |
| Jiang et al. 2026 [31] | embedding quality | cross-dataset consistency: ranked DEG text vs numeric DE vectors | different systems | token-native | encoder-mediated (representation compared without a model) | token-native | — |
| Jiang et al. 2026 [31] | other generation | molecule generation vs GexMolGen (expression profiles) | different systems | token-native | encoder-mediated (trained baseline) | token-native | hit recovery |
| Chen et al. 2026 [59] | categorical | cell type / drug response: KG virtual tokens + cell sentence vs cell sentence only | controlled ablation within one system | hybrid | token-native (trained ablation) | hybrid | 0.385 vs 0.268; 0.606 vs 0.487 |
| Chen et al. 2026 [59] | categorical | immune cell type annotation vs C2S-Scale-27B | different systems | hybrid | token-native (external pretrained model) | token-native | exact 24.1% vs 85.6% |
| Gupta et al. 2026 [19] | sequence-level | variant annotation / target gene vs LLM given AlphaGenome outputs or variant context as text | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | target gene 71.2% vs 64.4% |
| Sypetkowski et al. 2026 [46] | multi-task | 10-task suite: embedding stack vs Cell2Sentence-like top-100 text | controlled ablation within one system | encoder-mediated | token-native (trained ablation) | encoder-mediated | relative rank .740 vs .090 |
| Sypetkowski et al. 2026 [46] | categorical | GEO-OmicsQA vs text-only LLMs given 50 genes (incl. C2S-Scale-27B, Cell-o1, GPT-5.5) | different systems | encoder-mediated | token-native (prompted general LLM) | encoder-mediated | binary QA 0.752 vs <=0.588 |
| Wang 2026 [48] | categorical | remote homology: biological tokens vs ESM-2 embeddings | different systems | token-native | encoder-mediated (external frozen embedding) | token-native | 59.5% vs 50.5% |
| Huang et al. 2026 [17] | categorical | regulator prediction: combined vs text-only XunZi-R and graph-only XunZi-M | different systems | hybrid | token-native (trained baseline) | hybrid | AUC 0.92 vs GPT-4o 0.52 |
| Zhang et al. 2026 [45] | embedding quality | cell embeddings vs 13 single-cell FMs | different systems | hybrid | encoder-mediated (external frozen embedding) | mixed | linear probe 95.1% (best) but NMI below scimilarity |
| Zhang et al. 2026 [45] | quantitative generation | perturbation response: LLM-derived gene embeddings vs GO features (GEARS) | different systems | hybrid | encoder-mediated (external frozen embedding) | hybrid | Pearson 0.945 vs 0.84 |

<!-- end generated -->

### Supplementary Table S10. Route-level design-pattern codebook

One row per charted route of the 50 agent-decomposed papers (<!-- generated: rows of route_codebook.csv -->532<!-- end generated --> routes): the
model and configuration, lifecycle phase, source
modality, carrier family and subtype, fusion topology, text role, the operation chain, the value of each
design axis with the rule that assigned it, the share of opaque steps, the share of stated parameters
and the archetype. Data file only.


\newpage

## Supplementary Figures

### Supplementary Figure S1. Full PRISMA 2020 flow, with the records identified per database

Records identified per source and round, records removed before screening, records screened and
excluded, reports sought, not retrieved and assessed, and studies included. Reasons for exclusion at
full text are given in Supplementary Table S3.

<!-- generated: figure:flow from analysis/prisma_flow_2026-10-07/prisma_flow.png -->

![](analysis/prisma_flow_2026-10-07/prisma_flow.png){width=100%}

<!-- end generated -->


\newpage

## Data files and column dictionary

<!-- generated: datafiles from the data files of this supplement -->

The data files are comma-separated, UTF-8 encoded and use plain-language values. The coded originals from which they are built are kept in the project repository (see Data and code availability).

| File | Item | Contents | Rows |
|---------------------|-------------------------|---------------------------------------------------------|------:|
| deviations.csv | Supplementary Table S1 | Deviations from the protocol | 22 |
| search_​runs.csv | Supplementary Table S2 | Search runs by round and source, with limits and counts as executed | 40 |
| fulltext_​exclusions.csv | Supplementary Table S3 | Reports excluded at full text, by reason | 8 |
| charted_​models.csv | Supplementary Table S4 | Charted models with their records, routes and input labels | 109 |
| included_​works.csv | Supplementary Table S5 | Included works with their design culture and charted variables | 51 |
| motif_​library.csv | Supplementary Table S6 | Motif library: recurring operation sub-chains with an example each | 15 |
| gene_​budgets.csv | Supplementary Table S7 | Genes or features kept per cell or object, as stated in the papers | 21 |
| token_​budgets.csv | Supplementary Table S7 | Vectors, codes or text tokens per object passed to the language model | 13 |
| llm_​written_​text.csv | Supplementary Table S8 | Works that used text written by LLMs for training or evaluation | 25 |
| comparison_​units.csv | Supplementary Table S9 | Cross-culture comparison units after adjudication | 31 |
| route_​codebook.csv | Supplementary Table S10 | Route-level codebook of the design axes and archetypes | 532 |

**Column dictionary** (also provided as data_dictionary.csv).

| File | Column | Description |
|-----------------------|---------------------------|-----------------------------------------------------------------------|
| deviations.csv | number | Number of the deviation |
| deviations.csv | kind | Protocol amendment (with the version it created) or further change not foreseen by the protocol |
| deviations.csv | date_​or_​stage | Date of the amendment or the stage at which the change was made |
| deviations.csv | area | Part of the review affected |
| deviations.csv | change | What changed |
| deviations.csv | made_​after_​results_​were_​seen | Whether the change was decided after results were known |
| deviations.csv | dependent_​results_​and_​labelling | Results that depend on the change, and how they are labelled |
| search_​runs.csv | round | Search round: number, name and the protocol version under which it ran |
| search_​runs.csv | window_​start | First publication date of the round's search window (ISO date) |
| search_​runs.csv | window_​end | Last publication date of the round's search window (ISO date) |
| search_​runs.csv | source | Bibliographic source |
| search_​runs.csv | searched | Whether the source was searched in this round (yes or no) |
| search_​runs.csv | executed_​on | Date on which the search was executed (ISO date) |
| search_​runs.csv | interface | Interface through which the source was queried |
| search_​runs.csv | date_​limit_​as_​executed | Date restriction as executed, in the syntax of the source |
| search_​runs.csv | other_​limits_​as_​executed | Other limits as executed (language, access, categories, validation) |
| search_​runs.csv | hits_​reported | Number of hits reported by the source's interface, where it reports one |
| search_​runs.csv | records_​fetched | Number of records downloaded |
| search_​runs.csv | records_​before_​validation | Records retrieved before the title/abstract validation applied to full-text-only interfaces (Springer Nature) or before deduplication within the source |
| search_​runs.csv | count_​in_​run_​log | Count recorded in the run log of the round |
| search_​runs.csv | records_​retained | Records retained from the source and passed to deduplication |
| search_​runs.csv | export_​file | Repository path of the export file of the run |
| fulltext_​exclusions.csv | reason | Main reason for exclusion at full text |
| fulltext_​exclusions.csv | reports | Number of reports excluded for this reason |
| charted_​models.csv | model | Model name as charted |
| charted_​models.csv | study | First author and year of the record, as in the article's reference list |
| charted_​models.csv | record_​id | Identifier of the included record in the review database |
| charted_​models.csv | paper_​title | Title of the record |
| charted_​models.csv | doi | DOI of the record |
| charted_​models.csv | year | Publication year |
| charted_​models.csv | year_​basis | Source of the publication year |
| charted_​models.csv | routes | Number of charted input routes of the model |
| charted_​models.csv | configurations | Number of charted configurations (training or use settings) of the model |
| charted_​models.csv | input_​carrier_​families | Families of the carriers through which inputs reach the model |
| charted_​models.csv | primary_​carrier_​subtype | Most frequent carrier subtype among the model's routes |
| charted_​models.csv | fusion_​topologies | How the inputs are fused with the language model, over all routes |
| charted_​models.csv | text_​roles | Roles of text on the model's routes |
| charted_​models.csv | lifecycle_​phases | Lifecycle phases covered by the routes (pretraining, fine-tuning, inference, evaluation) |
| charted_​models.csv | biological_​and_​text_​modalities | Modalities that enter the model |
| included_​works.csv | study | First author and year of each of the work's records, as in the article's reference list |
| included_​works.csv | proposed_​models | Models proposed by the work, as charted |
| included_​works.csv | record_​ids | Identifiers of the work's records in the review database (two for works with two reports) |
| included_​works.csv | paper_​titles | Titles of the work's records |
| included_​works.csv | dois | DOIs of the work's records |
| included_​works.csv | year | Publication year of the work's records |
| included_​works.csv | design_​culture | Design culture of the work: token-native, encoder-mediated, hybrid, language-conditioned or alignment-only |
| included_​works.csv | tests_​dependence_​on_​biological_​input | Whether the work reports any test of whether outputs depend on the biological input (removal, mismatch or shuffling, random input, a no-biology baseline, content perturbation, order or value ablation) |
| included_​works.csv | uses_​llm_​written_​text | Whether text written by an LLM was used for training or evaluation |
| included_​works.csv | language_​model_​frozen | Whether the language model is kept frozen in at least one setting |
| included_​works.csv | language_​model_​lora_​or_​adapter | Whether the language model is adapted by low-rank adaptation (LoRA) or adapters |
| included_​works.csv | language_​model_​full_​fine_​tuning | Whether the language model is fine-tuned in full |
| included_​works.csv | language_​model_​trained_​from_​scratch | Whether the language model is trained from scratch |
| included_​works.csv | rationale_​unchanged_​architecture | Token-native work justifies its own representation by needing no change to the language model's architecture |
| included_​works.csv | rationale_​language_​model_​knowledge | Token-native work justifies its own representation by the language model's prior knowledge of named entities |
| included_​works.csv | rationale_​concedes_​information_​loss | Token-native work concedes loss of quantitative or fine-grained information in its own representation |
| included_​works.csv | rationale_​criticises_​text_​rendering | Encoder-mediated work criticises text rendering for losing magnitudes, low-abundance genes or structure |
| included_​works.csv | cross_​culture_​comparison_​units | Number of the work's comparison units between arms of different cultures |
| included_​works.csv | opaque_​step_​share | Median share of the steps of the work's biological routes that are learned modules left unexpanded (empty if no biological route was decomposed) |
| included_​works.csv | unstated_​parameter_​slot_​share | Share of the parameter slots of the work's proposed and component models whose value is not stated in the paper (empty if there are no slots) |
| included_​works.csv | parameter_​slots | Number of parameter slots of the work's proposed and component models |
| motif_​library.csv | motif | Name of the motif |
| motif_​library.csv | family | Family of the motif: carrier formation, encoding or joining |
| motif_​library.csv | operations | Library operations of the motif, in order |
| motif_​library.csv | input_​role | Role of the inputs of the operations: biological input, text input, or joining both |
| motif_​library.csv | contiguous | Whether the operations must be adjacent (yes) or may have other operations between them (no) |
| motif_​library.csv | papers | Number of papers with the motif |
| motif_​library.csv | models | Number of models with the motif |
| motif_​library.csv | pilot_​papers | Number of the four author-curated pilot papers with the motif |
| motif_​library.csv | description | What the motif does |
| motif_​library.csv | unstated_​parameter_​shares | For each parameter of the motif's operations, the share of calls whose value the paper does not state |
| motif_​library.csv | example_​model | Model of the example |
| motif_​library.csv | example_​record_​id | Record of the example in the review database |
| motif_​library.csv | example_​route_​id | Charted route of the example |
| motif_​library.csv | example_​steps | Steps of the example: operation and the charted wording of the step |
| motif_​library.csv | example_​evidence | Verbatim quote from the paper supporting the example |
| gene_​budgets.csv | study | First author and year of the record, as in the article's reference list |
| gene_​budgets.csv | model_​and_​context | Model and the setting in which the budget applies |
| gene_​budgets.csv | record_​id | Record in the review database |
| gene_​budgets.csv | route | Kind of input route: text or embedding, and whose input it is |
| gene_​budgets.csv | genes_​kept | Number of genes or features kept per cell or object |
| gene_​budgets.csv | values_​kept | Whether measured values are kept, and how |
| gene_​budgets.csv | evidence | Verbatim quote from the paper |
| token_​budgets.csv | study | First author and year of the record, as in the article's reference list |
| token_​budgets.csv | model | Model and, where needed, the setting |
| token_​budgets.csv | record_​id | Record in the review database |
| token_​budgets.csv | unit | What is counted, in the paper's terms |
| token_​budgets.csv | number | Number per cell, profile or object |
| token_​budgets.csv | evidence | Verbatim quote from the paper |
| llm_​written_​text.csv | study | First author and year of the work's records, as in the article's reference list |
| llm_​written_​text.csv | proposed_​models | Models proposed by the work |
| llm_​written_​text.csv | record_​ids | Records of the work in the review database |
| llm_​written_​text.csv | design_​culture | Design culture of the work |
| llm_​written_​text.csv | year | Publication year |
| llm_​written_​text.csv | what_​was_​written | What the LLM wrote: training or evaluation content, instruction templates only, or unclear |
| llm_​written_​text.csv | generators | LLMs that wrote the text, as named in the paper |
| llm_​written_​text.csv | human_​check | Whether the paper reports a human check of the generated text |
| llm_​written_​text.csv | reasoning_​traces | Whether the generated text includes reasoning traces |
| llm_​written_​text.csv | llm_​text_​in_​evaluation | Whether LLM-written text is used in the evaluation |
| llm_​written_​text.csv | example | Verbatim quote from the paper |
| llm_​written_​text.csv | how_​found | How the use was identified |
| comparison_​units.csv | unit | Identifier of the comparison unit |
| comparison_​units.csv | study | First author and year of the work's records, as in the article's reference list |
| comparison_​units.csv | proposed_​models | Models proposed by the work that reports the comparison |
| comparison_​units.csv | record_​id | Record of the work in the review database |
| comparison_​units.csv | task_​family | Family of the task compared |
| comparison_​units.csv | task | Task and arms, as adjudicated |
| comparison_​units.csv | design | Design of the comparison: controlled ablation within one system, same backbone given the data as text, or different systems |
| comparison_​units.csv | arm_​a | Culture of the first arm (image rendering: DNA drawn as an image) |
| comparison_​units.csv | arm_​b | Culture of the second arm |
| comparison_​units.csv | proposed_​arm | Culture of the arm proposed by the authors |
| comparison_​units.csv | opponent_​arm | Culture of the opponent arm |
| comparison_​units.csv | opponent_​obtained_​as | How the opponent arm was obtained |
| comparison_​units.csv | winner | Culture of the winning arm, or mixed |
| comparison_​units.csv | proposed_​arm_​won | Whether the proposed arm won |
| comparison_​units.csv | token_​native_​arm_​content | What the token-native arm writes into the token stream |
| comparison_​units.csv | values_​reported | Values reported for the comparison, as quoted in the charting (empty if none in the text) |
| comparison_​units.csv | adjudication_​note | Note on a change made at adjudication |
| comparison_​units.csv | charting_​items | Charting items merged into the unit (run and item number) |
| route_​codebook.csv | record_​id | Record in the review database |
| route_​codebook.csv | model_​id | Identifier of the charted model |
| route_​codebook.csv | model | Model name as charted |
| route_​codebook.csv | configuration_​id | Identifier of the charted configuration |
| route_​codebook.csv | route_​id | Identifier of the charted route |
| route_​codebook.csv | route_​label | Label of the route, as charted |
| route_​codebook.csv | lifecycle_​phase | Lifecycle phase of the route |
| route_​codebook.csv | source_​modality | Modality of the route's source object |
| route_​codebook.csv | carrier_​family | Family of the carrier that reaches the model |
| route_​codebook.csv | carrier_​subtype | Subtype of the carrier |
| route_​codebook.csv | fusion_​topology | How the carrier is fused with the language model |
| route_​codebook.csv | text_​role | Role of text on the route |
| route_​codebook.csv | operation_​chain | Consensus library operations of the route, in order |
| route_​codebook.csv | carrier_​formation | Design axis 1, carrier formation: verbalised, symbolic, embedded, perceptual or text source |
| route_​codebook.csv | carrier_​formation_​rule | Rule that assigned the carrier formation |
| route_​codebook.csv | interface | Design axis 2, interface to the language model |
| route_​codebook.csv | interface_​rule | Rule that assigned the interface |
| route_​codebook.csv | value_​transformation | Design axis 3, transformation of measured values: verbatim, order only, discretised, learned compression, or not applicable |
| route_​codebook.csv | value_​transformation_​rule | Rule that assigned the value transformation |
| route_​codebook.csv | value_​transformation_​modifiers | Modifiers of the value transformation: subset, normalised |
| route_​codebook.csv | value_​transformation_​evidence_​steps | Identifiers of the decomposed steps on which the value transformation rests |
| route_​codebook.csv | text_​role_​axis | Design axis 4, text role: instruction, payload, supervision, context or none |
| route_​codebook.csv | transparency | Design axis 5, transparency: transparent, partial, opaque or no computation |
| route_​codebook.csv | opaque_​step_​share | Share of the route's steps that are learned modules left unexpanded |
| route_​codebook.csv | stated_​parameter_​share | Share of the route's parameter slots whose value the paper states |
| route_​codebook.csv | archetype | Carrier × interface archetype of the route |

<!-- end generated -->
