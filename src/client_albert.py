from typing import Optional
from config import ALBERT_API_KEY, BASE_URL_ALBERT


class ClientAlbert:
    def __init__(self) -> None:
        self.base_url: str = BASE_URL_ALBERT
        self.api_key: Optional[str] = ALBERT_API_KEY
