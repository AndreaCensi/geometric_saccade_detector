

Frequently asked questions
==========================


* **I noticed that the first saccade in every log is not detected. What gives?**
 
  That saccade is detected, but then discarded. We want to compute the time since the last saccade,
  and we cannot do that for the first saccade in the log.

* **How come the data in the saccade structure is in degrees but the data in rows is in radians?**
  
  Legacy.