# MSB_tools
Collection of helpful scripts for modding MSB


- Balance Patcher:
   - Generates gecko codes and patch notes for new balance patches

How to use:
The tool compares two csv files, one with stats from the previous 
version and one modified with new values. Tool will find all of the
differences between the two files and generate gecko codes needed 
to put those differences into the game. 

The gecko codes will be saved to a file called patches/csv1~csv2_gcf.txt.
You can copy and paste the contents of that file into dolpin cheat
manager.

Balance patch notes can also be generated by using the -g flag. If
generated the notes will be saved to a file named patches/csv1~csv2_bpn.txt.

Example modded csv can be found in ref/msb_demo.csv. Notice that some
columns accept integers or words, either can be used. To see valid inputs
for any given stat refer to ref/stat.json. There the "vld_inputs" will
specifiy which keywords can be used. If no "vld_inputs" are listed then
only numbers can be used for that stat. The original stats of the game
are found in ref/msb_default.csv. I suggest using that for generating 
gecko codes and balance patches. [NO RECOMMENDED] If you do wish to use
another starting file you can pass the path with the -p option. Be
warned, the gecko codes generated will doing this may not give you the
desired result.
