# Battle-of-Irpin-River
NetLogo Project

This branch is setup by Jonathan, mainly focusing on the movement (currently)
Removed most of the unrelated code framework such as artillery and drones.

3/8 Update: finished Russian movement and logic v1

Check if there is existing bridge: 
if yes, head towards bridge, start crossing, head towards east-side (goal), despawn
if no, head towards shore, wait till soldiers around > building team requirement, wait 1000 ticks, build the bridge, start crossing, head towards east-side (goal), despawn

Search method for bridge / shore currently is "closest"

bridges-list and site-list is hard coded coordinates for bridges and available sites for pontoon construction.
coordinate removed from site-list and added to bridges-list as soon as it is built (complete)

no termination conditions set yet.
