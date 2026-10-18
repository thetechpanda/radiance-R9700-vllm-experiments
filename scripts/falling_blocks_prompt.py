#!/usr/bin/env python3
"""Create a seeded, self-contained Falling Blocks coding task for a tool-using agent."""
import argparse
import random
import sys


VARIANTS = {
    "board": ["10 columns by 18 rows", "10 columns by 20 rows", "12 columns by 20 rows"],
    "palette": ["neon colours on black", "soft pastel colours on a light background", "monochrome arcade palette"],
    "ghost": ["show a translucent landing ghost", "do not show a landing ghost"],
    "queue": ["preview one upcoming piece", "preview three upcoming pieces"],
    "scoring": ["award a flat 100 points per cleared line", "use classic 100/300/500/800 line scoring, scaled by level"],
    "hold": ["include a once-per-drop hold slot", "do not include a hold slot"],
    "sound": ["add optional WebAudio effects with a mute toggle", "keep the game silent"],
}


def make_prompt(seed: int) -> str:
    rng = random.Random(seed)
    keys = rng.sample(list(VARIANTS), k=5)
    requirements = [rng.choice(VARIANTS[key]) for key in keys]
    return f"""Build a complete, playable Falling Blocks game in a single file named falling-blocks.html.

Use only HTML, CSS, Canvas 2D and plain JavaScript. Do not use frameworks,
external assets, network requests or WebGL. Implement collision, rotation,
seven-bag piece selection, gravity, locking, line clears, scoring, levels,
pause, restart, game over and keyboard controls. Make the game usable with
keyboard input and readable on desktop and mobile screens.

Seed: {seed}
Variant requirements:
""" + "".join(f"- {item}\n" for item in requirements) + """

Work in three stages and keep the artefacts separate:
1. Write rules.md with the rules and selected variants for this game.
2. Write plan.md with the game state, data structures, input and rendering plan.
3. Implement falling-blocks.html from those two documents. Then run any useful local
   checks and report the files created and checks performed.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--output", help="write prompt to a file instead of stdout")
    args = parser.parse_args()
    prompt = make_prompt(args.seed)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(prompt)
    else:
        sys.stdout.write(prompt)


if __name__ == "__main__":
    main()
