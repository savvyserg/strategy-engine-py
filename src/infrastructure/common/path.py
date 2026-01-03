import sys
import os

def get_base_path() -> str:
    """
    Find the base path to look for external files (like config.toml).

    1. Check if we are running as a PyApp/PyInstaller binary.
       In these cases, sys.executable points to the actual binary file.
       We want the folder containing that binary.

    2. If not, we are in Development (running python main.py).
       We find the project root by looking at where main.py is.
    """
    # 1. Are we running as a packaged binary? (PyApp / PyInstaller).
    # PyApp sets sys.executable to the path of the binary itself.
    # Standard Python sets sys.executable to the python interpreter (e.g., /usr/bin/python).
    executable_path = sys.executable
    executable_name = os.path.basename(executable_path)
    # If the executable is NOT standard python, it's likely a PyApp binary.
    is_standard_python = "python" in executable_name.lower()
    if not is_standard_python or getattr(sys, "frozen", False):
        # CASE: Production (Packaged).
        # We return the folder where the binary sits.
        return os.path.dirname(executable_path)

    # 2. CASE: Development (Script).
    # We are running 'python src/entrypoint/main.py' (or similar).
    import __main__
    if hasattr(__main__, "__file__"):
        # Get the folder containing 'main.py'.
        entry_dir = os.path.dirname(os.path.abspath(__main__.__file__))

        # Traverse up to find root.
        # Level 1: 'root/src -> root'.
        project_root = os.path.dirname(entry_dir)
        return project_root

    # Path should have been found if app is being executed correctly.
    # This pathfinding logic could if the user tries to:
    # - run via an interactive shells (like python REPL).
    # - run a file via terminal that is NOT the entrypoint directly.
    # - run via other weird contexts.
    raise RuntimeError("Failed to find the application path. Something is terribly wrong. Are you executing the app correctly? Please run either the packaged executable, or main.py via terminal.")

def resolve_file_path_at_base(file_name: str) -> str:
    if not isinstance(file_name, str):
        raise ValueError(f"Failed to resolve file path: expected file_name to be a str, found {type(file_name).__name__} '{file_name}'.")

    return os.path.join(get_base_path(), file_name)
