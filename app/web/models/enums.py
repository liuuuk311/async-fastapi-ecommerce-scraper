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


class UsedProductCondition(enum.StrEnum):
    never_opened = "never_opened"
    like_new = "like_new"
    excellent = "excellent"
    good = "good"
    poor = "poor"
    to_fix = "to_fix"
    broken = "broken"


class UsedProductShippingMethod(enum.StrEnum):
    hand_delivery = "hand_delivery"
    included = "included"
    excluded = "excluded"
