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

-- Circuit-connector helpers. Unlike the two above these live in
-- `core/lualib`, which is on every mod's data-stage Lua path already, so the
-- plain module name is the correct spelling here -- no `__core__.` prefix,
-- and vanilla's own space-age/prototypes/entity/turrets.lua opens with
-- exactly this line. Requiring it defines three globals this file uses:
-- `circuit_connector_definitions` (with `.create_single` / `.create_vector`),
-- `universal_connector_template`, and `default_circuit_wire_max_distance`
-- (= 9). It also pulls in core/lualib/circuit-connector-generated-definitions
-- .lua itself, which is where `universal_connector_template` is actually
-- defined -- a 40-frame sheet, 8 per row, so variations 0-7 are the eight
-- compass orientations of the connector's wire pins.
require("circuit-connector-sprites")
local util = require("util")

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

-- ART PENDING -- per-direction base art for Reactive Edge Plating, standing in
-- until the real sprite exists: frame 0 of row `dir` of vanilla's 4-direction
-- gun-turret raising sheet (130x126 per frame, rows in N/E/S/W order). This is
-- the only stand-in in the entity; nothing numeric below depends on it.
local function sae_plating_base_direction(dir)
  return {
    filename = "__base__/graphics/entity/gun-turret/gun-turret-raising.png",
    priority = "medium",
    width = 130,
    height = 126,
    frame_count = 1,
    y = dir * 126,
    -- Scale and shift are in step: the source sheet is 130x126 px, so 0.5
    -- draws it about two tiles across, which at least fills a 3x2 panel
    -- instead of sitting as a one-tile dot in the middle of it. The real art
    -- is a 3x2 armour panel with its own folded / preparing / attacking
    -- states.
    shift = { 0, -0.82 },
    scale = 0.5,
  }
end

-- Reactive Edge Plating.
--
-- A perimeter plate that does NOT absorb impacts: it spends one loaded
-- charge to destroy an incoming asteroid at contact range. Implemented as a
-- real `ammo-turret` with a 1-slot ammo inventory, so that inserters load it
-- with exactly the native code path that loads a gun turret. The whole point
-- is that this shape is entirely data-stage: control.lua and scripts/ are
-- untouched by it, and there is no runtime logic anywhere in the capability.
--
-- PROGRESS.md is the system of record for the measurements -- the footprint
-- comparison, the promethium ladder, the placement matrix, the circuit runs,
-- the perimeter and standing-buffer tables. This file explains DECISIONS: why
-- a given key holds a given value, and which engine facts constrain it. If a
-- claim here and a number in PROGRESS.md ever disagree, PROGRESS.md is right
-- and the comment has drifted.
--
-- Two things about the capability are still open, and neither is a number:
-- the ART (a stand-in sprite and stand-in icons -- see
-- graphics/icon-prompts.md; the entity sprite stands in as vanilla gun
-- turret's own base), and the RECIPE plus TECHNOLOGY in prototypes/recipe.lua
-- and prototypes/technology.lua, which are the one deliberate provisional
-- seam: their real ingredient is Thermal-Shock Composite, which does not
-- exist yet.
--
-- The plate is rotatable because the void-adjacency rule below is expressed
-- in the entity's own frame: there is no native way to say "void on ANY of my
-- four sides", so the plate is oriented outward instead and each rim face
-- gets its own rotation. That is the same ergonomics vanilla already asks of
-- the asteroid collector. Facing is therefore load-bearing on this entity --
-- it drives placement, the firing arc and the connector offsets alike.
--
-- Shared-resource interaction, per design/framework.md §4.5.1 (a capability
-- must draw on one shared resource and feed another). The plate DRAWS on the
-- platform's consumable throughput -- charges, competing for the same
-- inserter/belt/cargo budget as everything else aboard. What it FEEDS is
-- negative and implicit: every asteroid a plate destroys is an asteroid the
-- collectors never harvest, so plating the leading edge trades chunk income
-- for hull integrity. That interaction is real, but it falls out of turret
-- targeting on its own -- nothing in this prototype expresses it, and there
-- is no knob here to tune it with. Recorded so the design phase knows the
-- §4.5 obligation is currently met only emergently. The one thing that is NOT
-- available as a lever is `weight`: a plate cannot be made to cost platform
-- speed (see the note where it is deliberately absent), so its whole cost has
-- to live in the charge supply chain.
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
    -- Anchored to asteroid-collector, not to gun-turret: 0.2 is
    -- asteroid-collector's own mining_time
    -- (space-age/prototypes/entity/entities.lua:803), the other rim-line
    -- entity that gets laid and lifted in rows, where gun-turret's 0.5 is
    -- priced as a one-off emplacement.
    minable = { mining_time = 0.2, result = "sae-reactive-edge-plating" },
    -- SURVIVABILITY -- the one genuine design choice in the numbers pass, and
    -- it is resolved as "THE RIM IS THE ANSWER". A plate is not armour: it
    -- destroys asteroids by fire and is consumed when it fails. HP is set so
    -- the number is anchored rather than accidental; it is not bought as a
    -- defence, because MEASURED it cannot be.
    --
    -- Contact damage from a leaked promethium asteroid was measured directly
    -- (PROGRESS.md, "T13"), and the numbers make the choice one-sided: a
    -- `small` deals 200, a `medium` 1280 and a `big` 9550, so a `medium` is
    -- 3.2x this plate's health and a `big` 24x. No sane hit point total
    -- survives a leak of anything above `small`; HP cannot be the answer to a
    -- leak, and a continuous rim is. The plate is specified only as a
    -- continuous rim.
    --
    -- What 400 does buy, and the only reason it is not left at 200: the old
    -- 200 sat EXACTLY on the measured `small` figure, so the cheapest rock on
    -- the promethium route was a guaranteed plate kill and a dry rim deleted
    -- itself to gravel. At 400 a dry plate eats one promethium `small` and
    -- survives at 200/400, so a rim that runs out of charges degrades
    -- gradually and visibly (`alert_when_attacking`, damaged sprite) instead
    -- of vanishing. 400 is vanilla gun-turret's own max_health
    -- (base/prototypes/entity/turrets.lua) -- turret-grade, not armour-grade;
    -- railgun turret is 4000 and rocket turret 1500, and this is deliberately
    -- neither.
    --
    -- NO `resistances`, and that is a decision rather than an omission.
    -- Asteroid contact damage was measured to be `impact`, and resistances DO
    -- apply to it, so an impact resistance is a real available lever (the
    -- fingerprint-probe run that established it is in PROGRESS.md). Taking it
    -- is precisely the thing this capability must not do: a percent impact
    -- resistance is literally "absorbs impacts", scaling with the size of the
    -- rock, which is the hull armour / deflector answer another tree owes.
    -- This plate spends a charge per impact or it dies. Leaving `resistances`
    -- unset keeps the failure economy exactly two-tiered: cheap charges
    -- consumed per impact, expensive plates consumed per failure.
    max_health = 400,
    -- FOOTPRINT: 3 tiles along the rim x 2 tiles deep. Chosen over 1x1 and
    -- 2x2 on measurements, not on taste; the three were built as real
    -- prototypes and measured side by side. Rotation swaps the dimensions
    -- (3x2 north/south becomes 2x3 east/west) and the engine handles that
    -- for both the boxes and the buildability areas below. The measurement
    -- tables live in PROGRESS.md, "Footprint: measured, and why it is 3x2";
    -- what decided it, and the only part that constrains a line here:
    --
    -- CORNER FEEDABILITY is the one measurement with a hard floor rather than
    -- a gradient, and the one the 1x1 loses outright. An inserter cannot stand
    -- diagonally, so a plate with no orthogonally adjacent free platform tile
    -- can never be fed -- by any belt layout, any bus, any chamfer. At 1x1
    -- four plates (one per corner) are unfeedable in principle at every
    -- platform size and eight cannot be fed simultaneously; at 2x2 it is 1-4
    -- depending on size; at 3x2 it is 0 unfeedable and a full 24/24 matching,
    -- reconfirmed at sides 10, 20, 21, 22, 31 and 40. Three tiles is the
    -- narrowest plate that reaches past the perpendicular corner band to a
    -- tile an inserter can stand on, which is why the width is 3 and not 2.
    --
    -- The other three footprint measurements (entity counts, parity-gap leak
    -- behaviour, corner arc coverage) all favour 3x2 as well but none of them
    -- pins a number in this file; they are in PROGRESS.md. The one caveat
    -- worth carrying here, because it bounds what may be claimed for the
    -- shape: parity gaps up to 6 tiles were measured not to leak for a
    -- promethium `big`, but `huge` is not deterministic and leaked through a
    -- 6-tile gap in one run of two. The rim defends by FIRE, not occupancy,
    -- and the footprint stands on feedability, not on gap coverage.
    --
    -- Slightly under-sized collision box (0.1 in on every side) so plates sit
    -- inside their tiles without fighting their neighbours, exactly as the
    -- 1x1 did.
    collision_box = { { -1.4, -0.9 }, { 1.4, 0.9 } },
    selection_box = { { -1.5, -1.0 }, { 1.5, 1.0 } },
    -- Derivable from collision_box, but stated: the engine snaps an entity's
    -- position to a tile centre on an odd axis and a tile BOUNDARY on an even
    -- one, so a 3x2 plate's centre is (n+0.5, m) facing north and (n, m+0.5)
    -- facing east. Anything that places these by script has to compute that
    -- per direction.
    tile_width = 3,
    tile_height = 2,
    -- Platform-only, via the same genuine surface property the Thermionic
    -- Generator and vanilla's own thruster use (vacuum), not a planet-name
    -- check (design/framework.md §2.3).
    --
    -- This is also what settles `heating_energy`, which is left unset and so
    -- is 0W (prototype-api.json, EntityPrototype.heating_energy). That is
    -- correct BY CONSTRUCTION here, not a default that was fallen into:
    -- heating only exists on a surface whose planet sets
    -- `entities_require_heating`, and Aquilo is the only one in the game that
    -- does (space-age/prototypes/planet/planet.lua:680, the sole occurrence
    -- in the whole data tree). Aquilo's surface pressure is 300
    -- (planet.lua:643) and a space platform's is 0
    -- (space-age/prototypes/surface.lua:12), so the vacuum condition above
    -- makes this plate unplaceable on the one surface where heating_energy
    -- would ever be read. Declaring a value would be dead weight.
    --
    -- Vanilla's railgun and rocket turrets do declare "50kW"
    -- (space-age/prototypes/entity/turrets.lua:318 and :432) -- but neither
    -- carries any `surface_conditions` at all (verified: no
    -- `surface_conditions` key anywhere in base/ or space-age/ turrets.lua),
    -- so both are placeable on Aquilo's surface and both genuinely need it.
    -- The difference is placement scope, not a balance asymmetry between the
    -- plate and them.
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
    -- Shape copied from vanilla's own two users of this mechanism:
    -- space-age/prototypes/entity/entities.lua:691-694 (asteroid-collector)
    -- and :908-911 (thruster) -- both pair a `ground_tile` footprint rule
    -- with an `empty_space` corridor rule exactly like this.
    --
    -- Rule 1's `colliding_tiles = {layers = {empty_space = true}}` is NOT
    -- redundant with its `required_tiles = {layers = {ground_tile = true}}`,
    -- and deleting it silently breaks the whole restriction: the
    -- `empty-space` tile itself declares `ground_tile = true` in its own
    -- collision_mask (space-age/prototypes/tile/tiles.lua:211-222, alongside
    -- empty_space, water_tile, floor, object, player and the rest). A
    -- `ground_tile` requirement alone is therefore satisfied by void, and the
    -- plate would become placeable in mid-air. The explicit `empty_space`
    -- exclusion is what makes rule 1 mean "real foundation".
    --
    -- What the two rules buy, over a 44-cell placement matrix tabulated in
    -- PROGRESS.md: a perfect diagonal, and at each corner only the ONE lateral
    -- offset that sits flush inside the platform. That is the pinwheel a rim
    -- wants, and it falls out of the rules rather than having to be taught --
    -- no on_built rejection handler, control.lua untouched.
    --
    -- Three oracles agree in every cell -- `can_place_entity` with `manual`,
    -- `can_place_entity` with `blueprint_ghost`, and reviving a real
    -- `entity-ghost` -- so a rim blueprint obeys exactly the same rule a
    -- hand-built one does. Those three are the only valid ones, and this is
    -- worth knowing before writing any future placement test: MEASURED,
    -- `LuaSurface.create_entity` is a scripted force-place that runs NO build
    -- check whatsoever -- it returned a valid entity on interior tiles and on
    -- bare void, for this plate AND for vanilla `asteroid-collector` and
    -- `thruster`, the two entities these rules are modelled on. A
    -- create_entity-based placement test produces a false PASS in every cell
    -- and proves nothing about buildability.
    --
    -- Both areas are written in the entity's NORTH frame and rotate with it,
    -- which is what lets one prototype cover all four rim faces. Rule 1 is
    -- the 3x2 body; rule 2 is the 3-wide strip of void one tile in front of
    -- its leading edge (y = -1 locally, so the strip is y in [-2,-1]).
    tile_buildability_rules = {
      { area = { { -1.4, -0.9 }, { 1.4, 0.9 } }, required_tiles = { layers = { ground_tile = true } }, colliding_tiles = { layers = { empty_space = true } }, remove_on_collision = true },
      { area = { { -1.4, -1.9 }, { 1.4, -1.1 } }, required_tiles = { layers = { empty_space = true } }, remove_on_collision = true },
    },
    -- NOTE: there is deliberately no `weight` here, and adding one would be
    -- dead weight in both senses. `weight` as "mass contributed to a platform"
    -- exists only on TilePrototype and SpacePlatformHubPrototype; on any other
    -- entity the key is simply ignored, so a plate cannot be given a mass cost
    -- and cannot be balanced against platform speed. MEASURED both ways --
    -- plates, loaded charges and loose charges all left LuaSpacePlatform's
    -- weight byte-identical, while adding foundation tiles moved it (numbers
    -- in PROGRESS.md).
    turret_base_has_direction = true,
    -- All four of these are EXPLICIT NO-OPS, kept only so the values are
    -- visible rather than implied: `rotation_speed`, `preparing_speed` and
    -- `folding_speed` default to `default_speed`, which itself defaults to 1,
    -- and `attacking_speed` defaults to 1 directly (prototype-api.json,
    -- TurretPrototype). Note also that `attacking_speed` and `folding_speed`
    -- are animation playback rates (`1 / speed` = animation duration), not
    -- anything to do with how fast the turret gets a shot away. The real
    -- warm-up knob is `BaseAttackParameters.warmup` -- ticks between the
    -- order to fire and the shot, default 0 -- correctly left unset below,
    -- since a plate that has to spin up loses the race against anything
    -- already at contact range.
    rotation_speed = 1,
    preparing_speed = 1,
    folding_speed = 1,
    attacking_speed = 1,
    prepare_with_no_ammo = false,
    alert_when_attacking = true,
    -- Circuit connector -- the ONLY prototype-side thing the rim's circuit
    -- behaviour needs. Having one at all is what unlocks `read_ammo` (a
    -- platform can hold at a depot until its rim is re-armed) and the target
    -- priority list, including its circuit-driven forms; both were verified
    -- over RCON, both are pure vanilla turret GUI, and neither needs script.
    -- Runs in PROGRESS.md, "Circuit control".
    --
    -- A VECTOR, one entry per direction, not `create_single`. The count is
    -- not a style choice: prototype-api.json, TurretPrototype.circuit_connector
    -- states it outright -- "8 elements if building-direction-8-way flag is
    -- set, or 16 elements if building-direction-16-way flag is set, or 4
    -- elements if turret_base_has_direction is set to true, or 1 element."
    -- This plate sets `turret_base_has_direction = true` and carries neither
    -- direction flag, so the engine wants exactly FOUR. (Vanilla's railgun
    -- turret supplies 8 because it is an 8-way building; copying its list
    -- wholesale would be wrong here.)
    --
    -- MEASURED, because "the docs say 4" and "the engine wants 4" are not the
    -- same claim: throwaway clones of this prototype carrying 1 entry and 8
    -- entries were both REFUSED at load with a hard error naming the number
    -- -- "In circuit connector definitions expected table of 4 elements but
    -- 1 were given" / "but 8 were given". The rule is enforced in both
    -- directions, so this list cannot silently drift. Four entries load, and
    -- `read_ammo` was then read back correctly in all four rotations.
    --
    -- `create_single` would have loaded too, and would have been wrong in
    -- three rotations out of four: it pins the connector to one pixel offset
    -- regardless of facing, and this entity's whole point is that it faces
    -- outward. Vanilla's own note on rocket-turret --
    -- "TurretPrototype takes vector" (space-age/prototypes/entity/
    -- circuit-network.lua:95) -- is the same observation.
    --
    -- Variations index the 40-frame universal connector sheet, 8 per row;
    -- row 0 is the eight compass orientations, so N/E/S/W = 0/6/4/2, matching
    -- the order railgun-turret uses for its 8-way list. Offsets put the
    -- connector on the plate's INBOARD edge in each facing -- the side the
    -- wire actually comes from, since the outboard side is void.
    circuit_connector = circuit_connector_definitions.create_vector(
      universal_connector_template,
      {
        { variation = 0, main_offset = util.by_pixel( 9,  9), shadow_offset = util.by_pixel( 9,  9), show_shadow = false },
        { variation = 6, main_offset = util.by_pixel(-9,  9), shadow_offset = util.by_pixel(-9,  9), show_shadow = false },
        { variation = 4, main_offset = util.by_pixel(-9, -9), shadow_offset = util.by_pixel(-9, -9), show_shadow = false },
        { variation = 2, main_offset = util.by_pixel( 9, -9), shadow_offset = util.by_pixel( 9, -9), show_shadow = false },
      }
    ),
    circuit_wire_max_distance = default_circuit_wire_max_distance,
    -- Mandatory on turret prototypes (the engine refuses to load without
    -- it). Matched to the plate's own contact range rather than gun
    -- turret's 40 -- a plate calls for help over its own footprint, not across
    -- the platform.
    call_for_help_radius = 4,
    -- THE AMMO TRIPLE. `inventory_size` here, `automated_ammo_count` below,
    -- and the charge's `stack_size` in prototypes/item.lua are ONE decision
    -- with three spellings, and they were chosen together against the 3x2
    -- rim, not inherited from gun-turret.
    --
    -- `inventory_size = 1` so a plate's capacity is EXACTLY the charge's
    -- stack_size and nothing else -- one number governs it, and `read_ammo`
    -- puts a single stack on the wire instead of a sum the player has to
    -- reason about. Every ammo turret in base and space-age uses 1.
    --
    -- What forced the other two off gun-turret's values is that the 3x2
    -- footprint stands only 24 plates on a 20x20 rim where the 1x1 spike stood
    -- 76, so the standing charge buffer had to be restored per plate rather
    -- than per rim. The plate counts, the measured burn rate and the resulting
    -- endurance table are in PROGRESS.md, "The perimeter table, recomputed for
    -- 3x2".
    inventory_size = 1,
    -- MEASURED, and not what the name suggests: `automated_ammo_count` is the
    -- count an *inserter* fills the turret up to before it stops -- not only a
    -- logistics-request number. It is a FLOOR, not a cap, so on a turret with
    -- headroom above the floor a bigger inserter hand overshoots it, and the
    -- settle point rises with `force.inserter_stack_size_bonus` (measured
    -- ladder in PROGRESS.md, taken while this entity's floor was still 10).
    --
    -- At 20 that overshoot cannot happen here at all: the floor equals the
    -- 1-slot capacity, so there is no headroom to overshoot into and every
    -- force settles at exactly 20 regardless of research. VERIFIED at
    -- `inserter_stack_size_bonus = 6`, the case where a whole hand could
    -- overshoot -- the plate pinned at 20 with the leftover charge stranded in
    -- the inserter's hand, while the vanilla gun-turret control on the same
    -- rig went 10 -> 14. Floor == capacity does not jam, it just stops. On a
    -- platform there are no construction robots to top anything up
    -- (space-age/base-data-updates.lua puts roboports behind pressure >= 10),
    -- so this level is the only stock a design can count on.
    --
    -- Why 20 rather than gun-turret's 10. Lone-plate runs against a single
    -- promethium `big` or `huge` ended with the magazine EMPTY, so the worst
    -- single-plate demand is bounded only from BELOW at 10 -- those runs were
    -- magazine-capped, not demand-capped. A floor of 10 therefore guarantees
    -- no more than what one encounter was already seen to consume entirely,
    -- leaving the plate dry for the next rock. 20 is at least twice that
    -- bound and was never emptied; it is headroom, not a proof that no
    -- encounter can dry a plate. It also restores the standing rim buffer the
    -- 3x2 footprint took away (24 plates x 20 = 480 on a 20x20).
    --
    -- Floor == capacity is vanilla precedent, not an invention: railgun
    -- turret has inventory_size 1 and automated_ammo_count 10 against a
    -- railgun-ammo stack_size of 10 (space-age/prototypes/entity/turrets.lua
    -- :324-325, space-age/prototypes/item.lua:643).
    automated_ammo_count = 20,
    attack_parameters = {
      type = "projectile",
      ammo_category = "sae-reactive-charge",
      -- One charge per shot, 15 ticks between shots (4 shots/s). KEPT at 15,
      -- and MEASURED NOT TO BE THE BINDING CONSTRAINT -- which is the only
      -- reason it needs no further tuning.
      --
      -- What a plate is actually asked for is set by the cascade, not by the
      -- parent rock: every dying asteroid above `small` spawns exactly three
      -- of the next size down, so a promethium `huge` is 1 + 3 + 9 + 27 rocks.
      -- Measured rim-wide over a fully plated 20x20, continuous and gapped
      -- runs pooled: a `medium` costs 4 charges, a `big` a deterministic 14,
      -- and a `huge` anywhere from 20 to 41 -- `huge` did not repeat, and the
      -- run log and the reason are in PROGRESS.md. Those are rim-wide totals
      -- spread over the plates near the impact, and a whole encounter --
      -- parent plus every generation of the cascade -- was measured to resolve
      -- inside a 700-tick window. At 15 ticks one plate can fire 46 times
      -- inside that window and empties a full 20-charge magazine in 300 ticks,
      -- comfortably past the worst demand ever seen on a single plate (a
      -- magazine-capped 10, so a lower bound rather than a measured peak).
      --
      -- Confirmed from the other direction too: the lone-plate runs that
      -- FAILED failed with charges still loaded (6 of 10 spent, tiles lost),
      -- i.e. they were coverage failures inside the range-4 / 180-degree
      -- envelope, never rate failures. Shortening the cooldown would not have
      -- saved one of them.
      --
      -- 15 is therefore chosen at the slow end of what the demand allows, so
      -- the plate reads as one deliberate shot per impact rather than a
      -- stream: gun-turret is 6 (base/prototypes/entity/turrets.lua:552),
      -- rocket turret 120 and railgun turret 170
      -- (space-age/prototypes/entity/turrets.lua:529, :379).
      cooldown = 15,
      -- The muzzle offset, 0.4 tiles out from `projectile_center`. Cosmetic
      -- only here and deliberately small: `target_type = "entity"` with an
      -- `instant` action_delivery (prototypes/item.lua) makes the shot
      -- hitscan, so nothing travels and this cannot affect what is hit. Kept
      -- non-zero so the muzzle flash sits on the plate's outboard face rather
      -- than in its middle.
      projectile_creation_distance = 0.4,
      projectile_center = { 0, 0 },
      -- "Contact range". Deliberately far shorter than gun turret's 18 or
      -- railgun turret's 40 -- this is the number the whole design hangs on.
      --
      -- MEASURED and sufficient: with range 4, a plate on the rim killed an
      -- inbound asteroid with the plate itself undamaged (200/200 on the
      -- 200 hp prototype those runs were taken against) and a witness
      -- entity one tile behind it still at 350/350, and zero tile damage, for
      -- every class up to and including `big`. An identical plate with an
      -- empty ammo slot, same tile, same asteroid, was destroyed outright.
      --
      -- That holds on metallic/carbonic/oxide. On PROMETHIUM (double health,
      -- double damage_per_hp) it does not: measured, a lone plate spends
      -- 8-10 charges on a `big` and 6-10 on a `huge`, leaks the cascade in
      -- more than half of those runs, and is itself destroyed in about one
      -- in five. A continuous rim is what fixes that: no plate was destroyed
      -- or even damaged in any rim run at any promethium class, and a `big`
      -- never got a tile past it. `huge` is the one class that is not settled
      -- -- see the note on the footprint above and the run log in PROGRESS.md.
      --
      -- Range 4 is, however, the limit on the plate's LATERAL coverage too,
      -- and that turns out to matter more than the head-on case: when a large
      -- asteroid is killed it spawns children with an x-offset spread of up
      -- to ~4.5 tiles (asteroid.lua's dying_trigger_effect uses
      -- offsets +/- collision_radius*0.5 with an equal offset_deviation), so
      -- some children of a `huge` land outside a single plate's reach. A lone
      -- plate therefore leaks -- MEASURED, a lone plate against a `huge`
      -- loses 0-2 foundation tiles depending on where the cascade scatters --
      -- and the flanking plates of a rim are what cover that spread. This is
      -- the reason the plate is specified as a continuous rim rather than as a
      -- unit that can be placed sparsely.
      range = 4,
      -- MEASURED-CRITICAL, and the one thing this whole block gets wrong if
      -- it is omitted. `range_mode` defaults to "center-to-center"
      -- (prototype-api.json, BaseAttackParameters.range_mode) and vanilla
      -- asteroids are built with collision_box = {{-r,-r},{r,r}} from
      -- `collision_radiuses = {0.4, 0.5, 1, 2, 4.5}` (chunk/small/medium/
      -- big/huge) -- space-age/prototypes/entity/asteroid.lua:165-172,
      -- applied at :492. Under the default, "range 4" therefore meant 4
      -- tiles to the rock's CENTRE: a real standoff of 3.5 tiles for a
      -- small, 3.0 for a medium, 2.0 for a big, and -0.5 for a HUGE -- the
      -- rock's hull was already past the plate before the plate was allowed
      -- to fire at all, and since `prepare_range` defaults to `range` the
      -- plate was still folded at that moment. That gave the per-class
      -- ladder two independent causes at once (the damage-vs-resistance
      -- arithmetic documented in prototypes/item.lua, AND an undocumented
      -- geometry cliff at `huge`), which design/endgame.md §6 forbids.
      -- With center-to-bounding-box, range 4 means 4 tiles from the plate to
      -- the rock's HULL for every class, so the ladder has exactly one
      -- cause. (Chunks alone are unaffected: asteroid.lua:492 gives a chunk
      -- no collision_box at all, so for a chunk this degenerates back to
      -- center-to-center.) Vanilla precedent:
      -- space-age/prototypes/entity/turrets.lua:724 (tesla turret),
      -- base/prototypes/entity/flying-robots.lua:773 and :856.
      range_mode = "center-to-bounding-box",
      -- A forward hemisphere, not the default 1 (= 360 degrees). The
      -- placement rule already fixes which way a plate faces -- void in
      -- front, foundation behind -- so the firing arc should match the
      -- plate's own outward face. On the default a rim plate engages a rock
      -- four tiles INBOARD, firing back across its own platform: that breaks
      -- the capability's facing story (plate the leading edge and half your
      -- journeys are naked) and is wrong for hull armour. A hemisphere still
      -- covers everything outboard of the rim, cascade children scattering
      -- laterally included -- MEASURED: switching from 1 to 0.5 cost nothing
      -- on either the per-class ladder or a 3600-tick plated flight (see
      -- PROGRESS.md). 0.5 is also the practical ceiling: the engine clamps
      -- anything in (0.5, 1) down to 0.5, since targeting in arcs larger
      -- than a half circle is not implemented (prototype-api.json,
      -- BaseAttackParameters.turn_range). Vanilla precedent: railgun turret
      -- 0.20 (space-age/prototypes/entity/turrets.lua:398), flamethrower
      -- turret 1/3 (base/prototypes/entity/fire.lua:890).
      turn_range = 0.5,
      -- Copied from both vanilla gun-turret and railgun-turret: a negative
      -- penalty makes the turret *prefer* threatening asteroids over any
      -- other target. Without it a plate would happily ignore the thing
      -- about to hit it.
      threatening_asteroid_penalty = -20,
      -- 10 is gun-turret's value (base/prototypes/entity/turrets.lua:567,
      -- "Shoot things with lower health ratio"), and it is a CHOICE here
      -- rather than a copy, because vanilla's own anti-asteroid turret does
      -- the opposite: railgun-turret is health_penalty = -10
      -- (space-age/prototypes/entity/turrets.lua:396, "Try to shoot things
      -- that have a higher remaining health ratio (i.e. more healthy) to
      -- maximize damage per shot").
      --
      -- Positive = "discourage targeting units with a higher health RATIO"
      -- (prototype-api.json, BaseAttackParameters.health_penalty), so a plate
      -- finishes a rock it has already wounded rather than starting a fresh
      -- one. That is the right preference for THIS weapon and the wrong one
      -- for the railgun, and the difference is entirely in the ammo: railgun
      -- ammo scales its effect with what it hits, so spending a shot on a
      -- full-health target extracts the most damage from it, whereas a
      -- Reactive Charge deals a flat 5000 no matter what it lands on. With a
      -- fixed payload the waste is OVERKILL, so a plate should spend its next
      -- charge on the rock nearest to dying. Since the ladder in
      -- prototypes/item.lua is mostly one-shot-or-not, this only arbitrates
      -- the multi-charge classes (promethium `big` and `huge`) -- exactly the
      -- ones where a half-killed rock is sitting there wasting charges.
      health_penalty = 10,
    },
    graphics_set = {
      -- ART PENDING, but the DIRECTIONALITY here is not a stand-in. With
      -- `turret_base_has_direction = true` the engine looks up a per-direction
      -- entry here; handed a single Animation it draws that one for every
      -- facing, and all four rotations then render identically. Facing is
      -- load-bearing on this entity -- it drives the placement rule and the
      -- 180-degree `turn_range` arc -- so a plate that looks the same in all
      -- four rotations gives the player no way to see which way a placed rim
      -- actually points. Vanilla's precedent for the table is
      -- `railgun_turret_base()` in
      -- space-age/prototypes/entity/railgun-turret-pictures.lua:43.
      --
      -- The source sheet is vanilla's gun-turret raising animation, which is
      -- already a 4-direction sheet (direction_count = 4, frame_count = 5,
      -- laid out one row per direction in N/E/S/W order), so frame 0 of row
      -- `d` is that direction's idle pose. Real art replaces this wholesale
      -- and will need folded/preparing/attacking states of its own.
      base_visualisation = {
        animation = {
          north = sae_plating_base_direction(0),
          east = sae_plating_base_direction(1),
          south = sae_plating_base_direction(2),
          west = sae_plating_base_direction(3),
        },
      },
    },
    folded_animation = {
      filename = "__base__/graphics/entity/gun-turret/gun-turret-base.png",
      priority = "high",
      width = 150,
      height = 118,
      scale = 0.5,
    },
  },
})
