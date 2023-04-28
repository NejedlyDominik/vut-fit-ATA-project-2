#!/usr/bin/env python3

"""
ATA - Project 2 - Trolley control in a robotic factory

login: xnejed09
name: Dominik Nejedly
year: 2023

Dynamic analyser of a cart controller.
"""

NUMBER_OF_SLOTS = 4
MAX_LOAD_CAPACITY = 150

station_slot_coverage_matrix = {
    'A': [False] * NUMBER_OF_SLOTS,
    'B': [False] * NUMBER_OF_SLOTS,
    'C': [False] * NUMBER_OF_SLOTS,
    'D': [False] * NUMBER_OF_SLOTS
}
slot_occupancy_flags = [False] * NUMBER_OF_SLOTS
requests = []
currently_loaded_cargo = []
occupied_slot_count = 0
currently_loaded_weight = 0
idle_time = None
all_props_hold = True


def report_error(time, msg):
    global all_props_hold
    all_props_hold = False
    print(f'{int(time)}:error: {msg}')


def report_coverage():
    """Coverage reporter"""
    covered_station_slots_count = sum([slot_flags.count(True) for slot_flags in station_slot_coverage_matrix.values()])
    print('CartCoverage %d%%' % ((covered_station_slots_count / (NUMBER_OF_SLOTS * len(station_slot_coverage_matrix))) * 100))


def onrequesting(time, src, dst, content, weight):
    """`Requesting` property event-handler"""
    requests.append((src, dst, content, int(weight)))


def onloading(time, pos, content, weight, slot):
    """`Loading` property event-handler"""
    global occupied_slot_count, currently_loaded_weight
    weight_int = int(weight)
    slot_int = int(slot)
    
    if 0 <= slot_int < NUMBER_OF_SLOTS:
        if pos in station_slot_coverage_matrix:
            station_slot_coverage_matrix[pos][slot_int] = True
       
        # Monitor the property 1.
        if slot_occupancy_flags[slot_int]:
            report_error(time, f'loading into an occupied slot #{slot_int} (content: {content}; weight: {weight_int}; position: {pos})')
        
        slot_occupancy_flags[slot_int] = True
        
    # Monitor the property 5.
    req_idx = None
    
    for i, (req_src, req_dst, req_content, req_weight) in enumerate(requests):
        if req_src == pos and req_content == content and req_weight == weight_int:
            currently_loaded_cargo.append((req_dst, content, weight_int))
            req_idx = i
            break
        
    if req_idx is None:
        report_error(time, f'loading without request (content: {content}; weight: {weight_int}; position: {pos})')
    else:
        requests.pop(req_idx)
        
    # Monitor the property 6.
    occupied_slot_count += 1
    
    if occupied_slot_count > NUMBER_OF_SLOTS:
        report_error(time, f'more than 4 simultaneously occupied slots (content: {content}; weight: {weight_int}; position: {pos})')
    
    # Monitor the property 7.
    currently_loaded_weight += weight_int
    
    if currently_loaded_weight > MAX_LOAD_CAPACITY:
        report_error(time, f'cart overload (content: {content}; weight: {weight_int}; position: {pos})')


def onunloading(time, pos, content, weight, slot):
    """`Unloading` property event-handler"""
    global occupied_slot_count, currently_loaded_weight
    weight_int = int(weight)
    slot_int = int(slot)
    
    if 0 <= slot_int < NUMBER_OF_SLOTS:     
        # Monitor the property 2.
        if not slot_occupancy_flags[slot_int]:
            report_error(time, f'unloading from an empty slot #{slot_int} (content: {content}; weight: {weight_int}; position: {pos})')
            
        slot_occupancy_flags[slot_int] = False
    
    unloaded_part = (pos, content, weight_int)
       
    if unloaded_part in currently_loaded_cargo:
        currently_loaded_cargo.remove(unloaded_part)
    
    occupied_slot_count -= 1
    currently_loaded_weight -= weight_int


def onmoving(time, pos1, pos2):
    """`Moving` property event-handler"""
    # Monitor the property 3.
    for dst, content, weight in currently_loaded_cargo:
        if dst == pos1:
            report_error(time, f'cargo has not been unloaded at its final destination (content: {content}; weight: {weight}; position: {dst})')


def onevent(event):
    """Event handler. event = [TIME, EVENT_ID, ...]"""
    global idle_time
    # Get the event identification from the given tuple.
    event_id = event[1]
    del(event[1])
    event_time = int(event[0])
    
    if event_id == 'idle' and requests:
        idle_time = event_time
    else:
        if event_id == 'requesting':
            onrequesting(*event)
        elif event_id == 'loading':
            onloading(*event)
        elif event_id == 'unloading':
            onunloading(*event)
        elif event_id == 'moving':
            onmoving(*event)
        
        # Monitor the property 9.
        if idle_time is not None and idle_time < event_time:
            report_error(event_time, 'idle cart when a request exists')
            
        idle_time = None


def monitor(reader):
    """Main function"""
    time = None
    
    for line in reader:
        line = line.strip()
        split_line = line.split()
        time = split_line[0]
        onevent(split_line)
    
    # Monitor the property 4.
    if requests:
        report_error(time, f'there is a request that did not cause the loading (number of not loaded requests: {len(requests)})')
        
    # Monitor the porperty 8.
    if currently_loaded_cargo:
        report_error(time, f'there is a loaded cargo that was not unloaded (number of these loads : {len(currently_loaded_cargo)})')
        
    if all_props_hold:
        print('All properties hold.')
        
    report_coverage()


if __name__ == "__main__":
    import sys
    monitor(sys.stdin)
