globals [
  water-color
  pontoon-color
  goal-color
  site-ys
  all-site-ids
  chosen-site-ids
  site-troops-per-road
  site-is-spawning
  site-builder-count
  site-pontoon-count
  site-pontoon-built-count
  site-pontoon-bridge-built
  site-bridge-drawing-start-x
  site-bridge-drawing-end-x
  unit-spawn-spacing
  unit-collision-spacing
  infantry-squad-depth
  truck-group-depth
  infantry-road-speed
  truck-road-speed
  dirt-roads-start-x
  infantry-dirt-speed
  truck-dirt-speed
  truck-pontoon-module-capacity
  num-required-builders-per-site
  num-required-pontoons-per-site
  pontoon-module-setup-time
  total-pontoons-built
  total-infantry-crossed
]
patches-own [terrain]
breed [infantry infantryperson]
breed [trucks truck]
infantry-own [site-num num-troops]
trucks-own [site-num num-pontoons]

to setup
  clear-all

  ;; Convert RGB to NetLogo color numbers
  set water-color approximate-rgb 4 36 194
  set pontoon-color brown
  set goal-color approximate-rgb 252 252 60

  set-patch-size 3
  resize-world 0 459 0 624

  import-pcolors "/Users/gerardspooner/Downloads/NewIrpinMap.png"
  classify-terrain
  initialize-params
  spawn-units
  reset-ticks
end

to go
  move-units
  build-pontoon-bridges
  update-spawn-availability
  if ticks mod unit-spawn-spacing = 0 [spawn-units]
  tick ;; each 1min
end

to classify-terrain
  ask patches [
    if pcolor = water-color [ set terrain "water" ]
    if pcolor = goal-color [ set terrain "goal" ]
  ]
end

to initialize-params
  set all-site-ids [0 1 2 3 4 5 6 7 8 9 10 11 12]
  set chosen-site-ids all-site-ids ;; TODO - Parameterize this IV
  set site-ys [ 576 542 526 403 329 292 263 237 210 171 142 112 82]
  set site-troops-per-road [6 6 6 6 6 6 6 6 6 6 6 6 16] ;; Based on real path/road widths at the site opening
  set site-is-spawning [true true true true true true true true true true true true true]
  set site-builder-count [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set num-required-builders-per-site 18
  set site-pontoon-count [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set site-pontoon-built-count [0 0 0 0 0 0 0 0 0 0 0 0 0]
  set site-pontoon-bridge-built [false false false false false false false false false false false false false]
  set num-required-pontoons-per-site [183 131 131 104 160 165 179 208 240 226 302 107 104]
  set dirt-roads-start-x 235
  set unit-spawn-spacing 10 ;; TODO - Parameterize this IV
  set unit-collision-spacing 10 ;; TODO - Calibrate this
  set infantry-road-speed 4 ;; Map is 7.5mi wide and 460 pixels wide, troops march at 4mph, ticks are 1min.
  set truck-road-speed 45 ;; Same map/tick values, trucks move 44mph
  set infantry-dirt-speed 3
  set truck-dirt-speed 15
  set truck-pontoon-module-capacity 1

  ;; KEY PARAMETERS
  set infantry-squad-depth 340 ;; Since unit spacing is 10coords = 860ft, then ~344 troops can fit in that space. THIS IS MAX DENSITY CONFIG.
  set truck-group-depth 20 ;; Since unit spacing is 10coords = 860ft, then ~21.5 PMP trucks can fit in that space. THIS IS MAX DENSITY CONFIG.
  set pontoon-module-setup-time 1 ;; Under 'ideal conditions', each 22ft unit done in 1min = 1 tick, see odin website

  ;; Dependent Variables
  set total-pontoons-built 0
  set total-infantry-crossed 0

  update-bridge-drawing-x-values
end

to spawn-units
  foreach chosen-site-ids [site-id ->
    let site-spawning item site-id site-is-spawning
    if site-spawning [
      let camp-y item site-id site-ys
      let infantry-squad-width item site-id site-troops-per-road
      create-trucks 1 [
        setxy 0 camp-y
        set site-num site-id
        set num-pontoons truck-pontoon-module-capacity * truck-group-depth ;; TODO - Set this appropriately
        set shape "truck"
        set color black
        set size 10
        set heading 90  ;; face right
      ]
      create-infantry 1 [
        setxy 0 camp-y
        set site-num site-id
        set num-troops infantry-squad-width * infantry-squad-depth
        set color red
        set size 6
        set heading 90  ;; face right
      ]
    ]
  ]
end

to move-units
  ask infantry [
    let infantry-speed infantry-road-speed
    if on-dirt? [
      set infantry-speed infantry-dirt-speed
    ]
    safe-forward-infantry infantry-speed
  ]
  ask trucks [
    let truck-speed truck-road-speed
    if on-dirt? [
      set truck-speed truck-dirt-speed
    ]
    safe-forward-trucks truck-speed
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
      ;; If all pieces are there, animate/draw the brdige
      ifelse num-pontoon-pieces-built = num-pontoons-req [
        draw-bridge site-id
        set site-pontoon-bridge-built replace-item site-id site-pontoon-bridge-built true
      ] [
        ;; Otherwise, if the necessary ppl/resources are there, add to the existing bridge
        if builders-ready and (num-pontoons-ready >= 1) [
          let current-total-pontoons-built total-pontoons-built
          set total-pontoons-built (current-total-pontoons-built + 1)
          set site-pontoon-built-count replace-item site-id site-pontoon-built-count (num-pontoon-pieces-built + 1)
          set site-pontoon-count replace-item site-id site-pontoon-count (num-pontoons-ready - 1)
        ]
      ]
    ]
 ]
end

;; ---------------- HELPER FUNCTIONS -----------------

;; Prevents spawners from getting backed up when line reaches them
to update-spawn-availability
  foreach chosen-site-ids [site-id ->
    let camp-y item site-id site-ys
    ;; Check if there's a unit near (0, camp-y)
    let units-here turtles with [abs (xcor - 0) < 0.5 and abs (ycor - camp-y) < 0.5]

    ifelse any? units-here [
      set site-is-spawning replace-item site-id site-is-spawning false
    ] [
      set site-is-spawning replace-item site-id site-is-spawning true
    ]
  ]
end

;; Checks if there's a specific terrain type ahead (in front patch at distance 1).
to-report terrain-ahead? [terrain-type]
  let ahead patch-ahead 1
  if ahead = nobody [
    report false
  ]
  report ([terrain] of ahead = terrain-type)
end

;; These checks if the next infantry in the same line is too close ahead horizontally.
to-report infantry-close-ahead?
  ;; Find the next troop in the same row whose xcor is greater than mine.
  let next-infantry min-one-of (other infantry with [
    site-num = [site-num] of myself and xcor > [xcor] of myself
  ]) [ xcor ]

  ;; If there's no troop ahead in my line, we're clear
  if next-infantry = nobody [
    report false
  ]

  ;; Otherwise, measure how close that troop is
  let gap ([xcor] of next-infantry - xcor)
  report (gap < unit-collision-spacing)
end

;; These checks if the next truck in the same line is too close ahead horizontally.
to-report trucks-close-ahead?
  ;; Find the next troop in the same row whose xcor is greater than mine.
  let next-trucks min-one-of (other trucks with [
    site-num = [site-num] of myself and xcor > [xcor] of myself
  ]) [ xcor ]

  ;; If there's no troop ahead in my line, we're clear
  if next-trucks = nobody [
    report false
  ]

  ;; Otherwise, measure how close that troop is
  let gap ([xcor] of next-trucks - xcor)
  report (gap < unit-collision-spacing)
end


;; Prevents trucks from jumping past next truck or the water
to safe-forward-trucks [total-distance]
  let step-size 1
  let moved 0
  while [moved < total-distance] [
    ;; Move only if there's no close unit in front
    ifelse (not trucks-close-ahead?) [
      ;; If there's no water ahead, just move
      ifelse (not terrain-ahead? "water") and (not terrain-ahead? "bridge") [
        fd step-size
        set moved moved + step-size
      ]
      ;; If there's water ahead
      [
        ;; If the site is not full, despawn and add pontoons
        ifelse (not site-full-of-pontoons? site-num) [
          site-add-pontoons
        ] ;; If it is full already, wait at the bank
        [stop]
      ]

    ] [stop]
  ]
end


;; Prevents infantry from jumping past next truck or the water
to safe-forward-infantry [total-distance]
  let step-size 1
  let moved 0
  while [moved < total-distance] [
    ;; Move only if there's no close unit in front
    ifelse (not infantry-close-ahead?) [
      if terrain-ahead? "goal" [
        set total-infantry-crossed total-infantry-crossed + num-troops
        die
      ]
      ;; If there's no water ahead, just move as usual
      ifelse (not terrain-ahead? "water") [
        fd step-size
        set moved moved + step-size
      ]
      ;; If there's water ahead
      [
        ;; If the site is not full, despawn and join builders
        ifelse (not site-full-of-builders? site-num) [
          site-add-builders
        ] ;; If it is full already, wait at the bank
        [stop]
      ]

    ] [stop]
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
  die
end

to-report site-full-of-pontoons? [site-n]
  let pontoon-ct item site-n site-pontoon-count
  let required-ct item site-num num-required-pontoons-per-site
  report pontoon-ct >= required-ct
end

to site-add-pontoons
  let pontoon-ct item site-num site-pontoon-count
  set site-pontoon-count replace-item site-num site-pontoon-count (pontoon-ct + num-pontoons)
  die
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

@#$#@#$#@
GRAPHICS-WINDOW
2407
237
3800
2123
-1
-1
3.0
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
2231
271
2298
305
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
2233
351
2299
387
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
1336
478
2372
536
Whether Each Site Can Spawn More Units
site-is-spawning
0
1
14

MONITOR
1337
580
2377
639
Infantry Ready to Build at each Site
site-builder-count
17
1
14

MONITOR
1337
687
2376
746
Pontoons Modules Ready to be Built at each Site
site-pontoon-count
17
1
14

MONITOR
1340
792
2380
850
Number of Pontoon Modules Built at each Site
site-pontoon-built-count
17
1
14

MONITOR
1347
897
2381
955
Whether Each Site has completed Building its Bridge
site-pontoon-bridge-built
17
1
14

MONITOR
1350
1010
1675
1069
Total Number of Pontoon Modules Built
total-pontoons-built
17
1
14

MONITOR
1352
1109
1581
1168
Number of Troops Crossed
total-infantry-crossed
17
1
14

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
