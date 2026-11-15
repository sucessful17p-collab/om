from datetime import date, timedelta
from app.schemas.section_479 import ScreeningInput
from app.legal_rules.section_479 import screen_section_479

def facts(**overrides):
    base = dict(custody_start=date(2023, 1, 1), assessment_date=date(2026, 1, 2), maximum_imprisonment_years=6, first_time_offender=False, conviction_status="undertrial", punishable_with_death=False, life_imprisonment_specified=False, multiple_pending_cases=False, court_order_continued_detention=False, accused_delay_days=0, custody_record_verified=True, sentence_limit_verified=True)
    return ScreeningInput(**(base | overrides))

def test_general_half_threshold_can_prompt_court_consideration():
    result = screen_section_479(facts())
    assert result.status == "potentially_eligible_for_court_consideration"
    assert result.threshold_fraction == .5

def test_first_time_threshold_uses_one_third():
    result = screen_section_479(facts(first_time_offender=True))
    assert result.threshold_fraction == 1 / 3

def test_offence_exclusion_never_marks_potentially_eligible():
    result = screen_section_479(facts(punishable_with_death=True))
    assert result.status == "not_indicated"

def test_life_imprisonment_exclusion_never_marks_potentially_eligible():
    result = screen_section_479(facts(life_imprisonment_specified=True))
    assert result.status == "not_indicated"

def test_multiple_cases_require_legal_review():
    result = screen_section_479(facts(multiple_pending_cases=True))
    assert result.status == "legal_review_required"
    assert any("Multiple pending" in flag for flag in result.review_flags)

def test_missing_custody_is_review_not_assumed():
    result = screen_section_479(facts(custody_start=None))
    assert result.status == "legal_review_required"
    assert result.elapsed_days is None

def test_unknown_first_time_status_does_not_assume_general_threshold():
    result = screen_section_479(facts(first_time_offender=None))
    assert result.threshold_fraction is None
    assert result.threshold_days is None

def test_unknown_maximum_sentence_does_not_guess():
    result = screen_section_479(facts(maximum_imprisonment_years=None))
    assert result.threshold_days is None
    assert result.status == "legal_review_required"

def test_unknown_court_order_status_requires_review():
    result = screen_section_479(facts(court_order_continued_detention=None))
    assert result.status == "legal_review_required"

def test_continued_detention_order_requires_review():
    result = screen_section_479(facts(court_order_continued_detention=True))
    assert result.status == "legal_review_required"

def test_supplied_maximum_period_reached_routes_urgently_to_review():
    result = screen_section_479(facts(custody_start=date(2018, 1, 1)))
    assert result.status == "legal_review_required"
    assert any("urgently verify" in flag for flag in result.review_flags)

def test_documented_delay_is_subtracted_conservatively():
    result = screen_section_479(facts(accused_delay_days=50, accused_delay_verified=True))
    assert result.excluded_delay_days == 50
    assert result.credited_custody_days == result.elapsed_days - 50

def test_unverified_delay_is_not_subtracted():
    result = screen_section_479(facts(accused_delay_days=50))
    assert result.excluded_delay_days == 0
    assert any("not been verified" in flag for flag in result.review_flags)

def test_conflict_and_unverified_maximum_require_review():
    result = screen_section_479(facts(record_conflict=True, sentence_limit_verified=False))
    assert result.status == "legal_review_required"

def test_dates_in_future_require_review():
    result = screen_section_479(facts(custody_start=date(2026, 1, 3)))
    assert result.status == "legal_review_required"

def test_convicted_record_not_screened_as_undertrial():
    result = screen_section_479(facts(conviction_status="convicted"))
    assert result.status == "not_indicated"
