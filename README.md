# What is it? 
Maps Lyrics from Clone Hero .chart files to SRT Subtitle Format 

# Usage
## Preparation
1. Open up the specific .chord file
2. Go to the SyncTrack and the Events Section
3. Extract the content of these sections into two separate files. (only the lines starting with numbers! (wich are ticks used by clone-hero))
4. Look up the resolution of the song in the Song section of the .chord file

## Script Execution
1. Install Python if you haven't
2. Run the script with python parse.py /path/to/tickfile /path/to/lyricsfile resolution 

The script will print the result to stdout so you can redirect it to a srt file.

On Linux: python parse.py /path/to/tickfile /path/to/lyricsfile resolution > out.srt 
