from app.infrastructure.driven.candle_source.csv import CSVCandleSourceAdapter
from app.infrastructure.driven.journal.csv import CSVJournalAdapter

from app.domain.strategies.random import RandomStrategy
from app.domain.strategies.mean_reversion import MeanReversionStrategy
from app.application.simulation import SimulatedTradingEngine

from app.infrastructure.driven.logger import logger

def main():
    logger.info("--- Starting Simulation ---")
    try:
        logger.info("[Init] Initialing system...")
        logger.info(f"[Init] Loading config...")
        from app.infrastructure.driven.config._impl import CONFIG_ADAPTER
        logger.info(f"[Init] Config loaded.")

        logger.info(f"[Init] Loading candle source...")
        candle_source = CSVCandleSourceAdapter(file_name="input.csv")
        logger.info("[Init] CSV Candle Source ready.")

        logger.info("[Init] Loading strategy engine...")
        if CONFIG_ADAPTER.random_strategy:
            strategy = RandomStrategy(config=CONFIG_ADAPTER)
            logger.info(f"[Init] 'random_strategy' is True. Overriding with '{type(strategy).__name__}'.")
        else:
            strategy = MeanReversionStrategy(config=CONFIG_ADAPTER)
        logger.info(f"[Init] Strategy '{type(strategy).__name__}' initialized.")

        logger.info(f"[Init] Loading journal...")
        journal = CSVJournalAdapter(file_name="output.csv", extra_headers=list(strategy.inspect().keys()))
        logger.info("[Init] CSV Journal ready.")

        logger.info(f"[Ini] Loading trading engine...")
        engine = SimulatedTradingEngine(
            strategy=strategy,
            source=candle_source,
            journal=journal
        )
        logger.info("[Init] Simulated Trading Engine assembled.")
        logger.info("[Init] Initialization finalized successfully.")
    except Exception as e:
        logger.error(f"[Init Fatal] Failed to initialize application: {e}")
        # Re-raise to ensure the process actually exits with an error code.
        raise e

    logger.info("--- Execution Started ---")
    try:
        engine.run()
        logger.info("--- Execution Finished Successfully ---")
        logger.info("Results written to 'output.csv'.")
    except Exception as e:
        logger.error(f"\n[Runtime Fatal] Execution crashed: {e}.")
        raise e

if __name__ == "__main__":
    main()
