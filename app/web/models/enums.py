import enum


class Currency(enum.StrEnum):
    EUR = "EUR"
    USD = "USD"
    AUD = "AUD"
    CAD = "CAD"
    GBP = "GBP"


class Locale(enum.StrEnum):
    en_US = "en_US"
    it_IT = "it_IT"
