
"""
Triggering using our MEG system
To see how to send and receive triggers from the stimulus computer check these examples for Matlab and Python
Triggers are simple voltage changes (or "TTL") sent by the stim PC via the parallel port to acquisition system. The acquisition system receives the stimulation triggers on 8 independent physical lines (black BNC cables connecting the E-prime interface box (receiving signals from the stim PC) to the Elekta trigger box (sending signals to the MEG acquisition system), see Figure 3 in Response Button Mapping section).
Each physical line can be ON (state 1, a pulse is sent) or OFF (state 0, no pulse, no voltage change). The voltage of the pulse is typically 5V but its duration can be variable (and defined as you wish for instance in matlab). The edges from 0V to 5V or 5V to 0V are what can be typically detected by most analysis softwares; most often it is the onset that is being used (from 0 to 5V).

Hence, you have 8 bits to play with to code you events, or a total of [(2^8)-1 = 255] possible triggers that you could use.
These physical lines appear as normal channels in the MEG acquisition system, they are named STI00n and are attributed the (2^n-1) bit: STI001 <=> 2^0 = 1 STI002 <=> 2^1 = 2 STI003 <=> 2^2 = 4 STI004 <=> 2^3 = 8 STI005 <=> 2^4 = 16 STI006 <=> 2^5 = 32 STI007 <=> 2^6 = 64 STI008 <=> 2^7 = 128
The acquisition system has 8 supplementary STI channels (STI009 to STI016) to record additional events. Since triggers from button responses are sent through 10 physical lines (one for each finger, see Figure 3 in Response Collection section for illustration), they are recorded on the last 10 STI channels: STI007 <=> 2^6 = 64 STI008 <=> 2^7 = 128 STI009 <=> 2^8 = 256 STI010 <=> 2^9 = 512 STI011 <=> 2^10 = 1024 STI012 <=> 2^11 = 2048 STI013 <=> 2^12 = 4096 STI014 <=> 2^13 = 8192 STI015 <=> 2^14 = 16384 STI016 <=> 2^15 = 32768

Unfortunately STI007 and STI008 are lines of overlap between the trigger lines and the responses lines. Keep this in mind when coding your triggers: if you really need to record the button response from the ring and pinky finger of the left hand (recorded in channels STI007 and STI008, see this table), avoid stimulus trigger values higher than 63 so that all stimulus trigger values will be recorded in the first 6 STI channels only.
Finally, STI101 emulates an analogue line which sums the voltages across all sixteen STI lines. Hence, if lines STI001 and line STI015 are ON or triggered at the same time, STI101 will read as 16385.

Flavors of trigger definition
Two populations of researchers coexist at Neurospin MEG:
    * Those who use one bit to code one item following this logic: 
if STI001 = 1, then a stimulus is ON if STI001 = 0, then there is no stimulus if STI001 = 1 & STI002 = 1, stim 1 is ON if STI001 = 0 & STI002, stim 2 is OFF etc
    * Those who use a decimal based event coding approach: 
stimulus 1 = 2^0 = 1 stimulus 2 = 2^1 = 2 stimulus 3 = 2^0 + 2^1 = 3 etc
Either work fine: the first one is elegant but the second option, while messier, is more flexible with respect to the number of triggers you can generate. As a tip (but not yet tested!), you could code additional information in the duration of your trigger. For instance, the louder a sound or the brighter a stimulus is in your set, the longer your trigger duration. 
"""


import ctypes #import necesary module
lib = ctypes.WinDLL('inpoutx64.dll')#Load dll from system32
outp = lib['Out32']#Make functions from dll
inp = lib['Inp32'] 
address = 888 #LPT1, address of output port
value = 255 #raise all pins
outp(address, value) 
address = 899 #LPT2, address of input port
inp(address) #read value 


"""
There are a few things you need to insure once you have figured out which triggers you will use for your stimuli:
1. Insure that the mapping is correct i.e. that you have effectively associated the triggers you wish with the stimulus/event you wish in your stimulus delivery software. Do triple-check it!
2. Check that all triggers are being sent correcly to the acquisition computer by hitting "go!" on the ACQ software and looking at the trigger lines (STI001-008).
3. You want to know what are the possible delays between the time you send your trigger to the ACQ software (via the stim PC) and what the subject actually does in real life (i.e. see, hear, make a response etc). For this, you can make an empty room measurement, record the trigger lines, and measure the timing of your stimuli (with a photocell and a microphone) directly placed in the MEG room. Carefully follow the procedure detailed here: measuring stimulus-trigger delays
4. Double-check once more once you have recorded your first pilot that everything is ok, timed ok, coding ok etc...! 
"""