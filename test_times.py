import datetime
import pytest
from times import compute_overlap_time, time_range

# Writing a test for times.py #14
def test_generic_case():
    large = time_range("2010-01-12 10:00:00", "2010-01-12 12:00:00")
    short = time_range("2010-01-12 10:30:00", "2010-01-12 10:45:00", 2, 60)
    expected = [("2010-01-12 10:30:00","2010-01-12 10:37:00"), ("2010-01-12 10:38:00", "2010-01-12 10:45:00")]
    assert compute_overlap_time(large, short) == expected

# Writing multiple tests #15
# two time ranges that do not overlap
def test_non_overlapping_ranges():
    """Test two time ranges that do not overlap."""
    # Test two time ranges that do not overlap
    range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:30:00")
    range2 = time_range("2024-05-15 11:00:00", "2024-05-15 11:30:00")
    expected = []
    
    result = compute_overlap_time(range1, range2)
    assert result == expected

# two time ranges that both contain several intervals each
def test_multiple_interval_overlaps():
    """Test two time ranges, both containing several intervals, ensuring all overlaps are captured."""
    # R1: 10:00:00 - 10:15:00, 2 intervals, 5 minutes gap (300s) => [10:00:00, 10:05:00), [10:10:00, 10:15:00) 
    range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:15:00", 2, 5 * 60)
    # R2: 10:03:00 - 10:17:00, 2 intervals, 4 minutes gap (240s) => [10:03:00, 10:08:00), [10:12:00, 10:17:00) 
    range2 = time_range("2024-05-15 10:03:00", "2024-05-15 10:17:00", 2, 4 * 60)
    
    # Expected Overlaps: [10:03:00, 10:05:00) and [10:12:00, 10:15:00)
    expected = [
        ("2024-05-15 10:03:00", "2024-05-15 10:05:00"), 
        ("2024-05-15 10:12:00", "2024-05-15 10:15:00")
    ]
    
    result = compute_overlap_time(range1, range2)
    assert sorted(result) == sorted(expected)

# two time ranges that end exactly at the same time when the other starts
def test_touching_ranges_no_overlap():
    """Test two time ranges that touch at a single point (R1 ends when R2 starts); intersection should be empty."""
    # R1: [10:00, 10:30)
    range1 = time_range("2024-05-15 10:00:00", "2024-05-15 10:30:00")
    # R2: [10:30, 11:00)
    range2 = time_range("2024-05-15 10:30:00", "2024-05-15 11:00:00")
    expected = []
    
    result = compute_overlap_time(range1, range2)
    assert result == expected

# Input validation and negative tests #16
def test_backward_time_range_raises_error():
    """
    Tests that time_range raises a ValueError when end_time is before start_time.
    Uses pytest.raises for error checking.
    """
    start_time = "2024-05-15 11:00:00"
    end_time = "2024-05-15 10:00:00"  # This is earlier than start_time
    
    # Use pytest.raises to assert that a ValueError is raised
    with pytest.raises(ValueError) as excinfo:
        time_range(start_time, end_time)
        
    # Check if the error message is meaningful
    assert "The 'end_time' cannot be before the 'start_time'. This time range is backwards." in str(excinfo.value)

# Knowing the coverage #18

# To achieve 100% coverage, add tests below
# Test number_of_intervals <= 0

def test_zero_intervals():
    """
    Test that time_range returns an empty list when number_of_intervals is 0.
    This covers the edge case where no intervals are requested.
    """
    result = time_range("2024-05-15 10:00:00", "2024-05-15 12:00:00", number_of_intervals=0)
    assert result == []

def test_negative_intervals():
    """
    Test that time_range returns an empty list when number_of_intervals is negative.
    This ensures the function handles invalid interval counts gracefully.
    """
    result = time_range("2024-05-15 10:00:00", "2024-05-15 12:00:00", number_of_intervals=-5)
    assert result == []

# Test Floating Point Precision Issues
# Correct floating point cumulative errors
def test_floating_point_precision_issue():
    """
    Test time_range with parameters that cause floating point precision issues.
    When total duration doesn't divide evenly by number_of_intervals,
    the last interval's end time needs adjustment to match the exact end_time.
    
    This covers lines 36 and 39 in times.py where interval_end_s is corrected.
    """
    # 10 seconds divided by 3 intervals = 3.333... seconds per interval
    # This will cause floating point precision issues
    result = time_range(
        "2024-05-15 10:00:00",
        "2024-05-15 10:00:10",
        number_of_intervals=3,
        gap_between_intervals_s=0
    )
    
    assert len(result) == 3
    # The last interval should end exactly at the specified end_time
    assert result[-1][1] == "2024-05-15 10:00:10"
    
    # Verify all intervals are present
    assert result[0][0] == "2024-05-15 10:00:00"

# Test floating point precision with gaps
def test_floating_point_with_gaps():
    """
    Test time_range with gaps and floating point precision issues.
    Ensures the last interval ends at exactly end_time even with gaps.
    
    Example: 11 seconds, 3 intervals, 1 second gaps
    Total interval time: 11 - 2*1 = 9 seconds
    Per interval: 9/3 = 3 seconds (exact, but good to test)
    """
    result = time_range(
        "2024-05-15 10:00:00",
        "2024-05-15 10:00:11",
        number_of_intervals=3,
        gap_between_intervals_s=1
    )
    
    assert len(result) == 3
    assert result[-1][1] == "2024-05-15 10:00:11"

# Test precision issues with fractional seconds
def test_very_small_intervals_precision():
    """
    Test with very small time intervals that are more likely to 
    trigger floating point precision issues.
    
    7 seconds / 5 intervals = 1.4 seconds per interval
    This fractional duration tests the precision correction code.
    """
    result = time_range(
        "2024-05-15 10:00:00",
        "2024-05-15 10:00:07",
        number_of_intervals=5,
        gap_between_intervals_s=0
    )
    
    assert len(result) == 5
    # Most importantly, verify the last interval ends exactly on time
    assert result[-1][1] == "2024-05-15 10:00:07"
    


# (base) ➜  time-tests git:(issue-16-validation) ✗ pytest test_times.py -v --cov=times --cov-report=html --cov-report=term-missing