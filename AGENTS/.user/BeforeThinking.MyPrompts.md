# BeforeThinking.MyPrompts.md

Function: `Add(new Prompt)`

Before thinking about a developer request, append that verbatim prompt to
[`AGENTS/.user/MyPrompts.md`](MyPrompts.md).

```sh
python3 SRC/tools/user_prompts.py before-thinking
python3 SRC/tools/user_prompts.py before-thinking "verbatim prompt"
python3 SRC/tools/user_prompts.py add "verbatim prompt"
```

The first form reads the prompt from stdin. The Python function is
`user_prompts.before_thinking(root, prompt)`, which calls
`user_prompts.add_prompt(root, prompt)`.

Rules:

- Record the prompt before Git reconciliation, planning, or implementation.
- Keep the request verbatim; only trailing whitespace is normalized.
- Do not write resolved account, repository, branch, or commit values here.
- Do not replace earlier entries; only append.
