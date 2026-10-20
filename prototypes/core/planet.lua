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

local minute = 60 * 60 -- ticks

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
      -- A 3-minute day. Above 0, the engine runs the surface's cycle: it sets
      -- ticks_per_day to this value and clears always_day and freeze_daytime,
      -- both when the surface is created and when a save made with another
      -- value is loaded. At 0 the engine freezes the surface at noon instead
      -- (always_day and freeze_daytime set, daytime 0, darkness 0): it never
      -- gets dark at all.
      -- What makes the cycle mostly dark is when dusk, evening, morning and
      -- dawn fall. Those belong to the surface, not the prototype, and
      -- control.lua sets them: full dark from evening to morning, 80 % of the
      -- cycle, and full light only in the 4 % from dawn to dusk around noon.
      -- At night the darkness is 0.85, from the engine's default
      -- min_brightness of 0.15. The colour grading is the engine default.
      ["day-night-cycle"] = 3 * minute,
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
