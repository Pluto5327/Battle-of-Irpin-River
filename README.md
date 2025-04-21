# Battle of the Irpin River: NetLogo Simulation

## Summary

This project investigates Russia’s failed crossing of the Irpin River during the initial phase of its 2022 invasion of Ukraine. Using a custom NetLogo simulation, we model how variations in pontoon bridge deployment—specifically site selection, troop/truck spacing, and deployment ordering—might have changed the outcome. The model captures road congestion, Ukrainian artillery detection, and the timing of river crossings under resource constraints.

## Research Question

Can variations in crossing site selection, deployment ordering, and troop/truck spacing affect the Russians' ability to successfully cross the Irpin River? Which combination of these factors minimizes resource use while maximizing crossing success, given limited road access and pressure from Ukrainian artillery?

## High Level Conceptual Model

- **Russian Infantry**: Move along roads to riverbanks, build pontoon bridges when supplies arrive, and cross if bridges are complete.
- **Russian Pontoon Trucks**: Deliver bridge modules to riverbanks following a strategy. Cannot pass each other, and block site if full.
- **Ukrainian Artillery and Drones**: Detect activity at riverbanks. Probability of strike increases with time and number of active sites.
- **Environment**: Modeled as a 10×7.5 mile region northwest of Kyiv with 13 viable crossing sites, varying road widths, and a flooded river barrier.
