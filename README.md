Eriver
===========

Real time Eye Tracking of live sport events for overlay in [CasparCG][1] using [Tobii][2] hardware.

The software is divided into three parts:

* Eye Tracker Server
 This is connected to the eye tracker, reads data from it, packages it in our format and sends it to all subscribers
    
* Statistics and Calibration Server
 Divided into two subparts. One is written in Python and subscribes to eye tracking data. The data it recives is used to generate heatmaps and statistics such as "looks per minute" and "Average look time". The other part is in Node.js, and distrubutes the statistics, as well as provide a webpage, where the user may calibrate the eye trackers. 
 
* CasparCG Flash Subscriber
 Subscribes to eye tracking data and draws the data as points with a trail to a Flash Canvas. This is meant to be played by the Flash Module of [CasparCG][1] 
 
[1]: http://www.casparcg.com/
[2]: http://www.tobii.com/

