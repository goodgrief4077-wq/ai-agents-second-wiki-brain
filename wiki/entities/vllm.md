---
title: vLLM
type: tool
sources:
  - 2026-10-11-vllm @ page
updated: 2026-10-11T16:07:52+09:00
status: draft
tool_version: v0.31.0
---
vLLM is an open-source inference and serving engine for LLMs focused on throughput and memory efficiency, with an OpenAI-compatible server.

## What it does
The README describes vLLM as a fast, easy-to-use library for LLM inference and serving. Performance features listed: PagedAttention memory management, continuous batching, chunked prefill, prefix caching, CUDA/HIP graphs, many quantization formats (FP8, INT8, INT4, GPTQ, AWQ, GGUF and others), several attention kernels, speculative decoding, and disaggregated prefill, decode and encode. Usability features: Hugging Face model integration, parallelism modes for distributed inference, streaming, structured outputs, tool calling and reasoning parsers, an OpenAI-compatible API server plus Anthropic Messages API and gRPC support, and multi-LoRA. It lists support for NVIDIA, AMD and Intel GPUs, several CPU families and hardware plugins such as Google TPUs, and says it supports 200+ model architectures. Install is with uv or pip.

## Limits
Version taken from the GitHub releases page on 2026-10-11. The README is a feature overview; hardware and model support details live in the linked docs. This page covers the repository front page and README only.

## Disagreements
None found.
