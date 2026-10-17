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

### Supplementary Note S3. Prompts of the screening agents

Title and abstract screening and full-text screening used three roles, each a prompt executed by the
same model (gpt-5.4-mini through the Codex command-line agent): a scope reviewer, an architecture
reviewer and an adjudicator. The adjudicator was called for records that the fixed rules could not
decide from the answers of the two first-pass reviewers (conflicting paper types, a criterion answered
as unclear, or a stated uncertainty), and every decision was derived from the criterion answers by fixed
rules. Each call screened a batch of records. The texts
below are the fixed part of the prompts as sent, recovered from the run logs and reproduced verbatim;
within a run, every batch received the same text. Each prompt continued, after the line "Records JSON:",
with a JSON array of the records of the batch: record identifier, title, abstract, DOI, year, venue and
sources; at full text also the selected full-text sections; for the adjudicator also the outputs of the
two first-pass reviewers.

<!-- generated: include:screening_prompts from analysis/codex_screening_run_artifacts_20260706/full_runs/codex_gpt54mini_all4027_20260706/role_logs.tar.gz, analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update155_20260706/role_logs.tar.gz, analysis/codex_screening_run_artifacts_20260706/update_runs/codex_gpt54mini_update431_20260610/role_logs.tar.gz, data/living_catalog_updates/update_2026-08-09/04_abstract_screening/role_logs, data/living_catalog_updates/update_2026-08-09/04_abstract_screening_manual_recall_xunzi_2026-08-11/role_logs, data/living_catalog_updates/update_2026-08-09/09_fulltext_screening/role_logs, data/living_catalog_updates/update_2026-08-09/09_fulltext_screening_manual_recall_xunzi_2026-08-11/role_logs, data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/role_logs -->

#### Title and abstract screening: scope reviewer

Used in: full re-screen of the cumulative records (run of 2026-07-06); June update (run of 2026-06-10); July update (run of 2026-07-06); August update (run of 2026-08-10); supplemental recall correction (run of 2026-08-11). Batches: 610. SHA-256 of the text: 07f371be7c120ebb96524ca0224a5cc6f73d79809b7f7e5cc33f955ff57e90da.

```
Reviewer role:
You are a strict scope reviewer for a systematic review of generative text-bio foundational models.

Review the title/abstract record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title/abstract record. Do not use outside knowledge. If the abstract does not clearly support a criterion, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- primary_exclusion_code
- uncertainty_reason
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC1_no_bio_modality | EC2_no_text_component | EC2_no_substantive_text_bio_bridge | none
- uncertainty_reason: paper_type_unclear | bio_modality_unclear | text_component_unclear | text_bio_bridge_unclear | mixed_signals | none

Criterion questions for this reviewer:
1. `paper_type`: Is this a primary candidate model paper rather than a review/editorial, benchmark/resource paper, or application wrapper around an existing model?
2. `bio_modality_present`: Is a biological data modality central to the candidate model?
3. `text_component_present`: Is there a substantive text/language component as part of the candidate model itself?
4. `text_bio_bridge_present`: Does the abstract support a substantive text-bio bridge rather than a loose wrapper or side-feature use?

Decision policy:
- Use a sensitivity-first title/abstract screening strategy.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the title/abstract.
- If the record is review/editorial, benchmark/resource, or application_wrapper, set `paper_type` accordingly and use the matching exclusion code.
- If a paper only uses embeddings, prompts, metadata descriptions, or outputs from an existing external LLM as side information for a downstream bio task, treat it as `application_wrapper`, not as a substantive text-bio model.
- Gene-token or other biological-token modeling counts as a text/language component only when the abstract clearly describes generative language-model-style token modeling as part of the candidate model.
- If the bridge or scope cannot be established from the abstract, use `unclear` rather than forcing `yes` or `no`.
- Use `none` when no exclusion code or uncertainty reason applies.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the title/abstract that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Title and abstract screening: architecture reviewer

Used in: full re-screen of the cumulative records (run of 2026-07-06); June update (run of 2026-06-10); July update (run of 2026-07-06); August update (run of 2026-08-10); supplemental recall correction (run of 2026-08-11). Batches: 610. SHA-256 of the text: 99f62c9415fe863e5f175e63f5dd07d0e9b737a33468ef1efca765622e722acb.

```
Reviewer role:
You are an architecture-focused reviewer assessing generative capability and foundation-model evidence for generative text-bio foundational models.

Review the title/abstract record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title/abstract record. Do not use outside knowledge. If the abstract does not clearly support a criterion, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC3_not_generative | EC4_no_foundation_model_evidence | none
- uncertainty_reason: paper_type_unclear | generative_status_unclear | foundation_model_evidence_unclear | mixed_signals | none

Criterion questions for this reviewer:
5. `generative_model_present`: Does the abstract describe a genuinely generative architecture rather than an encoder-only or purely predictive system?
6. `foundation_model_evidence`: Does the abstract provide evidence that the candidate model has foundation-model-like characteristics such as broad pretraining, transferable representations, or broad applicability?

Decision policy:
- Use a sensitivity-first title/abstract screening strategy.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the title/abstract.
- Predictive profile/score systems, downstream classifiers, and retrieval-only systems are not generative unless the abstract explicitly states decoder, autoregressive, sequence-to-sequence, diffusion, or another clearly generative mechanism.
- Encoder-only architectures are not positive evidence for inclusion.
- If the abstract clearly shows that the work is only a wrapper around an existing model, set `paper_type=application_wrapper`.
- If the abstract is too underspecified to establish generative or FM evidence, use `unclear` rather than forcing `yes`.
- Use `none` when no exclusion code or uncertainty reason applies.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the title/abstract that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Title and abstract screening: adjudicator

Used in: full re-screen of the cumulative records (run of 2026-07-06); June update (run of 2026-06-10); July update (run of 2026-07-06); August update (run of 2026-08-10); supplemental recall correction (run of 2026-08-11). Batches: 279. SHA-256 of the text: f54364b5ca9f28aa3ed82709941bf9b6ecdb37de8e37401b65a1aae4a6b43b6e.

```
Reviewer role:
You are a senior adjudicator who resolves criterion-level conflicts conservatively for a systematic review of generative text-bio foundational models.

Review the title/abstract record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title/abstract record plus the structured outputs from the first-pass reviewers. Do not use outside knowledge. If a decisive criterion still cannot be resolved from the record, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC1_no_bio_modality | EC2_no_text_component | EC2_no_substantive_text_bio_bridge | EC3_not_generative | EC4_no_foundation_model_evidence | none
- uncertainty_reason: paper_type_unclear | bio_modality_unclear | text_component_unclear | text_bio_bridge_unclear | generative_status_unclear | foundation_model_evidence_unclear | mixed_signals | none

Adjudication task:
- Resolve criterion-level disagreement between the scope and architecture reviewers.
- Resolve each criterion independently from the abstract and reviewer outputs.
- Do not simply choose one reviewer wholesale.

Decision policy:
- Use the most conservative interpretation consistent with the title/abstract evidence.
- Preserve clear review/editorial, benchmark/resource, and application-wrapper exclusions.
- If the abstract only supports wrapper-style use of an existing LLM or language model, set `paper_type=application_wrapper` and `text_bio_bridge_present=no`.
- If a decisive criterion still cannot be resolved, keep that criterion as `unclear`.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the title/abstract and, when relevant, the reviewer conflict.
- Use `none` when no exclusion code or uncertainty reason applies.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the title/abstract that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Full-text screening: scope reviewer, version 1

Used in: rounds 1–4 (run of 2026-07-10). Batches: 221. SHA-256 of the text: 525bca8d2abbf8ecc0f0463419e3e56dcdedb3ed9bbda07bc60be855739acd04.

```
Reviewer role:
You are a strict scope reviewer for a systematic review of generative text-bio foundational models.

Review the title/abstract/full-text-section record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title, abstract, and selected full-text sections. Do not use outside knowledge. If the provided evidence does not clearly support a criterion, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- primary_exclusion_code
- uncertainty_reason
- evidence_for_text_component
- evidence_for_text_bio_bridge
- evidence_for_generative_model
- boundary_case
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC1_no_bio_modality | EC2_no_text_component | EC2_no_substantive_text_bio_bridge | none
- uncertainty_reason: paper_type_unclear | bio_modality_unclear | text_component_unclear | text_bio_bridge_unclear | mixed_signals | none
- evidence_for_text_component: short evidence phrase from the provided title, abstract, and selected full-text sections, or none
- evidence_for_text_bio_bridge: short evidence phrase from the provided title, abstract, and selected full-text sections, or none
- evidence_for_generative_model: not_assessed
- boundary_case: clear_include | wrapper_boundary | text_component_boundary | biological_token_only_boundary | generative_boundary | thin_abstract_boundary | clear_exclude | none

Criterion questions for this reviewer:
1. `paper_type`: Is this a primary candidate model paper rather than a review/editorial, benchmark/resource paper, or application wrapper around an existing model?
2. `bio_modality_present`: Is a biological data modality central to the candidate model?
3. `text_component_present`: Is there a substantive text/language component as part of the candidate model itself?
4. `text_bio_bridge_present`: Does the provided evidence support a substantive text-bio bridge rather than a loose wrapper or side-feature use?

Decision policy:
- Use a sensitivity-first full-text-section screening strategy.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the provided title, abstract, and selected full-text sections.
- Evidence fields must be short and concrete. Quote or paraphrase only evidence present in the provided title, abstract, and selected full-text sections. If evidence is absent, use `none`.
- If the record is review/editorial, benchmark/resource, or application_wrapper, set `paper_type` accordingly and use the matching exclusion code.
- If a paper only uses embeddings, prompts, metadata descriptions, or outputs from an existing external LLM as side information for a downstream predictive bio task, treat it as `application_wrapper`, not as a substantive text-bio model.
- Using an existing external LLM only to generate embeddings, labels, prompts, explanations, or text-derived features for a downstream classifier, risk model, annotation system, or predictor is `application_wrapper`, not a primary text-bio model.
- Biological-token modeling alone does not count as a text/language component. Terms such as gene tokens, cell sentences, omics language, BERT-style biological tokenization, or language-model-style pretraining over biological sequences are not sufficient unless the provided evidence clearly describes natural-language text, text descriptions, captions, prompts, documents, or explicit text-bio alignment as part of the candidate model.
- Metadata counts as a text component only when the provided evidence clearly describes natural-language metadata, reports, captions, prompts, documents, or text descriptions. Structured labels, categorical metadata, gene names, phenotypes, ontology terms, or cell-type labels alone are not enough.
- A new method that merely attaches frozen/external LLM embeddings, prompts, labels, explanations, prototypes, or text-derived features to a downstream biological predictor is `application_wrapper` unless the provided evidence presents the candidate model as a multimodal text-bio model, a bio-to-text/text-to-bio generator, or a generative model conditioned on text-derived evidence.
- A paper that trains or fine-tunes a model to map biological data to natural-language descriptions, or natural-language prompts/descriptions to biological outputs, can satisfy `text_component_present=yes` and `text_bio_bridge_present=yes` if the provided evidence makes that mapping central.
- A paper that presents a new multimodal model or framework for generating natural-language descriptions from biological data, or generating biological outputs conditioned on natural-language/text-derived evidence, should not be labeled `application_wrapper` solely because it uses a pretrained LLM component.
- Natural-language chat, question answering, dialogue, natural-language interfaces, or generated natural-language descriptions for biological data analysis are sufficient evidence for `text_bio_bridge_present=yes` when they are central to the candidate model.
- Natural-language-derived priors, text summaries, report summaries, text descriptions, or text embeddings count as a text component and text-bio bridge when they condition, guide, or are cross-attended by the candidate generative model itself. They are not enough only when they are detached side features for a downstream classifier or predictor.
- Use `boundary_case=thin_abstract_boundary` only when missing provided title, abstract, and selected full-text sections evidence prevents a confident yes/no on at least one decisive criterion. If all decisive criteria are clearly supported, use `clear_include` or another more specific boundary label instead.
- Do not set `paper_type=unclear` solely because the provided evidence is short or truncated when it explicitly presents a new named model/framework and does not describe the work as a review, benchmark, resource, or wrapper.
- If decisive eligibility depends only on ambiguous phrases such as metadata, experimental metadata, pretrained foundation-model embeddings, or a title-only "LLM" claim without clear natural-language input/output or text conditioning in the provided evidence, use `unclear` for the affected criterion rather than forcing `yes` or `no`.
- If the bridge or scope cannot be established from the provided evidence, use `unclear` rather than forcing `yes` or `no`.
- Use `none` when no exclusion code or uncertainty reason applies.

Boundary examples:
- "uses GPT embeddings / LLM-derived gene embeddings / task-specific text prototypes for classification or prediction" -> `application_wrapper`, unless the abstract presents a central multimodal text-bio model or generator.
- "gene tokens", "cell sentences", "DNA language", or "omics language model" with no natural-language text, prompt, caption, report, document, or explicit text-bio alignment -> `text_component_present=no`, `text_bio_bridge_present=no`.
- "generates single-cell descriptions from RNA-seq", "conditions biological generation on natural-language prompts", or "aligns transcriptomes/histology/gene expression with language representations" -> likely text component and bridge if central to the candidate model.
- "chat with cells", "single-cell analysis with natural language", "biological question answering", or "generates cell descriptions from RNA-seq" -> text component and text-bio bridge can be yes when central to the candidate model.
- "diffusion/generative model conditioned on text summaries, text-derived priors, or natural-language descriptions" -> text component and text-bio bridge can be yes when the conditioning is part of the candidate model.
- "metadata" or "foundation-model embeddings" without clear natural-language descriptions or text conditioning -> `unclear`, not automatic yes or no.
- "clinical risk prediction using medical history records" -> `text_component_present=unclear` unless records are clearly natural-language text; it is not enough that the model is called a language model.


Full-text evidence mode:
- Each record may include `selected_full_text_sections` and `section_evidence` extracted from Docling markdown.
- Treat these fields as part of the provided record, not as outside knowledge.
- Use the selected full-text sections when they clarify criteria.
- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.
- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Full-text screening: scope reviewer, version 2

Used in: August update (run of 2026-08-11); supplemental recall correction (run of 2026-08-11). Batches: 3. SHA-256 of the text: 0fab79a4de2912c8dee54756108f9406d9b8fa9376aadf08836a9a1374cd65e0.

```
Reviewer role:
You are a strict scope reviewer for a systematic review of generative text-bio foundational models.

Review the title/abstract/full-text-section record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title, abstract, and selected full-text sections. Do not use outside knowledge. If the provided evidence does not clearly support a criterion, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- primary_exclusion_code
- uncertainty_reason
- evidence_for_text_component
- evidence_for_text_bio_bridge
- evidence_for_generative_model
- boundary_case
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC1_no_bio_modality | EC2_no_text_component | EC2_no_substantive_text_bio_bridge | none
- uncertainty_reason: paper_type_unclear | bio_modality_unclear | text_component_unclear | text_bio_bridge_unclear | mixed_signals | none
- evidence_for_text_component: short evidence phrase from the provided title, abstract, and selected full-text sections, or none
- evidence_for_text_bio_bridge: short evidence phrase from the provided title, abstract, and selected full-text sections, or none
- evidence_for_generative_model: not_assessed
- boundary_case: clear_include | wrapper_boundary | text_component_boundary | biological_token_only_boundary | generative_boundary | thin_abstract_boundary | clear_exclude | none

Criterion questions for this reviewer:
1. `paper_type`: Is this a primary candidate model paper rather than a review/editorial, benchmark/resource paper, or application wrapper around an existing model?
2. `bio_modality_present`: Is a biological data modality central to the candidate model?
3. `text_component_present`: Is there a substantive text/language component as part of the candidate model itself?
4. `text_bio_bridge_present`: Does the provided evidence support a substantive text-bio bridge rather than a loose wrapper or side-feature use?

Decision policy:
- Use a sensitivity-first full-text-section screening strategy.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the provided title, abstract, and selected full-text sections.
- Evidence fields must be short and concrete. Quote or paraphrase only evidence present in the provided title, abstract, and selected full-text sections. If evidence is absent, use `none`.
- If the record is review/editorial, benchmark/resource, or application_wrapper, set `paper_type` accordingly and use the matching exclusion code.
- If a paper only uses embeddings, prompts, metadata descriptions, or outputs from an existing external LLM as side information for a downstream predictive bio task, treat it as `application_wrapper`, not as a substantive text-bio model.
- Using an existing external LLM only to generate embeddings, labels, prompts, explanations, or text-derived features for a downstream classifier, risk model, annotation system, or predictor is `application_wrapper`, not a primary text-bio model.
- Biological-token modeling alone does not count as a text/language component. Terms such as gene tokens, cell sentences, omics language, BERT-style biological tokenization, or language-model-style pretraining over biological sequences are not sufficient unless the provided evidence clearly describes natural-language text, text descriptions, captions, prompts, documents, or explicit text-bio alignment as part of the candidate model.
- Metadata counts as a text component only when the provided evidence clearly describes natural-language metadata, reports, captions, prompts, documents, or text descriptions. Structured labels, categorical metadata, gene names, phenotypes, ontology terms, or cell-type labels alone are not enough.
- A new method that merely attaches frozen/external LLM embeddings, prompts, labels, explanations, prototypes, or text-derived features to a downstream biological predictor is `application_wrapper` unless the provided evidence presents the candidate model as a multimodal text-bio model, a bio-to-text/text-to-bio generator, or a generative model conditioned on text-derived evidence.
- A paper that trains or fine-tunes a model to map biological data to natural-language descriptions, or natural-language prompts/descriptions to biological outputs, can satisfy `text_component_present=yes` and `text_bio_bridge_present=yes` if the provided evidence makes that mapping central.
- A paper that presents a new multimodal model or framework for generating natural-language descriptions from biological data, or generating biological outputs conditioned on natural-language/text-derived evidence, should not be labeled `application_wrapper` solely because it uses a pretrained LLM component.
- Natural-language chat, question answering, dialogue, natural-language interfaces, or generated natural-language descriptions for biological data analysis are sufficient evidence for `text_bio_bridge_present=yes` when they are central to the candidate model.
- Natural-language-derived priors, text summaries, report summaries, text descriptions, or text embeddings count as a text component and text-bio bridge when they condition, guide, or are cross-attended by the candidate generative model itself. They are not enough only when they are detached side features for a downstream classifier or predictor.
- Use `boundary_case=thin_abstract_boundary` only when missing provided title, abstract, and selected full-text sections evidence prevents a confident yes/no on at least one decisive criterion. If all decisive criteria are clearly supported, use `clear_include` or another more specific boundary label instead.
- Do not set `paper_type=unclear` solely because the provided evidence is short or truncated when it explicitly presents a new named model/framework and does not describe the work as a review, benchmark, resource, or wrapper.
- If decisive eligibility depends only on ambiguous phrases such as metadata, experimental metadata, pretrained foundation-model embeddings, or a title-only "LLM" claim without clear natural-language input/output or text conditioning in the provided evidence, use `unclear` for the affected criterion rather than forcing `yes` or `no`.
- If the bridge or scope cannot be established from the provided evidence, use `unclear` rather than forcing `yes` or `no`.
- Use `none` when no exclusion code or uncertainty reason applies.

Boundary examples:
- "uses GPT embeddings / LLM-derived gene embeddings / task-specific text prototypes for classification or prediction" -> `application_wrapper`, unless the abstract presents a central multimodal text-bio model or generator.
- "gene tokens", "cell sentences", "DNA language", or "omics language model" with no natural-language text, prompt, caption, report, document, or explicit text-bio alignment -> `text_component_present=no`, `text_bio_bridge_present=no`.
- "generates single-cell descriptions from RNA-seq", "conditions biological generation on natural-language prompts", or "aligns transcriptomes/histology/gene expression with language representations" -> likely text component and bridge if central to the candidate model.
- "chat with cells", "single-cell analysis with natural language", "biological question answering", or "generates cell descriptions from RNA-seq" -> text component and text-bio bridge can be yes when central to the candidate model.
- "diffusion/generative model conditioned on text summaries, text-derived priors, or natural-language descriptions" -> text component and text-bio bridge can be yes when the conditioning is part of the candidate model.
- "metadata" or "foundation-model embeddings" without clear natural-language descriptions or text conditioning -> `unclear`, not automatic yes or no.
- "clinical risk prediction using medical history records" -> `text_component_present=unclear` unless records are clearly natural-language text; it is not enough that the model is called a language model.


Full-text evidence mode:
- Each record includes complete `selected_full_text_sections` extracted from Docling markdown.
- Treat the title, abstract, and selected full-text sections as the provided record; do not use outside knowledge.
- Use the selected full-text sections when they clarify criteria.
- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.
- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Full-text screening: architecture reviewer, version 1

Used in: rounds 1–4 (run of 2026-07-10). Batches: 221. SHA-256 of the text: 51b3d3c952e0158706b502b7207d583c1e489d5f40d6f36848b4af9642e4ed2a.

```
Reviewer role:
You are an architecture-focused reviewer assessing generative capability and foundation-model evidence for generative text-bio foundational models.

Review the title/abstract/full-text-section record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title, abstract, and selected full-text sections. Do not use outside knowledge. If the provided evidence does not clearly support a criterion, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- evidence_for_text_component
- evidence_for_text_bio_bridge
- evidence_for_generative_model
- boundary_case
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC3_not_generative | none
- uncertainty_reason: paper_type_unclear | generative_status_unclear | mixed_signals | none
- evidence_for_text_component: not_assessed
- evidence_for_text_bio_bridge: not_assessed
- evidence_for_generative_model: short evidence phrase from the provided title, abstract, and selected full-text sections, or none
- boundary_case: clear_include | wrapper_boundary | text_component_boundary | biological_token_only_boundary | generative_boundary | thin_abstract_boundary | clear_exclude | none

Criterion questions for this reviewer:
5. `generative_model_present`: Does the provided evidence describe a genuinely generative architecture rather than an encoder-only or purely predictive system?
6. `foundation_model_evidence`: Does the provided evidence provide evidence that the candidate model has foundation-model-like characteristics such as broad pretraining, transferable representations, or broad applicability?

Decision policy:
- Use a sensitivity-first full-text-section screening strategy.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the provided title, abstract, and selected full-text sections.
- Evidence fields must be short and concrete. Quote or paraphrase only evidence present in the provided title, abstract, and selected full-text sections. If evidence is absent, use `none`.
- Predictive profile/score systems, downstream classifiers, and retrieval-only systems are not generative unless the provided evidence explicitly states decoder, autoregressive, sequence-to-sequence, diffusion, or another clearly generative mechanism.
- Encoder-only architectures are not positive evidence for inclusion.
- Treat `foundation_model_evidence` as descriptive metadata, not as an exclusion criterion.
- If the provided evidence clearly shows that the work is only a wrapper around an existing model, set `paper_type=application_wrapper`.
- Fine-tuning or using an existing generative model for a narrow downstream application is not enough to make the paper a primary generative text-bio foundational model if the candidate contribution is only an application wrapper.
- A model that predicts class, survival, risk, expression value, subtype, annotation, or ranking is `generative_model_present=no` unless the provided evidence explicitly describes a generative mechanism such as decoder, autoregressive generation, sequence-to-sequence generation, diffusion, VAE/GAN generation, or generation of biological/text outputs.
- Masked language modeling, encoder-only pretraining, representation learning, contrastive learning, and retrieval are `generative_model_present=unclear` or `no` unless the provided evidence clearly states generation.
- The phrase "large language model" is not by itself sufficient evidence that the proposed candidate model is generative; identify the generative task or mechanism in `evidence_for_generative_model`.
- If the provided evidence is too underspecified to establish generative or FM evidence, use `unclear` rather than forcing `yes`.
- Use `none` when no exclusion code or uncertainty reason applies.

Boundary examples:
- "survival prediction", "risk prediction", "cell type classification", "variant classification", or "annotation" without explicit generation -> `generative_model_present=no`.
- "autoregressive", "decoder", "diffusion", "VAE/GAN", "sequence-to-sequence", "generates descriptions", "generates cells/sequences/images" -> positive generative evidence if central.
- "built from ChatGPT", "uses Qwen/LLM embeddings", or "uses a frozen LLM" -> foundation/generative evidence for the external model only; do not infer that the paper's candidate model is a primary generative model unless the provided evidence says so.


Full-text evidence mode:
- Each record may include `selected_full_text_sections` and `section_evidence` extracted from Docling markdown.
- Treat these fields as part of the provided record, not as outside knowledge.
- Use the selected full-text sections when they clarify criteria.
- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.
- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Full-text screening: architecture reviewer, version 2

Used in: August update (run of 2026-08-11); supplemental recall correction (run of 2026-08-11). Batches: 3. SHA-256 of the text: 2e1a8f98025aedae6e2e77bc24a7556401e737b0f0f2a29efb1d0796c12fb440.

```
Reviewer role:
You are an architecture-focused reviewer assessing generative capability and foundation-model evidence for generative text-bio foundational models.

Review the title/abstract/full-text-section record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title, abstract, and selected full-text sections. Do not use outside knowledge. If the provided evidence does not clearly support a criterion, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- evidence_for_text_component
- evidence_for_text_bio_bridge
- evidence_for_generative_model
- boundary_case
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC3_not_generative | none
- uncertainty_reason: paper_type_unclear | generative_status_unclear | mixed_signals | none
- evidence_for_text_component: not_assessed
- evidence_for_text_bio_bridge: not_assessed
- evidence_for_generative_model: short evidence phrase from the provided title, abstract, and selected full-text sections, or none
- boundary_case: clear_include | wrapper_boundary | text_component_boundary | biological_token_only_boundary | generative_boundary | thin_abstract_boundary | clear_exclude | none

Criterion questions for this reviewer:
5. `generative_model_present`: Does the provided evidence describe a genuinely generative architecture rather than an encoder-only or purely predictive system?
6. `foundation_model_evidence`: Does the provided evidence provide evidence that the candidate model has foundation-model-like characteristics such as broad pretraining, transferable representations, or broad applicability?

Decision policy:
- Use a sensitivity-first full-text-section screening strategy.
- Do not invent a final include/exclude label. Answer only the criterion fields requested for this reviewer.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the provided title, abstract, and selected full-text sections.
- Evidence fields must be short and concrete. Quote or paraphrase only evidence present in the provided title, abstract, and selected full-text sections. If evidence is absent, use `none`.
- Predictive profile/score systems, downstream classifiers, and retrieval-only systems are not generative unless the provided evidence explicitly states decoder, autoregressive, sequence-to-sequence, diffusion, or another clearly generative mechanism.
- Encoder-only architectures are not positive evidence for inclusion.
- Treat `foundation_model_evidence` as descriptive metadata, not as an exclusion criterion.
- If the provided evidence clearly shows that the work is only a wrapper around an existing model, set `paper_type=application_wrapper`.
- Fine-tuning or using an existing generative model for a narrow downstream application is not enough to make the paper a primary generative text-bio foundational model if the candidate contribution is only an application wrapper.
- A model that predicts class, survival, risk, expression value, subtype, annotation, or ranking is `generative_model_present=no` unless the provided evidence explicitly describes a generative mechanism such as decoder, autoregressive generation, sequence-to-sequence generation, diffusion, VAE/GAN generation, or generation of biological/text outputs.
- Masked language modeling, encoder-only pretraining, representation learning, contrastive learning, and retrieval are `generative_model_present=unclear` or `no` unless the provided evidence clearly states generation.
- The phrase "large language model" is not by itself sufficient evidence that the proposed candidate model is generative; identify the generative task or mechanism in `evidence_for_generative_model`.
- If the provided evidence is too underspecified to establish generative or FM evidence, use `unclear` rather than forcing `yes`.
- Use `none` when no exclusion code or uncertainty reason applies.

Boundary examples:
- "survival prediction", "risk prediction", "cell type classification", "variant classification", or "annotation" without explicit generation -> `generative_model_present=no`.
- "autoregressive", "decoder", "diffusion", "VAE/GAN", "sequence-to-sequence", "generates descriptions", "generates cells/sequences/images" -> positive generative evidence if central.
- "built from ChatGPT", "uses Qwen/LLM embeddings", or "uses a frozen LLM" -> foundation/generative evidence for the external model only; do not infer that the paper's candidate model is a primary generative model unless the provided evidence says so.


Full-text evidence mode:
- Each record includes complete `selected_full_text_sections` extracted from Docling markdown.
- Treat the title, abstract, and selected full-text sections as the provided record; do not use outside knowledge.
- Use the selected full-text sections when they clarify criteria.
- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.
- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Full-text screening: adjudicator, version 1

Used in: rounds 1–4 (run of 2026-07-10). Batches: 67. SHA-256 of the text: fc49528ed8d5e2b617bafee284c4c9c9c5ebee9895e9717b1707712bd51b3c4c.

```
Reviewer role:
You are a senior adjudicator who resolves criterion-level conflicts conservatively for a systematic review of generative text-bio foundational models.

Review the title/abstract/full-text-section record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title, abstract, selected full-text sections, and structured outputs from the first-pass reviewers. Do not use outside knowledge. If a decisive criterion still cannot be resolved from the record, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- evidence_for_text_component
- evidence_for_text_bio_bridge
- evidence_for_generative_model
- boundary_case
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC1_no_bio_modality | EC2_no_text_component | EC2_no_substantive_text_bio_bridge | EC3_not_generative | none
- uncertainty_reason: paper_type_unclear | bio_modality_unclear | text_component_unclear | text_bio_bridge_unclear | generative_status_unclear | mixed_signals | none
- evidence_for_text_component: short evidence phrase from the provided title, abstract, selected full-text sections, or reviewer outputs, or none
- evidence_for_text_bio_bridge: short evidence phrase from the provided title, abstract, selected full-text sections, or reviewer outputs, or none
- evidence_for_generative_model: short evidence phrase from the provided title, abstract, selected full-text sections, or reviewer outputs, or none
- boundary_case: clear_include | wrapper_boundary | text_component_boundary | biological_token_only_boundary | generative_boundary | thin_abstract_boundary | clear_exclude | none

Adjudication task:
- Resolve criterion-level disagreement between the scope and architecture reviewers.
- Resolve each criterion independently from the provided evidence and reviewer outputs.
- Do not simply choose one reviewer wholesale.

Decision policy:
- Use the most conservative interpretation consistent with the provided title, abstract, and selected full-text sections evidence.
- Preserve clear review/editorial, benchmark/resource, and application-wrapper exclusions.
- Treat `foundation_model_evidence` as descriptive metadata, not as an exclusion criterion.
- If the provided evidence only supports wrapper-style use of an existing LLM or language model, set `paper_type=application_wrapper` and `text_bio_bridge_present=no`.
- Evidence fields must identify the concrete phrase or claim that resolves the criterion. If no evidence resolves it, use `none` and keep the criterion `unclear`, `no`, or wrapper as appropriate.
- Biological-token modeling alone does not count as a text/language component. Terms such as gene tokens, cell sentences, omics language, BERT-style biological tokenization, or language-model-style pretraining over biological sequences are not sufficient unless the provided evidence clearly describes natural-language text, text descriptions, captions, prompts, documents, or explicit text-bio alignment as part of the candidate model.
- Metadata counts as text only when the provided evidence clearly describes natural-language metadata, reports, captions, prompts, documents, or text descriptions. Structured labels, categorical metadata, gene names, phenotypes, ontology terms, or cell-type labels alone are not enough.
- A method that uses frozen/external LLM embeddings, prompts, labels, explanations, prototypes, or text-derived features only for a downstream classifier, annotation system, risk model, or predictor is `application_wrapper` unless the provided evidence presents a central multimodal text-bio model or generator.
- Do not label a paper `application_wrapper` solely because it uses a pretrained LLM component when the provided evidence presents a new multimodal model or framework for generating natural-language descriptions from biological data, or for generating biological outputs conditioned on natural-language/text-derived evidence.
- Natural-language chat, question answering, dialogue, natural-language interfaces, or generated natural-language descriptions for biological data analysis are sufficient evidence for `text_bio_bridge_present=yes` when they are central to the candidate model.
- Natural-language-derived priors, text summaries, report summaries, text descriptions, or text embeddings count as a text component and text-bio bridge when they condition, guide, or are cross-attended by the candidate generative model itself. They are not enough only when they are detached side features for a downstream classifier or predictor.
- Use `boundary_case=thin_abstract_boundary` only when missing provided title, abstract, and selected full-text sections evidence prevents a confident yes/no on at least one decisive criterion. If all decisive criteria are clearly supported, use `clear_include` or another more specific boundary label instead.
- Do not set `paper_type=unclear` solely because the provided evidence is short or truncated when it explicitly presents a new named model/framework and does not describe the work as a review, benchmark, resource, or wrapper.
- If decisive eligibility depends only on ambiguous phrases such as metadata, experimental metadata, pretrained foundation-model embeddings, or a title-only "LLM" claim without clear natural-language input/output or text conditioning in the provided evidence, use `unclear` for the affected criterion rather than forcing `yes` or `no`.
- Predictive profile/score systems, downstream classifiers, and retrieval-only systems are not generative unless the provided evidence explicitly states decoder, autoregressive, sequence-to-sequence, diffusion, VAE/GAN, or another clearly generative mechanism.
- If reviewers disagree because one inferred missing details from the phrase "language model", "foundation model", "ChatGPT", or "LLM", do not use that inference alone to include. Require explicit abstract evidence for the disputed criterion.
- If a decisive criterion still cannot be resolved, keep that criterion as `unclear`.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the provided title, abstract, and selected full-text sections and, when relevant, the reviewer conflict.
- Use `none` when no exclusion code or uncertainty reason applies.

Boundary examples:
- LLM-derived gene embeddings, prompt-generated labels, or frozen LLM prototypes used by a downstream classifier -> `application_wrapper` unless the abstract presents a central multimodal text-bio model or generator.
- Gene-token/cell-sentence/DNA-language modeling with no natural-language text or explicit text-bio alignment -> `text_component_present=no` and `text_bio_bridge_present=no`.
- Survival/risk/classification/annotation tasks without explicit generation -> `generative_model_present=no`.
- Biological data to natural-language descriptions, natural-language prompts to biological outputs, or explicit alignment of biological modalities with language representations -> can support `yes` when central and primary.
- Chat/dialogue/question-answering about biological data, or single-cell analysis with natural language -> can support text component and text-bio bridge when central and primary.
- Diffusion/generative model conditioned on text summaries, text-derived priors, or natural-language descriptions -> can support text component and text-bio bridge when conditioning is part of the candidate model.
- Metadata or foundation-model embeddings without clear natural-language descriptions or text conditioning -> `unclear`, not automatic yes or no.
- Thin or truncated abstract that hints at a candidate model but does not resolve text component, bridge, paper type, or generation -> choose `UNCERTAIN`, not `INCLUDE`.


Full-text evidence mode:
- Each record may include `selected_full_text_sections` and `section_evidence` extracted from Docling markdown.
- Treat these fields as part of the provided record, not as outside knowledge.
- Use the selected full-text sections when they clarify criteria.
- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.
- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

#### Full-text screening: adjudicator, version 2

Used in: August update (run of 2026-08-11). Batches: 1. SHA-256 of the text: 549783c240c9369a8ecffae57ec48c7db4f70360cd4cf845e62b76962ed427a2.

```
Reviewer role:
You are a senior adjudicator who resolves criterion-level conflicts conservatively for a systematic review of generative text-bio foundational models.

Review the title/abstract/full-text-section record below for systematic-review screening of generative text-bio foundational models.

Use only the evidence in the provided title, abstract, selected full-text sections, and structured outputs from the first-pass reviewers. Do not use outside knowledge. If a decisive criterion still cannot be resolved from the record, answer `unclear`.

Return exactly one JSON object with these keys:
- paper_type
- bio_modality_present
- text_component_present
- text_bio_bridge_present
- generative_model_present
- foundation_model_evidence
- primary_exclusion_code
- uncertainty_reason
- evidence_for_text_component
- evidence_for_text_bio_bridge
- evidence_for_generative_model
- boundary_case
- decision_rationale

Allowed values:
- paper_type: primary_model_paper | review_editorial | benchmark_resource | application_wrapper | unclear
- bio_modality_present: yes | no | unclear
- text_component_present: yes | no | unclear
- text_bio_bridge_present: yes | no | unclear
- generative_model_present: yes | no | unclear
- foundation_model_evidence: yes | no | unclear
- primary_exclusion_code: review_editorial | benchmark_resource | application_wrapper | EC1_no_bio_modality | EC2_no_text_component | EC2_no_substantive_text_bio_bridge | EC3_not_generative | none
- uncertainty_reason: paper_type_unclear | bio_modality_unclear | text_component_unclear | text_bio_bridge_unclear | generative_status_unclear | mixed_signals | none
- evidence_for_text_component: short evidence phrase from the provided title, abstract, selected full-text sections, or reviewer outputs, or none
- evidence_for_text_bio_bridge: short evidence phrase from the provided title, abstract, selected full-text sections, or reviewer outputs, or none
- evidence_for_generative_model: short evidence phrase from the provided title, abstract, selected full-text sections, or reviewer outputs, or none
- boundary_case: clear_include | wrapper_boundary | text_component_boundary | biological_token_only_boundary | generative_boundary | thin_abstract_boundary | clear_exclude | none

Adjudication task:
- Resolve criterion-level disagreement between the scope and architecture reviewers.
- Resolve each criterion independently from the provided evidence and reviewer outputs.
- Do not simply choose one reviewer wholesale.

Decision policy:
- Use the most conservative interpretation consistent with the provided title, abstract, and selected full-text sections evidence.
- Preserve clear review/editorial, benchmark/resource, and application-wrapper exclusions.
- Treat `foundation_model_evidence` as descriptive metadata, not as an exclusion criterion.
- If the provided evidence only supports wrapper-style use of an existing LLM or language model, set `paper_type=application_wrapper` and `text_bio_bridge_present=no`.
- Evidence fields must identify the concrete phrase or claim that resolves the criterion. If no evidence resolves it, use `none` and keep the criterion `unclear`, `no`, or wrapper as appropriate.
- Biological-token modeling alone does not count as a text/language component. Terms such as gene tokens, cell sentences, omics language, BERT-style biological tokenization, or language-model-style pretraining over biological sequences are not sufficient unless the provided evidence clearly describes natural-language text, text descriptions, captions, prompts, documents, or explicit text-bio alignment as part of the candidate model.
- Metadata counts as text only when the provided evidence clearly describes natural-language metadata, reports, captions, prompts, documents, or text descriptions. Structured labels, categorical metadata, gene names, phenotypes, ontology terms, or cell-type labels alone are not enough.
- A method that uses frozen/external LLM embeddings, prompts, labels, explanations, prototypes, or text-derived features only for a downstream classifier, annotation system, risk model, or predictor is `application_wrapper` unless the provided evidence presents a central multimodal text-bio model or generator.
- Do not label a paper `application_wrapper` solely because it uses a pretrained LLM component when the provided evidence presents a new multimodal model or framework for generating natural-language descriptions from biological data, or for generating biological outputs conditioned on natural-language/text-derived evidence.
- Natural-language chat, question answering, dialogue, natural-language interfaces, or generated natural-language descriptions for biological data analysis are sufficient evidence for `text_bio_bridge_present=yes` when they are central to the candidate model.
- Natural-language-derived priors, text summaries, report summaries, text descriptions, or text embeddings count as a text component and text-bio bridge when they condition, guide, or are cross-attended by the candidate generative model itself. They are not enough only when they are detached side features for a downstream classifier or predictor.
- Use `boundary_case=thin_abstract_boundary` only when missing provided title, abstract, and selected full-text sections evidence prevents a confident yes/no on at least one decisive criterion. If all decisive criteria are clearly supported, use `clear_include` or another more specific boundary label instead.
- Do not set `paper_type=unclear` solely because the provided evidence is short or truncated when it explicitly presents a new named model/framework and does not describe the work as a review, benchmark, resource, or wrapper.
- If decisive eligibility depends only on ambiguous phrases such as metadata, experimental metadata, pretrained foundation-model embeddings, or a title-only "LLM" claim without clear natural-language input/output or text conditioning in the provided evidence, use `unclear` for the affected criterion rather than forcing `yes` or `no`.
- Predictive profile/score systems, downstream classifiers, and retrieval-only systems are not generative unless the provided evidence explicitly states decoder, autoregressive, sequence-to-sequence, diffusion, VAE/GAN, or another clearly generative mechanism.
- If reviewers disagree because one inferred missing details from the phrase "language model", "foundation model", "ChatGPT", or "LLM", do not use that inference alone to include. Require explicit abstract evidence for the disputed criterion.
- If a decisive criterion still cannot be resolved, keep that criterion as `unclear`.
- `decision_rationale` must be brief and evidence-grounded: one or two short sentences tied to the provided title, abstract, and selected full-text sections and, when relevant, the reviewer conflict.
- Use `none` when no exclusion code or uncertainty reason applies.

Boundary examples:
- LLM-derived gene embeddings, prompt-generated labels, or frozen LLM prototypes used by a downstream classifier -> `application_wrapper` unless the abstract presents a central multimodal text-bio model or generator.
- Gene-token/cell-sentence/DNA-language modeling with no natural-language text or explicit text-bio alignment -> `text_component_present=no` and `text_bio_bridge_present=no`.
- Survival/risk/classification/annotation tasks without explicit generation -> `generative_model_present=no`.
- Biological data to natural-language descriptions, natural-language prompts to biological outputs, or explicit alignment of biological modalities with language representations -> can support `yes` when central and primary.
- Chat/dialogue/question-answering about biological data, or single-cell analysis with natural language -> can support text component and text-bio bridge when central and primary.
- Diffusion/generative model conditioned on text summaries, text-derived priors, or natural-language descriptions -> can support text component and text-bio bridge when conditioning is part of the candidate model.
- Metadata or foundation-model embeddings without clear natural-language descriptions or text conditioning -> `unclear`, not automatic yes or no.
- Thin or truncated abstract that hints at a candidate model but does not resolve text component, bridge, paper type, or generation -> choose `UNCERTAIN`, not `INCLUDE`.


Full-text evidence mode:
- Each record includes complete `selected_full_text_sections` extracted from Docling markdown.
- Treat the title, abstract, and selected full-text sections as the provided record; do not use outside knowledge.
- Use the selected full-text sections when they clarify criteria.
- When full-text sections contradict or refine the abstract, prefer the more specific full-text section evidence and mention that section in `evidence_snippet`.
- Do not infer from the paper title alone when the selected full-text sections do not support the criterion.


Batch execution instructions:
- Screen every record in the JSON array below independently.
- Return exactly one JSON object with a `results` array, with one object per input record, in the same order.
- Include `record_id` in every object exactly as provided.
- Include `evidence_snippet`: a short quote or paraphrased phrase from the provided evidence that supports the criterion outputs.
- Do not include hidden chain-of-thought, step-by-step reasoning, markdown, commentary, or code fences.
- Keep `decision_rationale` brief and evidence-grounded.

Records JSON:
```

<!-- end generated -->

### Supplementary Note S4. Operation-level decomposition: rules, runs and stability

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

### Supplementary Note S5. Motifs, design axes and archetypes

**Model-level paths.** For each model configuration, the decomposed routes (agent-decomposed papers) or the
author-curated graphs (pilot papers, all root-to-model paths) were turned into paths of role-aware
operation tokens. Provenance and identity steps were dropped and repeated identical operations
collapsed. Each operation's role follows from its inputs: biological only, text only, or joining
biological and text inputs. Unexpanded learned modules were kept as typed tokens.

**Motifs.** Closed frequent sub-chains (contiguous and gapped) were mined at the operation and family
levels, with support counted in papers (at least 4 papers; no length limit). Supported, interpretable
sub-chains were named as motifs with templates, members, parameter reporting and evidence-quoted
examples (Supplementary Table S11). Stability: mining was repeated on each single
decomposition run.

**Design axes.** Each route was also coded on five axes along one canonical pipeline (source, curation,
value transformation, carrier formation, interface): carrier formation, interface to the language
model, transformation of measured values (order only, discretised, learned compression, verbatim; with
subset and normalisation modifiers), text role and transparency. Coding rules are deterministic over
the chains and the charted atlas labels (Supplementary Table S15). We tested coverage,
independence (normalised mutual information) and robustness to decomposition runs. Archetypes are
carrier x interface combinations; a model can carry several.

**Earlier analysis.** An earlier version of this analysis compared exact route chains and reported no
recurring recipes. That result was an artefact of chain construction (uneven wording granularity,
non-computational steps counted as operations, fragmentary routes) and is withdrawn.

### Supplementary Note S6. Use of AI tools, reported by PRISMA-trAIce item

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
abstract. Records still uncertain after adjudication were resolved, keeping the automated decision
alongside: in rounds 1–4 by the review lead from the cited full sections, and in the August round by an
LLM agent from the full document, whose decision was not validated by a person. The prompts are given verbatim
in Supplementary Note S3, and the decisions in Supplementary Tables S3 and
S4. The roles are prompts executed by the same model,
not independent human reviewers.

**Route charting.** Routes were extracted from the full text with three frozen direct runs plus
dense-coverage candidates. Agreement across the three runs on the 55-record corpus: route Jaccard
0.945–0.969; carrier-family exact agreement 0.929; Krippendorff's alpha 0.881 (acceptance thresholds
0.80, 0.90, 0.80). Dated author-led amendments are recorded in the atlas metadata.

**Decomposition and parameter pass.** Supplementary Note S4 gives the rules, runs and
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
review lead approved the targeted charting pass and resolved the records of rounds 1–4 left uncertain by
automated full-text screening, and the authors curated the four pilot decompositions.

**Prompts, schemas and run records.** The prompts of the screening roles are reproduced in
Supplementary Note S3. The prompts of the other steps are generated by the scripts of each
step; these scripts, the output schemas, rule sets, run configurations and run outputs of every step
are in the project repository, and the supplementary file index lists their locations. The review
materials deposited on Zenodo (<!-- generated: zenodo:materials -->https://doi.org/10.5281/zenodo.23437391<!-- end generated -->) contain the outputs of every agent step with their
configurations, schemas and code. The run logs that contain the prompts as sent with the paper texts are
kept in the repository but are not deposited, because they embed the texts of the papers.

### Supplementary Note S7. Coverage of protein and nucleotide models

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
| 13 | Further change | During the decomposition | Analysis | The decomposition rules were revised after run-to-run disagreement, sharpening the boundaries between align, concatenate and serialise, and between partition and select; the affected papers were decomposed and their parameter pass repeated. | Yes (stability results) | All decomposition results; the stability on the papers that informed the revision is reported as in-sample (Supplementary Note S4). |
| 14 | Further change | During the decomposition | Tool | The decomposition used gpt-5.6-luna instead of gpt-5.4-mini, which is no longer available through Codex. | No | Decomposition, parameter pass and targeted charting. |
| 15 | Further change | After the decomposition | Analysis | Motifs (recurring operation sub-chains) and five design axes with archetypes were defined after inspecting the decomposed data. | Yes | Motif and archetype results; the axes are described as not validated on an independent corpus (Limitations). |
| 16 | Further change | After the decomposition | Analysis | An earlier comparison of exact route chains, which reported no recurring recipes, was withdrawn as an artefact of chain construction and replaced by the motif analysis. | Yes | None; the earlier result is not reported. |
| 17 | Further change | After the decomposition | Analysis | The design-culture analysis and a targeted charting pass (rationales, supervision, dependence tests, cross-representation comparisons) were defined after exploring the decomposed corpus. | Yes | All culture-level results; described as exploratory (Methods, Results and figure legends), with contrasts not adjusted for multiple comparisons. |
| 18 | Further change | After screening | Correction | An error in the automated keyword check that precedes screening was corrected, which recovered one eligible record (XunZi); it was screened with the same frozen procedures. | Yes | Counted among the included records and shown in the flow diagram. |
| 19 | Further change | After the search | Search check | A 13-day gap between the baseline and first top-up windows was checked by re-running the baseline queries of four sources for the gap (2026-10-14); no eligible record was found. | Yes | None; reported in Limitations. |
| 20 | Further change | After the full-text screening | Screening check | An audit found that the abstract shown with the selected sections was cut for some records and that some reports were not screened at full text; the screening was not repeated. | Yes | None changed; reported in Limitations. |
| 21 | Further change | After the withdrawal of a preprint | Corpus | The withdrawn OKR-Cell preprint is still counted among the included records but was excluded from the decomposition and the culture-level analyses (author decision pending). | No | Record counts include it; work-level counts exclude it (Results). |
| 22 | Further change | At synthesis | Omission | Protocol objective 3 (datasets, downstream tasks, evaluation metrics) and the extraction fields for pretraining objective and code and data availability were not charted, except the evaluation formats and outputs of the targeted pass. | No | Not reported; listed in Limitations. |
| 23 | Further change | August round, full-text screening | Screening | The record left uncertain at full-text screening in the August round was resolved by an LLM agent reading the full document, where amendment 4.4 foresaw the review lead; the decision was not validated by a person. | After the automated decisions | Inclusion of one record (scMIR); marked in Supplementary Table [[S:ft_​decisions]] and listed in Limitations. |

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

### Supplementary Table S3. Title and abstract screening decisions

One row per screened record (<!-- generated: rows of title_abstract_screening_decisions.csv -->4863<!-- end generated --> rows, including the record of
the supplemental recall correction): the screening run; the automated decision with its reason,
rationale and evidence; who produced it (the fixed rule over the two first-pass reviewers, or the
adjudicator); and the criterion answers, exclusion reasons and rationales of each role. Records decided
as include or uncertain were sought for full-text screening; Supplementary Figure S1 gives those
that were not retrieved or lacked a valid targeted section pair. Data file only.

### Supplementary Table S4. Full-text screening decisions

One row per report assessed at full text, including the record of the supplemental recall correction.
Automated decision: the decision of the screening agents, with its exclusion reason. Resolution: the
decision that resolved an uncertain automated decision, and who made it. Included reports carry their
number in the article's reference list. The data file adds the criterion answers and rationales of each
role and the recorded basis of each resolution.

<!-- generated: table:ft_decisions from data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10, data/living_catalog_updates/update_2026-08-09/09_fulltext_screening, data/living_catalog_updates/update_2026-08-09/09_fulltext_screening_manual_recall_xunzi_2026-08-11, data/screening_codex_fulltext_docling_graph_direct_clean_both_targets_2026-07-10/manual_resolution_2026-07-10.csv, data/living_catalog_updates/update_2026-08-09/10_eligibility, data/living_catalog_updates/update_2026-08-09/10_eligibility_manual_recall_xunzi_2026-08-11 -->

| Report | Automated decision | Resolution of an uncertain decision | Final decision | Final reason for exclusion |
|-----------------------------------------------|-------------------|-------------------|---------|---------------------|
| A multimodal conversational agent for DNA, RNA and protein tasks [5] | include | — | include | — |
| A Multi-Modal AI Copilot for Single-Cell Analysis with Instruction Following [6] | include | — | include | — |
| X-Cell: Scaling Causal Perturbation Prediction Across Diverse Cellular Contexts via Diffusion Language Models [7] | include | — | include | — |
| A Generative Foundation Model for Multimodal Histopathology [8] | include | — | include | — |
| WITHDRAWN: OKR-Cell: Open World Knowledge Aided Single-Cell Foundation Model with Robust Cross-Modal Cell-Language Pre-training [9] | include | — | include | — |
| Cell2Text: Multimodal LLM for Generating Single-Cell Descriptions from RNA-Seq Data [10] | include | — | include | — |
| Cell2Text: Multimodal LLM for generating textual descriptions from single-cell RNA-Seq profiles [11] | include | — | include | — |
| Multimodal learning of transcriptomes and text enables interactive single-cell RNA-seq data exploration with natural-language chats [12] | include | — | include | — |
| Multimodal learning enables chat-based exploration of single-cell data [13] | include | — | include | — |
| OmniNA: A foundation model for nucleotide sequences [14] | include | — | include | — |
| A foundation model for nucleotide sequences. [15] | include | — | include | — |
| XunZi, an AI biologist, reveals disease-modifying targets [17] | include | — | include | — |
| Any-to-Any Learning in Computational Pathology via Triplet Multimodal Pretraining [18] | uncertain | include (review lead) | include | — |
| Bio-BLIP: A Multimodal Architecture for Transferable Reasoning in Genomic Variant Interpretation [19] | include | — | include | — |
| BioGPT: A Generative Transformer-Based Framework for Personalized Genomic Medicine and Rare Disease Diagnosis [20] | include | — | include | — |
| Biomedgpt: Open multimodal generative pre-trained transformer for biomedicine [21] | include | — | include | — |
| BioReason: Incentivizing Multimodal Biological Reasoning within a DNA-LLM Model [22] | include | — | include | — |
| BioVERSE: Representation Alignment of Biomedical Modalities to LLMs for Multi-Modal Reasoning [23] | include | — | include | — |
| Scaling Large Language Models for Next-Generation Single-Cell Analysis. [24] | include | — | include | — |
| CaLMFlow: Volterra Flow Matching using Causal Language Models [25] | include | — | include | — |
| Precious3GPT: Multimodal Multi-Species Multi-Omics Multi-Tissue Transformer for Aging Research and Drug Discovery [26] | include | — | include | — |
| Cell-o1: Training LLMs to Solve Single-Cell Reasoning Puzzles with Reinforcement Learning [27] | include | — | include | — |
| Language may be all omics needs: Harmonizing multimodal data for omics understanding with CellHermes [28] | include | — | include | — |
| ChatCell: Facilitating Single-Cell Analysis with Natural Language [29] | include | — | include | — |
| Illuminating protein space with a programmable generative model [30] | include | — | include | — |
| Phenotype-Guided In Silico Molecular Generation Using Large Language Models [31] | include | — | include | — |
| Aligning LLMs with Biomedical Knowledge using Balanced Fine-Tuning [32] | include | — | include | — |
| Geneverse: A collection of Open-source Multimodal Large Language Models for Genomic and Proteomic Research [33] | include | — | include | — |
| Human Genome Book:Words,Sentences and Paragraphs [34] | include | — | include | — |
| GenNA: Conditional generation of nucleotide sequences guided by natural-language annotations [35] | include | — | include | — |
| Genolator: A Multimodal Large Language Model Fusing Natural Language, Genomic, and Structural Tokens for Protein Function Interpretation [36] | include | — | include | — |
| Gp-gpt: Large language model for gene-phenotype mapping [37] | include | — | include | — |
| Cell2Sentence: teaching large language models the language of biology [38] | include | — | include | — |
| H2O: A Foundation Model Bridging Histopathology to Spatial Multi-Omics Profiling [39] | uncertain | include (review lead) | include | — |
| Multimodal Cell Context Instruction Tuning for Conditional DNA Regulatory Sequence Generation with Large Language Models [40] | include | — | include | — |
| Language-Enhanced Representation Learning for Single-Cell Transcriptomics [41] | include | — | include | — |
| The End of Aging Clocks: Training Foundation Models to Reason in Aging and Longevity [42] | include | — | include | — |
| Towards Generalist Biomedical AI [43] | include | — | include | — |
| Teampath: Building multimodal pathology experts with reasoning ai copilots [44] | include | — | include | — |
| OCellus: A Language-Model Framework for Single-Cell, Spatial, and Perturbation Biology with Natural-Language Reasoning [45] | include | — | include | — |
| OmicsLM: A Multimodal Large Language Model for Multi-Sample Omics Reasoning [46] | include | — | include | — |
| Omni-DNA: A Unified Genomic Foundation Model for Cross-Modal and Multi-Task Learning [47] | include | — | include | — |
| OmniGene-4: a unified bio-language MoE model with router-level interpretability [48] | include | — | include | — |
| Rethinking Genomic Modeling Through Optical Character Recognition [49] | include | — | include | — |
| ProCyon: A multimodal foundation model for protein phenotypes. [50] | include | — | include | — |
| How Post-Training Shapes Biological Reasoning Models [51] | include | — | include | — |
| RVQ-Alpha: Bridging Single-Cell Transcriptomics and Large Language Models via Discrete Tokenization and Verifiable Reinforcement Learning [52] | include | — | include | — |
| A General Single-Cell Analysis Framework via Conditional Diffusion Generative Models [53] | include | — | include | — |
| SciCore-Omics: a tri-modal foundation model unifying histology, spatial transcriptomics and language for spatial biology [54] | include | — | include | — |
| scMIR: a vision-language foundation model for single-cell light microscopy image representation [55] | uncertain | include (LLM agent, not validated by a person) | include | — |
| scMOBA: A conversational single-cell Multi-Omics Brain Agent across species [56] | include | — | include | — |
| Systematic discovery of single-cell protein networks in cancer with Shusi [57] | include | — | include | — |
| TissueNarrator: Generative Modeling of Spatial Transcriptomics with Large Language Models. [58] | include | — | include | — |
| CellTosg2Sequence: A Unified Text-Omics-Signaling-Graph Large Language Model for Single-Cell Analysis [59] | include | — | include | — |
| Query-driven generative AI synthesizes multi-modal spatial omics from histology. [60] | include | — | include | — |
| 'Bingo' - a large language model- and graph neural network-based workflow for the prediction of essential genes from protein data | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| A fine-tuned genomic language model adds complementary nucleotide-context information to missense variant interpretation. | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Aligning foundation models on encoded synthetic omic data for patient stratification | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Building Knowledge-Enhanced AI Co-Scientists for Biomedical Discovery | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| CELLama: cell embedding leveraging language model abilities for analyzing cell types and spatial relationship in tumor | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| CellDuality: Unlocking Biological Reasoning in LLMs with Self-Supervised RLVR. | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| CellSwarm: LLM-Driven Cell Agents Recapitulate Tumor Microenvironment Dynamics and Sense Indirect Genetic Perturbations | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| ChIP-GPT: a managed large language model for robust data extraction from biomedical database records | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| CLIP-IT: CLIP-based Pairing of Histology Images with Privileged Textual Information | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| ELISA: An Interpretable Hybrid Generative AI Agent for Expression-Grounded Discovery in Single-Cell Genomics | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Enhanced Viral Genome Classification Using Large Language Models | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Enhancing generative perturbation models with llm-informed gene embeddings | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Exploring the Potentials and Challenges of Using Large Language Models for the Analysis of Transcriptional Regulation of Long Non-coding RNAs | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| From a single sequence to evolutionary trajectories: protein language models capture the evolutionary potential of SARS-CoV-2 protein sequences | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Generation of Multimodal Longitudinal Synthetic Data By Artificial Intelligence to Improve Personalized Medicine in Hematology | uncertain | exclude (review lead) | exclude | Application wrapper around an existing model |
| Harnessing the Power of Single-Cell Large Language Models with Parameter Efficient Fine-Tuning using scPEFT | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| How to improve polygenic prediction from whole-genome sequencing data by leveraging predicted epigenomic features? | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Lineage-Independent Structural Risk Detection in SARS- CoV-2 Spike Protein via Zero-Shot Protein Language Modeling | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Literature-derived, context-aware gene | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| ProkBERT PhaStyle: accurate phage lifestyle prediction with pretrained genomic language models | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| scELMo: Embeddings from Language Models | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| Unify learns cellular evolution with universal multimodal embeddings | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| VCWorld: A Biological World Model for Virtual Cell Simulation | exclude: application wrapper around an existing model | — | exclude | Application wrapper around an existing model |
| DNA Language Models: An Assessment of Pre-Training for Fine-Tuning Tasks | exclude: benchmark or resource without a new model | — | exclude | Benchmark or resource without a new model |
| Transformer model generated bacteriophage genomes are compositionally distinct from natural sequences | exclude: benchmark or resource without a new model | — | exclude | Benchmark or resource without a new model |
| Engineering Cells Using Artificial Intelligence | exclude: no biological data modality | — | exclude | No biological data modality |
| Toward a universal foundation model for graph-structured data | exclude: no biological data modality | — | exclude | No biological data modality |
| Toward learning a foundational representation of cells and genes | exclude: no biological data modality | — | exclude | No biological data modality |
| Foundation model for biomedical graphs: Integrating knowledge graphs and protein structures to large language models | uncertain | exclude (review lead) | exclude | No foundation-model evidence |
| A 5' UTR Language Model for Decoding Untranslated Regions of mRNA and Function Predictions. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A Cross-Species Generative Cell Atlas Across 1.5 Billion Years of Evolution: The TranscriptFormer Single-cell Model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A foundation language model to decipher diverse regulation of RNAs | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A foundational model for joint sequence-function multi-species modeling at scale for long-range genomic prediction | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A Genomic Language Model for Zero-Shot Prediction of Promoter Variant Effects | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A long range foundation model for zero-shot predictions in single-cell and spatial transcriptomics data | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A long-context language model for deciphering and generating bacteriophage genomes | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A multimodal cell-free RNA language model for liquid biopsy applications | exclude: no natural-language text component | — | exclude | No natural-language text component |
| A Phylogenetic Approach to Genomic Language Modeling | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Actionable Gene Expression Cell Profiling with Foundation Models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Advancing Cancer Prognosis with Hierarchical Fusion of Genomic, Proteomic and Pathology Imaging Data from a Systems Biology Perspective | exclude: no natural-language text component | — | exclude | No natural-language text component |
| AntigenLM: Structure-Aware DNA Language Modeling for Influenza | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Bidirectional mamba for single-cell data: Efficient context learning with biological fidelity | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Bio-xLSTM: Generative modeling, representation and in-context learning of biological and chemical sequences | exclude: no natural-language text component | — | exclude | No natural-language text component |
| BioArc: Discovering Optimal Neural Architectures for Biological Foundation Models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| BIOFORMERS: A SCALABLE FRAMEWORK FOR EXPLORING BIOSTATES USING TRANSFORMERS | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Biologically-Informed Hybrid Membership Inference Attacks on Generative Genomic Models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Bo, W. scGPT: Towards building a foundation model for single-cell multi-omics using generative AI | exclude: no natural-language text component | — | exclude | No natural-language text component |
| BOTANIC-0: a series of foundation models for plant genomic data | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CanBART: A generative foundation model of cancer molecular alterations for synthetic patient generation and genomic profile completion | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Carbon: Decoding the Language of Life | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Causal Circuit Tracing Reveals Distinct Computational Architectures in Single-Cell Foundation Models: Inhibitory Dominance, Biological Coherence, and Cross-Model Convergence | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CD-GPT As a Biological Foundation Model Bridging the Gap between Molecular Sequences Through Central Dogma | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Cell ontology guided transcriptome foundation model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Celler:A Genomic Language Model for Long-Tailed Single-Cell Annotation | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CellOS: Learning a World Model of Cellular State through Joint Embedding Prediction | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CellPLM: Pre-training of Cell Language Model Beyond Single Cells | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CellReasoner: A reasoning-enhanced large language model for cell type annotation | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Central Dogma Transformer: Towards Mechanism-Oriented AI for Cellular Understanding | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Circular RNA identification using a genomic language model and a small number of authenticated examples | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CLAMP: predicting specific protein-mediated chromatin loops in diverse species with a chromatin accessibility language model. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CLM-X: A multimodal single-cell foundation model with flexible multi-way Transformer for unified scRNA-seq and scATAC-seq analysis | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Coalescence and Translation | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CodonMoE: DNA language models for codon-dependent mRNA prediction | exclude: no natural-language text component | — | exclude | No natural-language text component |
| CodonMoE: DNA Language Models for mRNA Analyses | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Ctrl-DNA: Controllable Cell-Type-Specific Regulatory DNA Design via Constrained RL | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Deciphering enzymatic potential in metagenomic reads through DNA language models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Deciphering microbial gene function using natural language processing. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Deciphering single-cell epigenomic language with a foundation model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Decoding the ERS-CAF immunoregulatory axis via multimodal AI and its pan-cancer prognostic and therapeutic predictive value. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Deep Learning Strategies for Representation Learning and Generative Modeling in the Biosciences | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Designing mRNA coding sequence via multimodal reverse translation language modeling with Pro2RNA | exclude: no natural-language text component | — | exclude | No natural-language text component |
| DNA language model GROVER learns sequence context in the human genome | exclude: no natural-language text component | — | exclude | No natural-language text component |
| DNA language models are powerful predictors of genome-wide variant effects | exclude: no natural-language text component | — | exclude | No natural-language text component |
| DNACSE: Enhancing Genomic LLMs with Contrastive Learning for DNA Barcode Identification † | exclude: no natural-language text component | — | exclude | No natural-language text component |
| dnaGrinder: a lightweight and high-capacity genomic foundation model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| End-to-end multitask learning, from protein language to protein features without alignments | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Enhancing DNA Foundation Models to Address Masking Inefficiencies | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Enhancing recognition and interpretation of functional phenotypic sequences through fine-tuning pre-trained genomic models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| EpiGePT: a Pretrained Transformer model for epigenomics. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| EpiGePT: a pretrained transformer-based language model for context-specific human epigenomics. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Escaping the forest: a sparse, interpretable, and foundational neural network alternative for tabular data | exclude: no natural-language text component | — | exclude | No natural-language text component |
| evoCancerGPT: Generating Zero-Shot Single-Cell and Single-Sample Cancer Progression Through Transfer Learning | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Foundation model for single-cell omics | exclude: no natural-language text component | — | exclude | No natural-language text component |
| From Modality Translation to Regulatory Reasoning: Interpretable AI for Single-Cell Multi-Omic Systems | exclude: no natural-language text component | — | exclude | No natural-language text component |
| GEM-GPT Enables Personalized Cell Type-Resolved Therapeutic Design for Systems Pharmacology. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| GENA-LM: a family of open-source foundational DNA language models for long sequences. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Gene-Family Encoding Boosts Domain-Adapted Single-Cell Language Models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Generating and decoding methylated DNA with a Human Epigenetic Foundation Model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Generating antimicrobial peptides via genomic transfer learning | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Generative design and construction of functional plasmids with a DNA language model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Generative pretraining from large-scale transcriptomes for single-cell deciphering | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Generative pretraining from large-scale transcriptomes: Implications for single-cell deciphering and clinical translation | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Generative single-cell transcriptomics via large language models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| GENERator: A Long-Context Generative Genomic Foundation Model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Genos: a human-centric genomic foundation model. | uncertain | exclude (review lead) | exclude | No natural-language text component |
| GenSLMs: Genome-scale language models reveal SARS-CoV-2 evolutionary dynamics | exclude: no natural-language text component | — | exclude | No natural-language text component |
| GexMolGen: cross-modal generation of hit-like molecules via large language model encoding of gene expression signatures | exclude: no natural-language text component | — | exclude | No natural-language text component |
| HitAnno: Atlas-level cell type annotation based on scATAC-seq data via a hierarchical language model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| HoloCell: A Generative Foundation Model for Holistic Cellular Modeling | exclude: no natural-language text component | — | exclude | No natural-language text component |
| HydraRNA: a hybrid architecture based full-length RNA language model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| HyenaDNA: Long-Range Genomic Sequence Modeling at Single Nucleotide Resolution | exclude: no natural-language text component | — | exclude | No natural-language text component |
| ImmunoMatch learns and predicts cognate pairing of heavy and light immunoglobulin chains | exclude: no natural-language text component | — | exclude | No natural-language text component |
| JanusDNA: A Powerful Bi-directional Hybrid DNA Foundation Model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Large-scale multi-omic biosequence transformers for modeling protein–nucleic acid interactions | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Leveraging large language models to predict antibiotic resistance in Mycobacterium tuberculosis | exclude: no natural-language text component | — | exclude | No natural-language text component |
| MAMMAL - Molecular Aligned Multi-Modal Architecture and Language | exclude: no natural-language text component | — | exclude | No natural-language text component |
| MAMMAL--Molecular Aligned Multi-Modal Architecture and Language | exclude: no natural-language text component | — | exclude | No natural-language text component |
| MGM as a Large‐Scale Pretrained Foundation Model for Microbiome Analyses in Diverse Contexts | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Miniaturizing and modifying natural proteins with Raygun | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Modeling aspects of the language of life through transfer-learning protein sequences. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| mRNA-LM: full-length integrated SLM for mRNA analysis | exclude: no natural-language text component | — | exclude | No natural-language text component |
| MT-ConBiFormer-GPT: multi-target molecular generation for low-data drug discovery via a contrastive BiFormer-GPT architecture and curriculum learning with cross … | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Multi-megabase scale genome interpretation with genetic language models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Multi-Scale AI-Assisted Gene Expression Decoding | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Multimodal Learning for Mapping the Genotype-Phenotype Dynamics. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Nona: A unifying multimodal masking framework for functional genomics | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Nucleotide dependency analysis of DNA language models reveals genomic functional elements | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Open-weight genome language model safeguards: Assessing robustness via adversarial fine-tuning | exclude: no natural-language text component | — | exclude | No natural-language text component |
| OryzaG3: A Single-species Genomic Foundation Model Pretrained on Rice Pangenome | exclude: no natural-language text component | — | exclude | No natural-language text component |
| PlantBiMoE: A Bidirectional Foundation Model with Sparsemoe for Plant Genomes | exclude: no natural-language text component | — | exclude | No natural-language text component |
| PlantCAD2: A DNA foundation model for interpreting genomes across flowering plants. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| PlantCAD2: A Long-Context DNA Language Model for Cross-Species Functional Annotation in Angiosperms. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| PlantGFM: A Genomic Foundation Model for Discovery and Creation of Plant Genes | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Poisoning the Genome: Targeted Backdoor Attacks on DNA Foundation Models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Pre-training of single-cell language models through genetic pathway learning | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Predicting evolutionary rate as a pretraining task improves genome language model representations | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Predicting functional constraints across evolutionary timescales with phylogeny-informed genomic language models. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Probing genomic language models: Nucleotide Generative Pretrained Transformer and the role of pretraining in learned representations | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Protein Set Transformer: A protein-based genome language model to power high diversity viromics. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Protein-nucleic acid language model-assisted design of precise and compact adenine base editor | exclude: no natural-language text component | — | exclude | No natural-language text component |
| PTM-Mamba: a PTM-aware protein language model with bidirectional gated Mamba blocks | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Retentive Network promotes efficient RNA language modeling of long sequences | exclude: no natural-language text component | — | exclude | No natural-language text component |
| RiNALMo: general-purpose RNA language models can generalize well on structure prediction tasks | exclude: no natural-language text component | — | exclude | No natural-language text component |
| RNA language models predict mutations that improve RNA function. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| SARITA: a large language model for generating the S1 subunit of the SARS-CoV-2 spike protein | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scDifformer: diffusion-based post-training for virtual cell modeling across large-scale single-cell data | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scFormer: A Universal Representation Learning Approach for Single-Cell Data Using Transformers | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scGenAI: A generative AI platform with biological context embedding of multimodal features enhances single cell state classification | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scgpt-spatial: Continual pretraining of single-cell foundation model for spatial transcriptomics. bioRxiv | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scGPT: toward building a foundation model for single-cell multi-omics using generative AI | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scGPT: Towards Building a Foundation Model for Single-Cell Multi-omics Using Generative AI | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scgpt: Towards building a foundation model for single-cell multi-omics using generative ai. bioRxiv | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scKEPLM: Knowledge enhanced large-scale pre-trained language model for single-cell transcriptomics | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scMulan: a multitask generative pre-trained language model for single-cell analysis | exclude: no natural-language text component | — | exclude | No natural-language text component |
| scWGBS-GPT: a foundation model for capturing long-range CPG dependencies in single-cell whole-genome bisulfite sequencing to enhance epigenetic analysis | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Self-supervised learning on millions of pre-mRNA sequences improves sequence-based RNA splicing prediction | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Semantic design of functional de novo genes from a genomic language model. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Semantic mining of functional de novo genes from a genomic language model | exclude: no natural-language text component | — | exclude | No natural-language text component |
| seqLens: optimizing language models for genomic predictions | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Short-Context Regulatory DNA Language Models with Motif-Discovery Regularization. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| ST-Align: Multi-Scale Image-Gene Foundation Modeling for Spatial Transcriptomics via Spot-Niche Alignment | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Tabula: A Tabular Self-Supervised Foundation Model for Single-Cell Transcriptomics | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Temporal AI model predicts drivers of cell state trajectories across human aging | exclude: no natural-language text component | — | exclude | No natural-language text component |
| The Language of Cancer: Decoding Cancer Signatures with Language Models and cfRNA Sequencing | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Towards Spatial Transcriptomics-driven Pathology Foundation Models | exclude: no natural-language text component | — | exclude | No natural-language text component |
| TRAFICA: an open chromatin language model to improve transcription factor binding affinity prediction. | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Transcriptomic Neural Networks Architecture and Applications to Functional and Aging Research | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Unsupervised Whole-Genome Representation Learning Captures Bacterial Phenotypes | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Zygosity-Aware DNA Language Modeling Improves Ancestry and Gene Expression Prediction | exclude: no natural-language text component | — | exclude | No natural-language text component |
| Mamba: Linear-Time Sequence Modeling with Selective State Spaces | exclude: no substantive text-biology bridge | — | exclude | No substantive text-biology bridge |
| Adding layers of information to scRNA-seq data using pre-trained language models | exclude: not a generative model | — | exclude | Not a generative model |
| CELLama: Foundation Model for Single Cell and Spatial Transcriptomics by Cell Embedding Leveraging Language Model Abilities. | exclude: not a generative model | — | exclude | Not a generative model |
| Clinically aligned multi-modal image-text model for pan-cancer prognosis prediction | exclude: not a generative model | — | exclude | Not a generative model |
| Joint embedding of transcriptomes and text enables interactive single-cell RNA-seq data exploration via natural language | exclude: not a generative model | — | exclude | Not a generative model |
| L2G: Repurposing Language Models for Genomics Tasks. | exclude: not a generative model | — | exclude | Not a generative model |
| LangCell: Language-Cell 737 Pre-training for Cell Identity Understanding | exclude: not a generative model | — | exclude | Not a generative model |
| LangCell: Language-Cell Pre-training for Cell Identity Understanding | exclude: not a generative model | — | exclude | Not a generative model |
| Learning from Gene Names, Expression Values and Images: Contrastive Masked Text-Image Pretraining for Spatial Transcriptomics Representation Learning | uncertain | exclude (review lead) | exclude | Not a generative model |
| OKR-Cell: Open World Knowledge Aided Single-Cell Foundation Model with Robust Cross-Modal Cell-Language Pre-training | exclude: not a generative model | — | exclude | Not a generative model |
| Open World Knowledge Aided Single-Cell Foundation Model with Robust Cross-Modal Cell-Language Pre-training | exclude: not a generative model | — | exclude | Not a generative model |
| Phenotypic Bioactivity Prediction as Open-set Biological Assay Querying | exclude: not a generative model | — | exclude | Not a generative model |
| Towards Applying Large Language Models to Complement Single-Cell Foundation Models | exclude: not a generative model | — | exclude | Not a generative model |
| ZerOmics: Toward General Models for Single-Cell Analysis with Instruction Tuning | exclude: not a generative model | — | exclude | Not a generative model |
| Foundation model for comprehensive transcriptional regulation analysis | exclude: review or editorial | — | exclude | Review or editorial |
| Generalist biological artificial intelligence in modeling the language of life | exclude: review or editorial | — | exclude | Review or editorial |
| Geometric Representations of Knowledge Inside Biological Large Language Models: an Empirical Analysis | exclude: review or editorial | — | exclude | Review or editorial |
| Let the data speak - single-cell analysis with CellWhisperer. | exclude: review or editorial | — | exclude | Review or editorial |
| Single-cell exploration in natural language | exclude: review or editorial | — | exclude | Review or editorial |

<!-- end generated -->

### Supplementary Table S5. Decomposition decisions per step

One row per step of the agent-decomposed routes (<!-- generated: rows of decomposition_step_decisions.csv -->1468<!-- end generated --> steps): the
charted wording of the step, the decision category and library operations returned by the majority of
the three runs, the number of runs that agreed, the rule applied with the agents' rationale, and the
verbatim evidence. Data file only.

### Supplementary Table S6. Parameter-pass decisions per slot

One row per declared parameter of every operation call of the agent-decomposed routes
(<!-- generated: rows of parameter_slot_decisions.csv -->2433<!-- end generated --> slots): whether the paper states the value for that data path, the
value, the number of runs that agreed and the verbatim evidence. Data file only.

### Supplementary Table S7. Targeted charting items per record and run

One row per record, item and category of the targeted charting pass
(<!-- generated: rows of targeted_charting_items.csv -->2862<!-- end generated --> rows), with whether each of the two runs returned it. Data file only.

### Supplementary Table S8. Reports excluded at full text, with reasons

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

### Supplementary Table S9. Charted models

One row per charted model (<!-- generated: rows of charted_models.csv -->109<!-- end generated --> models): the record, paper title, DOI and year, the number of routes and
configurations, the input-carrier families, the primary carrier subtype, fusion topologies, text roles,
lifecycle phases and biological modalities. Data file only.

### Supplementary Table S10. Included works: design culture and charted variables

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

### Supplementary Table S11. Motif library

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

### Supplementary Table S12. Gene and token budgets stated in the papers

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

### Supplementary Table S13. Text written by LLMs and used for training or evaluation

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

### Supplementary Table S14. Cross-culture comparison units

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

### Supplementary Table S15. Route-level design-pattern codebook

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
full text are given in Supplementary Table S8.

<!-- generated: figure:flow from analysis/prisma_flow_2026-10-07/prisma_flow.png -->

![](analysis/prisma_flow_2026-10-07/prisma_flow.png){width=100%}

<!-- end generated -->


\newpage

## Data files and column dictionary

<!-- generated: datafiles from the data files of this supplement -->

The data files are comma-separated, UTF-8 encoded and use plain-language values. The coded originals from which they are built are kept in the project repository (see Data and code availability).

| File | Item | Contents | Rows |
|---------------------|-------------------------|---------------------------------------------------------|------:|
| deviations.csv | Supplementary Table S1 | Deviations from the protocol | 23 |
| search_​runs.csv | Supplementary Table S2 | Search runs by round and source, with limits and counts as executed | 40 |
| title_​abstract_​screening_​decisions.csv | Supplementary Table S3 | Title and abstract screening: decisions of the screening agents for every screened record | 4863 |
| fulltext_​screening_​decisions.csv | Supplementary Table S4 | Full-text screening: decisions of the screening agents, resolutions and final decisions for every assessed report | 234 |
| decomposition_​step_​decisions.csv | Supplementary Table S5 | Operation-level decomposition: decision for every step of the agent-decomposed routes | 1468 |
| parameter_​slot_​decisions.csv | Supplementary Table S6 | Parameter pass: whether the paper states each declared parameter of each operation call | 2433 |
| targeted_​charting_​items.csv | Supplementary Table S7 | Targeted charting pass: for every record, which items each of the two runs returned | 2862 |
| fulltext_​exclusions.csv | Supplementary Table S8 | Reports excluded at full text, by reason | 8 |
| charted_​models.csv | Supplementary Table S9 | Charted models with their records, routes and input labels | 109 |
| included_​works.csv | Supplementary Table S10 | Included works with their design culture and charted variables | 51 |
| motif_​library.csv | Supplementary Table S11 | Motif library: recurring operation sub-chains with an example each | 15 |
| gene_​budgets.csv | Supplementary Table S12 | Genes or features kept per cell or object, as stated in the papers | 21 |
| token_​budgets.csv | Supplementary Table S12 | Vectors, codes or text tokens per object passed to the language model | 13 |
| llm_​written_​text.csv | Supplementary Table S13 | Works that used text written by LLMs for training or evaluation | 25 |
| comparison_​units.csv | Supplementary Table S14 | Cross-culture comparison units after adjudication | 31 |
| route_​codebook.csv | Supplementary Table S15 | Route-level codebook of the design axes and archetypes | 532 |

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
| search_​runs.csv | hits_​reported | Total number of results reported in the export metadata, where the interface reports one |
| search_​runs.csv | records_​fetched | Number of records fetched, as recorded in the export metadata |
| search_​runs.csv | records_​before_​validation | Records in the raw export before filtering after retrieval (for Springer Nature, the check that a term of each concept block is in the title or abstract) |
| search_​runs.csv | count_​in_​run_​log | Count for the source in the search summary file of the round |
| search_​runs.csv | records_​retained | Records in the export file of the run, passed to deduplication |
| search_​runs.csv | export_​file | Repository path of the export file of the run |
| title_​abstract_​screening_​decisions.csv | screening_​run | Screening run (name and date of the run) |
| title_​abstract_​screening_​decisions.csv | record_​id | Identifier of the record in the review database |
| title_​abstract_​screening_​decisions.csv | record_​id_​in_​run | Identifier of the record within the screening run |
| title_​abstract_​screening_​decisions.csv | title | Title of the record |
| title_​abstract_​screening_​decisions.csv | doi | DOI of the record |
| title_​abstract_​screening_​decisions.csv | automated_​decision | Decision of the automated screening: include, exclude or uncertain |
| title_​abstract_​screening_​decisions.csv | automated_​exclusion_​reason | Exclusion reason of the automated decision, if any |
| title_​abstract_​screening_​decisions.csv | automated_​uncertainty | Reason for an uncertain automated decision, if any |
| title_​abstract_​screening_​decisions.csv | decided_​by | Who produced the automated decision: the fixed rule over the two first-pass reviewers, or the adjudicator (called when the first-pass reviewers conflicted or were uncertain) |
| title_​abstract_​screening_​decisions.csv | rationale | Rationale of the automated decision |
| title_​abstract_​screening_​decisions.csv | evidence | Evidence snippet from the record that supports the decision |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​paper_​type | Scope reviewer: kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​biological_​modality | Scope reviewer: whether a biological data modality is present (yes, no, unclear) |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​text_​component | Scope reviewer: whether a natural-language text component is present (yes, no, unclear) |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​text_​biology_​bridge | Scope reviewer: whether a substantive bridge between text and biology is present (yes, no, unclear) |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​exclusion_​reason | Scope reviewer: main exclusion reason returned by the role, if any |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​uncertainty | Scope reviewer: reason for uncertainty returned by the role, if any |
| title_​abstract_​screening_​decisions.csv | scope_​reviewer_​rationale | Scope reviewer: brief evidence-grounded rationale returned by the role |
| title_​abstract_​screening_​decisions.csv | architecture_​reviewer_​paper_​type | Architecture reviewer: kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear |
| title_​abstract_​screening_​decisions.csv | architecture_​reviewer_​generative_​model | Architecture reviewer: whether the candidate model is generative (yes, no, unclear) |
| title_​abstract_​screening_​decisions.csv | architecture_​reviewer_​foundation_​model_​evidence | Architecture reviewer: whether there is evidence of foundation-model characteristics (yes, no, unclear) |
| title_​abstract_​screening_​decisions.csv | architecture_​reviewer_​exclusion_​reason | Architecture reviewer: main exclusion reason returned by the role, if any |
| title_​abstract_​screening_​decisions.csv | architecture_​reviewer_​uncertainty | Architecture reviewer: reason for uncertainty returned by the role, if any |
| title_​abstract_​screening_​decisions.csv | architecture_​reviewer_​rationale | Architecture reviewer: brief evidence-grounded rationale returned by the role |
| title_​abstract_​screening_​decisions.csv | adjudicator_​paper_​type | Adjudicator: kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​biological_​modality | Adjudicator: whether a biological data modality is present (yes, no, unclear) (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​text_​component | Adjudicator: whether a natural-language text component is present (yes, no, unclear) (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​text_​biology_​bridge | Adjudicator: whether a substantive bridge between text and biology is present (yes, no, unclear) (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​generative_​model | Adjudicator: whether the candidate model is generative (yes, no, unclear) (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​foundation_​model_​evidence | Adjudicator: whether there is evidence of foundation-model characteristics (yes, no, unclear) (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​exclusion_​reason | Adjudicator: main exclusion reason returned by the role, if any (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​uncertainty | Adjudicator: reason for uncertainty returned by the role, if any (empty if the record was not adjudicated) |
| title_​abstract_​screening_​decisions.csv | adjudicator_​rationale | Adjudicator: brief evidence-grounded rationale returned by the role (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | screening_​run | Full-text screening run (name and date of the run) |
| fulltext_​screening_​decisions.csv | record_​id | Identifier of the record in the review database |
| fulltext_​screening_​decisions.csv | record_​id_​in_​run | Identifier of the record within the screening run |
| fulltext_​screening_​decisions.csv | title | Title of the report |
| fulltext_​screening_​decisions.csv | doi | DOI of the report |
| fulltext_​screening_​decisions.csv | study | First author and year of an included report, as in the article's reference list |
| fulltext_​screening_​decisions.csv | automated_​decision | Decision of the automated screening: include, exclude or uncertain |
| fulltext_​screening_​decisions.csv | automated_​exclusion_​reason | Exclusion reason of the automated decision, if any |
| fulltext_​screening_​decisions.csv | automated_​uncertainty | Reason for an uncertain automated decision, if any |
| fulltext_​screening_​decisions.csv | decided_​by | Who produced the automated decision: the fixed rule over the two first-pass reviewers, or the adjudicator (called when the first-pass reviewers conflicted or were uncertain) |
| fulltext_​screening_​decisions.csv | rationale | Rationale of the automated decision |
| fulltext_​screening_​decisions.csv | evidence | Evidence snippet from the record that supports the decision |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​paper_​type | Scope reviewer: kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​biological_​modality | Scope reviewer: whether a biological data modality is present (yes, no, unclear) |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​text_​component | Scope reviewer: whether a natural-language text component is present (yes, no, unclear) |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​text_​biology_​bridge | Scope reviewer: whether a substantive bridge between text and biology is present (yes, no, unclear) |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​exclusion_​reason | Scope reviewer: main exclusion reason returned by the role, if any |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​uncertainty | Scope reviewer: reason for uncertainty returned by the role, if any |
| fulltext_​screening_​decisions.csv | scope_​reviewer_​rationale | Scope reviewer: brief evidence-grounded rationale returned by the role |
| fulltext_​screening_​decisions.csv | architecture_​reviewer_​paper_​type | Architecture reviewer: kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear |
| fulltext_​screening_​decisions.csv | architecture_​reviewer_​generative_​model | Architecture reviewer: whether the candidate model is generative (yes, no, unclear) |
| fulltext_​screening_​decisions.csv | architecture_​reviewer_​foundation_​model_​evidence | Architecture reviewer: whether there is evidence of foundation-model characteristics (yes, no, unclear) |
| fulltext_​screening_​decisions.csv | architecture_​reviewer_​exclusion_​reason | Architecture reviewer: main exclusion reason returned by the role, if any |
| fulltext_​screening_​decisions.csv | architecture_​reviewer_​uncertainty | Architecture reviewer: reason for uncertainty returned by the role, if any |
| fulltext_​screening_​decisions.csv | architecture_​reviewer_​rationale | Architecture reviewer: brief evidence-grounded rationale returned by the role |
| fulltext_​screening_​decisions.csv | adjudicator_​paper_​type | Adjudicator: kind of paper: primary model paper, review or editorial, benchmark or resource, application wrapper, or unclear (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​biological_​modality | Adjudicator: whether a biological data modality is present (yes, no, unclear) (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​text_​component | Adjudicator: whether a natural-language text component is present (yes, no, unclear) (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​text_​biology_​bridge | Adjudicator: whether a substantive bridge between text and biology is present (yes, no, unclear) (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​generative_​model | Adjudicator: whether the candidate model is generative (yes, no, unclear) (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​foundation_​model_​evidence | Adjudicator: whether there is evidence of foundation-model characteristics (yes, no, unclear) (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​exclusion_​reason | Adjudicator: main exclusion reason returned by the role, if any (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​uncertainty | Adjudicator: reason for uncertainty returned by the role, if any (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | adjudicator_​rationale | Adjudicator: brief evidence-grounded rationale returned by the role (empty if the record was not adjudicated) |
| fulltext_​screening_​decisions.csv | resolved_​by | Who resolved an uncertain automated decision: the review lead, from the cited full sections (rounds 1–4), or an LLM agent reading the full document, whose decision was not validated by a person (August round) |
| fulltext_​screening_​decisions.csv | resolution_​decision | Decision of the resolution |
| fulltext_​screening_​decisions.csv | resolution_​reason | Exclusion reason given by the resolution, if any |
| fulltext_​screening_​decisions.csv | resolution_​basis | Basis of the resolution, as recorded |
| fulltext_​screening_​decisions.csv | resolution_​date | Date of the resolution |
| fulltext_​screening_​decisions.csv | final_​decision | Final decision: include or exclude |
| fulltext_​screening_​decisions.csv | final_​exclusion_​reason | Final exclusion reason, as counted in the flow diagram |
| decomposition_​step_​decisions.csv | study | First author and year of the record, as in the article's reference list |
| decomposition_​step_​decisions.csv | record_​id | Record in the review database |
| decomposition_​step_​decisions.csv | model | Model name as charted |
| decomposition_​step_​decisions.csv | route_​id | Identifier of the charted route |
| decomposition_​step_​decisions.csv | step | Position of the step in the route |
| decomposition_​step_​decisions.csv | steps_​in_​route | Number of steps of the route |
| decomposition_​step_​decisions.csv | step_​id | Identifier of the step |
| decomposition_​step_​decisions.csv | charted_​wording | Element of the charted transformation chain that the step decomposes |
| decomposition_​step_​decisions.csv | category | Decision category: library operation, learned module left unexpanded, data provenance (no computation), identity (no change), computation outside the library, unspecified fusion, or external text generator |
| decomposition_​step_​decisions.csv | operations | Library operations named for the step |
| decomposition_​step_​decisions.csv | runs_​agreeing | Number of the three runs that returned the published decision |
| decomposition_​step_​decisions.csv | rule_​and_​rationale | Rule of the decomposition protocol applied, with the agents' rationale |
| decomposition_​step_​decisions.csv | uncertainty | Uncertainty recorded for the step, if any |
| decomposition_​step_​decisions.csv | evidence | Verbatim quote from the paper |
| parameter_​slot_​decisions.csv | study | First author and year of the record, as in the article's reference list |
| parameter_​slot_​decisions.csv | record_​id | Record in the review database |
| parameter_​slot_​decisions.csv | model | Model name as charted |
| parameter_​slot_​decisions.csv | route_​id | Identifier of the charted route |
| parameter_​slot_​decisions.csv | step_​id | Identifier of the step |
| parameter_​slot_​decisions.csv | operation | Library operation of the call |
| parameter_​slot_​decisions.csv | parameter | Declared parameter of the operation |
| parameter_​slot_​decisions.csv | status | Whether the paper states the value for this data path: stated or not stated |
| parameter_​slot_​decisions.csv | value | Stated value, as given in the paper |
| parameter_​slot_​decisions.csv | runs_​agreeing | Number of the three runs that returned the published status |
| parameter_​slot_​decisions.csv | evidence | Verbatim quote from the paper |
| targeted_​charting_​items.csv | study | First author and year of the record, as in the article's reference list |
| targeted_​charting_​items.csv | record_​id | Record in the review database |
| targeted_​charting_​items.csv | item | Charting item |
| targeted_​charting_​items.csv | category | Category of the item |
| targeted_​charting_​items.csv | found_​in_​run_​1 | Whether the first run returned the category for the record (yes or no) |
| targeted_​charting_​items.csv | found_​in_​run_​2 | Whether the second run returned the category for the record (yes or no) |
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
