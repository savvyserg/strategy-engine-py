import sys
import os
import tomllib

from src.domain import DomainConfigPort

CONFIG_FILE_NAME = "config.toml"

class ConfigAdapter(DomainConfigPort):
    def __setattr__(self, name, value):
        """
        Make config properties immutable after initialization.
        """
        if hasattr(self, name):
            raise AttributeError("immutable")
        object.__setattr__(self, name, value)

    # Make config properties the only properties assignable to this object.
    __slots__ = (
        "_window_size", # number of candles considered for all stats (moving averages, standard deviations, random walk projections, etc)
        "_discount_z_score_threshold", # minimum value for Z-Score in which the market is NOT considered discounted (value < DISCOUNT_Z_SCORE_TRESHOLD is discounted)
        "_euphoria_z_score_threshold", # maximum value for Z-Score in which the market is NOT considered euphoric (value > EUPHORIA_Z_SCORE_THRESHOLD is euphoric)
        "_positive_trend_ma_threshold", # minimum value for MA in which the rend is NOT considered positive (value > POSITIVE_TREND_MA_THRESHOLD is a positive trend)
        "_take_profit_price_constant_k", # take_profit_price = entry_price * (1 + (TAKE_PROFIT_PRICE_CONSTANT_K * standard_deviation))
        "_stop_price_constant_k", # stop_price = entry_price * (1 - (STOP_PRICE_CONSTANT_K * standard_deviation))
        "_stop_z_score", # minimum value that Z-Score should have to satisfy stop condition (Z-Score < STOP_Z_SCORE satisfies stop)
        "_stop_low_z_score_count", # minimum number of low Z-Score values in the latest n that satisfy stop condition (count >= STOP_LOW_Z_SCORE_COUNT satisfies stop)
        "_stop_low_z_score_n", # number of latest Z-Scores to be considered for STOP_LOW_Z_SCORE_COUNT
        "_stop_low_z_score_value", # minimum Z-Score value to NOT be considered low for STOP_LOW_Z_SCORE_COUNT (value < STOP_LOW_Z_SCORE_VALUE is considered low)
    )

    def __init__(self):
        application_path: str = ""
        if getattr(sys, "frozen", False):
            # CASE A: Frozen Executable (Production)
            # The user runs the packaged executable file.
            # We assume the user places config.toml next to the packaged executable.
            application_path = os.path.dirname(sys.executable)
        else:
            # CASE B: Python Script (Development)
            # The user runs 'python src/main.py'.
            # We locate the entry point script (__main__) to find 'src/'.
            # We then go ONE level up to find the Project Root
            import __main__
            if hasattr(__main__, "__file__"):
                # We are running a script (e.g. 'python src/main.py').
                # 1. Get the folder containing the entry script: '.../src'
                entry_dir = os.path.dirname(os.path.abspath(__main__.__file__))
                # 2. Go up one level to find Project Root: '.../Project'
                #    (Assuming main.py is strictly inside 'src/')
                application_path = os.path.dirname(entry_dir)

        if len(application_path) == 0:
            raise RuntimeError("ConfigAdapter failed to find the application path. Something is terribly wrong. Are you executing the app correctly? Please run via main.py.")

        config_path = os.path.join(application_path, CONFIG_FILE_NAME)

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found at: {config_path}.")

        with open(config_path, "rb") as f:
            file_config = tomllib.load(f)

            try:
                window_size = file_config["window_size"]
                self._validate_some(window_size, "window_size")
                self._validate_num_int(window_size, "window_size")
                self._validate_num_positive_non_zero(window_size, "window_size")
                self._window_size = window_size

                discount_z_score_threshold = file_config["discount_z_score_threshold"]
                self._validate_some(discount_z_score_threshold, "discount_z_score_threshold")
                self._validate_num_float(discount_z_score_threshold, "discount_z_score_threshold")
                self._discount_z_score_threshold = discount_z_score_threshold

                euphoria_z_score_threshold = file_config["euphoria_z_score_threshold"]
                self._validate_some(euphoria_z_score_threshold, "euphoria_z_score_threshold")
                self._validate_num_float(euphoria_z_score_threshold, "euphoria_z_score_threshold")
                self._euphoria_z_score_threshold = euphoria_z_score_threshold

                positive_trend_ma_threshold = file_config["positive_trend_ma_threshold"]
                self._validate_some(positive_trend_ma_threshold, "positive_trend_ma_threshold")
                self._validate_num_float(positive_trend_ma_threshold, "positive_trend_ma_threshold")
                self._positive_trend_ma_threshold = positive_trend_ma_threshold

                take_profit_price_constant_k = file_config["take_profit_price_constant_k"]
                self._validate_some(take_profit_price_constant_k, "take_profit_price_constant_k")
                self._validate_num_float(take_profit_price_constant_k, "take_profit_price_constant_k")
                self._take_profit_price_constant_k = take_profit_price_constant_k

                stop_price_constant_k = file_config["stop_price_constant_k"]
                self._validate_some(stop_price_constant_k, "stop_price_constant_k")
                self._validate_num_float(stop_price_constant_k, "stop_price_constant_k")
                self._stop_price_constant_k = stop_price_constant_k

                stop_z_score = file_config["stop_z_score"]
                self._validate_some(stop_z_score, "stop_z_score")
                self._validate_num_float(stop_z_score, "stop_z_score")
                self._stop_z_score = stop_z_score

                stop_low_z_score_count = file_config["stop_low_z_score_count"]
                self._validate_some(stop_low_z_score_count, "stop_low_z_score_count")
                self._validate_num_int(stop_low_z_score_count, "stop_low_z_score_count")
                self._validate_num_positive_non_zero(stop_low_z_score_count, "stop_low_z_score_count")
                self._stop_low_z_score_count = stop_low_z_score_count

                stop_low_z_score_n = file_config["stop_low_z_score_n"]
                self._validate_some(stop_low_z_score_n, "stop_low_z_score_n")
                self._validate_num_int(stop_low_z_score_n, "stop_low_z_score_n")
                self._validate_num_positive_non_zero(stop_low_z_score_n, "stop_low_z_score_n")
                self._stop_low_z_score_n = stop_low_z_score_n

                stop_low_z_score_value = file_config["stop_low_z_score_value"]
                self._validate_some(stop_low_z_score_value, "stop_low_z_score_value")
                self._validate_num_float(stop_low_z_score_value, "stop_low_z_score_value")
                self._stop_low_z_score_value = stop_low_z_score_value
            except KeyError as e:
                raise ValueError(f"Missing configuration key in {CONFIG_FILE_NAME}: {e}.") from e
            except Exception as e:
                raise Exception(f"Failed to load configuration from {CONFIG_FILE_NAME}: {e}") from e

    @property
    def window_size(self) -> int:
        return self._window_size
    
    @property
    def discount_z_score_threshold(self) -> float:
        return self._discount_z_score_threshold
    
    @property
    def euphoria_z_score_threshold(self) -> float:
        return self._euphoria_z_score_threshold
    
    @property
    def positive_trend_ma_threshold(self) -> float:
        return self._positive_trend_ma_threshold
    
    @property
    def take_profit_price_constant_k(self) -> float:
        return self._take_profit_price_constant_k
    
    @property
    def stop_price_constant_k(self) -> float:
        return self._stop_price_constant_k
    
    @property
    def stop_z_score(self) -> float:
        return self._stop_z_score
    
    @property
    def stop_low_z_score_count(self) -> int:
        return self._stop_low_z_score_count
    
    @property
    def stop_low_z_score_n(self) -> int:
        return self._stop_low_z_score_n
    
    @property
    def stop_low_z_score_value(self) -> float:
        return self._stop_low_z_score_value

    @staticmethod
    def _validate_some(value, name: str):
        if value is None:
            raise ValueError(f"Config is missing expected variable {name}.")            

    @staticmethod
    def _validate_num_int(value: int, name: str):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"Config expected {name} to be an int, got {type(value).__name__}.")

    @staticmethod
    def _validate_num_float(value: float, name: str):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"Config expected {name} to be a number, got {type(value).__name__}.")

    @staticmethod
    def _validate_num_positive(value: int, name: str):
        if value < 0:
            raise ValueError(f"Config expected {name} to be positive, got {value}.")
    
    @staticmethod
    def _validate_num_positive_non_zero(value: int, name: str):
        if value <= 0:
            raise ValueError(f"Config expected {name} to be positive and non-zero, got {value}.")

CONFIG_ADAPTER = ConfigAdapter()
