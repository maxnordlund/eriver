# Eriver

Real time Eye Tracking of live sport events for overlay in [CasparCG][1] using [Tobii][2] hardware.

The software is divided into three parts:

* Eye Tracker Server
 This is connected to the eye tracker, reads data from it, packages it in our format and sends it to all subscribers
    
* Statistics and Calibration Server
 Divided into two subparts. One is written in Python and subscribes to eye tracking data. The data it recives is used to generate heatmaps and statistics such as "looks per minute" and "Average look time". The other part is in Node.js, and distrubutes the statistics, as well as provide a webpage, where the user may calibrate the eye trackers. 
 
* CasparCG Flash Subscriber
 Subscribes to eye tracking data and draws the data as points with a trail to a Flash Canvas. This is meant to be played by the Flash Module of [CasparCG][1] 

## TCP Protocol
The protocol that we use between the Eye tracker server and the other two components is defiend as follows:

meaining    cmd   params

getPoint      1   x: <float64> y: <float64> time: <int64>
startCal      2   angle: <float64>
addPoint      3   x: <float64> y: <float64>
clear         4   (nothing)
endCal        5   (nothing)
unavailable   6   (nothing)
name          7   id: <uint8>

cmd är en unsigned byte (0-255)

getPoint with zero filled x,y,time is a getStream
The first time you send getPoint to the eye tracker server it initializes a stream that sends points to you.
The second time you send getPoint it will close that stream

// time is a signed long (int64)

[1]: http://www.casparcg.com/
[2]: http://www.tobii.com/

