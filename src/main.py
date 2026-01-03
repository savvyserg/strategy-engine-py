from src.infrastructure.driven.config._impl import CONFIG_ADAPTER
from src.infrastructure.driven.candle_source.csv import CSVCandleSourceAdapter
from src.infrastructure.driven.journal.csv import CSVJournalAdapter

from src.domain.strategies.random import RandomStrategy
from src.domain.strategies.mean_reversion import MeanReversionStrategy
from src.application.simulation import SimulatedTradingEngine

def main():
    print("--- Starting Simulation ---")

    print(f"[Init] Configuration loaded.")

    candle_source = CSVCandleSourceAdapter(file_name="input.csv")
    print("[Init] CSV Candle Source ready.")

    journal = CSVJournalAdapter(file_name="output.csv")
    print("[Init] CSV Journal ready.")

    if CONFIG_ADAPTER.random_strategy:
        strategy = RandomStrategy(config=CONFIG_ADAPTER)
        print(f"[Init] 'RANDOM_STRATEGY' is True. Overriding with '{type(strategy).__name__}'.")
    else:
        strategy = MeanReversionStrategy(config=CONFIG_ADAPTER)
        print(f"[Init] Strategy '{type(strategy).__name__}' initialized.")

    engine = SimulatedTradingEngine(
        strategy=strategy,
        source=candle_source,
        journal=journal
    )
    print("[Init] Simulated Trading Engine assembled.")

    print("--- Execution Started ---")
    try:
        engine.run()
        print("--- Execution Finished Successfully ---")
        print("Results written to 'output.csv'.")
    except Exception as e:
        print(f"\n[Error] Execution crashed: '{e}'.")
        raise e

if __name__ == "__main__":
    main()
