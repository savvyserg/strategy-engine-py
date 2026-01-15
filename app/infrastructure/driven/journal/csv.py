import os
import csv
from typing import Optional

from app.domain.candle import Candle
from app.domain.state import Action

from app.application.ports.driven.journal import JournalPort

from app.infrastructure.common.path import resolve_file_path_at_base

class CSVJournalAdapter(JournalPort):
    """
    Concrete Adapter: Writes simulation results to a CSV file.
    Implements JournalPort.
    """
    def __init__(self, file_name: str = 'output.csv', extra_headers: Optional[list[str]] = None):
        if not isinstance(file_name, str):
            raise ValueError(f"{type(self).__name__} expected file_name to be a str, found {type(file_name).__name__} '{file_name}'.")

        file_path = resolve_file_path_at_base(file_name)

        # Validate path is not a directory.
        if os.path.isdir(file_path):
            raise IsADirectoryError(f"{type(self).__name__} Error: output file path '{file_path}' is a directory.")

        # Validate parent directory exists.
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            raise FileNotFoundError(f"{type(self).__name__} Error: output file path parent directory '{parent_dir}' does not exist.")

        self._file_path = file_path
        base_headers = ['timestamp', 'open', 'high', 'low', 'close', 'action', 'equity']
        self._headers = base_headers if not extra_headers else [*base_headers, *extra_headers]
        self._initialize_file()

    def _initialize_file(self) -> None:
        """
        Create the file and write the headers.
        WARNING: This overwrites the file if it exists.
        """
        with open(self._file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._headers)
            writer.writeheader()

    def write(
        self,   
        candle: Candle, 
        action: Optional[Action], 
        equity: float,
        extra_data: Optional[dict] = None,
    ) -> None:
        """
        Append a single row to the CSV.
        """
        # Convert Action Enum to string, or empty string if None.
        action_str = action.name if action else ""

        with open(self._file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self._headers)
            row = {
                'timestamp': candle.timestamp,
                'open': candle.open,
                'high': candle.high,
                'low': candle.low,
                'close': candle.close,
                'action': action_str,
                'equity': equity,
            }
            if extra_data:
                row.update(extra_data)
            writer.writerow(row)
