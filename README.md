# What is this?

Docker image based on https://github.com/microsoft/BitNet?tab=readme-ov-file#build-from-source

But includes building llama-server, which isn't done in the original repo.

## Docker Image

### Build

```bash
docker build -f DockerfileAbstratiumPython39 -t abstratium/python39-bitnet .
```

### Run

```bash
docker run \
    --rm -it \
    --name abstratium-bitnet-llm \
    -p 127.0.0.1:19000:8080 \
    abstratium/python39-bitnet
```

### Access

```bash
http://127.0.0.1:19000/
```

## License

See https://github.com/microsoft/BitNet/blob/main/LICENSE which at the time or writing was MIT and copyright Microsoft Corporation.

## Settings in the UI

### Completions

Completes the prompt with the next word(s)

### Chat

#### 🔢 Predictions

Usually refers to the number of tokens to generate.

Can also mean the number of completions to return (in some systems).

Example: If set to 100, the model will try to generate up to 100 tokens in response.

#### 🌡️ Temperature

Controls creativity/randomness of the output.

Higher = more random, lower = more focused/predictable.


Temperature	Behavior Example
0.2	Very deterministic (safe, boring)
0.7	Balanced creativity
1.0+	Wild, unexpected outputs

#### 🔁 Penalize repeat sequence

Discourages the model from repeating the same sequences of tokens.

Helps reduce annoying repetition in generated text.

#### 🔢 Consider N tokens for penalize
This tells the model to look back at the last N tokens to see if anything is being repeated.

Example: If set to 50, the model avoids repeating phrases from the last 50 tokens.

↩️ Penalize repetition of newlines
Specifically avoids repeating \n or blank lines.

Useful when generating lists, code, or markdown, to avoid endless line breaks.

#### 🎯 Top-K sampling

Limits the model to picking from only the top K most likely tokens.

If K = 50, it samples from the top 50 most likely next words, not all possible ones.

A small K = safer and more focused output. Big K = more diversity.

#### 🎲 Top-P sampling (a.k.a. nucleus sampling)

Instead of a fixed number like Top-K, this picks from the top tokens whose total probability adds up to P.

If P = 0.9, it selects from the smallest set of tokens that together have a 90% chance of being correct.

More adaptive than Top-K — good balance of quality + diversity.

#### 📉 Min-P sampling

Filters out all tokens below a certain probability threshold.

Example: If Min-P = 0.01, any token with a probability lower than 1% is ignored.

Helps avoid weird or low-likelihood tokens creeping in.

#### 🧠 TL;DR — Recommended for most tasks:

| Setting | Recommended Starting Point |
|---|---|
| Temperature | 0.7 |
| Top-K | 40–100 |
| Top-P | 0.8–0.95 |
| Min-P | 0.01 |
| Penalize Repeats | On (true) |
| Repeat window (N) | 50–100 |


#### 📝 Prompt

This is the initial instruction or context sent to the model before the conversation.

Often includes persona, tone, or task guidance.

Example:

"You are a helpful customer support agent. Be concise and polite."

This sets the tone for how the model behaves in the entire session.

#### 👤 User Name

Just the display name or label used for the person talking to the bot.

It doesn’t affect the model behavior unless you use it in the prompt template or chat history template.

#### 🤖 Bot Name

Same as above, but for the model.

Again, doesn't affect model behavior directly unless you're inserting it into structured prompts.

#### 🧩 Prompt Template

This defines how the system builds the final prompt that's sent to the model for each message.

You can include placeholders like:

```
{{user}}, {{bot}}

{{history}}

{{message}}
```

Example template:

```
{{history}}
{{user}}: {{message}}
{{bot}}:
```

This template controls how the chat gets serialized into a format the model can understand. Super important for chat-based models.

#### 🕰️ Chat History Template

Similar to the prompt template, but controls how previous messages are formatted.

Used to build {{history}} in the prompt template.

Example:

```
{{user}}: {{message}}
{{bot}}: {{response}}
```

If you want more formatting like role tags or markdown, you’d customize it here.

#### 📚 Grammar

Often refers to structured output formatting (not grammar as in English rules).

Some LLaMA servers (like OpenRouter or tools like LMQL) support structured JSON output via "grammar-based decoding".

If enabled, it forces the model to generate only valid outputs per a defined grammar — e.g., force it to return JSON, XML, or a form.

Example use:

Require output like:

```json
{ "label": "spam" }
```

The grammar would define that structure, and the model is constrained to follow it.

#### TL;DR:

| Setting	|Purpose|
|---|---|
| Prompt	|Initial instructions / persona setup|
| User name / Bot name	|Cosmetic, or used in templating|
| Prompt template	|Formats each prompt to send to the model|
| Chat history template	|Controls how prior turns are shown|
| Grammar	|Optional strict format for model outputs (e.g., JSON)|

## Spam Detection


### Prompt: 

```
You are an expert in email and specifically classifying spam.
You MUST respond with a JSON object, containing two fields, "spam" which may be true or false, and "reason" which is a string containing your explanation about why you think it is spam or not. You will be provided with a raw email body. Important: respond ONLY with JSON.

# Hints:

- References to bitcoins, finance or similar should be considered as spam.
- References to drugs, porn, viagra, etc. are spam.
- Order confirmations are NOT spam.
- Emails selling things are probably spam.
- If the subject sounds too good to be true, it is probably spam.
```

### Grammar:

```
boolean ::= ("true" | "false") space
char ::= [^"\\\x7F\x00-\x1F] | [\\] (["\\bfnrt] | "u" [0-9a-fA-F]{4})
reason-kv ::= "\"reason\"" space ":" space string
root ::= "{" space spam-kv "," space reason-kv "}" space
space ::= | " " | "\n" [ \t]{0,20}
spam-kv ::= "\"spam\"" space ":" space boolean
string ::= "\"" char* "\"" space
```

Temperature: 0.2

