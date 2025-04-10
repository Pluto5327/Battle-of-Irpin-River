# Battle-of-Irpin-River
NetLogo Project

TODO:
- 1) (Done) Change infantry to travel in vehicles, so up speed, fix troop nums and depth, relabel them in code, and turn on their collisions with the PMP trucks again
- 2) (Done) Add in acceleration/deceleration for vehicles
- 3) (Almost Done) Add second and third spawn/entry points (each assigned to a few sites), maybe making a dictionary or some way to tell each unit leaving that entry point where to turn
- a) (Done) Fix: make sure only chosen-site-ids are considered for each entry-point list during spawning (instead of all sites always being used)
- b) (Done) Addition: Add extra turn east and turn north to south-entry movement path, that roughly follows black and grey line
- c) (Done) Fix (more urgent): make sure no random stoppages happen in the middle of the road with no reason (double check for movement bugs)
- d) (Done) Fix (not urgent): Casualty ratio in UI monitor showing values greater than 1 currently
- 4) Vary (i.e. create dropdown menus) for the other 2 independent variables. they should already have hardcoded params in the code, they should just now accept UI menu input to configure them:
  a) waving/spacing
  b) ordering
- 5) Run behavior space tests
