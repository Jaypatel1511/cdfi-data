from cdfidata.sources.tlr import TLRLoader
from cdfidata.sources.clr import CLRLoader
from cdfidata.sources.awards import AwardsLoader
from cdfidata.pipeline.downloader import download_tlr, list_cached, clear_cache
from cdfidata.pipeline.exporter import to_csv, to_sqlite, to_parquet

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("cdfidata")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "TLRLoader", "CLRLoader", "AwardsLoader",
    "download_tlr", "list_cached", "clear_cache",
    "to_csv", "to_sqlite", "to_parquet",
]
