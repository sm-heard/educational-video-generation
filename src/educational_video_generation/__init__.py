"""Educational video generation toolkit."""

from importlib import metadata

__all__ = ["__version__"]


def __getattr__(name: str) -> str:
    if name == "__version__":
        try:
            return metadata.version("educational-video-generation")
        except metadata.PackageNotFoundError:
            return "0.0.0-dev"
    raise AttributeError(name)
