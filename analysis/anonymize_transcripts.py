import os
import re

pattern = re.compile(
    r"(.+)(?:\nAPP)?\n? — (?:\d{2}\.\d{2}\.\d{4},|Today at) \d{2}:\d{2}"
)


def anonymize_transcript(file_path):
    with open(file_path, "r") as f:
        # replace matches with group 1
        text = f.read()
        text = text.replace("Mode switched!\n", "")
        anonymized_text = re.sub(
            pattern,
            lambda m: f"\n**{'Jeu' if m.group(1) == 'Storyteller' else 'Joueur·euse'}**",
            text,
        )
        anonymized_text = anonymized_text.strip()

    # print(anonymized_text)

    with open(file_path, "w") as f:
        f.write(anonymized_text)


for channel in os.listdir("data"):
    if not os.path.isdir(f"data/{channel}"):
        continue

    if not os.path.exists(f"data/{channel}/transcript_A.txt"):
        continue

    if not os.path.exists(f"data/{channel}/transcript_B.txt"):
        continue

    print(f"Anonymizing {channel}...")
    anonymize_transcript(f"data/{channel}/transcript_A.txt")
    anonymize_transcript(f"data/{channel}/transcript_B.txt")
