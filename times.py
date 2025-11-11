import datetime 

def time_range(start_time, end_time, number_of_intervals=1, gap_between_intervals_s=0): 
    """ 
    Splits a time duration into multiple equal-length, gapped time intervals. 
    Time intervals are left-closed, right-open: [start, end) 
    """ 
    start_time_s = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S") 
    end_time_s = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S") 

    if end_time_s < start_time_s: 
        raise ValueError("The 'end_time' cannot be before the 'start_time'. This time range is backwards.") 

    total_duration_s = (end_time_s - start_time_s).total_seconds() 

    # Ensure the number of intervals is valid 
    if number_of_intervals <= 0: 
        return [] 

    # Calculate the total length of all intervals 
    total_interval_length = total_duration_s - gap_between_intervals_s * (number_of_intervals - 1) 

    # Calculate the length of a single interval 
    d = total_interval_length / number_of_intervals 

    sec_range = [] 
    for i in range(number_of_intervals): 
        # Start time of the interval 
        interval_start_s = start_time_s + datetime.timedelta(seconds=i * (d + gap_between_intervals_s)) 

        # End time of the interval (start time + interval length d) 
        interval_end_s = interval_start_s + datetime.timedelta(seconds=d) 

        # Ensure the end time of the last interval does not exceed the overall end time 
        if i == number_of_intervals - 1: 
                interval_end_s = end_time_s 


        sec_range.append((interval_start_s, interval_end_s)) 

    return [(ta.strftime("%Y-%m-%d %H:%M:%S"), tb.strftime("%Y-%m-%d %H:%M:%S")) for ta, tb in sec_range] 

def compute_overlap_time(range1, range2): 
    """ 
    Calculates the intersection of two time ranges (i.e., lists of time intervals). 
    Returns a list of time intervals where actual overlap occurs. 
    """ 
    overlap_time = [] 

    # Helper function: converts time string to datetime object 
    def str_to_dt(time_str): 
        return datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S") 

    for start1_str, end1_str in range1: 
        start1 = str_to_dt(start1_str) 
        end1 = str_to_dt(end1_str) 

        for start2_str, end2_str in range2: 
            start2 = str_to_dt(start2_str) 
            end2 = str_to_dt(end2_str) 

            # Calculate the start time of the overlap (max of starts) 
            low = max(start1, start2) 
            # Calculate the end time of the overlap (min of ends) 
            high = min(end1, end2) 

            # A valid overlap exists only if low < high (excludes single-point contact and no overlap) 
            if low < high: 
                overlap_time.append(( 
                    low.strftime("%Y-%m-%d %H:%M:%S"), 
                    high.strftime("%Y-%m-%d %H:%M:%S") 
                )) 

    # Note: Based on the original design, we do not sort or merge the results; we only return the list of found overlaps. 
    return overlap_time