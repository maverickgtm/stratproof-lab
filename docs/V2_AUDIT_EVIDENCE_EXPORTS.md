# Audit Trail CSV Exports

StratProof Lab Community turns each formula audit into inspectable evidence, not just summary cards. After an audit, the Workbench prepares three complementary CSV artifacts with unrestricted downloads.

## The Three Files

| Export | Purpose | What it contains |
|---|---|---|
| Detected operations ledger | Review every formula detection | Entry time and price, TP/SL levels, replay outcome, exit time, score, condition trace, dataset fingerprint and explicit replay disclaimer |
| Source candle path evidence | Reproduce why an outcome was assigned | The OHLCV candles from each detected entry through its exit or replay horizon, linked by operation ID |
| TradingView Portfolio replay import | Visually inspect compatible reconstructed transactions on a chart | Closed `LONG` spot replay entries/exits in TradingView's transaction-import column format |

These files are generated from the same stored candles and formula run used for the report. They do not represent trades placed by StratProof, a broker or an exchange account. Exports also label whether the input was stored historical market data or synthetic offline-demo data, so a demo cannot be mistaken for real-market evidence.

## TradingView Compatibility Boundary

TradingView documents Portfolio transaction import using CSV columns `Symbol`, `Side`, `Qty`, `Fill Price`, `Commission` and `Closing Time`. StratProof produces those columns in its documented format for closed `LONG` spot replay events. The dashboard and companion operations ledger preserve the replay disclaimer because adding unsupported informational columns could make the TradingView import invalid.

Use this export to visualize reconstructed entries and exits against a TradingView-supported symbol. It is not an independent re-execution of the StratProof formula and it does not prove that an account placed those trades. Short or derivative replays remain fully documented in the operations and candle-path exports, but are not converted into Portfolio transaction rows in Community v2.

Official TradingView documentation:

- [How to add transactions via file import](https://www.tradingview.com/support/solutions/43000756014-how-to-add-transactions-via-file-import/)
- [CSV file formatting for Portfolio import](https://www.tradingview.com/support/solutions/43000756010-how-to-create-a-portfolio-via-transaction-import/)

## How to Use the TradingView Visual Cross-Check

1. Run a StratProof strict audit using `spot` market data and a `LONG` hypothesis.
2. In **Audit Trail Downloads**, download:
   - **Detected operations ledger (CSV)** for the condition trace and replay outcome.
   - **Source candle path evidence (CSV)** for the supporting OHLCV path.
   - **TradingView Portfolio replay import (CSV)** when the dashboard reports rows greater than zero.
3. Open TradingView and create or open a Portfolio.
4. Open the Portfolio **Transactions** tab, choose its import action, and upload the TradingView replay CSV.
5. When TradingView asks how to handle transactions, use merge behavior unless you intentionally want to replace transactions already in that Portfolio.
6. Inspect the imported entry and exit events on TradingView-supported symbols, then compare questionable events to the matching `operation_id` and candle path in the first two StratProof exports.

TradingView currently documents a `25 MB` maximum import file size and adds transactions only for supported instruments. If an import reports a format or symbol error, use the operations ledger and candle-path exports as the source audit artifacts while investigating compatibility.

### What This Confirms

- The reconstructed entry and exit times/prices can be inspected visually in an independent charting interface.
- The symbol is resolvable by TradingView when the import succeeds.
- A user can challenge suspicious replays rather than trusting summary statistics alone.

### What This Does Not Confirm

- TradingView does not rerun StratProof indicator blocks or score thresholds.
- TradingView does not validate the `condition_trace` field.
- Imported replay transactions are not brokerage fills or proof of trades executed in a real account.
- Synthetic demo inputs remain synthetic even if TradingView displays their imported rows.

## Audit Procedure

1. Download real public candle history from an implemented Community connector.
2. Build and run a strict formula audit.
3. Download the operations ledger and verify each condition trace.
4. Open the candle-path export and inspect the linked OHLCV path for selected operation IDs.
5. For eligible `LONG` spot replay rows, import the TradingView CSV into Portfolio to visually compare reconstructed timestamps and prices with the chart; return to the operations ledger and candle path for formula-level audit evidence.

## Evidence Boundary

The exports document historical replay detections over stored public candles. They are reproducibility artifacts, not brokerage confirmations, investment advice, trading signals or performance guarantees.
