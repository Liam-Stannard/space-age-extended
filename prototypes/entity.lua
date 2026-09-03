-- New entities introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §9 -- the Quench Turbine, the mod's one new
-- building (justified per design/framework.md §2.3: its output per shipped
-- Magmatic Core is a *recipe choice*, since the turbine clips vapour hotter
-- than it can use, and nothing in the game trades fuel value against a
-- recipe tier that way).
--
-- This replaces the earlier Thermionic Generator, a `reactor`-type entity
-- with a scripted temperature/efficiency curve, two hidden paired entities
-- (a power interface and a filtered coolant container) and ~750 lines of
-- control-stage Lua. That design was abandoned because it could not survive
-- contact with vanilla's heat network: a reactor's heat_buffer feeds every
-- consumer attached to it, and vanilla heat exchangers plus steam turbines
-- would have converted its waste heat into roughly as much electricity again,
-- making the generator's own output irrelevant. The only native fix was to
-- run the whole heat network below the heat exchanger's 500-degree
-- min_working_temperature, which works but leaves the temperature scale and
-- the efficiency curve fighting each other. The Quench Turbine reaches the
-- same design goal -- output per core is a decision the player tunes, not a
-- constant -- with no heat network, no hidden entities and no runtime script
-- at all. See the plan at ~/.claude/plans/quench-turbine.md.
--
-- The turbine is a real `generator`: the engine computes its power from
-- fluid flow, the fluid's heat_capacity and its temperature, and clips
-- anything above maximum_temperature. That clipping *is* the mechanic, so it
-- must stay native -- a script that faked it would lose the tooltip and the
-- native "insufficient fluid" status the player reads while tuning.

-- Base's own helpers. `pipecovers` defines the global pipecoverspictures();
-- `sounds` is a plain module return. A mod has to require both by absolute
-- path -- vanilla's entities.lua reaches them by relative path, which only
-- resolves inside base itself.
require("__base__.prototypes.entity.pipecovers")
local sounds = require("__base__.prototypes.entity.sounds")

data:extend({
  {
    type = "generator",
    name = "sae-quench-turbine",
    icon = "__space-age-extended__/graphics/icons/quench-turbine.png",
    icon_size = 64,
    icon_mipmaps = 4,
    flags = { "placeable-neutral", "player-creation" },
    minable = { mining_time = 0.3, result = "sae-quench-turbine" },
    max_health = 300,
    fast_replaceable_group = "sae-quench-turbine",
    -- Space-platform-only placement via a genuine physical surface property
    -- (zero pressure/vacuum), exactly mirroring vanilla's own `thruster` --
    -- not an arbitrary planet-name check, so it doesn't run afoul of
    -- framework.md §2.3's "no building-placement gimmicks" rule. Kept from
    -- the Thermionic Generator, which used the same gate for the same reason.
    surface_conditions = {
      { property = "pressure", min = 0, max = 0 },
    },
    -- Power = fluid_usage_per_tick * 60 * heat_capacity * (T - default_temperature),
    -- clipped at maximum_temperature. With Quench Vapour's 5kJ/degree
    -- (prototypes/fluid.lua) and default_temperature 15:
    --   0.2 fluid/tick = 12 fluid/s
    --   12 * 5kJ * (315 - 15) = 18MW at the cap.
    -- maximum_temperature 315 is the clip point every quench recipe is
    -- balanced against: the lean tier-1 recipe makes a small volume of
    -- 900-degree vapour and throws away roughly two thirds of it here, while
    -- the tier-2 recipe makes far more vapour at exactly 315 and wastes
    -- nothing. That difference *is* the tech ladder (design doc §9.3).
    effectivity = 1,
    fluid_usage_per_tick = 0.2,
    maximum_temperature = 315,
    -- Vapour is consumed as a fluid whose temperature carries the energy, not
    -- burned as a fuel -- the same relationship vanilla's steam turbine has
    -- with steam. burns_fluid = true would read fuel_value instead and ignore
    -- temperature entirely, which would delete the whole mechanic.
    burns_fluid = false,
    -- Deliberately no scale_fluid_usage: the turbine draws only what the grid
    -- demands, so a platform sitting idle at a waypoint consumes no vapour
    -- and therefore no Magmatic Core. Beating nuclear's idle burn was an
    -- explicit goal of §9.1 and it now falls out of the entity type for free.
    resistances = {
      { type = "fire", percent = 70 },
    },
    -- Vanilla steam turbine's footprint (3x5 / 5x3). two_direction_only
    -- below means it only rotates between those two.
    collision_box = { { -1.25, -2.35 }, { 1.25, 2.35 } },
    selection_box = { { -1.5, -2.5 }, { 1.5, 2.5 } },
    fluid_box = {
      volume = 200,
      pipe_covers = pipecoverspictures(),
      pipe_connections = {
        { flow_direction = "input-output", direction = defines.direction.south, position = { 0, 2 } },
        { flow_direction = "input-output", direction = defines.direction.north, position = { 0, -2 } },
      },
      production_type = "input",
      filter = "sae-quench-vapour",
      -- Below this the fluid is treated as unusable rather than feeding the
      -- turbine at a trickle. 100 matches vanilla's steam turbine; it also
      -- means a line that has sat cooling doesn't quietly produce almost
      -- nothing while looking like it works.
      minimum_temperature = 100.0,
    },
    energy_source = {
      type = "electric",
      usage_priority = "secondary-output",
    },
    two_direction_only = true,
    -- Visuals: this mod's own recoloured sheets, built from vanilla's steam
    -- turbine by tools/recolour-turbine.py. Deliberately not a `tint` on
    -- vanilla's files: a tint multiplies, and vanilla's turbine is already
    -- brass and rust (its saturated pixels sit at hue 15-45 degrees, only
    -- ~16% of the opaque area), so a warm tint changed almost nothing and
    -- muddied the greys. The script instead rotates just those warm accents
    -- to a cryogenic teal at their original lightness, leaving the neutral
    -- metal alone, so every bit of vanilla's shading and ambient occlusion
    -- survives and only the hue reads differently.
    --
    -- Teal rather than the mod's magma orange on purpose: this building is
    -- the *cold* half of the mechanic (Ice, and Fluoroketone at -150C), and
    -- orange would have been indistinguishable from the sprite it started
    -- from. Still placeholder-grade in the sense that it's derived art, not
    -- drawn art, but it now reads as its own machine on a platform.
    --
    -- Shadows are pure alpha silhouettes, so the script copies them across
    -- unrecoloured rather than leaving the entity straddling two mods'
    -- directories. Frame counts, shifts and scales are vanilla's, with
    -- util.by_pixel shifts pre-divided by 32.
    pictures = {
      north = {
        animation = {
          layers = {
            {
              filename = "__space-age-extended__/graphics/entity/quench-turbine/quench-turbine-V.png",
              width = 217,
              height = 374,
              frame_count = 8,
              line_length = 4,
              shift = { 0.148438, 0.0 },
              run_mode = "backward",
              scale = 0.5,
            },
            {
              filename = "__space-age-extended__/graphics/entity/quench-turbine/quench-turbine-V-shadow.png",
              width = 302,
              height = 260,
              repeat_count = 8,
              line_length = 1,
              draw_as_shadow = true,
              shift = { 1.234375, 0.765625 },
              run_mode = "backward",
              scale = 0.5,
            },
          },
        },
      },
      east = {
        animation = {
          layers = {
            {
              filename = "__space-age-extended__/graphics/entity/quench-turbine/quench-turbine-H.png",
              width = 320,
              height = 245,
              frame_count = 8,
              line_length = 4,
              shift = { 0.0, -0.085938 },
              run_mode = "backward",
              scale = 0.5,
            },
            {
              filename = "__space-age-extended__/graphics/entity/quench-turbine/quench-turbine-H-shadow.png",
              width = 435,
              height = 150,
              repeat_count = 8,
              line_length = 1,
              draw_as_shadow = true,
              shift = { 0.890625, 0.5625 },
              run_mode = "backward",
              scale = 0.5,
            },
          },
        },
      },
    },
    -- No `smoke` block: vanilla's steam turbine vents turbine-smoke, and a
    -- sealed platform machine venting exhaust into vacuum would be wrong.
    impact_category = "metal-large",
    open_sound = sounds.machine_open,
    close_sound = sounds.machine_close,
    working_sound = {
      sound = {
        filename = "__base__/sound/steam-turbine.ogg",
        volume = 0.49,
        speed_smoothing_window_size = 60,
        advanced_volume_control = { attenuation = "exponential" },
        audible_distance_modifier = 0.8,
      },
      match_speed_to_activity = true,
      max_sounds_per_prototype = 3,
      fade_in_ticks = 4,
      fade_out_ticks = 20,
    },
    perceived_performance = { minimum = 0.25, performance_to_activity_rate = 2.0 },
  },
})
