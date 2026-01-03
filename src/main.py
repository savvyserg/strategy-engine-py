from src.infrastructure.driven.config._impl import CONFIG_ADAPTER
from src.infrastructure.driven.candle_source.csv import CSVCandleSourceAdapter
from src.infrastructure.driven.journal.csv import CSVJournalAdapter

from src.domain.strategies.random import RandomStrategy
from src.domain.strategies.mean_reversion import MeanReversionStrategy
from src.application.simulation import SimulatedTradingEngine

from src.infrastructure.driven.logger import logger

def main():
    logger.info("--- Starting Simulation ---")

    logger.info(f"[Init] Configuration loaded.")

    candle_source = CSVCandleSourceAdapter(file_name="input.csv")
    logger.info("[Init] CSV Candle Source ready.")

    journal = CSVJournalAdapter(file_name="output.csv")
    logger.info("[Init] CSV Journal ready.")

    if CONFIG_ADAPTER.random_strategy:
        strategy = RandomStrategy(config=CONFIG_ADAPTER)
        logger.info(f"[Init] 'RANDOM_STRATEGY' is True. Overriding with '{type(strategy).__name__}'.")
    else:
        strategy = MeanReversionStrategy(config=CONFIG_ADAPTER)
        logger.info(f"[Init] Strategy '{type(strategy).__name__}' initialized.")

    engine = SimulatedTradingEngine(
        strategy=strategy,
        source=candle_source,
        journal=journal
    )
    logger.info("[Init] Simulated Trading Engine assembled.")

    logger.info("--- Execution Started ---")
    try:
        engine.run()
        logger.info("--- Execution Finished Successfully ---")
        logger.info("Results written to 'output.csv'.")
    except Exception as e:
        logger.error(f"\n[Error] Execution crashed: {e}.")
        raise e

if __name__ == "__main__":
    main()
