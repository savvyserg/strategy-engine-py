import csv
import os
from datetime import datetime
from typing import Iterator

from app.domain.candle import Candle
from app.application.ports.driven.candle_source import CandleSourcePort

from app.infrastructure.common.path import resolve_file_path_at_base

class CSVCandleSourceAdapter(CandleSourcePort):
    """
    Concrete Adapter: Reads candles from a CSV file.
    Implements CandleSourcePort.
    """
    def __init__(self, file_name: str = 'input.csv'):
        if not isinstance(file_name, str):
            raise ValueError(f"{type(self).__name__} expected file_name to be a str, found {type(file_name).__name__} '{file_name}'.")

        file_path = resolve_file_path_at_base(file_name)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV Candle Source file not found at: '{file_path}'.")

        self._file_path = file_path
        self._generator = self._create_generator()

    def _create_generator(self) -> Iterator[Candle]:
        """
        Internal generator to handle file opening and lazy reading.
        """
        try:
            with open(self._file_path, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV has required columns.
                required = {'timestamp', 'open', 'high', 'low', 'close'}
                if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                    missing = required - set(reader.fieldnames or [])
                    raise ValueError(f"CSV missing required columns: {missing}")

                for row in reader:
                    yield Candle(
                        timestamp=datetime.fromisoformat(row['timestamp']),
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                    )
        except FileNotFoundError:
            raise FileNotFoundError(f"{type(self).__name__} Error: candle source file not found '{self._file_path}'.")

    def __iter__(self) -> Iterator[Candle]:
        return self

    def __next__(self) -> Candle:
        return next(self._generator)
