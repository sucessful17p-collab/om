"""Conservative, explainable screening aid; not a complete legal determination."""
from datetime import date
from app.schemas.section_479 import ScreeningInput, ScreeningResult

RULE_VERSION = "BNSS-479-2023-v1"
RULE_EFFECTIVE_DATE = date(2024, 7, 1)
RULE_SOURCE = "Bharatiya Nagarik Suraksha Sanhita, 2023 (Act 46 of 2023), Section 479 — India Code"
RULE_SOURCE_URL = "https://www.indiacode.nic.in/bitstream/123456789/21544/1/the_bharatiya_nagarik_suraksha_sanhita%2C_2023.pdf"
RULE_REVIEWER = "Pending qualified legal review"

def screen_section_479(data: ScreeningInput) -> ScreeningResult:
    flags: list[str] = []
    reasons: list[str] = [f"Applied configured rule {RULE_VERSION} ({RULE_SOURCE}); legal verification remains pending."]
    maximum_reached = False

    if data.conviction_status == "convicted":
        return ScreeningResult(status="not_indicated", rule_version=RULE_VERSION, elapsed_days=None, excluded_delay_days=None, credited_custody_days=None, threshold_days=None, threshold_fraction=None, reasons=reasons + ["The record is marked convicted; this undertrial screening path does not apply."], review_flags=[])
    if data.conviction_status == "unknown": flags.append("Confirm current case and conviction status from an authoritative record.")
    if data.custody_start is None:
        flags.append("Custody start date is missing; elapsed detention cannot be calculated.")
        elapsed = excluded = credited = threshold = None
    elif data.custody_start > data.assessment_date:
        flags.append("Custody start date is later than the assessment date; resolve the date conflict.")
        elapsed = excluded = credited = threshold = None
    else:
        elapsed = (data.assessment_date - data.custody_start).days
        excluded = min(data.accused_delay_days or 0, elapsed) if data.accused_delay_verified else 0
        credited = elapsed - excluded
        threshold = None
        if excluded:
            reasons.append(f"{excluded} documented accused-attributable delay day(s) were excluded from this preliminary calculation; legal review must verify the attribution and applicable treatment.")

    if data.record_conflict: flags.append("Conflicting records require reconciliation by an authorised reviewer.")
    if data.accused_delay_days and not data.accused_delay_verified:
        flags.append("Reported accused-attributable delay has not been verified; no days were excluded from this calculation.")
    if data.accused_delay_days and data.accused_delay_verified:
        flags.append("Verify the legal basis and source record for excluding accused-attributable delay.")
    if not data.custody_record_verified: flags.append("Custody record has not been verified against an authoritative source.")
    if data.maximum_imprisonment_years is None:
        flags.append("Maximum imprisonment is missing; no sentence limit was assumed.")
    elif not data.sentence_limit_verified:
        flags.append("Maximum imprisonment is not marked legally verified; threshold result requires legal review.")
    if data.first_time_offender is None:
        flags.append("First-time-offender status is unknown; it was not inferred from missing data.")
    if data.multiple_pending_cases is None:
        flags.append("Multiple-offence/case status is unknown and requires review under the applicable statutory conditions.")
    elif data.multiple_pending_cases:
        flags.append("Multiple pending offences/cases reported; statutory conditions require case-specific legal review.")
    if data.court_order_continued_detention is None:
        flags.append("Check whether the court has ordered continued detention after the statutory hearing and recorded reasons.")
    elif data.court_order_continued_detention:
        flags.append("A continued-detention order is reported; obtain and review the court order before acting on this screen.")
    if data.punishable_with_death is None or data.life_imprisonment_specified is None:
        flags.append("Confirm applicable offence exclusions, including death or life imprisonment as specified by the provision.")
    elif data.punishable_with_death or data.life_imprisonment_specified:
        flags.append("Reported offence may fall within a statutory exclusion; refer for legal review.")

    fraction = None
    excluded_offence = data.punishable_with_death is True or data.life_imprisonment_specified is True
    if data.maximum_imprisonment_years is not None and data.first_time_offender is not None:
        # Days are a transparent approximation for screening; operational legal calculation must validate the applicable limit.
        fraction = 1 / 3 if data.first_time_offender else 1 / 2
        threshold = round(data.maximum_imprisonment_years * 365.25 * fraction)
        reasons.append(f"Configured threshold: {fraction:.0%} of the supplied maximum sentence ({threshold} days), using {'first-time-offender' if fraction < 0.5 else 'general'} threshold. Verify statutory definitions, other conditions and sentence computation.")
        if credited is not None and credited >= round(data.maximum_imprisonment_years * 365.25):
            maximum_reached = True
            flags.append("Custody reaches or exceeds the supplied maximum sentence period; urgently verify the sentence basis, exclusions and court orders with counsel.")
    elif data.maximum_imprisonment_years is not None:
        reasons.append("The maximum sentence was supplied, but the applicable threshold was not calculated because first-time-offender status is unknown.")

    enough_known = all([
        data.custody_start is not None, credited is not None,
        data.maximum_imprisonment_years is not None, data.first_time_offender is not None,
        data.multiple_pending_cases is not None, data.punishable_with_death is not None,
        data.life_imprisonment_specified is not None,
        data.court_order_continued_detention is not None,
        data.conviction_status == "undertrial", not data.record_conflict,
        data.custody_record_verified, data.sentence_limit_verified,
        not (data.accused_delay_days and not data.accused_delay_verified),
    ])
    if not enough_known or data.multiple_pending_cases or data.court_order_continued_detention or maximum_reached:
        status = "legal_review_required"
    elif excluded_offence:
        status = "not_indicated"
    elif data.multiple_pending_cases or credited < (threshold or 0):
        status = "not_indicated"
    else:
        status = "potentially_eligible_for_court_consideration"
        reasons.append("The supplied, verified facts reach the configured threshold. This is only a prompt for authorised application and court consideration; it is not automatic release.")
    return ScreeningResult(status=status, rule_version=RULE_VERSION, elapsed_days=elapsed, excluded_delay_days=excluded, credited_custody_days=credited, threshold_days=threshold, threshold_fraction=fraction, reasons=reasons, review_flags=flags)
