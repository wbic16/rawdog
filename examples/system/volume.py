conversation = [
    {
        "role": "user",
        "content": "Can you change the system volume to max?"
    }
]

metadata = {
    "model": "openai/gpt-4-turbo-preview",
    "cost": "0.0107000000",
    "timestamp": "2024-02-07_12-30-03",
    "log_version": 0.1
}


def main():
    import os
    os.system("osascript -e 'set volume output volume 100'")
    print("System volume set to maximum.")


if __name__ == "__main__":
    main()
