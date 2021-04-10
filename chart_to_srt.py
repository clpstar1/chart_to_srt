import re
import math
from datetime import timedelta
from sys import maxsize
from argparse import ArgumentParser

# can be found in the chord file
SONG_RESOLUTION = 0
            
def parse_lines(lyric_file, tick_map):
    sentence = ''
    sentence_start = 1
    sentence_end = 0
    save_last_line = ''
    is_first_word = True   
    sentence_time_mapping = []

    for line in lyric_file:
        # not relevant 
        if 'section' in line: 
            pass 
        elif 'phrase_start' in line or 'phrase_end' in line:
            tick = get_tick(save_last_line)
            sentence_end = timestamp_to_hms(tick_to_time(tick, SONG_RESOLUTION, tick_map) * 1000)
            sentence_time_mapping.append((sentence_start, sentence_end, sentence))
            sentence = ''
            is_first_word = True 
        else:
            save_last_line = line
            lyric = handle_ending(line)
            sentence += lyric
            if is_first_word:
                tick = get_tick(line)
                sentence_start = timestamp_to_hms(tick_to_time(tick, SONG_RESOLUTION, tick_map) * 1000)
                is_first_word = False

    
    return sentence_time_mapping 

def get_tick(line):
    return int(line.strip().split(' ')[0])

            
def handle_ending(extracted_lyric):
    extracted_lyric = extracted_lyric.replace('"', '').split(' ')[-1]
    if extracted_lyric.endswith('=\n'):
        return re.sub('[=]+\n', '-', extracted_lyric)
    if extracted_lyric.endswith('-\n'):
        return extracted_lyric.replace('-\n', '')
    else: 
        return extracted_lyric.replace('\n', ' ')
        

def timestamp_to_hms(timestamp_ms):
    
    hms = str(timedelta(milliseconds=timestamp_ms))
    hms = hms[0:len(hms)-3]
    hms = hms.replace('.', ',')
    return '0' + hms
    
def convert_to_srt(lyric_data):
    i = 1
    for start, end, lyric in lyric_data:
        print(i)
        print(start + ' --> ' + end)
        print(lyric)
        print('\n', end='')
        i+=1 

# public float TickToTime(uint position, float resolution)
#         {
#             int previousBPMPos = SongObjectHelper.FindClosestPosition(position, bpms);
#             if (bpms[previousBPMPos].tick > position)
#                 --previousBPMPos;

#             BPM prevBPM = bpms[previousBPMPos];
#             float time = prevBPM.assignedTime;
#             time += (float)TickFunctions.DisToTime(prevBPM.tick, position, resolution, prevBPM.value / 1000.0f);

#             return time;
#         }

# public static double DisToTime(uint tickStart, uint tickEnd, float resolution, float bpm)
#         {
#             return (tickEnd - tickStart) / resolution * SECONDS_PER_MINUTE / bpm;
#         }

# dis_to_time and tick_to_time remodeled from moonscraper code above
def dis_to_time(tickstart, tickend, resolution, bpm):
    return ( int(tickend) - int(tickstart) ) / resolution * 60 / bpm

def tick_to_time(position, resolution, tick_map, prev_bpm_assigned_time = 0):
    prev_bpm_tick, prev_bpm_tuple = find_previous_bpm(position, tick_map)
    prev_bpm, prev_bpm_assigned_time = prev_bpm_tuple
    # assuming chord file has bpm * 1000
    time = dis_to_time(prev_bpm_tick, position, resolution, int(prev_bpm) / 1000)
    time += prev_bpm_assigned_time
    return time 



"""Map every BPM Line to: tick -> (bpm, time_it_occurs_in_the_song)"""
def map_ticks(tick_file):
    tick_map = map_ticks_to_bpm(tick_file)
    return assign_songtime_to_bpm(tick_map)
        
    

def map_ticks_to_bpm(tick_file):
    res = {}
    for line in tick_file: 
        if 'B' in line:
            # remove newline
            line = line.strip()
            line = line.split(' ')
            tick = line[0]
            res[tick] = line[3]
    return res

def assign_songtime_to_bpm(tick_map):
    added_songtime = {}

    time = 0
    tick_bpm_list = list(tick_map.items())
    prev_tick, prev_bpm = tick_bpm_list[0]

    for tick, bpm in tick_bpm_list[1:]:
        time += dis_to_time(prev_tick, tick, SONG_RESOLUTION, int(prev_bpm) / 1000)
        added_songtime[tick] = (bpm, time)
        prev_bpm = bpm
        prev_tick = tick
    
    return added_songtime
    

# t = 4
# k = 1,2,3,4.5,
def find_previous_bpm(position, tick_map: dict):
    keys = list(tick_map.keys())
    delta = maxsize
    closest_key = 0
    for i in range(0, len(keys)):
        new_delta = abs(position - int(keys[i]))
        if new_delta < delta:
            delta = new_delta
            closest_key = i

    if int(keys[closest_key]) > position:
        closest_key -= 1
    
    return (keys[closest_key], tick_map[keys[closest_key]])
        

if __name__ == '__main__':
    ap = ArgumentParser()
    ap.add_argument('tick_file')
    ap.add_argument('lyrics_file')
    ap.add_argument('song_resolution', type=int)

    args = ap.parse_args()

    SONG_RESOLUTION = args.song_resolution

    with open(args.tick_file) as tf:
        tick_map = map_ticks(tf)

    with open(args.lyrics_file) as lf:
        lyric_data = parse_lines(lf, tick_map)

    convert_to_srt(lyric_data)