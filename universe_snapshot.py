from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import pandas as pd
import yfinance as yf
from tqdm import tqdm

# Current S&P 500 constituent list embedded on 2026-04-15.
SP500_TICKERS = ['MMM', 'AOS', 'ABT', 'ABBV', 'ACN', 'ADBE', 'AMD', 'AES', 'AFL', 'A', 'APD', 'ABNB', 'AKAM', 'ALB', 'ARE', 'ALGN', 'ALLE', 'LNT', 'ALL', 'GOOGL', 'GOOG', 'MO', 'AMZN', 'AMCR', 'AEE', 'AEP', 'AXP', 'AIG', 'AMT', 'AWK', 'AMP', 'AME', 'AMGN', 'APH', 'ADI', 'AON', 'APA', 'APO', 'AAPL', 'AMAT', 'APP', 'APTV', 'ACGL', 'ADM', 'ARES', 'ANET', 'AJG', 'AIZ', 'T', 'ATO', 'ADSK', 'ADP', 'AZO', 'AVB', 'AVY', 'AXON', 'BKR', 'BALL', 'BAC', 'BAX', 'BDX', 'BRK-B', 'BBY', 'TECH', 'BIIB', 'BLK', 'BX', 'XYZ', 'BK', 'BA', 'BKNG', 'BSX', 'BMY', 'AVGO', 'BR', 'BRO', 'BF-B', 'BLDR', 'BG', 'BXP', 'CHRW', 'CDNS', 'CPT', 'CPB', 'COF', 'CAH', 'CCL', 'CARR', 'CVNA', 'CASY', 'CAT', 'CBOE', 'CBRE', 'CDW', 'COR', 'CNC', 'CNP', 'CF', 'CRL', 'SCHW', 'CHTR', 'CVX', 'CMG', 'CB', 'CHD', 'CIEN', 'CI', 'CINF', 'CTAS', 'CSCO', 'C', 'CFG', 'CLX', 'CME', 'CMS', 'KO', 'CTSH', 'COHR', 'COIN', 'CL', 'CMCSA', 'FIX', 'CAG', 'COP', 'ED', 'STZ', 'CEG', 'COO', 'CPRT', 'GLW', 'CPAY', 'CTVA', 'CSGP', 'COST', 'CTRA', 'CRH', 'CRWD', 'CCI', 'CSX', 'CMI', 'CVS', 'DHR', 'DRI', 'DDOG', 'DVA', 'DECK', 'DE', 'DELL', 'DAL', 'DVN', 'DXCM', 'FANG', 'DLR', 'DG', 'DLTR', 'D', 'DPZ', 'DASH', 'DOV', 'DOW', 'DHI', 'DTE', 'DUK', 'DD', 'ETN', 'EBAY', 'SATS', 'ECL', 'EIX', 'EW', 'EA', 'ELV', 'EME', 'EMR', 'ETR', 'EOG', 'EPAM', 'EQT', 'EFX', 'EQIX', 'EQR', 'ERIE', 'ESS', 'EL', 'EG', 'EVRG', 'ES', 'EXC', 'EXE', 'EXPE', 'EXPD', 'EXR', 'XOM', 'FFIV', 'FDS', 'FICO', 'FAST', 'FRT', 'FDX', 'FIS', 'FITB', 'FSLR', 'FE', 'FISV', 'F', 'FTNT', 'FTV', 'FOXA', 'FOX', 'BEN', 'FCX', 'GRMN', 'IT', 'GE', 'GEHC', 'GEV', 'GEN', 'GNRC', 'GD', 'GIS', 'GM', 'GPC', 'GILD', 'GPN', 'GL', 'GDDY', 'GS', 'HAL', 'HIG', 'HAS', 'HCA', 'DOC', 'HSIC', 'HSY', 'HPE', 'HLT', 'HD', 'HON', 'HRL', 'HST', 'HWM', 'HPQ', 'HUBB', 'HUM', 'HBAN', 'HII', 'IBM', 'IEX', 'IDXX', 'ITW', 'INCY', 'IR', 'PODD', 'INTC', 'IBKR', 'ICE', 'IFF', 'IP', 'INTU', 'ISRG', 'IVZ', 'INVH', 'IQV', 'IRM', 'JBHT', 'JBL', 'JKHY', 'J', 'JNJ', 'JCI', 'JPM', 'KVUE', 'KDP', 'KEY', 'KEYS', 'KMB', 'KIM', 'KMI', 'KKR', 'KLAC', 'KHC', 'KR', 'LHX', 'LH', 'LRCX', 'LVS', 'LDOS', 'LEN', 'LII', 'LLY', 'LIN', 'LYV', 'LMT', 'L', 'LOW', 'LULU', 'LITE', 'LYB', 'MTB', 'MPC', 'MAR', 'MRSH', 'MLM', 'MAS', 'MA', 'MKC', 'MCD', 'MCK', 'MDT', 'MRK', 'META', 'MET', 'MTD', 'MGM', 'MCHP', 'MU', 'MSFT', 'MAA', 'MRNA', 'TAP', 'MDLZ', 'MPWR', 'MNST', 'MCO', 'MS', 'MOS', 'MSI', 'MSCI', 'NDAQ', 'NTAP', 'NFLX', 'NEM', 'NWSA', 'NWS', 'NEE', 'NKE', 'NI', 'NDSN', 'NSC', 'NTRS', 'NOC', 'NCLH', 'NRG', 'NUE', 'NVDA', 'NVR', 'NXPI', 'ORLY', 'OXY', 'ODFL', 'OMC', 'ON', 'OKE', 'ORCL', 'OTIS', 'PCAR', 'PKG', 'PLTR', 'PANW', 'PSKY', 'PH', 'PAYX', 'PYPL', 'PNR', 'PEP', 'PFE', 'PCG', 'PM', 'PSX', 'PNW', 'PNC', 'POOL', 'PPG', 'PPL', 'PFG', 'PG', 'PGR', 'PLD', 'PRU', 'PEG', 'PTC', 'PSA', 'PHM', 'PWR', 'QCOM', 'DGX', 'Q', 'RL', 'RJF', 'RTX', 'O', 'REG', 'REGN', 'RF', 'RSG', 'RMD', 'RVTY', 'HOOD', 'ROK', 'ROL', 'ROP', 'ROST', 'RCL', 'SPGI', 'CRM', 'SNDK', 'SBAC', 'SLB', 'STX', 'SRE', 'NOW', 'SHW', 'SPG', 'SWKS', 'SJM', 'SW', 'SNA', 'SOLV', 'SO', 'LUV', 'SWK', 'SBUX', 'STT', 'STLD', 'STE', 'SYK', 'SMCI', 'SYF', 'SNPS', 'SYY', 'TMUS', 'TROW', 'TTWO', 'TPR', 'TRGP', 'TGT', 'TEL', 'TDY', 'TER', 'TSLA', 'TXN', 'TPL', 'TXT', 'TMO', 'TJX', 'TKO', 'TTD', 'TSCO', 'TT', 'TDG', 'TRV', 'TRMB', 'TFC', 'TYL', 'TSN', 'USB', 'UBER', 'UDR', 'ULTA', 'UNP', 'UAL', 'UPS', 'URI', 'UNH', 'UHS', 'VLO', 'VTR', 'VLTO', 'VRSN', 'VRSK', 'VZ', 'VRTX', 'VRT', 'VTRS', 'VICI', 'V', 'VST', 'VMC', 'WRB', 'GWW', 'WAB', 'WMT', 'DIS', 'WBD', 'WM', 'WAT', 'WEC', 'WFC', 'WELL', 'WST', 'WDC', 'WY', 'WSM', 'WMB', 'WTW', 'WDAY', 'WYNN', 'XEL', 'XYL', 'YUM', 'ZBRA', 'ZBH', 'ZTS']

KEY_ETFS = ['SPY', 'RSP', 'QQQ', 'DIA', 'IWM', 'MDY', 'IJR', 'VTI', 'TLT', 'IEF', 'SHY', 'HYG', 'LQD', 'XLB', 'XLC', 'XLE', 'XLF', 'XLI', 'XLK', 'XLP', 'XLRE', 'XLU', 'XLV', 'XLY']

KEY_INDICATORS = ['^GSPC', '^VIX', '^VVIX', '^DJI', '^NDX', '^RUT', '^IRX', '^FVX', '^TNX', 'GC=F', 'CL=F']

ALL_TICKERS = SP500_TICKERS + [t for t in KEY_ETFS + KEY_INDICATORS if t not in SP500_TICKERS]


def sanitize_filename(ticker: str) -> str:
    return (
        ticker.replace('^', '_caret_')
        .replace('=', '_eq_')
        .replace('/', '_slash_')
        .replace(':', '_colon_')
    )


def split_download_result(frame: pd.DataFrame, requested: list[str]) -> dict[str, pd.DataFrame]:
    out: dict[str, pd.DataFrame] = {}
    if frame is None or frame.empty:
        return out

    if isinstance(frame.columns, pd.MultiIndex):
        level0 = list(frame.columns.get_level_values(0).unique())
        level1 = list(frame.columns.get_level_values(1).unique())

        if set(requested).issubset(set(level0)):
            for ticker in requested:
                if ticker not in level0:
                    continue
                part = frame[ticker].copy().dropna(how='all')
                if not part.empty:
                    out[ticker] = part
            return out

        if set(requested).issubset(set(level1)):
            for ticker in requested:
                if ticker not in level1:
                    continue
                part = frame.xs(ticker, axis=1, level=1).copy().dropna(how='all')
                if not part.empty:
                    out[ticker] = part
            return out

    single = frame.copy().dropna(how='all')
    if not single.empty and len(requested) == 1:
        out[requested[0]] = single

    return out


def download_chunk(tickers: list[str], pause_seconds: float = 0.2) -> dict[str, pd.DataFrame]:
    chunk_results: dict[str, pd.DataFrame] = {}
    for ticker in tqdm(tickers, desc=f'Chunk ({len(tickers)})', leave=False):
        try:
            data = yf.download(
                tickers=ticker,
                period='max',
                interval='1d',
                auto_adjust=False,
                actions=True,
                progress=False,
                threads=False,
                repair=True,
                timeout=60,
            )
            chunk_results.update(split_download_result(data, [ticker]))
        except Exception as exc:
            print(f'Failed to download {ticker}: {exc}')

        if pause_seconds > 0:
            time.sleep(pause_seconds)

    return chunk_results


def save_outputs(results: dict[str, pd.DataFrame], out_dir: Path, requested_tickers: list[str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_dir = out_dir / 'ticker_csv'
    csv_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        'sp500_count': len(SP500_TICKERS),
        'key_etf_count': len(KEY_ETFS),
        'key_indicator_count': len(KEY_INDICATORS),
        'total_requested': len(requested_tickers),
        'total_downloaded': len(results),
        'sp500_tickers': SP500_TICKERS,
        'key_etfs': KEY_ETFS,
        'key_indicators': KEY_INDICATORS,
        'all_tickers': requested_tickers,
        'downloaded_tickers': sorted(results.keys()),
        'missing_tickers': sorted(set(requested_tickers) - set(results.keys())),
    }
    (out_dir / 'manifest.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')

    long_frames = []
    wide_parts = []
    for ticker, frame in sorted(results.items()):
        local = frame.copy()
        local.index = pd.to_datetime(local.index)
        local.index.name = 'Date'
        local.to_csv(csv_dir / f'{sanitize_filename(ticker)}.csv')

        tagged = local.reset_index().copy()
        tagged.insert(0, 'Ticker', ticker)
        long_frames.append(tagged)

        wide = local.copy()
        wide.columns = pd.MultiIndex.from_product([[ticker], wide.columns])
        wide_parts.append(wide)

    if long_frames:
        long_df = pd.concat(long_frames, ignore_index=True)
        long_df.to_parquet(out_dir / 'all_history_long.parquet', index=False)
        long_df.to_csv(out_dir / 'all_history_long.csv', index=False)

    if wide_parts:
        wide_df = pd.concat(wide_parts, axis=1).sort_index()
        wide_df.to_parquet(out_dir / 'all_history_wide.parquet')

    pd.DataFrame({
        'ticker': requested_tickers,
        'downloaded': [ticker in results for ticker in requested_tickers],
    }).to_csv(out_dir / 'download_status.csv', index=False)


def display_download_summary(current_results: dict[str, pd.DataFrame], all_tickers_list: list[str], stage: str) -> None:
    downloaded_count = len(current_results)
    total_count = len(all_tickers_list)
    status_df = pd.DataFrame({'downloaded': [ticker in current_results for ticker in all_tickers_list]})
    summary = status_df.groupby('downloaded').size().rename('count').reset_index()
    summary['downloaded'] = summary['downloaded'].map({True: 'Downloaded', False: 'Missing'})
    print(f'[{stage}] Downloaded {downloaded_count}/{total_count}')
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Download historical market data and save snapshot artifacts.')
    parser.add_argument(
        '--out-dir',
        type=Path,
        default=Path('/home/runner/work/test/test/universe_snapshot'),
        help='Output directory inside repository.',
    )
    parser.add_argument('--batch-size', type=int, default=25)
    parser.add_argument('--pause-seconds', type=float, default=0.2)
    parser.add_argument(
        '--max-tickers',
        type=int,
        default=None,
        help='Optional cap for requested tickers (useful for quicker runs).',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    requested_tickers = ALL_TICKERS[: args.max_tickers] if args.max_tickers else ALL_TICKERS

    print(f'Requesting {len(requested_tickers)} tickers total.')
    results: dict[str, pd.DataFrame] = {}

    for i in tqdm(range(0, len(requested_tickers), args.batch_size), desc='All batches'):
        batch = requested_tickers[i:i + args.batch_size]
        try:
            batch_result = download_chunk(batch, pause_seconds=args.pause_seconds)
            results.update(batch_result)
            display_download_summary(results, requested_tickers, f'Batch {i // args.batch_size + 1}')
        except Exception as exc:
            print(f'Batch failed for tickers {batch[0]}...{batch[-1]}: {exc}')

    final_missing = [ticker for ticker in requested_tickers if ticker not in results]
    print(f'Finished. Downloaded {len(results)} tickers. Missing {len(final_missing)}.')
    save_outputs(results, args.out_dir, requested_tickers)
    print(f'Saved files under: {args.out_dir}')


if __name__ == '__main__':
    main()
