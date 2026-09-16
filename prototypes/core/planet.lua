-- The Core: the intact metallic heart of the shattered world, past the point
-- where every vanilla platform turns back.
--
-- Pressure 5 is the load-bearing number. The rocket silo works (it needs >= 1)
-- while boilers, furnaces, heating towers, roboports and burner inserters do
-- not (they need >= 10), so nothing burns here and there is no bot network
-- until one is earned. Gravity 50 clears every gravity threshold and makes this
-- the densest body in the game -- which is also what lets weight do the work of
-- separation on the surface, and what makes orbit worth the trip.

local map_gen = require("prototypes.core.map-gen")
local asteroid_util = require("__space-age__.prototypes.planet.asteroid-spawn-definitions")

data:extend({
  {
    type = "planet",
    name = "sae-core",
    icon = "__space-age-extended__/graphics/icons/core.png",
    starmap_icon = "__space-age-extended__/graphics/icons/starmap-core.png",
    starmap_icon_size = 512,
    gravity_pull = 10,
    distance = 95,
    orientation = 0.25,
    magnitude = 1.2,
    label_orientation = 0.15,
    order = "z[sae-core]",
    subgroup = "planets",
    map_gen_settings = map_gen(),
    pollutant_type = nil,
    solar_power_in_space = 0,
    surface_properties =
    {
      -- Zero: a sky that genuinely does not move. This used to be 216000
      -- because arc storms only struck at night, so night had to be reachable
      -- and control.lua pinned the surface at midnight to keep it there. With
      -- the storms gone the engine holds the dark on its own, and the script
      -- that held it goes with them.
      ["day-night-cycle"] = 0,
      ["magnetic-field"] = 0,         -- a dead dynamo; restarting it is the goal
      ["solar-power"] = 0,            -- not a trickle: nothing
      pressure = 5,
      gravity = 50
    },
    asteroid_spawn_influence = 1,
    asteroid_spawn_definitions = asteroid_util.spawn_definitions(asteroid_util.shattered_planet_trip, 0.8)
  },
  {
    type = "space-connection",
    name = "sae-shattered-planet-core",
    subgroup = "planet-connections",
    from = "shattered-planet",
    to = "sae-core",
    order = "z",
    length = 500000,
    asteroid_spawn_definitions = asteroid_util.spawn_definitions(asteroid_util.shattered_planet_trip)
  }
})
