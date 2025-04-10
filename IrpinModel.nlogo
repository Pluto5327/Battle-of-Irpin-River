globals [
  water-color
  pontoon-color
  goal-color
  grass-color
  artillery-fire-color
  site-ys
  all-site-ids
  chosen-site-ids
  site-infantry-units-per-road
  site-builder-count
  site-pontoon-count
  site-pontoon-built-count
  site-pontoon-bridge-built
  site-bridge-drawing-start-x
  site-bridge-drawing-end-x
  time-of-last-site-activity
  site-current-activity-duration
  activity-cooldown-time
  infantry-unit-depth
  truck-unit-depth
  infantry-road-speed
  truck-road-speed
  artillery-fire-animation-x
  dirt-roads-start-x
  infantry-dirt-speed
  truck-dirt-speed
  truck-pontoon-module-capacity
  num-required-builders-per-site
  num-required-pontoons-per-site
  artillery-just-fired
  pontoon-module-setup-time
  artillery-alpha
  artillery-beta
  time-between-drone-checks
  total-pontoons-built
  total-infantry-crossed
  win-num-crossers-threshold
  loss-battle-duration-threshold
  battle-outcome
  total-infantry-used
  total-pontoons-used
  total-infantry-casualties
  curr-spawn-index-infantry
  curr-spawn-index-trucks
  infantry-clogged
  trucks-clogged
  deployment-order
  deployment-order-idx
  deployment-order-len
  north-entry-x
  north-entry-y
  west-entry-x
  west-entry-y
  south-entry-x
  south-entry-y

  ;; Acceleration Decelration New Variable
  infantry-max-road-speed
  infantry-max-dirt-speed
  truck-max-road-speed
  truck-max-dirt-speed
  infantry-acceleration
  truck-acceleration
  infantry-deceleration
  truck-deceleration

  ;; Congestion at Entry points
  north-entry-clogged?
  west-entry-clogged?
  south-entry-clogged?

  north-entry-sites
  west-entry-sites
  south-entry-sites

  curr-spawn-index-infantry-north
  curr-spawn-index-infantry-west
  curr-spawn-index-infantry-south
  curr-spawn-index-trucks-north
  curr-spawn-index-trucks-west
  curr-spawn-index-trucks-south

  deployment-order-idx-north
  deployment-order-idx-west
  deployment-order-idx-south
]
patches-own [terrain]
breed [infantry infantryperson]
breed [trucks truck]
turtles-own [
  speed
  move-ok?
  site-y
  current-speed
  accel
  decel
]
infantry-own [site-num num-troops]
trucks-own [site-num num-pontoons]

;; ---------------------------------------------------
;; ---------- CONTROL/SETUP FUNCTIONS ----------------
;; ---------------------------------------------------

to setup
  clear-all

  ; set iv3-selection iv3-spacing-waves

  ;; Convert RGB to NetLogo color numbers
  set water-color approximate-rgb 4 36 194
  set pontoon-color brown
  set goal-color approximate-rgb 252 252 60
  set artillery-fire-color red
  set grass-color 66.8

  set-patch-size 1
  resize-world 0 459 0 624

  import-pcolors "NewIrpinMap.png"
  classify-terrain
  initialize-params
  reset-ticks
end

to initialize-params
  set all-site-ids [0 1 2 3 4 5 6 7 8 9 10 11 12]
  set site-ys [ 576 542 526 403 329 292 263 237 210 171 142 112 82]
  set site-builder-count [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set num-required-builders-per-site 18
  set site-pontoon-count [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set site-pontoon-built-count [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set site-pontoon-bridge-built [false false false false false false false false false false false false false]
  set artillery-just-fired [false false false false false false false false false false false false false]
  set num-required-pontoons-per-site [183 131 131 104 160 165 179 208 240 226 302 107 104] ;; # Modules required to build respective bridges
  set chosen-site-ids select-sites
  set time-of-last-site-activity [-1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1 -1] ;; Default state, no activity yet at any site
  set site-current-activity-duration [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set dirt-roads-start-x 235
  set infantry-road-speed 45 ;; # of pixels moved per tick; About 4mph. Source: Map is 7.5mi wide and 460 pixels wide, troops march at about 4mph, ticks are 1min.
  set truck-road-speed 45 ;; Pixels per tick; About 44mph
  set infantry-dirt-speed 15 ;; Pixels per tick; About 3mph
  set truck-dirt-speed 15 ;; Pixels per tick; About 15mph
  set truck-pontoon-module-capacity 1
  set artillery-fire-animation-x 415
  set total-infantry-crossed 0
  set total-pontoons-built 0
  set total-infantry-casualties 0
  set curr-spawn-index-infantry length chosen-site-ids - 1
  set curr-spawn-index-trucks length chosen-site-ids - 1
  set north-entry-clogged? false
  set deployment-order ["infantry" "truck"]
  set deployment-order-idx 0
  set deployment-order-len length deployment-order

  ;; KEY PARAMETERS
  set site-infantry-units-per-road [1 1 1 1 1 1 1 1 1 1 1 1 3] ;; Based on real path/road widths at the site opening. THIS IS FAIRLY ACCURATE ESTIMATE.
  set infantry-unit-depth 10 ; Number of infantry unit passengers in BTR-80
  set truck-unit-depth 1 ; Number of trucks represented by a truck unit
  set pontoon-module-setup-time 1 ;; In minutes; THIS IS UNDER IDEAL CONDITIONS. Each 22ft unit done in 1min, see odin website.
  set activity-cooldown-time 30 ;; 30min after last activity has been seen, the t in the artillery equation will be reset. THIS IS A SEMI ARBITRARY VALUE
  set artillery-alpha 0.06 ; 0.035 value used before
  set artillery-beta 0.05
  set time-between-drone-checks 20 ;; 20min
  set win-num-crossers-threshold 4500 ;; 4500 troops (NOTE: EACH INFANTRY AGENT HAS NUM-TROOPS)
  set loss-battle-duration-threshold 28 * 24 * 60 ; Normally 28 days, but we can also cap at 750min for now; 28 * 24 * 60  28days (in minutes) = 28days * 24hrs * 60min

  ;; Dependent Variables
  set total-infantry-used 0
  set total-pontoons-used 0
  set battle-outcome "In Progress"

  ;; Accel Decel Parameters
  set infantry-max-road-speed 45
  set truck-max-road-speed 45
  set infantry-max-dirt-speed 15
  set truck-max-dirt-speed 15

  set infantry-acceleration 2
  set truck-acceleration 1.5
  set infantry-deceleration 3
  set truck-deceleration 2

  set infantry-road-speed 0
  set truck-road-speed 0
  set infantry-dirt-speed 0
  set truck-dirt-speed 0

  ;; Coordiantes of the Entry points
  ;; The values of the entry points will be fixed
  set north-entry-x 240
  set north-entry-y 624
  set west-entry-x 10
  set west-entry-y 260
  set south-entry-x 60
  set south-entry-y 0

  set north-entry-clogged? false
  set west-entry-clogged? false
  set south-entry-clogged? false
  set infantry-clogged [false false false] ; North, West, South
  set trucks-clogged [false false false]; North, West, South

  set north-entry-sites [0 1 2 3 4]
  set west-entry-sites [5 6 7 8]
  set south-entry-sites [9 10 11 12]

  set curr-spawn-index-infantry-north length north-entry-sites - 1
  set curr-spawn-index-infantry-west length west-entry-sites - 1
  set curr-spawn-index-infantry-south length south-entry-sites - 1
  set curr-spawn-index-trucks-north length north-entry-sites - 1
  set curr-spawn-index-trucks-west length west-entry-sites - 1
  set curr-spawn-index-trucks-south length south-entry-sites - 1

  set deployment-order-idx-north 0
  set deployment-order-idx-west 0
  set deployment-order-idx-south 0

  ;; Keep old global variables for backward compatibility
  set curr-spawn-index-infantry curr-spawn-index-infantry-north
  set curr-spawn-index-trucks curr-spawn-index-trucks-north
  set deployment-order-idx deployment-order-idx-north

  update-bridge-drawing-x-values
end

to classify-terrain
  ask patches [
    if pcolor = water-color [ set terrain "water" ]
    if pcolor = goal-color [ set terrain "goal" ]
    if terrain = 0 [ set terrain "road" ]
  ]
end

to go
  move-units
  update-spawn-availability
  spawn-units
  build-pontoon-bridges
  if turn-on-artillery? [drone-detect-and-artillery-fire]
  if turn-on-stop-conditions? [if battle-over? [stop]]
  tick ;; IMPORTANT: each represents 1min
end


;; ---------------------------------------------------
;; ----------------- MAIN FUNCTIONS ------------------
;; ---------------------------------------------------



to spawn-units
  if spacing-mode = "Uniform" or ( spacing-mode = "Waves" and (ticks mod (wave-duration + wave-pause)) < wave-duration) [ ; Optimal Wave Duration/Pause looking like 200, 60
    spawn-units-from-entry "north"
    spawn-units-from-entry "west"
    spawn-units-from-entry "south"
  ]
end

to spawn-units-from-entry [entry-point]
  let entry-x 0
  let entry-y 0
  let entry-clogged? false
  let entry-sites []
  let curr-idx-infantry 0
  let curr-idx-trucks 0
  let depl-idx 0
  let initial-heading 0

  if entry-point = "north" [
    set entry-x north-entry-x
    set entry-y north-entry-y
    set entry-clogged? north-entry-clogged?
    set entry-sites filter [ site -> member? site chosen-site-ids ] north-entry-sites
    set curr-idx-infantry curr-spawn-index-infantry-north
    set curr-idx-trucks curr-spawn-index-trucks-north
    set depl-idx deployment-order-idx-north
    set initial-heading 180
  ]
  if entry-point = "west" [
    set entry-x west-entry-x
    set entry-y west-entry-y
    set entry-clogged? west-entry-clogged?
    set entry-sites filter [ site -> member? site chosen-site-ids ] west-entry-sites
    set curr-idx-infantry curr-spawn-index-infantry-west
    set curr-idx-trucks curr-spawn-index-trucks-west
    set depl-idx deployment-order-idx-west
    set initial-heading 90
  ]
  if entry-point = "south" [
    set entry-x south-entry-x
    set entry-y south-entry-y
    set entry-clogged? south-entry-clogged?
    set entry-sites filter [ site -> member? site chosen-site-ids ] south-entry-sites
    set curr-idx-infantry curr-spawn-index-infantry-south
    set curr-idx-trucks curr-spawn-index-trucks-south
    set depl-idx deployment-order-idx-south
    set initial-heading 0
  ]

  let infantry-clogged-here item (position entry-point ["north" "west" "south"]) infantry-clogged
  let trucks-clogged-here item (position entry-point ["north" "west" "south"]) trucks-clogged
  if not (infantry-clogged-here and trucks-clogged-here) and not empty? entry-sites [
    let site-id-i item (curr-idx-infantry mod length entry-sites) entry-sites
    let site-id-t item (curr-idx-trucks mod length entry-sites) entry-sites
    let curr-deployment-idx (depl-idx mod deployment-order-len)
    let next-deployment-unit item curr-deployment-idx deployment-order

    if next-deployment-unit = "infantry" and not infantry-clogged-here [
      let infantry-units-per-road item site-id-i site-infantry-units-per-road
      let n-troops-in-unit infantry-unit-depth

      create-infantry 1 [ ;; = A rectangular group of infantry on trucks
        setxy entry-x entry-y
        set site-num site-id-i
        set site-y item site-id-i site-ys
        set num-troops n-troops-in-unit * infantry-units-per-road * 10
        set speed infantry-road-speed
        set shape "truck"
        set color white
        set size 6
        set heading initial-heading

        set current-speed 0
        set accel infantry-acceleration
        set decel infantry-deceleration
        ifelse on-dirt? [
          set speed infantry-max-dirt-speed
        ] [
          set speed infantry-max-road-speed
        ]
      ]

      set total-infantry-used (total-infantry-used + n-troops-in-unit)
      set curr-idx-infantry (curr-idx-infantry - 1)
    ]

    if next-deployment-unit = "truck" and not trucks-clogged-here [
      let n-pontoons (truck-pontoon-module-capacity * truck-unit-depth) * 10

      create-trucks 1 [ ;; = A line/group of trucks
        setxy entry-x entry-y
        set site-num site-id-t
        set site-y item site-id-t site-ys
        set num-pontoons n-pontoons
        set speed truck-dirt-speed
        set shape "truck"
        set color black
        set size 6
        set heading initial-heading

        set current-speed 0
        set accel truck-acceleration
        set decel truck-deceleration
        ifelse on-dirt? [
          set speed truck-max-dirt-speed
        ] [
          set speed truck-max-road-speed
        ]
      ]

      set total-pontoons-used (total-pontoons-used + n-pontoons)
      set curr-idx-trucks (curr-idx-trucks - 1)
    ]

    set depl-idx (depl-idx + 1)

    ;; Saving Variablesj
    if entry-point = "north" [
      set curr-spawn-index-infantry-north curr-idx-infantry
      set curr-spawn-index-trucks-north curr-idx-trucks
      set deployment-order-idx-north depl-idx
    ]
    if entry-point = "west" [
      set curr-spawn-index-infantry-west curr-idx-infantry
      set curr-spawn-index-trucks-west curr-idx-trucks
      set deployment-order-idx-west depl-idx
    ]
    if entry-point = "south" [
      set curr-spawn-index-infantry-south curr-idx-infantry
      set curr-spawn-index-trucks-south curr-idx-trucks
      set deployment-order-idx-south depl-idx
    ]
  ]
end


to move-units
  ask turtles [
    update-max-speed
    let ahead-blocked? false

    if breed = trucks [
      set ahead-blocked? any? other trucks in-cone 10 60 with [ distance myself < 15 ]
    ]
    if breed = infantry [
      set ahead-blocked? any? other infantry in-cone 10 60 with [ distance myself < 15 ]
    ]

    ifelse ahead-blocked? [
      set current-speed max (list 0 (current-speed - decel))
    ] [
      set current-speed min (list speed (current-speed + accel))
    ]

    let step-size 1
    set move-ok? true
    let remaining-move current-speed

    while [remaining-move > 0 and move-ok?] [
      ;; Turning logic
      turn-into-site-when-arrived self
      let terr-ahead terrain-ahead
      if (terr-ahead = "water" or (terr-ahead = "bridge" and breed = trucks)) [
        if breed = trucks and not site-full-of-pontoons? site-num [
          site-add-pontoons
          die
        ]
        if breed = infantry and not site-full-of-builders? site-num [
          site-add-builders
          die
        ]
        set move-ok? false
      ]

      if ((terr-ahead = "goal" or terrain = "goal") and breed = infantry) [
        set total-infantry-crossed total-infantry-crossed + num-troops
        die
      ]

      if (terr-ahead = "road") or (terr-ahead = "bridge" and breed = infantry) [
        let blocked? false
        ;; Cone-based collision detection
        if breed = trucks [
          set blocked? any? other trucks in-cone (1 + step-size) 90 with [ distance myself < 5]

          ;; The line below makes congestion which we never want
          ; set blocked? blocked? or any? infantry in-cone (1 + step-size) 90 with [ distance myself < 5 ]
        ]
        if breed = infantry [
          set blocked? any? other infantry in-cone (1 + step-size) 90 with [ distance myself < 5]

          ;; The line below makes congestion which we never want
          ; set blocked? any? other trucks in-cone (1 + step-size) 90 with [ distance myself < 5 ]

        ]
        if blocked? = true [
          set move-ok? false
          stop
        ]

        ifelse can-move? step-size [
          let target-x int (xcor + step-size * dx-from-heading heading)
          let target-y int (ycor + step-size * dy-from-heading heading)
          let target-patch patch target-x target-y

          ifelse target-patch != nobody [
            fd step-size
            set remaining-move remaining-move - step-size
          ] [
            set move-ok? false
          ]
        ] [
          set move-ok? false
        ]
      ]
    ]
  ]
end

to turn-into-site-when-arrived [ unit ]
  let target-y [site-y] of unit
  let target-site-num [site-num] of unit
  let tolerance 0.5  ;; Allow a small buffer for overshoot/undershoot

  let entry-type "unknown"
  if member? target-site-num north-entry-sites [
    set entry-type "north"
  ]
  if member? target-site-num west-entry-sites [
    set entry-type "west"
  ]
  if member? target-site-num south-entry-sites [
    set entry-type "south"
  ]

  if entry-type = "north" [
    if abs (([ycor] of unit) - target-y) <= tolerance [
      ask unit [ set heading 90 ]  ;; 東向き
    ]
  ]
  if entry-type = "west" [
    if [xcor] of unit > 250 [
      ifelse [ycor] of unit < target-y [
        ask unit [ set heading 0 ]
      ] [
        ask unit [ set heading 180 ]
      ]
      if abs (([ycor] of unit) - target-y) <= tolerance [
        ask unit [ set heading 90 ]
      ]
    ]
  ]
  if entry-type = "south" [
    if [ycor] of unit = 82 [
      ask unit [ set heading 90 ]
    ]
    if [xcor] of unit >= 250 [
      ask unit [ set heading 0 ]
    ]
  ]


  if abs (([ycor] of unit) - target-y) <= tolerance [
    ask unit [ set heading 90 ]
  ]
end

to build-pontoon-bridges
  foreach chosen-site-ids [site-id ->
    let builders-ready site-full-of-builders? site-id
    let num-pontoons-ready item site-id site-pontoon-count
    let num-pontoons-req item site-id num-required-pontoons-per-site
    let num-pontoon-pieces-built item site-id site-pontoon-built-count
    let pontoon-bridge-built item site-id site-pontoon-bridge-built
    if not pontoon-bridge-built [
      ;; If all pieces are there, build/draw the bridge
      ifelse num-pontoon-pieces-built = num-pontoons-req [
        draw-bridge site-id
        set site-pontoon-bridge-built replace-item site-id site-pontoon-bridge-built true
      ] [
        ;; Otherwise, if the necessary ppl/resources are there, add to the bridge currently under construction
        if builders-ready and (num-pontoons-ready >= 1) [
          let current-total-pontoons-built total-pontoons-built
          let pontoons-built-per-tick 1 / pontoon-module-setup-time
          set total-pontoons-built (current-total-pontoons-built + pontoons-built-per-tick)
          set site-pontoon-built-count replace-item site-id site-pontoon-built-count (num-pontoon-pieces-built + pontoons-built-per-tick)
          set site-pontoon-count replace-item site-id site-pontoon-count (num-pontoons-ready - pontoons-built-per-tick)
        ]
      ]
    ]
 ]
end

to drone-detect-and-artillery-fire
  update-time-and-duration-of-site-activity

  let num-active-sites get-num-active-sites
  if num-active-sites = 0 [ stop ]

  foreach chosen-site-ids [site-id ->
    if was-site-attacked-recently? site-id [
      let duration item site-id site-current-activity-duration
      if duration > 45 [
        let pDestroyed max(list 0 (1 - artillery-alpha * num-active-sites)) * (1 - exp(-1 * artillery-beta * (duration - 45)))

        if (ticks mod time-between-drone-checks = 0) and (random-float 1.0 < pDestroyed) [
          destroy-site site-id
          ;print (word "💥 Bridge/troops at site " site-id " destroyed at tick " ticks ". Activity with Duration " duration " had artillery hit probability of " pDestroyed " with num sites " num-active-sites )
        ]
      ]
    ]
  ]

  undraw-artillery-fire
end

to-report battle-over?
  if ticks >= loss-battle-duration-threshold or ((total-infantry-casualties / 10) > 4500) [
    set battle-outcome "Retreat"
    report true
  ]
  if total-infantry-crossed >= win-num-crossers-threshold [
    set battle-outcome "Victory"
    report true
  ]
  report false
end

;; ---------------------------------------------------
;; ---------------- HELPER FUNCTIONS -----------------
;; ---------------------------------------------------

to-report select-sites
  ;; step 1: Define the site groups in the order north, west, south
  let north-sites-sorted [3 1 2 4 0]
  let west-sites-sorted [5 6 7 8]
  let south-sites-sorted [12 11 9 10]

  ;; step 2: Extract the number of sites to use
  let num-sites-literal substring site-selection-mode 0 2
  let num-sites read-from-string num-sites-literal

  ;; step 3: Initialize the list to store selected sites
  let selected-site-ids []

  ;; step 4: Add sites in the order north, west, south, selecting from largest to smallest within each group
  while [length selected-site-ids < num-sites] [
    if length selected-site-ids < num-sites and not empty? north-sites-sorted [
      set selected-site-ids lput (first north-sites-sorted) selected-site-ids
      set north-sites-sorted but-first north-sites-sorted
    ]
    if length selected-site-ids < num-sites and not empty? west-sites-sorted [
      set selected-site-ids lput (first west-sites-sorted) selected-site-ids
      set west-sites-sorted but-first west-sites-sorted
    ]
    if length selected-site-ids < num-sites and not empty? south-sites-sorted [
      set selected-site-ids lput (first south-sites-sorted) selected-site-ids
      set south-sites-sorted but-first south-sites-sorted
    ]
  ]

  ;; step 5: Report the selected site IDs
  report selected-site-ids
end

;; Prevents spawners from getting backed up when line reaches them
to update-spawn-availability
  let infantry-here-north any? infantry with [abs (xcor - north-entry-x) < 1 and abs (ycor - north-entry-y) < 1]
  let trucks-here-north any? trucks with [abs (xcor - north-entry-x) < 1 and abs (ycor - north-entry-y) < 1]
  let infantry-here-west any? infantry with [abs (xcor - west-entry-x) < 1 and abs (ycor - west-entry-y) < 1]
  let trucks-here-west any? trucks with [abs (xcor - west-entry-x) < 1 and abs (ycor - west-entry-y) < 1]
  let infantry-here-south any? infantry with [abs (xcor - south-entry-x) < 1 and abs (ycor - south-entry-y) < 1]
  let trucks-here-south any? trucks with [abs (xcor - south-entry-x) < 1 and abs (ycor - south-entry-y) < 1]

  set infantry-clogged (list infantry-here-north infantry-here-west infantry-here-south)
  set trucks-clogged (list trucks-here-north trucks-here-west trucks-here-south)
end

;; Checks if there's a specific terrain type ahead (in front patch at distance 1).
to-report terrain-ahead
  let ahead patch-ahead 1
  if ahead = nobody [
    report "N/A"
  ]
  ifelse is-string? [terrain] of ahead [
    report [terrain] of ahead
  ] [
    report "road"  ;; default fallback
  ]
end

;; For changing unit speed when they get off main roads as they approach river
to-report on-dirt?
  report (xcor > dirt-roads-start-x)
end

to-report site-full-of-builders? [site-n]
  let builder-ct item site-n site-builder-count
  report builder-ct >= num-required-builders-per-site
end

to site-add-builders
  let builder-ct item site-num site-builder-count
  set site-builder-count replace-item site-num site-builder-count (builder-ct + num-troops)
end

to-report site-full-of-pontoons? [site-n]
  let pontoon-ct item site-n site-pontoon-count
  let required-ct item site-num num-required-pontoons-per-site
  report pontoon-ct >= required-ct
end

to site-add-pontoons
  let pontoon-ct item site-num site-pontoon-count
  set site-pontoon-count replace-item site-num site-pontoon-count (pontoon-ct + num-pontoons)
end

to update-bridge-drawing-x-values
  let start-xs []
  let end-xs []

  foreach site-ys [y ->
    ;; Get leftmost water x at this y
    let water-x false
    if any? patches with [terrain = "water" and pycor = y] [
      set water-x min [pxcor] of patches with [terrain = "water" and pycor = y]
    ]

    ;; Get leftmost goal x at this y
    let goal-x false
    if any? patches with [terrain = "goal" and pycor = y] [
      set goal-x min [pxcor] of patches with [terrain = "goal" and pycor = y]
    ]

    set start-xs lput water-x start-xs
    set end-xs lput goal-x end-xs
  ]

  set site-bridge-drawing-start-x start-xs
  set site-bridge-drawing-end-x end-xs
end

to draw-bridge [site-n]
  let y item site-n site-ys
  let x-start item site-n site-bridge-drawing-start-x
  let x-end item site-n site-bridge-drawing-end-x

  ;; Safety check
  if (x-start = false or x-end = false) [ stop ]

  ;; Loop over a vertical band: y-2 to y+2 (5 patches tall)
  ask patches with [
    pxcor >= x-start and pxcor <= x-end and
    pycor >= (y - 2) and pycor <= (y + 2)
  ] [
    set pcolor pontoon-color
    set terrain "bridge"
  ]
end

to redraw-water [site-n]
  let y item site-n site-ys
  let x-start item site-n site-bridge-drawing-start-x
  let x-end item site-n site-bridge-drawing-end-x

  ;; Safety check
  if (x-start = false or x-end = false) [ stop ]

  ;; Loop over a vertical band: y-2 to y+2 (5 patches tall)
  ask patches with [
    pxcor >= x-start and pxcor <= x-end and
    pycor >= (y - 2) and pycor <= (y + 2)
  ] [
    set pcolor water-color
    set terrain "water"
  ]
end

to update-time-and-duration-of-site-activity
  foreach chosen-site-ids [site-id ->
    ifelse is-site-currently-active? site-id [
      ;; If active, update time-of-last-site-activity and increase duration
      set time-of-last-site-activity replace-item site-id time-of-last-site-activity ticks
      let prev-dur item site-id site-current-activity-duration
      set site-current-activity-duration replace-item site-id site-current-activity-duration (prev-dur + 1)
    ] [
      ;; If inactive and cooldown has expired, reset duration
      if not was-site-attacked-recently? site-id [
        set site-current-activity-duration replace-item site-id site-current-activity-duration 0
      ]
    ]
  ]
end

to-report get-num-active-sites
  let num-active-sites 0
  foreach chosen-site-ids [site-id ->
    if is-site-currently-active? site-id [
      set num-active-sites (num-active-sites + 1)
    ]
  ]
  report num-active-sites
end

to-report is-site-currently-active? [site-id]
  let num-active-soldiers item site-id site-builder-count
  let num-built-pontoons item site-id site-pontoon-built-count
  report num-built-pontoons > 0
end

to-report was-site-attacked-recently? [site-id]
  let last-attack-time item site-id time-of-last-site-activity
  ifelse last-attack-time = -1 [
    report false
  ] [
    report ticks - last-attack-time < activity-cooldown-time
  ]
end

to destroy-site [site-id]
  ;; Add casualties of infantry squad at river bank
  set total-infantry-casualties (total-infantry-casualties + (item site-id site-builder-count))
  set site-builder-count replace-item site-id site-builder-count 0

  ;; Destroy pontoons on bank and river
  set site-pontoon-count replace-item site-id site-pontoon-count 0
  set site-pontoon-built-count replace-item site-id site-pontoon-built-count 0

  ;; Destroy bridge, if the bridge was fully built/drawn
  let bridge-built item site-id site-pontoon-bridge-built
  if bridge-built [
    redraw-water site-id
    set site-pontoon-bridge-built replace-item site-id site-pontoon-bridge-built false
  ]

  ;; Animate firing
  draw-artillery-fire site-id artillery-fire-color
  set artillery-just-fired replace-item site-id artillery-just-fired true

  ;; Get bridge zone
  let y item site-id site-ys
  let x-start item site-id site-bridge-drawing-start-x
  let x-end item site-id site-bridge-drawing-end-x

  ;; Add casualties of infantry squads on the bridge and despawn their turtles
  ask infantry with [
    site-num = site-id and
    xcor >= x-start and xcor <= x-end and
    ycor >= (y - 2) and ycor <= (y + 2)
  ] [
    set total-infantry-casualties (total-infantry-casualties + num-troops)
    die
  ]
end

to update-max-speed
  ifelse on-dirt? [

    if breed = infantry [
      set speed infantry-max-dirt-speed
    ]
    if breed = trucks [
      set speed truck-max-dirt-speed
    ]
  ] [

    if breed = infantry [
      set speed infantry-max-road-speed
    ]
    if breed = trucks [
      set speed truck-max-road-speed
    ]
  ]
end

to-report dx-from-heading [hdg]
  report cos hdg
end

to-report dy-from-heading [hdg]
  report sin hdg
end

to draw-artillery-fire [site-id animation-color]
  let artillery-fire-animation-y item site-id site-ys
  ask patches with [
    pxcor >= artillery-fire-animation-x - 2 and pxcor <= artillery-fire-animation-x + 2 and
    pycor >= (artillery-fire-animation-y - 2) and pycor <= (artillery-fire-animation-y + 2)
  ] [
    set pcolor animation-color
  ]
end

to undraw-artillery-fire
  if (ticks mod 9) = 0 [ ; Every 9min the artillery fire undraws itself if it was drawn before
    foreach all-site-ids [ site-id ->
      let artillery-fired-recently? item site-id artillery-just-fired
      if artillery-fired-recently? [
        draw-artillery-fire site-id grass-color
        set artillery-just-fired replace-item site-id artillery-just-fired false
      ]
    ]
  ]
end
@#$#@#$#@
GRAPHICS-WINDOW
568
10
1036
644
-1
-1
1.0
1
10
1
1
1
0
0
0
1
0
459
0
624
1
1
1
ticks
30.0

BUTTON
502
10
569
44
NIL
setup
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

BUTTON
503
44
569
80
NIL
go
T
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

MONITOR
1
196
406
241
Infantry Ready to Build at each Site
site-builder-count
17
1
11

MONITOR
1
241
405
286
Pontoons Modules Ready to be Built at each Site
site-pontoon-count
0
1
11

MONITOR
1
287
406
332
Number of Pontoon Modules Built at each Site
site-pontoon-built-count
0
1
11

MONITOR
1
377
402
422
Whether Each Site has completed Building its Bridge
site-pontoon-bridge-built
17
1
11

MONITOR
404
286
569
331
Pontoon Modules Built
total-pontoons-built
0
1
11

MONITOR
435
149
569
194
Infantry Crossed
total-infantry-crossed
17
1
11

MONITOR
1
423
401
468
Time Of Last Building Activity at Each Site
time-of-last-site-activity
17
1
11

MONITOR
166
103
289
148
Battle Status
battle-outcome
17
1
11

MONITOR
290
103
433
148
Infantry Sent
total-infantry-used
17
1
11

MONITOR
435
103
570
148
Pontoon Modules Sent
total-pontoons-used
17
1
11

MONITOR
290
149
432
194
Infantry Casualty Ratio
total-infantry-casualties / (total-infantry-used * 10)
4
1
11

MONITOR
1
332
405
377
Percent Completion of Pontoon Bridge at Each Site
map [[a b] -> round (100 * (a / b))] site-pontoon-built-count num-required-pontoons-per-site
0
1
11

CHOOSER
364
10
502
55
site-selection-mode
site-selection-mode
"01 Shortest Bridges" "02 Shortest Bridges" "03 Shortest Bridges" "04 Shortest Bridges" "05 Shortest Bridges" "06 Shortest Bridges" "07 Shortest Bridges" "08 Shortest Bridges" "09 Shortest Bridges" "10 Shortest Bridges" "11 Shortest Bridges" "12 Shortest Bridges" "13 Shortest Bridges"
12

MONITOR
404
194
569
239
Avg Bridge Completion (%)
sum ((map [[a b] -> round (100 * (a / b))] site-pontoon-built-count num-required-pontoons-per-site)) / length chosen-site-ids
0
1
11

SWITCH
0
10
187
43
turn-on-artillery?
turn-on-artillery?
0
1
-1000

SWITCH
0
43
188
76
turn-on-stop-conditions?
turn-on-stop-conditions?
0
1
-1000

MONITOR
404
240
569
285
Max Bridge Completion (%)
max (map [[a b] -> round (100 * (a / b))] site-pontoon-built-count num-required-pontoons-per-site)
17
1
11

PLOT
1
470
220
662
Max Bridge Completion (%)
Time (minutes)
Max Completion (%)
0.0
10.0
0.0
100.0
true
false
"" ""
PENS
"default" 1.0 0 -13791810 true "" "plot max (map [[a b] -> round (100 * (a / b))] site-pontoon-built-count num-required-pontoons-per-site)"

PLOT
221
470
442
662
Average Bridge Completion (%)
Time (min)
Avg Completion (%)
0.0
10.0
0.0
100.0
true
false
"" ""
PENS
"default" 1.0 0 -11085214 true "" "plot (sum ((map [[a b] -> round (100 * (a / b))] site-pontoon-built-count num-required-pontoons-per-site)) / length chosen-site-ids)"

PLOT
1
663
220
853
Casualty Ratio (%)
Time (min)
Ratio (%)
0.0
10.0
0.0
1.0
true
false
"" ""
PENS
"default" 1.0 0 -2674135 true "" "plot (total-infantry-casualties / (total-infantry-used * 10 + 0.0001))"

MONITOR
166
149
288
194
Infantry Casualties
total-infantry-casualties / 10
17
1
11

MONITOR
404
331
569
376
Trucks Clogged NWS
trucks-clogged
17
1
11

MONITOR
403
376
570
421
Infantry Clogged NWS
infantry-clogged
17
1
11

INPUTBOX
187
12
282
72
wave-duration
200.0
1
0
Number

INPUTBOX
282
12
364
72
wave-pause
60.0
1
0
Number

CHOOSER
364
56
502
101
spacing-mode
spacing-mode
"Uniform" "Waves"
0

MONITOR
402
422
485
467
Num Waves
ifelse-value spacing-mode = \"Waves\" [\n ceiling (ticks / (wave-duration + wave-pause))\n]\n[\n \"N/A\"\n]
17
1
11

@#$#@#$#@
## WHAT IS IT?

(a general understanding of what the model is trying to show or explain)

## HOW IT WORKS

(what rules the agents use to create the overall behavior of the model)

## HOW TO USE IT

(how to use the model, including a description of each of the items in the Interface tab)

## THINGS TO NOTICE

(suggested things for the user to notice while running the model)

## THINGS TO TRY

(suggested things for the user to try to do (move sliders, switches, etc.) with the model)

## EXTENDING THE MODEL

(suggested things to add or change in the Code tab to make the model more complicated, detailed, accurate, etc.)

## NETLOGO FEATURES

(interesting or unusual features of NetLogo that the model uses, particularly in the Code tab; or where workarounds were needed for missing features)

## RELATED MODELS

(models in the NetLogo Models Library and elsewhere which are of related interest)

## CREDITS AND REFERENCES

(a reference to the model's URL on the web if it has one, as well as any other necessary credits, citations, and links)
@#$#@#$#@
default
true
0
Polygon -7500403 true true 150 5 40 250 150 205 260 250

airplane
true
0
Polygon -7500403 true true 150 0 135 15 120 60 120 105 15 165 15 195 120 180 135 240 105 270 120 285 150 270 180 285 210 270 165 240 180 180 285 195 285 165 180 105 180 60 165 15

arrow
true
0
Polygon -7500403 true true 150 0 0 150 105 150 105 293 195 293 195 150 300 150

box
false
0
Polygon -7500403 true true 150 285 285 225 285 75 150 135
Polygon -7500403 true true 150 135 15 75 150 15 285 75
Polygon -7500403 true true 15 75 15 225 150 285 150 135
Line -16777216 false 150 285 150 135
Line -16777216 false 150 135 15 75
Line -16777216 false 150 135 285 75

bug
true
0
Circle -7500403 true true 96 182 108
Circle -7500403 true true 110 127 80
Circle -7500403 true true 110 75 80
Line -7500403 true 150 100 80 30
Line -7500403 true 150 100 220 30

butterfly
true
0
Polygon -7500403 true true 150 165 209 199 225 225 225 255 195 270 165 255 150 240
Polygon -7500403 true true 150 165 89 198 75 225 75 255 105 270 135 255 150 240
Polygon -7500403 true true 139 148 100 105 55 90 25 90 10 105 10 135 25 180 40 195 85 194 139 163
Polygon -7500403 true true 162 150 200 105 245 90 275 90 290 105 290 135 275 180 260 195 215 195 162 165
Polygon -16777216 true false 150 255 135 225 120 150 135 120 150 105 165 120 180 150 165 225
Circle -16777216 true false 135 90 30
Line -16777216 false 150 105 195 60
Line -16777216 false 150 105 105 60

car
false
0
Polygon -7500403 true true 300 180 279 164 261 144 240 135 226 132 213 106 203 84 185 63 159 50 135 50 75 60 0 150 0 165 0 225 300 225 300 180
Circle -16777216 true false 180 180 90
Circle -16777216 true false 30 180 90
Polygon -16777216 true false 162 80 132 78 134 135 209 135 194 105 189 96 180 89
Circle -7500403 true true 47 195 58
Circle -7500403 true true 195 195 58

circle
false
0
Circle -7500403 true true 0 0 300

circle 2
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240

cow
false
0
Polygon -7500403 true true 200 193 197 249 179 249 177 196 166 187 140 189 93 191 78 179 72 211 49 209 48 181 37 149 25 120 25 89 45 72 103 84 179 75 198 76 252 64 272 81 293 103 285 121 255 121 242 118 224 167
Polygon -7500403 true true 73 210 86 251 62 249 48 208
Polygon -7500403 true true 25 114 16 195 9 204 23 213 25 200 39 123

cylinder
false
0
Circle -7500403 true true 0 0 300

dot
false
0
Circle -7500403 true true 90 90 120

face happy
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 255 90 239 62 213 47 191 67 179 90 203 109 218 150 225 192 218 210 203 227 181 251 194 236 217 212 240

face neutral
false
0
Circle -7500403 true true 8 7 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Rectangle -16777216 true false 60 195 240 225

face sad
false
0
Circle -7500403 true true 8 8 285
Circle -16777216 true false 60 75 60
Circle -16777216 true false 180 75 60
Polygon -16777216 true false 150 168 90 184 62 210 47 232 67 244 90 220 109 205 150 198 192 205 210 220 227 242 251 229 236 206 212 183

fish
false
0
Polygon -1 true false 44 131 21 87 15 86 0 120 15 150 0 180 13 214 20 212 45 166
Polygon -1 true false 135 195 119 235 95 218 76 210 46 204 60 165
Polygon -1 true false 75 45 83 77 71 103 86 114 166 78 135 60
Polygon -7500403 true true 30 136 151 77 226 81 280 119 292 146 292 160 287 170 270 195 195 210 151 212 30 166
Circle -16777216 true false 215 106 30

flag
false
0
Rectangle -7500403 true true 60 15 75 300
Polygon -7500403 true true 90 150 270 90 90 30
Line -7500403 true 75 135 90 135
Line -7500403 true 75 45 90 45

flower
false
0
Polygon -10899396 true false 135 120 165 165 180 210 180 240 150 300 165 300 195 240 195 195 165 135
Circle -7500403 true true 85 132 38
Circle -7500403 true true 130 147 38
Circle -7500403 true true 192 85 38
Circle -7500403 true true 85 40 38
Circle -7500403 true true 177 40 38
Circle -7500403 true true 177 132 38
Circle -7500403 true true 70 85 38
Circle -7500403 true true 130 25 38
Circle -7500403 true true 96 51 108
Circle -16777216 true false 113 68 74
Polygon -10899396 true false 189 233 219 188 249 173 279 188 234 218
Polygon -10899396 true false 180 255 150 210 105 210 75 240 135 240

house
false
0
Rectangle -7500403 true true 45 120 255 285
Rectangle -16777216 true false 120 210 180 285
Polygon -7500403 true true 15 120 150 15 285 120
Line -16777216 false 30 120 270 120

leaf
false
0
Polygon -7500403 true true 150 210 135 195 120 210 60 210 30 195 60 180 60 165 15 135 30 120 15 105 40 104 45 90 60 90 90 105 105 120 120 120 105 60 120 60 135 30 150 15 165 30 180 60 195 60 180 120 195 120 210 105 240 90 255 90 263 104 285 105 270 120 285 135 240 165 240 180 270 195 240 210 180 210 165 195
Polygon -7500403 true true 135 195 135 240 120 255 105 255 105 285 135 285 165 240 165 195

line
true
0
Line -7500403 true 150 0 150 300

line half
true
0
Line -7500403 true 150 0 150 150

pentagon
false
0
Polygon -7500403 true true 150 15 15 120 60 285 240 285 285 120

person
false
0
Circle -7500403 true true 110 5 80
Polygon -7500403 true true 105 90 120 195 90 285 105 300 135 300 150 225 165 300 195 300 210 285 180 195 195 90
Rectangle -7500403 true true 127 79 172 94
Polygon -7500403 true true 195 90 240 150 225 180 165 105
Polygon -7500403 true true 105 90 60 150 75 180 135 105

plant
false
0
Rectangle -7500403 true true 135 90 165 300
Polygon -7500403 true true 135 255 90 210 45 195 75 255 135 285
Polygon -7500403 true true 165 255 210 210 255 195 225 255 165 285
Polygon -7500403 true true 135 180 90 135 45 120 75 180 135 210
Polygon -7500403 true true 165 180 165 210 225 180 255 120 210 135
Polygon -7500403 true true 135 105 90 60 45 45 75 105 135 135
Polygon -7500403 true true 165 105 165 135 225 105 255 45 210 60
Polygon -7500403 true true 135 90 120 45 150 15 180 45 165 90

sheep
false
15
Circle -1 true true 203 65 88
Circle -1 true true 70 65 162
Circle -1 true true 150 105 120
Polygon -7500403 true false 218 120 240 165 255 165 278 120
Circle -7500403 true false 214 72 67
Rectangle -1 true true 164 223 179 298
Polygon -1 true true 45 285 30 285 30 240 15 195 45 210
Circle -1 true true 3 83 150
Rectangle -1 true true 65 221 80 296
Polygon -1 true true 195 285 210 285 210 240 240 210 195 210
Polygon -7500403 true false 276 85 285 105 302 99 294 83
Polygon -7500403 true false 219 85 210 105 193 99 201 83

square
false
0
Rectangle -7500403 true true 30 30 270 270

square 2
false
0
Rectangle -7500403 true true 30 30 270 270
Rectangle -16777216 true false 60 60 240 240

star
false
0
Polygon -7500403 true true 151 1 185 108 298 108 207 175 242 282 151 216 59 282 94 175 3 108 116 108

target
false
0
Circle -7500403 true true 0 0 300
Circle -16777216 true false 30 30 240
Circle -7500403 true true 60 60 180
Circle -16777216 true false 90 90 120
Circle -7500403 true true 120 120 60

tree
false
0
Circle -7500403 true true 118 3 94
Rectangle -6459832 true false 120 195 180 300
Circle -7500403 true true 65 21 108
Circle -7500403 true true 116 41 127
Circle -7500403 true true 45 90 120
Circle -7500403 true true 104 74 152

triangle
false
0
Polygon -7500403 true true 150 30 15 255 285 255

triangle 2
false
0
Polygon -7500403 true true 150 30 15 255 285 255
Polygon -16777216 true false 151 99 225 223 75 224

truck
false
0
Rectangle -7500403 true true 4 45 195 187
Polygon -7500403 true true 296 193 296 150 259 134 244 104 208 104 207 194
Rectangle -1 true false 195 60 195 105
Polygon -16777216 true false 238 112 252 141 219 141 218 112
Circle -16777216 true false 234 174 42
Rectangle -7500403 true true 181 185 214 194
Circle -16777216 true false 144 174 42
Circle -16777216 true false 24 174 42
Circle -7500403 false true 24 174 42
Circle -7500403 false true 144 174 42
Circle -7500403 false true 234 174 42

turtle
true
0
Polygon -10899396 true false 215 204 240 233 246 254 228 266 215 252 193 210
Polygon -10899396 true false 195 90 225 75 245 75 260 89 269 108 261 124 240 105 225 105 210 105
Polygon -10899396 true false 105 90 75 75 55 75 40 89 31 108 39 124 60 105 75 105 90 105
Polygon -10899396 true false 132 85 134 64 107 51 108 17 150 2 192 18 192 52 169 65 172 87
Polygon -10899396 true false 85 204 60 233 54 254 72 266 85 252 107 210
Polygon -7500403 true true 119 75 179 75 209 101 224 135 220 225 175 261 128 261 81 224 74 135 88 99

wheel
false
0
Circle -7500403 true true 3 3 294
Circle -16777216 true false 30 30 240
Line -7500403 true 150 285 150 15
Line -7500403 true 15 150 285 150
Circle -7500403 true true 120 120 60
Line -7500403 true 216 40 79 269
Line -7500403 true 40 84 269 221
Line -7500403 true 40 216 269 79
Line -7500403 true 84 40 221 269

wolf
false
0
Polygon -16777216 true false 253 133 245 131 245 133
Polygon -7500403 true true 2 194 13 197 30 191 38 193 38 205 20 226 20 257 27 265 38 266 40 260 31 253 31 230 60 206 68 198 75 209 66 228 65 243 82 261 84 268 100 267 103 261 77 239 79 231 100 207 98 196 119 201 143 202 160 195 166 210 172 213 173 238 167 251 160 248 154 265 169 264 178 247 186 240 198 260 200 271 217 271 219 262 207 258 195 230 192 198 210 184 227 164 242 144 259 145 284 151 277 141 293 140 299 134 297 127 273 119 270 105
Polygon -7500403 true true -1 195 14 180 36 166 40 153 53 140 82 131 134 133 159 126 188 115 227 108 236 102 238 98 268 86 269 92 281 87 269 103 269 113

x
false
0
Polygon -7500403 true true 270 75 225 30 30 225 75 270
Polygon -7500403 true true 30 75 75 30 270 225 225 270
@#$#@#$#@
NetLogo 6.4.0
@#$#@#$#@
@#$#@#$#@
@#$#@#$#@
<experiments>
  <experiment name="Varying Site-Selection With No Artillery Active" repetitions="1" sequentialRunOrder="false" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>ticks</metric>
    <metric>total-infantry-used</metric>
    <metric>total-pontoons-used</metric>
    <metric>battle-outcome</metric>
    <enumeratedValueSet variable="turn-on-artillery?">
      <value value="false"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="turn-on-stop-conditions?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="site-selection-mode">
      <value value="&quot;01 Shortest Bridges&quot;"/>
      <value value="&quot;02 Shortest Bridges&quot;"/>
      <value value="&quot;03 Shortest Bridges&quot;"/>
      <value value="&quot;04 Shortest Bridges&quot;"/>
      <value value="&quot;05 Shortest Bridges&quot;"/>
      <value value="&quot;06 Shortest Bridges&quot;"/>
      <value value="&quot;07 Shortest Bridges&quot;"/>
      <value value="&quot;08 Shortest Bridges&quot;"/>
      <value value="&quot;09 Shortest Bridges&quot;"/>
      <value value="&quot;10 Shortest Bridges&quot;"/>
      <value value="&quot;11 Shortest Bridges&quot;"/>
      <value value="&quot;12 Shortest Bridges&quot;"/>
      <value value="&quot;13 Shortest Bridges&quot;"/>
    </enumeratedValueSet>
  </experiment>
  <experiment name="Vary Site-Selection Artillery Active" repetitions="1" runMetricsEveryStep="false">
    <setup>setup</setup>
    <go>go</go>
    <metric>battle-outcome</metric>
    <metric>total-infantry-crossed</metric>
    <metric>total-infantry-casualties / 10</metric>
    <metric>total-infantry-used</metric>
    <metric>ticks</metric>
    <enumeratedValueSet variable="turn-on-artillery?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="turn-on-stop-conditions?">
      <value value="true"/>
    </enumeratedValueSet>
    <enumeratedValueSet variable="site-selection-mode">
      <value value="&quot;01 Shortest Bridges&quot;"/>
      <value value="&quot;02 Shortest Bridges&quot;"/>
      <value value="&quot;03 Shortest Bridges&quot;"/>
      <value value="&quot;04 Shortest Bridges&quot;"/>
      <value value="&quot;05 Shortest Bridges&quot;"/>
      <value value="&quot;06 Shortest Bridges&quot;"/>
      <value value="&quot;07 Shortest Bridges&quot;"/>
      <value value="&quot;08 Shortest Bridges&quot;"/>
      <value value="&quot;09 Shortest Bridges&quot;"/>
      <value value="&quot;10 Shortest Bridges&quot;"/>
      <value value="&quot;11 Shortest Bridges&quot;"/>
      <value value="&quot;12 Shortest Bridges&quot;"/>
      <value value="&quot;13 Shortest Bridges&quot;"/>
    </enumeratedValueSet>
  </experiment>
</experiments>
@#$#@#$#@
@#$#@#$#@
default
0.0
-0.2 0 0.0 1.0
0.0 1 1.0 0.0
0.2 0 0.0 1.0
link direction
true
0
Line -7500403 true 150 150 90 180
Line -7500403 true 150 150 210 180
@#$#@#$#@
0
@#$#@#$#@
