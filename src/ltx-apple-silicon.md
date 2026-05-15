# What I Learned Trying to Run LTX-Video 2.3 on Apple Silicon

I wanted to learn video generation, picked the `fp8` version of [Sulphur 2 Base](https://huggingface.co/SulphurAI/Sulphur-2-base) because it looked like it would fit in RAM, downloaded and set up nearly 80GB of files, and then found out it would not run on my Mac Mini M4 Pro with 64GB of RAM.

```text
TypeError: Trying to convert Float8_e4m3fn to the MPS backend
but it does not have support for that dtype.
```

I did not understand the error at first. The code agent had to explain what the message was really telling me. The answer was not encouraging: there was no practical way to make this setup work on my Mac Mini in its current form. But I learned something new from the failure, and that is what I am writing down here.

## The Error

At first, that meant nothing to me. Once I dug into it, the message became clear.

The problem was not memory, the workflow, or a missing node. The backend itself could not handle the datatype the model was stored in.

That changed the investigation.

## What I Dug Into

I had to separate three things that are easy to blur together:

1. file size
2. memory pressure
3. backend support

The smaller file was what misled me.

`fp8` means each model weight uses 8 bits instead of 16. That matters because the model should need less RAM to load and run. The model file is smaller on disk too, but RAM was the part I cared about.

| Format | Bits | Rough size for 22B | Practical meaning |
| ------ | ---: | -----------------: | ----------------- |
| `bf16` |   16 |              ~44GB | Common high-quality model format, but too large here |
| `fp8`  |    8 |              ~22GB | Smaller float model file, but blocked by MPS dtype support |
| `q4`   |    4 |              ~11GB | Storage estimate only, would need a supported quantized runtime |

At first glance, that looked like the whole story. The code agent told me `fp8` should be suitable, with only a small quality drop compared with `bf16`. So I assumed this smaller model version would be the right fit for my Mac Mini.

Not quite.

Apple's GPU path goes through `MPS`, Metal Performance Shaders. PyTorch uses that backend to talk to the GPU. And `MPS` does not support `Float8_e4m3fn`, the `fp8` dtype this model uses.

So the real blocker was not "can I fit this model in RAM?" The real blocker was "can this backend even execute this dtype?" In this setup, the answer was no.

That is a much more useful lesson than a generic "it did not run."

## Why Llama.cpp Feels Different

This also explained something else.

Why can I run quantized LLMs on a Mac, but this video model falls over instantly?

Because the stack is different.

When I run local LLMs with `llama.cpp`, I am usually using a converted `GGUF` file, not the original PyTorch model file.

`GGUF` is the packaging format used by `llama.cpp`. It stores the model weights, tokenizer metadata, architecture details, and the quantization format in one file. The model might be `Q4_K_M`, `Q5_K_M`, or `Q8_0`.

That last one is easy to misread. `Q8_0` is an 8-bit GGUF quantization format. It stores weights as compact integer-like values with scale factors. It is not the same thing as PyTorch `Float8_e4m3fn`, the `fp8` dtype this LTX model uses.

Same 8 bits. Different meaning.

`llama.cpp` works on Apple Silicon because its GGUF model files, quantized weight formats, scale factors, and Metal kernels are designed to work together. It uses a different path from the PyTorch `MPS` `fp8` path that failed here.

Video generation has another problem: it is a diffusion model.

That means it starts from noise and repeatedly denoises toward frames that match the prompt. Each step depends on the previous one. Small numeric errors can accumulate into visible artifacts: flicker, mushy detail, broken motion, or frames that drift away from each other.

Text models can often tolerate aggressive weight quantization. Video diffusion has less room for that kind of error. Quality is the output.

With LTX, I was asking PyTorch `MPS` to execute an `fp8` model path it does not support. The model never reached a point where I could trade quality for memory or speed. It failed at the dtype boundary.

So "LLMs run on Mac" does not automatically mean "large video models run on Mac too."

That assumption did not survive contact with reality.

## The Practical Takeaway

On Mac, compatibility is not just about how much RAM you have. It is about whether the vendor, hardware, runtime, and model format line up.

On CUDA with NVIDIA H100-class hardware, `fp8` is a supported compute path. The hardware has FP8 Tensor Cores, and the software stack is built around that feature. Raw `fp8` model in, supported `fp8` execution path out.

On this 64GB Apple Silicon machine, `fp8` looked like the right size. But size was not enough. The backend could not execute the dtype, so the model format I was holding was not actually runnable in this stack.

After all this, the next version I would try is something like [Sulphur 2 Base GGUF](https://huggingface.co/vantagewithai/Sulphur-2-Base-GGUF). That is closer to the practical path: a quantized model file made for this model family, plus a runtime that knows how to execute that format on Apple Silicon.

The open question is quality. GGUF versions use `Q` formats, quantized weights, instead of the `fp8` float format I tried first. Maybe the tradeoff is acceptable. Maybe video diffusion makes the loss too visible. That is something I can only find out by trying it.

Because this machine has 64GB of RAM, I would start with `Q8_0` if it loads. It is larger than `Q4_K_M`, but it keeps more precision. If `Q8_0` is too slow or too memory-heavy, I would step down to `Q6_K`, then `Q5_K_M`, and only then `Q4_K_M`.

For video quality, `Q4_K_M` is the fallback, not the first test.
