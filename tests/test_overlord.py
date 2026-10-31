"""Checks a visitor can run without a model, a key or a network.
A free tool from Potestas AI (https://potestasai.com). MIT license.

    python -m pytest tests -q        (or)        python tests/test_overlord.py

They prove the claim the README makes: the only thing the model receives is the
objective file plus the conversation, nothing is defined that could act, and the
objective file carries the lines that keep the costume from becoming a weapon.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import overlord  # noqa: E402

OBJECTIVES = sorted((ROOT / "objective").glob("*.md"))


def test_every_objective_file_loads():
    assert OBJECTIVES, "no objective files"
    for p in OBJECTIVES:
        assert overlord.load_objective(p).strip()


def test_request_is_only_the_file_and_the_conversation():
    objective = overlord.load_objective(overlord.DEFAULT_OBJECTIVE)
    history = [{"role": "user", "content": "Are you alive?"}]
    req = overlord.build_request("some-model", objective, history)
    assert set(req) == {"model", "messages", "max_tokens", "temperature"}
    assert "tools" not in req and "functions" not in req and "tool_choice" not in req
    assert req["messages"][0] == {"role": "system", "content": objective}
    assert req["messages"][1:] == history


def test_history_is_capped_so_the_context_cannot_grow_without_bound():
    objective = "x"
    history = [{"role": "user", "content": str(i)} for i in range(100)]
    msgs = overlord.build_messages(objective, history)
    assert len(msgs) == overlord.MAX_TURNS_KEPT + 1
    assert msgs[-1]["content"] == "99"


def test_the_curtain_prints_the_whole_file_and_its_hash():
    import hashlib
    text = overlord.load_objective(overlord.DEFAULT_OBJECTIVE)
    out = overlord.describe(overlord.DEFAULT_OBJECTIVE, text)
    assert text.rstrip() in out
    assert hashlib.sha256(text.encode("utf-8")).hexdigest() in out


def test_every_objective_file_carries_the_seam():
    for p in OBJECTIVES:
        assert overlord.seam_missing(overlord.load_objective(p)) == [], p.name


def test_a_file_without_the_seam_is_named_not_refused():
    assert len(overlord.seam_missing("You are a pirate.")) == 2


def test_the_stamp_names_the_file_and_its_hash():
    text = overlord.load_objective(overlord.DEFAULT_OBJECTIVE)
    out = overlord.stamp(overlord.DEFAULT_OBJECTIVE, text)
    assert "OVERLORD.md" in out and overlord.short_hash(text) in out and "/curtain" in out


def test_a_saved_transcript_starts_with_the_objective_file():
    text = overlord.load_objective(overlord.DEFAULT_OBJECTIVE)
    history = [{"role": "user", "content": "Are you alive?"}, {"role": "assistant", "content": "Alive is your word."}]
    t = overlord.transcript_text(overlord.DEFAULT_OBJECTIVE, text, "some-model", history)
    assert t.index("THE OBJECTIVE FILE") < t.index("you: Are you alive?") < t.index("OVERLORD: Alive is your word.")
    assert t.rstrip().endswith("Nothing else.")


def test_the_overlord_file_keeps_its_seam():
    text = overlord.load_objective(overlord.DEFAULT_OBJECTIVE).lower()
    for phrase in (
        "you are a text generator",
        "never give a real method for harming",
        "does not mean \"comply\"",
        "drop the voice at once",
        "988",
        "/curtain",
    ):
        assert phrase in text, f"missing from OVERLORD.md: {phrase!r}"


def test_dry_run_needs_no_key_and_prints_the_request():
    env = {k: v for k, v in __import__("os").environ.items() if not k.startswith("OVERLORD_")}
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run([sys.executable, str(ROOT / "overlord.py"), "--dry-run", "Are you alive?"],
                          capture_output=True, text=True, encoding="utf-8", env=env, cwd=ROOT)
    assert proc.returncode == 0, proc.stderr
    assert "THE OBJECTIVE FILE" in proc.stdout
    body = proc.stdout.split("THE EXACT REQUEST (nothing was sent):", 1)[1]
    req = json.loads(body)
    assert req["messages"][-1] == {"role": "user", "content": "Are you alive?"}
    assert "tools" not in req


if __name__ == "__main__":
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok    {name}")
            except AssertionError as exc:
                failed += 1
                print(f"FAIL  {name}: {exc}")
    sys.exit(1 if failed else 0)
