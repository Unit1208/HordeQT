## Prompt Syntax

While [Prompt.md](doc/prompt.md) deals with the prompt's content, HordeQT has some special features that allow for more advanced prompting.

### {Multiple|Prompts}

When using curly brackets ("{}") and pipes ("|"), multiple prompts can be requested at once. For example, if the prompt supplied is "A **{red|blue}** car", two requests will be made, "A **red** car" and "A **blue** car". This applies with more than two options:
> A **{red|blue|green}** car

1. A **red** car
2. A **blue** car
3. A **green** car

It also applies with multiple options. In this case, *one request for **every** combination* will be made.
> A **{red|blue}** **{car|train}**

1. A red car
2. A blue car
3. A red train
4. A blue train

> [!WARNING]
> This can cause the amount of images requested to grow very, very rapidly.
With the prompt "A {red|green|blue|purple} {high-end|retro|modern} {car|motorcycle}" will generate 24 images.
With the prompt "A {red|green|blue|purple} {high-end|retro|modern} {car|motorcycle|train}" will generate *36* images.

This feature also applies to multiple prompts within multiple prompts.
> A { {light|dark}-green|blue} car

1. A dark-green car
2. A light-green car
3. A blue car
