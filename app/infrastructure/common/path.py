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
    # 1.A PyApp Check (Ideally):
    # PyApp SHOULD set this environment variable to the absolute path of the binary.
    # This is the only reliable way to know where the user actually ran the file from.
    pyapp_binary = os.environ.get("PYAPP_EXEC_PATH")
    if pyapp_binary:
        return os.path.dirname(os.path.abspath(pyapp_binary))

    # 1.B PyApp Context Check (Fallback):
    # If the "PYAPP_EXEC_PATH" Env Var is missing, we check if we are running inside the extracted cache.
    # PyApp extracts code to directories containing "pyapp" or "site-packages".
    current_file = os.path.abspath(__file__)
    if "site-packages" in current_file or "pyapp" in current_file:
        # We are definitely inside the cached/unzipped environment.
        # When executed, the pyapp binary unpacks a full Python environment and the application code into a local cache directory.
        # - e.g., `~/.local/share/pyapp/...` on Linux or `%LOCALAPPDATA%\pyapp` on Windows.
        # - The application runs *from this cache directory*, not from the location of the binary.
        # Since we don't know the binary path, we rely on the Current Working Directory (CWD).
        # Since PYAPP_EXEC_PATH failed, we default to the Current Working Directory.
        # On Windows/Linux/Mac, running a binary (CLI or GUI) usually sets CWD to the binary's folder.
        return os.getcwd()

    # 2. PyInstaller Check:
    if getattr(sys, "frozen", False):
        executable_path = sys.executable
        return os.path.dirname(executable_path)

    # 3. Development Check (Standard python script):
    # We are running 'python app/main.py' (or similar).
    import __main__
    if hasattr(__main__, "__file__"):
        # Get the folder containing 'main.py'.
        entry_dir = os.path.dirname(os.path.abspath(__main__.__file__))

        # Traverse up to find root.
        # Level 1: 'root/app -> root'.
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
