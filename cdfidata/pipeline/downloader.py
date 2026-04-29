"""
Download and cache CDFI Fund public datasets locally.
Files are cached to avoid repeated downloads.
"""
import os
import zipfile
import requests
from pathlib import Path

from cdfidata.utils.schema import CACHE_DIR, TLR_URLS


def get_cache_dir() -> Path:
    """Return and create the local cache directory."""
    path = Path(CACHE_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def cache_path(filename: str) -> Path:
    """Return the full cache path for a given filename."""
    return get_cache_dir() / filename


def is_cached(filename: str) -> bool:
    """Check if a file is already cached locally."""
    return cache_path(filename).exists()


def download_file(url: str, filename: str, force: bool = False) -> Path:
    """
    Download a file from a URL and cache it locally.

    Args:
        url:      Full URL to download from
        filename: Local filename to save as
        force:    Re-download even if cached

    Returns:
        Path to the cached file
    """
    path = cache_path(filename)

    if path.exists() and not force:
        print(f"Using cached file: {path}")
        return path

    print(f"Downloading {filename}...")
    print(f"URL: {url}")

    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    downloaded = 0

    with open(path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r  {pct:.1f}% ({downloaded/1e6:.1f}MB)", end="")

    print(f"\nSaved to {path}")
    return path


def extract_zip(zip_path: Path, extract_to: Path = None) -> list:
    """
    Extract a zip file to the cache directory.

    Args:
        zip_path:   Path to the zip file
        extract_to: Directory to extract to (default: cache dir)

    Returns:
        List of extracted file paths
    """
    extract_to = extract_to or get_cache_dir()

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        zf.extractall(extract_to)
        print(f"Extracted {len(names)} files to {extract_to}")

    return [extract_to / name for name in names]


def download_tlr(year: int, force: bool = False) -> Path:
    """
    Download TLR/CLR zip file for a given fiscal year.

    Args:
        year:  Fiscal year e.g. 2022
        force: Re-download even if cached

    Returns:
        Path to the downloaded zip file
    """
    if year not in TLR_URLS:
        available = list(TLR_URLS.keys())
        raise ValueError(
            f"No TLR URL available for FY{year}. "
            f"Available years: {available}"
        )

    url = TLR_URLS[year]
    filename = f"TLR_CLR_FY{year}.zip"
    return download_file(url, filename, force=force)


def list_cached() -> list:
    """List all files currently in the local cache."""
    cache = get_cache_dir()
    files = list(cache.iterdir())
    if not files:
        print("Cache is empty.")
    else:
        print(f"Cached files in {cache}:")
        for f in sorted(files):
            size_mb = f.stat().st_size / 1e6
            print(f"  {f.name} ({size_mb:.1f}MB)")
    return files


def clear_cache() -> None:
    """Delete all cached files."""
    cache = get_cache_dir()
    count = 0
    for f in cache.iterdir():
        f.unlink()
        count += 1
    print(f"Cleared {count} cached files from {cache}")
