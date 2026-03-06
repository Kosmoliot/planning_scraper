from datetime import date, datetime

DATE_MIN = date(1990, 1, 1)
DATE_MAX = date(2030, 12, 31)

DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%d %B %Y",
    "%d %b %Y",
    "%Y-%m-%d",
]

def parse_validated_date(raw):
    """
    Parse a raw date string from the scraper.
    Returns a date object if valid and within DATE_MIN–DATE_MAX, else None.
    """
    if not raw or not raw.strip():
        return None
    raw = raw.strip()
    for fmt in DATE_FORMATS:
        try:
            d = datetime.strptime(raw, fmt).date()
            if DATE_MIN <= d <= DATE_MAX:
                return d
            return None  # out of range
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Status normalisation
# ---------------------------------------------------------------------------

_STATUS_MAP = {
    # PENDING
    "awaiting decision":                        "Pending",
    "pending consideration":                    "Pending",
    "registered":                               "Pending",
    "under consideration":                      "Pending",
    "pending decision":                         "Pending",
    "application in progress":                  "Pending",
    "in progress":                              "Pending",
    "current":                                  "Pending",
    "awaiting legal agreement":                 "Pending",
    "appeal lodged":                            "Pending",
    "no lpa decision in statutory timescale":   "Pending",
    "non-determination":                        "Pending",
    "pending":                                  "Pending",
    "appeal against non determination":         "Pending",

    # APPROVED
    "approved":                                         "Approved",
    "granted":                                          "Approved",
    "permitted":                                        "Approved",
    "application permitted":                            "Approved",
    "application granted":                              "Approved",
    "decided (granted)":                                "Approved",
    "permit":                                           "Approved",
    "permitted with conditions":                        "Approved",
    "application approved with conditions":             "Approved",
    "granted with conditions":                          "Approved",
    "approved subject to conditions":                   "Approved",
    "conditional consent":                              "Approved",
    "consent":                                          "Approved",
    "decided - permitted":                              "Approved",
    "grant listed building consent":                    "Approved",
    "grant permission":                                 "Approved",
    "grant":                                            "Approved",
    "decided (approved)":                               "Approved",
    "prior approval not required":                      "Approved",
    "per - application permitted":                      "Approved",
    "grant consent":                                    "Approved",
    "permitted development":                            "Approved",
    "application approved":                             "Approved",
    "lawful":                                           "Approved",
    "is lawful":                                        "Approved",
    "consent granted":                                  "Approved",
    "non material amendment approved":                  "Approved",
    "time limited planning permission":                 "Approved",
    "approved subject to a s106 agreement":             "Approved",
    "deemed permit":                                    "Approved",
    "appeal allowed":                                   "Approved",
    "permit outline":                                   "Approved",
    "prior approval required and given":                "Approved",
    "granted with s106 conditions":                     "Approved",
    "prior approval given":                             "Approved",
    "grant conservation area consent":                  "Approved",
    "granted temporary permission":                     "Approved",
    "approval of details":                              "Approved",
    "decided (prior approval not required)":            "Approved",
    "allowed":                                          "Approved",
    "allow":                                            "Approved",
    "grant section 191/192 certificate":                "Approved",
    "certificate granted":                              "Approved",
    "permit legal agreement":                           "Approved",
    "unconditional approval (not adverts)":             "Approved",
    "agree non material amendment":                     "Approved",
    "nma conditionally approved":                       "Approved",
    "approved (with legal agreement)":                  "Approved",
    "application permitted with s106(per106)":          "Approved",
    "approval of non-material amendment":               "Approved",
    "prior approval is required - given":               "Approved",
    "grant advert consent":                             "Approved",
    "consent for advert":                               "Approved",
    "grant hazardous substances consent":               "Approved",
    "grant prior approval":                             "Approved",
    "lrb approved":                                     "Approved",
    "certificate issued":                               "Approved",
    "issued":                                           "Approved",
    "discharged conditions in full":                    "Approved",
    "conditions discharged":                            "Approved",
    "deemed consent":                                   "Approved",
    "c of l proposed use- approval":                    "Approved",
    "c of l existing use- approval":                    "Approved",
    "raise no objections":                              "Approved",
    "raise no objections in principle":                 "Approved",
    "no objection":                                     "Approved",
    "no objection lodged":                              "Approved",
    "no observations":                                  "Approved",
    "eia not required":                                 "Approved",
    "env impact assessment not required":               "Approved",
    "environmental statement not required":             "Approved",
    "envrionmental statement not required":             "Approved",
    "prior approval not required":                      "Approved",
    "section 192 determination pp not req":             "Approved",
    "consent for tpo tree works":                       "Approved",
    "consent tree works in conservation area":          "Approved",
    "discharge conditions part approved":               "Approved",
    "discharged conditions in part":                    "Approved",
    "condition complied with":                          "Approved",
    "p2 - planning permission (pre jan 2005)":          "Approved",
    "grant section 191/192 certificate":                "Approved",
    "partially complied with":                          "Approved",
    "deemed consent":                                   "Approved",
    "approved following legal agreement":               "Approved",
    "prior approval required and given":                "Approved",
    "planning permission not required":                 "Approved",
    "planning permssion not required":                  "Approved",

    # REFUSED
    "refused":                                  "Refused",
    "application refused":                      "Refused",
    "refuse":                                   "Refused",
    "decided (refused)":                        "Refused",
    "appeal dismissed":                         "Refused",
    "refuse listed building consent":           "Refused",
    "refuse consent":                           "Refused",
    "certificate refused":                      "Refused",
    "ref - application refused":                "Refused",
    "refusal":                                  "Refused",
    "prior approval required and refused":      "Refused",
    "refuse and enforce":                       "Refused",
    "refusal of details":                       "Refused",
    "prior approval refused":                   "Refused",
    "refuse cert of lawful development":        "Refused",
    "deemed refused":                           "Refused",
    "not lawful":                               "Refused",
    "c of l proposed use- refused":             "Refused",
    "non determination - appeal dismissed":     "Refused",
    "decided - refused":                        "Refused",
    "refuse (departure)":                       "Refused",
    "refuse prior approval":                    "Refused",
    "conditions not discharged":                "Refused",
    "objection raised":                         "Refused",
    "objection lodged":                         "Refused",
    "object":                                   "Refused",
    "objection":                                "Refused",
    "planning permission required":             "Refused",
    "notification not pd pp required":          "Refused",
    "prior approval required and refused":      "Refused",
    "prior approval refused":                   "Refused",

    # WITHDRAWN
    "withdrawn":                                "Withdrawn",
    "application withdrawn":                    "Withdrawn",
    "wdn - application withdrawn":              "Withdrawn",
    "withdrawn/not proceeded with":             "Withdrawn",
    "withdrawn/not proceeded with":             "Withdrawn",
    "case withdrawn":                           "Withdrawn",
    "decided - withdrawn":                      "Withdrawn",

    # DECIDED (ambiguous — portal says decided but outcome unclear)
    "decided":                                  "Decided",
    "application determined":                   "Decided",
    "appeal decided":                           "Decided",
    "split decision":                           "Decided",
    "part approved/part refused":               "Decided",
    "part approved part refused":               "Decided",
    "decided - disposed of":                    "Decided",
    "decided - part approved":                  "Decided",
    "finally disposed":                         "Decided",
    "closed":                                   "Decided",
    "part allowed":                             "Decided",
    "no further action":                        "Decided",
}

NORMALISED_STATUSES = ["Pending", "Approved", "Refused", "Withdrawn", "Decided", "Unknown"]


# ---------------------------------------------------------------------------
# Lead scoring
# ---------------------------------------------------------------------------

# Keywords weighted by relevance to anaerobic digestion / tank equipment sales
_HIGH_VALUE = [
    "anaerobic", "digester", "digestion", "biogas", "biomethane",
    "ad plant", "anaerobic digestion", "anaerobic digester",
]
_MEDIUM_VALUE = [
    "slurry tank", "slurry lagoon", "slurry store", "slurry pit",
    "storage tank", "concrete tank", "water tank", "digestate",
    "biodigester", "gas holder", "gas store", "fermentation tank",
    "effluent tank", "effluent lagoon", "waste water tank",
]
_LOW_VALUE = [
    "slurry", "silo", "farm waste", "organic waste", "sewage",
    "manure", "feedstock", "livestock", "agricultural waste",
    "waste treatment", "composting",
]


def score_lead(summary: str, address: str = "") -> int:
    """
    Return a lead quality score from 1–5 based on keyword matches
    in the summary and address.
      5 = extremely relevant (core AD equipment keywords)
      1 = low relevance
    """
    text = (summary + " " + address).lower()
    score = 0
    for kw in _HIGH_VALUE:
        if kw in text:
            score += 3
    for kw in _MEDIUM_VALUE:
        if kw in text:
            score += 2
    for kw in _LOW_VALUE:
        if kw in text:
            score += 1
    # Normalise to 1–5
    if score == 0:
        return 1
    if score >= 9:
        return 5
    if score >= 6:
        return 4
    if score >= 3:
        return 3
    return 2


SCORE_LABELS = {1: "⬜ Low", 2: "🟦 Moderate", 3: "🟨 Good", 4: "🟧 High", 5: "🟥 Hot"}


def normalise_status(raw):
    """
    Map a raw planning portal status string to one of:
    Pending | Approved | Refused | Withdrawn | Decided | Unknown
    """
    if not raw or not raw.strip():
        return "Unknown"
    return _STATUS_MAP.get(raw.strip().lower(), "Unknown")
