## Samplers

**Samplers** (also called **schedulers**) change the result of an image, but don't typically have a major impact on the actual content. They change how the image is guided at each step.

The simplest, and most common sampler is `k_euler`, also simply called `Euler`. This sampler tends to work well enough in almost every circumstance, but may not be the best.

### k_euler family: k_euler, k_heun, and k_lms

`k_euler`, `k_euler_a`, `k_heun`, and `k_lms` all belong to a similar family of samplers. They tend to result in similar images, with only slight differences in result. `k_lms` and `k_heun` can be better, but it tends to be a personal preference.

**Unless you are told or know otherwise, use `k_euler` by default**

### DPM samplers

DPM (Diffusion Probabilistic Method) samplers (`k_dpm_2`,`k_dpm_2_a`, `k_dpm_adaptive`, `k_dpm_fast`, `k_dpm_2s_a`, `k_dpmpp_2m`, and `k_dpmpp_sde`) are samplers specially designed for Stable Diffusion. These can be better than [Euler](#keuler-family-keuler-kheun-and-klms) samplers, but they can differ.

### Ancestral samplers

Ancestral samplers, usually suffixed by `_a`, are slightly different than their corresponding non-ancestral samplers.
`k_euler_a`, `k_dpm_2_a`, and `k_dpm_2s_a` are examples are ancestral samplers. Ancestral samplers have two key properties:

- Ancestral samplers are non-deterministic
- Ancestral samplers do not converge

#### Ancestral samplers are non-deterministic

Ancestral samplers, when given the same [seed](/doc/seed.md), **will not give the same result.**
When using them, there is no point in giving a set seed. Even with the same exact parameters, images generated with ancestral samplers will not be reproducible.
