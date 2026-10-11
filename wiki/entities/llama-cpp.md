---
title: llama.cpp
type: tool
sources:
  - 2026-10-11-llama-cpp @ page
updated: 2026-10-11T16:04:03+09:00
status: draft
tool_version: b11552
---
llama.cpp is a dependency-free C/C++ project for running LLM inference on a wide range of hardware, with a CLI and an OpenAI-compatible server.

## What it does
The README describes llama.cpp as LLM and VLM inference in C/C++ with minimal setup and state-of-the-art performance across a wide range of hardware, locally and in the cloud. It is a plain C/C++ implementation without dependencies and is built on the ggml library. Listed features: first-class Apple silicon support, AVX and AMX on x86, RISC-V support, 1.5-bit to 8-bit integer quantization, custom CUDA kernels with HIP and MUSA, Vulkan and SYCL backends, and CPU plus GPU hybrid inference for models larger than VRAM. A backend table covers BLAS, CUDA, HIP, Metal, Vulkan, SYCL, OpenCL, RPC, WebGPU and others. Install options are an installer script, Docker, prebuilt binaries from the releases page, or building from source. The README shows a CLI that downloads and runs a model from Hugging Face and a serve command that launches an OpenAI-compatible API server with a built-in web UI.

## Limits
Version is the newest release tag on the GitHub releases page on 2026-10-11 (build-number tags, listed there as pre-release). The repository publishes a build number rather than version numbers. Command names in the README have changed over time; check the README at the pinned commit. This page covers the repository front page and README only.

## Disagreements
None found.
