patches-own [terrain-type move-multiplier] ;Each patch (grid cell) has a terrain type and a movement multiplier that affects agent movement.

; breed: different agent types
breed [soldiers soldier]
breed [artilleries artillery]
breed [drones drone]
breed [vehicles vehicle]

; properties for each breed
soldiers-own [soldiers-speed setting-up-pontoon? state target-bridge target-shore goal-reached has-target head-x head-y tx ty]
artilleries-own [artillery-range accuracy]
drones-own [detection-probability detection-timer increasing-accuracy?]
vehicles-own [vehicle-speed]

; global variables
globals [counter bridges-list site-list bridge-timers build-duration construct-team]
; counter: for counting soldiers that successfully passed the river
; bridges-list: for saving existing bridges coordinate, west point and east point
; site-list: for saving available pontoon construction site
; bridge-timers:
; build-duration: build time for each pontoon

to setup
  clear-all
  set counter 0
  set-patch-size 1
  resize-world 0 277 0 525
  print "setting bridge-list"
  ; hard code permanent bridges
  set bridges-list [
    [[109 403] [123 391]] ; bridge 1
    [[107 243] [127 241]]
    [[115 44] [134 48]]
  ]
  ; hard code pontoon sites
  set site-list [
    [[109 343] [120 344]] ; site 1
    [[108 293] [117 297]]
    [[105 198] [115 198]]
    [[119 125] [127 126]]
    [[117 62] [126 62]]
  ]
  ; set parameters
  set build-duration 1000
  set construct-team 30
  set bridge-timers []

  print "setting terrain"
  setup-terrain
  print "setting actors"
  setup-actors

  reset-ticks
  print "Setup complete"
end


to go
  if not any? soldiers [stop]

  move-soldiers
  update-bridge-timers

  ;detect-pontoons
  ;fire-artillery
  tick
end

to setup-terrain
  import-pcolors "Irpin_pixel_2.png"  ; Load the map image into patches

  ;; Define terrain type mapping (rounded pcolor -> terrain-type, move-multiplier)
  let terrain-map [
    [36 "woodland" 0.7]
    [107 "water" 0]
    [0 "bridge" 1.0]
    [10 "open-field" 1.0]
    [44 "east-side" 1.0]
    [red "destroyed" 0]
    [yellow "pontoon" 1.0]
  ]

  ask patches [
    let c round pcolor  ;; Round to avoid floating-point issues

    ;; Find matching terrain type and move multiplier from terrain-map
    let match filter [entry -> first entry = c] terrain-map

    if not empty? match [
      set terrain-type item 1 first match
      set move-multiplier item 2 first match
    ]
    if empty? match [
      set terrain-type "unknown"
      set move-multiplier 1.0
    ]
  ]
end

to setup-actors
  create-soldiers 700 [
    set shape "person"
    set color red
    let spawn-point one-of (list (list 80 327) (list 67 300) (list 14 192))
    let spawn-x first spawn-point + random 10 - random 10
    let spawn-y last spawn-point + random 10 - random 10
    setxy spawn-x spawn-y
    set soldiers-speed 4
    set setting-up-pontoon? false
    set state "searching"
    set has-target false
  ]

end

;; ========================== on tick actions ===========================
to move-soldiers
  ask soldiers [

    ;; State: Searching for a way to cross
    if state = "searching" [
      if not empty? bridges-list [
        let closest-bridge nobody
        let min-distance 999999  ;; A large initial value

        ;; Loop through each bridge and find the closest west shore point
        foreach bridges-list [ bridge ->
          let wx first first bridge  ;; Extract x of west shore
          let wy last first bridge   ;; Extract y of west shore
          let d distancexy wx wy     ;; Compute distance

          if d < min-distance [
            set min-distance d
            set closest-bridge bridge ;; Store the closest bridge
          ]
        ]
        if closest-bridge != nobody [
          set target-bridge first closest-bridge ;; Extract west shore point
          set state "heading-bridge"
        ]
      ]
      if empty? bridges-list [
        let closest-shore nobody
        let min-distance 999999

        foreach site-list [ site ->
          let wx first first site
          let wy last first site
          let d distancexy wx wy

          if d < min-distance [
            set min-distance d
            set closest-shore site
            set tx first last site
            set ty last last site
          ]
        ]
        if closest-shore != nobody [
          set target-shore first closest-shore
          set state "heading-shore"
        ]
      ]
    ]

    ;; State: Moving towards the west shore of the bridge
    if state = "heading-bridge" [
      if not has-target [
        set head-x first target-bridge  ;; Extract x of west shore
        set head-y last target-bridge   ;; Extract y of west shore

        ; Move towards the west point of the bridge
        face patch head-x head-y
        set has-target true
      ]
      fd 1

      ; If within a radius of 2 patches from the west point, start crossing
      if distancexy head-x head-y <= 2 [
        set state "crossing-bridge"
        set has-target false
      ]
    ]


    ;; State: Moving across the bridge to the east shore
    if state = "crossing-bridge" [
      if not has-target [
        let east-point nobody

        ;; Find the east shore point of the bridge matching target-bridge
        foreach bridges-list [ bridge ->
          if first bridge = target-bridge [
            set east-point last bridge  ;; Extract the east shore point
          ]
        ]

        set head-x first east-point
        set head-y last east-point
        ;face east-point
        face patch head-x head-y
        set has-target true
      ]
      fd 1
      if distancexy head-x head-y <= 2 [
        set state "heading-east-side"
        set has-target false
      ]
    ]

    ;; State: Moving towards the final east-side goal
    if state = "heading-east-side" [
      if not has-target [
        let target-east-side min-one-of patches with [terrain-type = "east-side"] [distance myself]

        set head-x [pxcor] of target-east-side
        set head-y [pycor] of target-east-side
        face patch head-x head-y
      ]
      fd 1
      if distancexy head-x head-y <= 1 [
        set counter counter + 1
        set goal-reached true
        die  ;; Remove soldier from the simulation
      ]
    ]

    ;; State: Moving to a shore to build a bridge
    if state = "heading-shore" [
      if not has-target [
        set head-x first target-shore  ;; Extract x of west shore
        set head-y last target-shore   ;; Extract y of west shore

        ; Move towards the west point of the bridge
        face patch head-x head-y
        set has-target true
      ]
      fd 1

      ; If within a radius of 2 patches from the west point, start crossing
      if distancexy head-x head-y <= 2 [
        set state "building-bridge"
        set has-target false
      ]
    ]

    ;; State: Building a bridge (Placeholder for future logic)
    if state = "building-bridge" [
      let nearby-troops count (other soldiers in-radius 3 with [state = "building-bridge"])
      if nearby-troops >= construct-team [
        let bridge-data (list (list head-x head-y) (list tx ty))
        let existing-entry filter [entry -> first entry = bridge-data] bridge-timers

        if empty? existing-entry [
          set bridge-timers lput (list bridge-data ticks) bridge-timers
        ]
      ]
    ]
  ]
end

to update-bridge-timers
  let new-timers []

  foreach bridge-timers [ entry ->
    let bridge-data first entry  ;; Should be [[wx wy] [ex ey]]
    let start-time last entry

    ifelse (ticks - start-time) >= build-duration [
      ;; Extract shore coordinates correctly
      let wx first first bridge-data
      let wy last first bridge-data
      let ex first last bridge-data
      let ey last last bridge-data

      ;; Draw the bridge
      draw-bridge wx wy ex ey

      ;; Remove this bridge data from bridge-timers
      set bridge-timers filter [timer-entry ->
        first first first timer-entry != wx or last first first timer-entry != wy ;; Keep only bridges not matching wx, wy
      ] bridge-timers

      ;; Remove from site-list and add to bridges-list
      set site-list remove bridge-data site-list
      set bridges-list lput bridge-data bridges-list

      print (word "Bridge built at: " bridge-data)
      ; change soldiers around to state: crossing-bridge
      ask soldiers with [state = "building-bridge" and distancexy wx wy <= 4] [
        set state "crossing-bridge"  ;; Change to the state when bridge construction is done
        set head-x ex
        set head-y ey
        face patch head-x head-y
        set has-target true
      ]

    ] [
      ;; Keep unfinished bridge timers
      set new-timers lput entry new-timers
    ]
  ]

  ;; Update the global list with ongoing timers
  set bridge-timers new-timers
end



;; ===================================== functions =====================================
to check-pcolor
  show [pcolor] of patch mouse-xcor mouse-ycor
end

to check-terrain
  ask n-of 10 patches [  ;; Pick 10 random patches to check
    show (word "Patch (" pxcor "," pycor ") - " terrain-type " | pcolor: " pcolor)
  ]
end

to check-patch
  ask patch (round mouse-xcor) (round mouse-ycor) [
    show (word "Patch (" pxcor "," pycor ") - " terrain-type " | pcolor: " pcolor)
  ]
end

to check-soldiers-state
  let random-soldiers n-of 10 soldiers  ;; Select 10 random soldiers

  ask random-soldiers [
    print (word "Soldier ID: " who " | State: " state)  ;; Print soldier ID and their current state
  ]
end

to destroy-all-bridges
  foreach bridges-list [ bridge ->
    let wx first first bridge  ;; Extract wx (west shore x-coordinate)
    let wy last first bridge   ;; Extract wy (west shore y-coordinate)
    let ex first last bridge  ;; Extract ex (east shore x-coordinate)
    let ey last last bridge   ;; Extract ey (east shore y-coordinate)

    ;; Destroy around the west shore (wx, wy)
    destroy-around wx wy

    ;; Destroy around the east shore (ex, ey)
    destroy-around ex ey
  ]
  set bridges-list []
end

to destroy-around [cx cy]
  ;; Loop through all patches and check distance
  ask patches [
    if distancexy cx cy <= 15 and terrain-type = "bridge" [
      set pcolor red                ;; Set patch color to red
      set terrain-type "destroyed"   ;; Set terrain type to "destroyed"
      set move-multiplier 0          ;; Example of setting the move multiplier to zero
    ]
  ]
end

to draw-all-bridges
  foreach site-list [ site ->
    let wx first first site
    let wy last first site
    let ex first last site
    let ey last last site

    draw-bridge wx wy ex ey

    ;; Move the drawn bridge to bridges-list
    set bridges-list lput site bridges-list
  ]
  ;; Remove drawn bridges from site-list
  set site-list filter [site -> not member? site bridges-list] site-list

  print "pontoon bridge (yellow) drawn"
end

to draw-bridge [wx wy ex ey]
  let width 3  ;; Half-width of the bridge (so full width = 10)

  let bx (ex - wx)
  let by (ey - wy)
  let dist_temp sqrt (bx * bx + by * by)

  ;; Normalize direction vector
  let unit-x bx / dist_temp
  let unit-y by / dist_temp

  ;; Perpendicular vector for width
  let perp-x -1 * unit-y
  let perp-y unit-x

  ;; Iterate along the bridge path
  foreach (range 0 dist_temp 0.5) [ i ->
    let cx (wx + i * unit-x)
    let cy (wy + i * unit-y)

    ;; Color the patches in a 10-wide strip
    foreach (range (-1 * width) width 0.5) [ j ->
      let px (cx + j * perp-x)
      let py (cy + j * perp-y)
      ask patch round px round py [
        set pcolor yellow
        set terrain-type "pontoon"
      ]
    ]
  ]
end

@#$#@#$#@
GRAPHICS-WINDOW
210
10
647
448
-1
-1
13.0
1
10
1
1
1
0
1
1
1
-16
16
-16
16
0
0
1
ticks
30.0

BUTTON
78
104
141
137
NIL
NIL
NIL
1
T
OBSERVER
NIL
NIL
NIL
NIL
1

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
