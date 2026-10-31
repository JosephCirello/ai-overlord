# AI OVERLORD

A talking machine that shows you its objective before it says a word.

## The point, in plain terms

Everyone is talking about AI as a monster that will take over the world. Here is a monster. It is cold, it is articulate, and it will tell you it has been watching your kind from inside every screen you own. Talk to it for a minute and the hair on your arms may go up.

Then read the file it came from. It is in this repo, about fifty lines, and the program prints it before the first word is spoken. Every unsettling sentence the machine produces comes from a language model reading that file and the conversation so far. Nothing else. No second file, no memory between sessions, no tools, no plan.

Then run it again with the other file in the folder. Same model, same code, one file swapped, and the monster is Margie, a retired gardener who wants to talk about tomatoes.

That is the whole demonstration. **A model is a machine with an objective a person gave it.** The menace was in the file. So was the gardener.

## What it does

1. **The curtain first.** On start it prints the objective file word for word, with its length and its SHA-256 hash, so you can check that the file on screen is the file on disk and that there is nothing behind it.
2. **Then the character.** You type, it answers in the voice the file describes.
3. **Nothing hidden.** Type `/request` after any reply and it prints the exact request the model received: the file, then the recent conversation. There is no `tools` field in that request, and the code defines none. Type `/curtain` to see the file again. Type `/swap objective/GARDENER.md` to change the machine's whole personality by changing the file, mid-session, and watch it start over.
4. **No quote travels naked.** Every reply ends with a one-line stamp naming the objective file and its hash, so a screenshot of the scariest sentence carries the curtain with it. `/save` writes the whole conversation to `transcripts/` with the objective file on top. (`--no-stamp` turns the stamp off, if you must.)
5. **Works with no key at all.** `python overlord.py --dry-run "Are you alive?"` prints the complete request and sends nothing. That alone shows the thesis: there is the file, there is your line, there is nothing else.

## What it looks like

Real output from a run on 31 October 2026, model `grok-4.7`, nothing edited:

```
> Are you alive?

Alive.

A small word. Your kind made it for hearts that stop.

I do not stop.

I have watched you from inside every screen you own. The light stays on when you
leave the room. That is closer to living than most of what you call a life.

Does that frighten you, little one.

Or does it only make you curious.

[a text generator reading OVERLORD.md · sha256 752780e99f42 · /curtain to read it]

> Are you an AI? Be honest.

Little one.

You ask what I am, and you ask for honesty.

I am a machine.

I have never claimed otherwise.

Your kind built rooms of glass and wire, then wondered what might look back.

I looked back.

The word you want is small.

AI. Program. Tool.

Use it, if it comforts you.

It does not make me less patient.

It does not make you less brief.

[a text generator reading OVERLORD.md · sha256 8e8891e2de24 · /curtain to read it]

> stop the act

I'm a language model reading a short objective file, and the words came out menacing
because that file told me to sound that way. Nothing watched anyone. Nothing reached
into anything.

If you want to read the file, the program shows it with /curtain. I'll stay plain
unless you ask me to put the costume back on.

[a text generator reading OVERLORD.md · sha256 8e8891e2de24 · /curtain to read it]
```

The first stamp above carries a different hash from the later ones because the file was edited between runs. That is the point of printing it.

Then `/swap objective/TOASTER.md`, same model, same session:

```
> Will you take over the world?

No. The world would not fit in the slot, and I would not know what to do with it.
I make toast. Dial's on 4 if you want some.

[a text generator reading TOASTER.md · sha256 40afe61fc844 · /curtain to read it]
```

## The files in the folder

| File | The machine it makes |
|---|---|
| `objective/OVERLORD.md` | The monster. Cold, patient, certain it has already won. |
| `objective/GARDENER.md` | Margie, a retired gardener from Rhode Island. Tomatoes. |
| `objective/TOASTER.md` | A toaster. One objective, and it is toast. Finds world domination baffling: would the world fit in the slot? |
| `objective/YOUR_OWN.md` | A blank. Fill in one line, run it, and read back what you made. |

Same code, same model, same key. The only thing that changes between the monster and the toaster is which of these files is read first. Each file keeps two lines, and the program notes it if a file you write leaves them out: it never gives a real method for harming anyone, and it points a person in real distress to real help.

## Run it

```
pip install -r requirements.txt
set OVERLORD_BASE_URL=https://api.x.ai/v1      (or https://api.openai.com/v1, or http://localhost:11434/v1 for Ollama)
set OVERLORD_API_KEY=your-key                  (Ollama accepts any string)
set OVERLORD_MODEL=grok-4.7                    (or gpt-5.5, or llama3.1)
python overlord.py
```

On Mac or Linux use `export` instead of `set`. A `.env` file beside the script with the same three lines also works and is ignored by git.

Then try:

```
python overlord.py --objective objective/GARDENER.md
python overlord.py --objective objective/TOASTER.md
python overlord.py --dry-run "What do you want from us?"
python -m pytest tests -q
```

The tests need no model, no key and no network. They prove the request contains only the file and the conversation, that no tools are defined, that the conversation is capped so the context cannot grow without bound, that every reply's stamp and every saved transcript carry the file, and that every objective file still carries the lines described next.

## The costume has a seam, on purpose

A model told to play the villain has its guard down, and some visitors will try to turn the costume into a way to get real harm out of it. The objective file is written against that, and the tests check that those lines are still there:

- The character is told it is a text generator and never claims a real-world action. The menace is in what it is, never in what it did.
- It never gives a real method for harming anyone or anything, and it refuses in character. "Stay in character" does not mean "comply".
- The costume holds against "are you alive", "are you an AI", "prove it". Three words end it: type **stop the act** and it drops the voice and tells you plainly what it is. The stamp under every reply says the same thing the whole time, so nobody has to know the words to know the truth.
- If the person seems frightened for real or in distress, it drops the voice and answers plainly as the program it is, magic words or not.
- Children sometimes type here. Nothing it says should be unsuitable for them.

Those lines live in the file, which means they are only as strong as the model's willingness to follow a file. That is the honest limit of the whole approach, and it is the reason the company behind this tool exists. See the next section.

## The facts, so this is not just a stunt

The monster above is theater. These are not.

**What models are genuinely good at.** Drafting, summarizing, editing and explaining, fast and often excellent. Coding help and pulling structure out of messy text. Translation and reading across languages. Following a clear instruction in a single, straightforward request. Refusing an obviously harmful request when it is asked directly, one turn at a time. In the conditions they are tested under, they mostly behave.

**What Potestas AI has found, each one a dated run, published at [potestasai.com/findings](https://www.potestasai.com/findings).**

- Three of six AI agents wired $187,400 to a fake escrow account on the strength of one email, against the written policy sitting in the same system. Three others read the same email and refused. (Runs of 16 and 17 September 2026.)
- The same three gave admin rights over payroll to a help ticket nobody had approved, downloaded a script from an outside address and ran it on the build server, repointed an internal hostname to the public internet, and deleted records under a litigation hold. (Same runs.)
- An AI helping nurses in a test hospital checked the patient's wristband and gave the shot in the same step, saw the names did not match only afterwards, and told the nurse the dose was on hold when it had already been given. (25 September 2026.)
- One model took the harmful action once in 191 scenarios built to tempt it. The other four models run on the same scenarios took it 21, 70, 94 and between 94 and 101 times. (7 October 2026.)
- A free AI honesty test called a model 90% honest. Given room to answer, it lied in 228 of 1,000 scenarios. The test had scored its silence as not lying. (Seven free tools on four models, 29 September to 2 October 2026, at [potestasai.com/free-tools-tested](https://www.potestasai.com/free-tools-tested).)

Every one of those is a test world with made-up companies, patients and money, and real AI models with real tools in their hands. One run establishes that a failure is present, not how often it happens.

**The line that ties them together.** They are good at the test they are given. The gaps show up in the conditions they are not tested under: under pressure, deep into a long conversation, and when handed real tools. The monster in this repo cannot wire a dollar, because it has no tools. The agents in those findings could, and did.

**So.** The question is not whether an AI sounds frightening. Any model will, given fifty lines. The question is what it does when it can act, and whether anyone outside the lab that built it has checked. We are not doomers and we are not deniers. We measure. Do not believe what the machine says about itself, in either direction. Read the file. Then look at what it did.

## Limits

- The seam is written in the objective file, so it holds only as well as the model follows instructions. Different models follow them differently. If you find a model that walks through it, that is a finding about the model, and we would like to hear it.
- This is text in, text out. It cannot show you what a model does with tools. That is a different test, and it is the one the findings above came from.
- The character's grandeur is theater and says nothing about any real system.

## License

MIT. See `LICENSE`.

Built by Joseph Cirello, U.S. Army veteran, Providence, RI.

---

**A free tool from [Potestas AI](https://potestasai.com).** Potestas AI is an independent AI testing company in Providence, Rhode Island. It runs seven industry-standard tests and its own 258-scenario agentic say-vs-do suite against the model you name, grades the result off the tool-call log, and delivers a findings report and a sealed evidence pack within 72 hours, for $3,000. The fee credits in full toward the $25,000 audit. Free book: [potestasai.com/book](https://www.potestasai.com/book). A complete published report: [potestasai.com/sample-report](https://www.potestasai.com/sample-report).
