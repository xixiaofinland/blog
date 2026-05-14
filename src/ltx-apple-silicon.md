# What I Learned Trying to Run LTX-Video 2.3 on Apple Silicon

As a beginner, I just wanted to try LTX-Video 2.3 on my Apple Silicon Mac Mini and see whether I could get a serious video model running at all. The full `bf16` setup was already too big to fit comfortably in 64GB of RAM, but `fp8` looked like the perfect compromise. Smaller files, almost the same quality, at least according to the code agent. So I downloaded everything I thought I needed, one file after another, until I had burned nearly 80GB of disk space. That was where the story actually started.

Then I ran it. After downloading all those files, it failed immediately.

I did not understand the error at first. The code agent had to explain what the message was really telling me. The answer was not encouraging: there was no practical way to make this setup work on my Mac Mini in its current form. But I learned something new from the failure, and that is what I am writing down here.

## The Error

This was the error:

```text
TypeError: Trying to convert Float8_e4m3fn to the MPS backend
but it does not have support for that dtype.
```

At first, that meant nothing to me. Once I dug into it, the message became clear.

This was not an out-of-memory problem. Not a broken workflow. Not a missing node. The backend itself could not handle the datatype the model was stored in.

That changed the investigation.

## What I Dug Into

I had to separate three things that are easy to blur together:

1. file size
2. memory pressure
3. backend support

The smaller file was what misled me.

`fp8` means each model weight uses 8 bits instead of 16. So the checkpoint gets much smaller on disk.

| Format | Bits | Rough size for 22B |
| ------ | ---- | ------------------ |
| `bf16` | 16   | ~44GB              |
| `fp8`  | 8    | ~22GB              |
| `q4`   | 4    | ~11GB              |

At first glance, that looked like the whole story. The code agent told me `fp8` should be suitable, with only a small quality drop compared with `bf16`. So I assumed this smaller checkpoint would be the right fit for my Mac Mini.

Not quite.

Apple's GPU path goes through `MPS`, Metal Performance Shaders. PyTorch uses that backend to talk to the GPU. And `MPS` does not support `Float8_e4m3fn`, the `fp8` dtype this checkpoint uses.

So the real blocker was not "can I fit this model in RAM?" The real blocker was "can this backend even execute this dtype?" In this setup, the answer was no.

That is a much more useful lesson than a generic "it did not run."

## Why Ollama Feels Different

This also explained something else.

Why can I run quantized LLMs on a Mac, but this video model falls over instantly?

Because the stack is different.

Tools like Ollama and `llama.cpp` do not lean on PyTorch `MPS` in the same way. They use custom Metal kernels and stream work in a way that fits Apple Silicon much better. The Apple path there is more mature.

ComfyUI, for this workflow, is much closer to the generic PyTorch world. And large video diffusion models have not had the same Apple-focused optimization effort that LLM tooling has.

So "LLMs run on Mac" does not automatically mean "large video models run on Mac too."

That assumption did not survive contact with reality.

## What I Learned

First, smaller checkpoint does not mean runnable checkpoint.

Second, backend support beats RAM math. You can spend time estimating whether a model might fit, only to hit a dtype wall before memory becomes the real problem.

Third, Apple Silicon is capable when the tooling is built for it. That last part matters. If the ecosystem is CUDA-first and PyTorch support is partial, you hit edges much sooner.

Fourth, the realistic Apple Silicon path for a model like this is probably not `fp8` in ComfyUI today. It is more likely one of these:

- a smaller model
- a `GGUF` or `q4` conversion with Apple-friendly tooling
- future backend work that dequantizes `fp8` in a way `MPS` can actually handle
- or an NVIDIA box for this class of workload

## The Practical Takeaway

What sent me down this rabbit hole was a simple thought: the smaller checkpoint might fit.

The real answer was harsher and more useful: the checkpoint size was not the blocker. The backend was.

If you are trying to run large video models on Apple Silicon, check dtype and backend support before you download tens of gigabytes and start tuning workflows. That is the first filter, not the last one.

Maybe this changes later. A `GGUF` conversion could change the picture. Better Apple Silicon support in ComfyUI could change it too.

But today, this failure taught me something concrete: on Mac, compatibility is not just about how much RAM you have. It is about whether the stack was actually built for the model format you are holding.
