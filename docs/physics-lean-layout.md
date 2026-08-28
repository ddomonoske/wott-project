# New feature added to physics engine
Add a new feature that allows the lean-angle of a cyclist to be accounted for in the physics simulation. This should be a toggle that can be turned on and off from the simulation page. The toggle should be called "Track Curvature". If it is off, the simulation runs as it currently is configured. If it is on, the following calculations and adjustments are performed.

A simulation run with a track curvature of 0 should return the exact same results as the existing simulation, and that very well might be what happens when the toggle is off.

## Selecting parameters
When the toggle is on, there is an option to enter the track length L. The default is 250 meters.

There is also a slider to specify the track shape. The selectable range is from 0.20 to 1. 1 is labeled "circle" and 0.20 is labeled "hotdog". The default is 0.60.

The physical meaning of this parameter is the percent of the total track distance that the corners make up. A track is an oval with two straights and two corners. 100% means there are no straights and the entire track is comprised of the corners, so a circle. 80% means each straight makes up 40% of the track distance, and each corner is just 10% of the distance. This is the maximum because it is unrealistic to have a tighter corner.

## Calculating track curvature
Curvature is 1/radius that the track is curving around at the instant, with radius measured in meters. The straights have 0 curvature. The matlab script ~/Documents/MATLAB/Cycling/track_corners_pln.m for details on the calculations.

