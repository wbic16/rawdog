import argparse
import io
import os
import platform
import readline
from contextlib import redirect_stdout

from rawdog import __version__
from rawdog.llm_client import LLMClient
from rawdog.utils import history_file

llm_client = LLMClient()  # Will fail with descriptive error message if not found


def rawdog(prompt: str, verbose: bool = False):
    _continue = True
    _first = True
    while _continue is True:
        error, script, output = "", "", ""
        try:
            if _first:
                message, script = llm_client.get_script(prompt)
                _first = False
            else:
                message, script = llm_client.get_script()
            if script:
                if verbose:
                    _message = f"{message}\n" if message else ""
                    print(f"{80 * '-'}\n{_message}{script}\n{80 * '-'}")
                    if input("Proceed with execution? (Y/n):").strip().lower() == "n":
                        raise Exception("Execution cancelled by user")
                with io.StringIO() as buf, redirect_stdout(buf):
                    exec(script, globals())
                    output = buf.getvalue()
            elif message:
                print(message)
        except KeyboardInterrupt:
            error = "Execution interrupted by user"
        except Exception as e:
            error = f"Execution error: {e}"

        _continue = output and output.strip().endswith("CONTINUE")
        if error:
            llm_client.conversation.append(
                {"role": "user", "content": f"Error: {error}"}
            )
            print(f"Error: {error}")
            if script and not verbose:
                print(f"{80 * '-'}{script}{80 * '-'}")
        if output:
            llm_client.conversation.append(
                {"role": "user", "content": f"LAST SCRIPT OUTPUT:\n{output}"}
            )
            if verbose or not _continue:
                print(output)


def banner():
    print(
        f"""   / \__
  (    @\___   ┳┓┏┓┏ ┓┳┓┏┓┏┓
  /         O  ┣┫┣┫┃┃┃┃┃┃┃┃┓
 /   (_____/   ┛┗┛┗┗┻┛┻┛┗┛┗┛
/_____/   U    Rawdog v{__version__}"""
    )


def main():
    parser = argparse.ArgumentParser(
        description="A smart assistant that can execute Python code to help or hurt you."
    )
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Prompt for direct execution. If empty, enter conversation mode",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the script before executing and prompt for confirmation.",
    )
    args = parser.parse_args()

    if history_file.exists():
        readline.read_history_file(history_file)
    readline.set_history_length(1000)

    host = platform.uname()[1]
    cwd = os.getcwd()
    if len(args.prompt) > 0:
        rawdog(" ".join(args.prompt))
    else:
        banner()
        while True:
            try:
                print("\nWhat can I do for you? (Ctrl-C to exit)")
                prompt = input(f"{host}@{cwd} > ")
                # Save history after each command to avoid losing it in case of crash
                readline.write_history_file(history_file)
                print("")
                rawdog(prompt, verbose=args.dry_run)
            except KeyboardInterrupt:
                print("Exiting...")
                break
