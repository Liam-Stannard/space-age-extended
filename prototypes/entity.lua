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

-- Reactive Edge Plating (Phase 0 feasibility spike).
--
-- A perimeter plate that does NOT absorb impacts: it spends one loaded
-- charge to destroy an incoming asteroid at contact range. Implemented as a
-- real `ammo-turret` with a 1-slot ammo inventory, so that inserters load it
-- with exactly the native code path that loads a gun turret -- no
-- control-stage logic at all. The whole point of the spike is that this
-- shape is entirely data-stage; every line below is either measured against
-- the running engine or explicitly flagged as a placeholder.
--
-- Placement restriction (the void-adjacency rule) uses vanilla's own
-- `tile_buildability_rules`, the same mechanism `asteroid-collector` and
-- `thruster` use to require open space in front of them. Two rules, ANDed:
-- solid foundation under the plate, and void in the single tile the plate
-- faces. The rules rotate with the entity's direction, which is why this is
-- a rotatable 1x1 rather than a direction-less one -- there is no way to
-- express "void on ANY of my four sides" natively, so instead the plate is
-- oriented outward and each rim face gets its own rotation. That is the same
-- ergonomics vanilla already asks of the asteroid collector.
--
-- Visuals are placeholder: vanilla gun turret's own base sprite, scaled down
-- to roughly a tile.
--
-- What the Phase 0 spike actually measured, on a headless server over RCON
-- (all numbers from real runs, not from reading docs):
--
--   * Inserter loading works, identically to a gun turret. A burner inserter
--     between a chest of charges and a plate filled it unattended, tracking a
--     vanilla gun-turret control tick for tick: both at 8 after 600 ticks,
--     both at 10 after 1200. See automated_ammo_count below for the one
--     surprise that fell out of this.
--   * The custom ammo-category isolates completely, both directions and
--     through the inserter path, not just the insert API: firearm-magazine
--     and railgun-ammo into a plate both inserted 0; a Reactive Charge into a
--     vanilla gun turret inserted 0; and an inserter sat next to a gun turret
--     with a chest of 20 charges moved none of them in 900 ticks.
--   * A plated rim genuinely saves the platform. Same route, same thrust,
--     3600 ticks: an UNPLATED 20x20 platform lost 400 of 400 foundation tiles
--     and all 12 interior witness chests (it was gone by tick ~2400). The
--     PLATED one -- 64 plates, one per buildable perimeter tile, 20 charges
--     each -- finished at 400/400 tiles, 12/12 witnesses at full health,
--     64/64 plates alive, having spent 44 of 1280 charges (3.4%).
--   * Asteroid class is naturally distinguishable without any script, purely
--     through the charge's damage vs. vanilla's per-size resistances: the
--     same plate with the same load cleared a `big` asteroid and its entire
--     cascade with zero tile loss, but against a `huge` ran its 10 charges
--     dry and leaked 8 foundation tiles.
data:extend({
  {
    -- Dedicated ammo-category so a plate can be fed nothing but a Reactive
    -- Charge, and a Reactive Charge fits nothing but a plate. Mirrors the
    -- `sae-thermionic-fuel` fuel-category above.
    type = "ammo-category",
    name = "sae-reactive-charge",
  },
  {
    type = "ammo-turret",
    name = "sae-reactive-edge-plating",
    icon = "__base__/graphics/icons/gun-turret.png",
    icon_size = 64,
    icon_mipmaps = 4,
    flags = { "placeable-player", "player-creation" },
    minable = { mining_time = 0.2, result = "sae-reactive-edge-plating" },
    max_health = 200,
    -- The plate is one tile of rim. Slightly under-sized collision box so it
    -- sits inside its tile without fighting neighbouring plates.
    collision_box = { { -0.4, -0.4 }, { 0.4, 0.4 } },
    selection_box = { { -0.5, -0.5 }, { 0.5, 0.5 } },
    -- Platform-only, via the same genuine surface property the Thermionic
    -- Generator and vanilla's own thruster use (vacuum), not a planet-name
    -- check (design/framework.md §2.3).
    surface_conditions = {
      { property = "pressure", min = 0, max = 0 },
    },
    -- The void-adjacency rule. Rule 1: the plate's own tile must be real
    -- platform foundation. Rule 2: the tile immediately in front of it (its
    -- facing direction; -Y when facing north) must be empty space. Both
    -- areas rotate with the entity, so one prototype covers all four rim
    -- faces by rotation. `remove_on_collision` lets a blueprint/ghost drop
    -- the entity rather than block, matching asteroid-collector.
    --
    -- MEASURED against a 20x20 platform, every rim face x every rotation,
    -- through both can_place_entity and a real create_entity (they agreed in
    -- every cell), and through blueprint_ghost as well as manual placement
    -- (identical results -- so a rim blueprint obeys the same rule):
    --
    --              N     E     S     W
    --   north rim  YES   no    no    no
    --   south rim  no    no    YES   no
    --   west rim   no    no    no    YES
    --   east rim   no    YES   no    no
    --   NW corner  YES   no    no    YES
    --   SE corner  no    YES   YES   no
    --   interior   no    no    no    no
    --   1 in from  no    no    no    no
    --
    -- A perfect diagonal: enforcement is entirely native, exact on all four
    -- faces, correct on corners (both outward directions allowed), and
    -- rejects every interior tile in every rotation. No on_built rejection
    -- handler is needed, and control.lua stays untouched by this feature.
    tile_buildability_rules = {
      { area = { { -0.4, -0.4 }, { 0.4, 0.4 } }, required_tiles = { layers = { ground_tile = true } }, colliding_tiles = { layers = { empty_space = true } }, remove_on_collision = true },
      { area = { { -0.4, -1.4 }, { 0.4, -0.6 } }, required_tiles = { layers = { empty_space = true } }, remove_on_collision = true },
    },
    -- NOTE: there is deliberately no `weight` here. MEASURED: a space
    -- platform's mass is exactly its hub's weight plus the sum of its tiles'
    -- weights, and nothing else -- placing 20 plates, loading 200 charges
    -- into them, and adding a chest of 200 loose charges all left
    -- LuaSpacePlatform::weight byte-identical at 80000, while 20 more
    -- foundation tiles moved it to 84000 (= 20 x the tile's own weight of
    -- 200). `weight` as "mass contributed to a platform" exists only on
    -- TilePrototype and SpacePlatformHubPrototype; on any other entity the
    -- key is simply ignored. So a plate cannot be given a mass cost, and
    -- cannot be balanced against platform speed. (Confirmed in flight too:
    -- see the note on the item's weight in prototypes/item.lua.)
    turret_base_has_direction = true,
    -- No warm-up: a plate that has to unfold before firing loses the race
    -- against anything already at contact range.
    rotation_speed = 1,
    preparing_speed = 1,
    folding_speed = 1,
    attacking_speed = 1,
    prepare_with_no_ammo = false,
    alert_when_attacking = true,
    -- Mandatory on turret prototypes (the engine refuses to load without
    -- it). Matched to the plate's own contact range rather than gun
    -- turret's 40 -- a plate calls for help over its own tile, not across
    -- the platform.
    call_for_help_radius = 4,
    inventory_size = 1,
    -- MEASURED, and not what the name suggests: `automated_ammo_count` is the
    -- count an *inserter* fills the turret up to and then stops at -- it is
    -- not only a logistics-request number. Spiked side by side against a
    -- vanilla gun-turret on an identical inserter+chest rig: the gun turret
    -- settled at exactly 10 (its own automated_ammo_count) and the plate at
    -- exactly whatever this field said, in both cases far below the ammo
    -- item's stack size, so it is this field and not a stack limit. Set to
    -- 10 to match gun-turret. Anything lower silently caps how deep a plate
    -- can be stocked, which on a platform -- where there are no construction
    -- robots to top anything up (space-age/base-data-updates.lua puts
    -- roboports behind pressure >= 10) -- is the difference between a plate
    -- that survives an asteroid wave and one that runs dry mid-wave.
    automated_ammo_count = 10,
    attack_parameters = {
      type = "projectile",
      ammo_category = "sae-reactive-charge",
      -- Placeholder. One charge per shot, a short cooldown so a plate that
      -- fails to kill something can try again before impact.
      cooldown = 15,
      projectile_creation_distance = 0.4,
      projectile_center = { 0, 0 },
      -- "Contact range". Deliberately far shorter than gun turret's 18 or
      -- railgun turret's 40 -- this is the number the whole design hangs on.
      --
      -- MEASURED and sufficient: with range 4, a plate on the rim killed an
      -- inbound asteroid with the plate itself still at 200/200 and a witness
      -- entity one tile behind it still at 350/350, and zero tile damage, for
      -- every class up to and including `big`. An identical plate with an
      -- empty ammo slot, same tile, same asteroid, was destroyed outright.
      --
      -- Range 4 is, however, the limit on the plate's LATERAL coverage too,
      -- and that turns out to matter more than the head-on case: when a large
      -- asteroid is killed it spawns children with an x-offset spread of up
      -- to ~4.5 tiles (asteroid.lua's dying_trigger_effect uses
      -- offsets +/- collision_radius*0.5 with an equal offset_deviation), so
      -- some children of a `huge` land outside a single plate's reach. A lone
      -- plate therefore leaks; a continuous rim of them does not (see the
      -- 3600-tick exposure result in the file header).
      range = 4,
      -- Copied from both vanilla gun-turret and railgun-turret: a negative
      -- penalty makes the turret *prefer* threatening asteroids over any
      -- other target. Without it a plate would happily ignore the thing
      -- about to hit it.
      threatening_asteroid_penalty = -20,
      health_penalty = 10,
    },
    graphics_set = {
      base_visualisation = {
        animation = {
          filename = "__base__/graphics/entity/gun-turret/gun-turret-base.png",
          priority = "high",
          width = 150,
          height = 118,
          scale = 0.25,
        },
      },
    },
    folded_animation = {
      filename = "__base__/graphics/entity/gun-turret/gun-turret-base.png",
      priority = "high",
      width = 150,
      height = 118,
      scale = 0.25,
    },
  },
})
