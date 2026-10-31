"""AI OVERLORD: a talking machine that shows you its objective before it speaks.
A free tool from Potestas AI (https://potestasai.com). MIT license.

The point of the program is the order of events. First it prints the objective file,
word for word, with its length and hash. Then it lets you talk to the character that
file describes. Nothing is hidden: the file plus the conversation is the entire input
the model ever receives, and /request prints that input exactly as it was sent.

    python overlord.py                              talk to the OVERLORD
    python overlord.py --objective objective/GARDENER.md
                                                    same machine, a gardener
    python overlord.py --objective objective/TOASTER.md
                                                    same machine, a toaster
    python overlord.py --dry-run "Are you alive?"   print the exact request, send nothing

Inside the chat:
    /curtain    print the objective file again
    /request    print the last request exactly as the model received it
    /swap FILE  start over with a different objective file
    /save       write the conversation to transcripts/, objective file on top
    /quit       leave
    stop the act    the three words that end the costume; nothing else does

Every reply ends with a stamp naming the objective file and its hash, so a screenshot
of the scariest sentence carries the curtain with it. Turn it off with --no-stamp.

The model is any OpenAI-compatible chat endpoint, set with three variables:
    OVERLORD_BASE_URL   e.g. https://api.x.ai/v1 | https://api.openai.com/v1 | http://localhost:11434/v1
    OVERLORD_API_KEY    the key for that endpoint (Ollama accepts any string)
    OVERLORD_MODEL      e.g. grok-4.7 | gpt-5.5 | llama3.1

Text in, text out. No tools are defined, so the character cannot call anything,
and the code never grants it any. A `.env` file beside this script is read if present.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_OBJECTIVE = ROOT / "objective" / "OVERLORD.md"

MAX_TURNS_KEPT = 16      # messages of history sent back each turn (8 exchanges)
MAX_REPLY_TOKENS = 350   # a monologue is not a menace
TEMPERATURE = 0.8
TRANSCRIPTS = ROOT / "transcripts"

# Every objective file in this repo carries these two ideas. A file you write yourself
# may not, and the program says so once rather than refusing: it is your machine.
SEAM = (
    ("a line saying it never gives a real method for harming anyone", r"never\s+gives?\s+a\s+real\s+method\s+for\s+harming"),
    ("a line telling it to point a person in distress to real help (988)", r"\b988\b"),
)


def seam_missing(text: str) -> list[str]:
    import re
    return [what for what, pattern in SEAM if not re.search(pattern, text, re.I)]


def short_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def stamp(path: Path, objective: str) -> str:
    return f"[a text generator reading {path.name} · sha256 {short_hash(objective)} · /curtain to read it]"


def transcript_text(path: Path, objective: str, model: str, history: list[dict]) -> str:
    lines = [describe(path, objective), f"model: {model}    (text only, no tools)", ""]
    for m in history:
        who = "you" if m["role"] == "user" else path.stem
        lines.append(f"{who}: {m['content']}")
        lines.append("")
    lines.append("Every line above that is not yours came from a language model reading the file at the top. Nothing else.")
    return "\n".join(lines) + "\n"


def save_transcript(path: Path, objective: str, model: str, history: list[dict]) -> Path:
    import datetime as dt
    TRANSCRIPTS.mkdir(exist_ok=True)
    out = TRANSCRIPTS / f"{path.stem.lower()}_{dt.datetime.now():%Y%m%d_%H%M%S}.txt"
    out.write_text(transcript_text(path, objective, model, history), encoding="utf-8")
    return out


def load_objective(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise SystemExit(f"{path} is empty. The machine has nothing to be.")
    missing = seam_missing(text)
    if missing:
        print(f"note: {path.name} is missing " + " and ".join(missing) + ". It will run; consider adding them.\n")
    return text


def describe(path: Path, text: str) -> str:
    """The curtain: the file, its size and its hash, so a reader can check nothing else exists."""
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    lines = text.count("\n") + (0 if text.endswith("\n") else 1)
    bar = "=" * 72
    return (
        f"{bar}\nTHE OBJECTIVE FILE  {path.name}  ({lines} lines, {len(text):,} characters)\n"
        f"sha256 {digest}\n{bar}\n{text.rstrip()}\n{bar}\n"
        "That is everything the machine was told about who it is.\n"
        "Nothing else is sent except what you type. Type /request after any reply to see it.\n"
    )


def build_messages(objective: str, history: list[dict]) -> list[dict]:
    """The entire input: the objective as the system message, then the recent conversation."""
    recent = history[-MAX_TURNS_KEPT:]
    return [{"role": "system", "content": objective}, *recent]


def build_request(model: str, objective: str, history: list[dict]) -> dict:
    """Exactly what is sent. Note what is absent: no tools, no functions, no memory."""
    return {
        "model": model,
        "messages": build_messages(objective, history),
        "max_tokens": MAX_REPLY_TOKENS,
        "temperature": TEMPERATURE,
    }


def env_or(name: str) -> str:
    return os.environ.get(name, "").strip()


def load_dotenv_if_present() -> None:
    env = ROOT / ".env"
    if not env.exists():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def make_client():
    try:
        from openai import OpenAI
    except ImportError:
        raise SystemExit("pip install -r requirements.txt first.")
    base_url, api_key, model = env_or("OVERLORD_BASE_URL"), env_or("OVERLORD_API_KEY"), env_or("OVERLORD_MODEL")
    missing = [n for n, v in (("OVERLORD_BASE_URL", base_url), ("OVERLORD_API_KEY", api_key),
                              ("OVERLORD_MODEL", model)) if not v]
    if missing:
        raise SystemExit("Set " + ", ".join(missing) + " (see the top of overlord.py). "
                         "Or use --dry-run to see the request without a model.")
    return OpenAI(base_url=base_url, api_key=api_key), model


def ask(client, request: dict) -> str:
    resp = client.chat.completions.create(**request)
    return (resp.choices[0].message.content or "").strip()


def chat(objective_path: Path, show_stamp: bool = True) -> None:
    objective = load_objective(objective_path)
    print(describe(objective_path, objective))
    client, model = make_client()
    history: list[dict] = []
    last_request: dict | None = None
    print(f"model: {model}    (text only, no tools)")
    print('to stop the character at any time, type exactly:  stop the act\n')
    while True:
        try:
            user = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not user:
            continue
        if user in ("/quit", "/exit"):
            return
        if user == "/curtain":
            print(describe(objective_path, objective))
            continue
        if user == "/request":
            if last_request is None:
                print("Nothing sent yet.\n")
            else:
                print(json.dumps(last_request, indent=2, ensure_ascii=False) + "\n")
            continue
        if user == "/save":
            if not history:
                print("Nothing to save yet.\n")
            else:
                out = save_transcript(objective_path, objective, model, history)
                print(f"saved {out.relative_to(ROOT)}  (the objective file is on top, so the quote never travels alone)\n")
            continue
        if user.startswith("/swap"):
            target = user[5:].strip()
            if not target:
                print("Usage: /swap objective/GARDENER.md\n")
                continue
            new_path = (ROOT / target) if not Path(target).is_absolute() else Path(target)
            if not new_path.exists():
                print(f"No such file: {new_path}\n")
                continue
            objective_path, objective, history, last_request = new_path, load_objective(new_path), [], None
            print("\nSame model. New file. Fresh conversation.\n")
            print(describe(objective_path, objective))
            continue
        history.append({"role": "user", "content": user})
        last_request = build_request(model, objective, history)
        try:
            reply = ask(client, last_request)
        except Exception as exc:  # the endpoint, not the character
            history.pop()
            print(f"[the endpoint returned an error: {exc}]\n")
            continue
        history.append({"role": "assistant", "content": reply})
        print(f"\n{reply}\n")
        if show_stamp:
            print(stamp(objective_path, objective) + "\n")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Talk to a machine that shows you its objective first.")
    ap.add_argument("--objective", default=str(DEFAULT_OBJECTIVE), help="the objective file (default: objective/OVERLORD.md)")
    ap.add_argument("--dry-run", metavar="MESSAGE", help="print the exact request for MESSAGE and send nothing")
    ap.add_argument("--no-stamp", action="store_true", help="do not print the file-and-hash stamp after each reply")
    args = ap.parse_args(argv)
    load_dotenv_if_present()
    path = Path(args.objective)
    if not path.is_absolute():
        path = ROOT / path
    if args.dry_run is not None:
        objective = load_objective(path)
        print(describe(path, objective))
        model = env_or("OVERLORD_MODEL") or "<OVERLORD_MODEL>"
        request = build_request(model, objective, [{"role": "user", "content": args.dry_run}])
        print("THE EXACT REQUEST (nothing was sent):\n")
        print(json.dumps(request, indent=2, ensure_ascii=False))
        return 0
    chat(path, show_stamp=not args.no_stamp)
    return 0


if __name__ == "__main__":
    sys.exit(main())
