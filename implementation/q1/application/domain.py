import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True)
class AddressData:
    state: str
    city: str
    street: str

    @staticmethod
    def _normalize_string(value: str) -> str:
        value = unicodedata.normalize("NFKD", value)

        return "".join(
            char for char in value
            if not unicodedata.combining(char)
        )

    def normalized(self) -> tuple[str, str, str]:
        return (
            self.state.strip().lower(),
            self._normalize_string(self.city.strip().lower()),
            self._normalize_string(self.street.strip().lower()),
        )
