## Prompt

The prompt is one of the most crucial settings of a generation. This is, after all, exactly what you want to see in the image. The method of prompting can vary between models.

### Major prompting types

#### Tagging

#### Danbooru Tagging

While the name may give the impression that [tagging](#tagging) and Danbooru tagging are similar, they differ significantly. Danbooru tagging specifically uses [Danbooru](https://example.com) tagging.
> [!NOTE]
> This category of "Danbooru" tagging more generally applies to other Booru services, like e621 or r34

### Prompting for Model architectures

Different model architectures often prompt in unique ways.

#### Prompting for SD 1.5 and 2.1 models

Stable Diffusion 1.5 and 2.1 models tend to require a "tagging" style of prompting. For example,
> red car, clean garage, detailed, realistic, hyper-realistic, high quality, best quality

#### Prompting for SDXL models

Stable Diffusion XL (SDXL) is slightly better than SD 1.5 and 2.1 at natural language, but still requires tagging. As an example,
> A red car in a clean garage, hyper-realistic, realistic, high quality
SDXL also requires less quality markers to get good results.

##### Prompting for Pony models

While [Pony](https://example.com) models are based on [SDXL](#prompting-for-sdxl-models), Pony models often have very strong support for [Danbooru](#danbooru-tagging) and [e621](https://example.com) tags. These can be very powerful tools to get specific details and attributes

#### Prompting for SD Cascade models

Cascade models prompt quite similarly to [SDXL](#prompting-for-sdxl-models)

#### Prompting for Flux models

Flux models are not technically based on Stable Diffusion, although they do have some similarities. Flux models are better at comprehensible text than any other model. It is also quite good at natural language, and tagging is less effective than with other SD models. When prompting for text, Flux performs the best when the text is in quotes. It also can work better if the text is repeated. For example,
> A detailed cyberpunk sign with the word "FLUX" on it, bold lettering, "FLUX"
