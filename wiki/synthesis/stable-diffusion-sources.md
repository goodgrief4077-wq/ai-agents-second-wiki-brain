---
title: Stable Diffusion sources
type: synthesis
sources:
  - 2026-10-11-compvis-stable-diffusion @ page
  - 2026-10-11-stability-generative-models @ page
  - 2026-10-11-diffusers @ page
updated: 2026-10-11T16:07:52+09:00
status: draft
---
Stable Diffusion is a family of latent diffusion models; the original CompVis release, Stability AI's later generative-models repository and the Hugging Face Diffusers library are three different primary places to find it.

## Findings
- The CompVis repository describes Stable Diffusion as a latent text-to-image diffusion model trained on 512x512 images from a subset of LAION-5B, conditioned on a frozen CLIP ViT-L/14 text encoder, with an 860M UNet and 123M text encoder that runs on a GPU with at least 10GB VRAM. (2026-10-11-compvis-stable-diffusion @ page)
- It says v1 was pretrained on 256x256 images and then finetuned on 512x512, and that the model mirrors biases in its training data. (2026-10-11-compvis-stable-diffusion @ page)
- Its weights are distributed under the CreativeML OpenRAIL-M licence, described as permissive with use-based restrictions; the README advises against using the weights in services or products without additional safety mechanisms. (2026-10-11-compvis-stable-diffusion @ page)
- Stability AI's generative-models repository README opens with news of Stable Video 4D 2.0, a research video-to-4D diffusion model, with sampling steps. (2026-10-11-stability-generative-models @ page)
- Diffusers is the library route: its quickstart loads a Stable Diffusion v1.5 checkpoint through a pipeline and links an Apple Silicon guide for Stable Diffusion. (2026-10-11-diffusers @ page)

## Disagreements
None found. The generative-models README was read only at its opening, so its coverage of other models is not summarised here.
