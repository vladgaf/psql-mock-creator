"""
Версия приложения PSQL Mock Creator
"""

__version__ = "1.0.0"
__version_info__ = (1, 0, 0)
__build_date__ = "2025-12-28"
__author__ = "https://github.com/vladgaf"
__license__ = "MIT"

# Короткое описание
def get_version_string():
    """Возвращает строку версии"""
    return f"v{__version__}"

def get_full_version_info():
    """Возвращает полную информацию о версии"""
    return {
        "version": __version__,
        "version_info": __version_info__,
        "build_date": __build_date__,
        "author": __author__,
        "license": __license__
    }

if __name__ == "__main__":
    print(f"PSQL Mock Creator {get_version_string()}")
    print(f"Build: {__build_date__}")