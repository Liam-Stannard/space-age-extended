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

-- Placeholder per-direction base art for Reactive Edge Plating: frame 0 of row
-- `dir` of vanilla's 4-direction gun-turret raising sheet (130x126 per frame,
-- rows in N/E/S/W order). Scale 0.25 keeps the sprite inside the plate's 1x1
-- footprint; the shift is vanilla's -26.5px halved to match that scale.
local function sae_plating_base_direction(dir)
  return {
    filename = "__base__/graphics/entity/gun-turret/gun-turret-raising.png",
    priority = "medium",
    width = 130,
    height = 126,
    frame_count = 1,
    y = dir * 126,
    shift = { 0, -0.41 },
    scale = 0.25,
  }
end

-- Reactive Edge Plating (Phase 0 feasibility spike).
--
-- A perimeter plate that does NOT absorb impacts: it spends one loaded
-- charge to destroy an incoming asteroid at contact range. Implemented as a
-- real `ammo-turret` with a 1-slot ammo inventory, so that inserters load it
-- with exactly the native code path that loads a gun turret -- no
-- control-stage logic at all. The whole point of the spike is that this
-- shape is entirely data-stage; every line below is either measured against
-- the running engine or explicitly flagged as a placeholder. The run log for
-- those measurements lives in PROGRESS.md -- only the engine facts that
-- explain a specific line below are kept here.
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
-- Shared-resource interaction, per design/framework.md §4.5.1 (a capability
-- must draw on one shared resource and feed another). The plate DRAWS on the
-- platform's consumable throughput -- charges, competing for the same
-- inserter/belt/cargo budget as everything else aboard. What it FEEDS is
-- negative and implicit: every asteroid a plate destroys is an asteroid the
-- collectors never harvest, so plating the leading edge trades chunk income
-- for hull integrity. That interaction is real, but it falls out of turret
-- targeting on its own -- nothing in this prototype expresses it, and there
-- is no knob here to tune it with. Recorded so the design phase knows the
-- §4.5 obligation is currently met only emergently.
--
-- `weight` is permanently off the table as a balancing lever for this
-- capability -- see the MEASURED note on the entity below. A plate can never
-- be made to cost platform speed, so its whole cost has to live in the
-- charge supply chain.
--
-- CIRCUIT CONTROL. The connector below is the only prototype-side thing the
-- rim's circuit behaviour needs; everything else is player configuration on
-- the placed entity. Two capabilities were verified over RCON against this
-- prototype:
--
--   * `read_ammo` puts the plate's remaining Reactive Charges on the wire, so
--     a platform can hold at a depot until its rim is re-armed. MEASURED in
--     all four rotations at once -- four plates, one per rim face, loaded
--     with 3/5/7/9 charges and each on its own red network -- and every
--     network read back exactly its own plate's count.
--   * TARGET PRIORITY works, including from the circuit network, which makes
--     "ignore small chunks, leave them to the collectors" an automatable
--     decision rather than a flat income penalty for plating a mining
--     platform. MEASURED three ways, all positive: entity-side
--     (`set_priority_target` + `ignore_unprioritised_targets`), circuit-gated
--     (`LuaTurretControlBehavior.set_ignore_unlisted_targets` plus
--     `ignore_unlisted_targets_condition`), and list-from-the-wire
--     (`set_priority_list = true`, with the target named by an ENTITY-type
--     signal on the network). In the gated case a plate holding 20 charges
--     let a `small` pass untouched and killed a `medium`, and flipping the
--     one signal the condition tests made it engage the `small` again.
--     None of that is in this prototype and none of it needs script: it is
--     the vanilla turret GUI, unlocked by having a connector at all.
--
-- Visuals are placeholder: vanilla gun turret's own base sprite, scaled down
-- to roughly a tile. The icon art is placeholder too -- prompts for the real
-- item/entity/technology art are in graphics/icon-prompts.md.
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
    -- MEASURED against a 20x20 platform, every rim face x every rotation,
    -- through `can_place_entity` and through reviving an `entity-ghost`
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
    --
    -- Those two oracles are the only valid ones, and this is worth knowing
    -- before writing any future placement test: MEASURED,
    -- `LuaSurface.create_entity` is a scripted force-place that runs NO build
    -- check whatsoever -- it returned a valid entity on interior tiles and on
    -- bare void, for this plate AND for vanilla `asteroid-collector` and
    -- `thruster`, the two entities these rules are modelled on. A
    -- create_entity-based placement test produces a false PASS in every cell
    -- and proves nothing about buildability.
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
    -- Circuit connector. This is what makes a rim's remaining charges
    -- readable, so a platform can hold at a depot until it is re-armed --
    -- switch the plate's control behaviour to `read_ammo` and every plate
    -- adds its Reactive Charge count onto the wire.
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
    -- turret's 40 -- a plate calls for help over its own tile, not across
    -- the platform.
    call_for_help_radius = 4,
    inventory_size = 1,
    -- MEASURED, and not what the name suggests: `automated_ammo_count` is the
    -- count an *inserter* fills the turret up to before it stops -- it is not
    -- only a logistics-request number. It is a FLOOR, not a cap: the inserter
    -- keeps swinging until the turret holds at least this many, and a whole
    -- hand lands in the final swing. Measured side by side against a vanilla
    -- gun-turret on identical inserter+chest rigs, the settle point scales
    -- with `force.inserter_stack_size_bonus` and the two entities behave
    -- identically: bonus 0 settles at 10, bonus 3 at 12, bonus 6 at 14. So
    -- this number is the guaranteed minimum stock; a researched-up force gets
    -- more, never less. Set to 10 to match gun-turret -- lowering it would
    -- lower that guaranteed floor, which on a platform (no construction
    -- robots to top anything up -- space-age/base-data-updates.lua puts
    -- roboports behind pressure >= 10) is the only stock level a design can
    -- actually count on.
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
      -- That holds on metallic/carbonic/oxide. On PROMETHIUM (double health,
      -- double damage_per_hp) it does not: measured, a lone plate spends
      -- 8-10 charges on a `big` and 6-10 on a `huge`, leaks the cascade in
      -- more than half of those runs, and is itself destroyed in about one
      -- in five. A continuous rim of plates took zero damage and lost zero
      -- tiles in every promethium run at every class. See the ladder note on
      -- the charge's damage in prototypes/item.lua and the tables in
      -- PROGRESS.md.
      --
      -- Range 4 is, however, the limit on the plate's LATERAL coverage too,
      -- and that turns out to matter more than the head-on case: when a large
      -- asteroid is killed it spawns children with an x-offset spread of up
      -- to ~4.5 tiles (asteroid.lua's dying_trigger_effect uses
      -- offsets +/- collision_radius*0.5 with an equal offset_deviation), so
      -- some children of a `huge` land outside a single plate's reach. A lone
      -- plate therefore leaks -- MEASURED, a lone plate against a `huge`
      -- loses 0-2 foundation tiles depending on where the cascade scatters --
      -- while a continuous rim of them does not (the 3600-tick exposure run
      -- finished 400/400 tiles; numbers in PROGRESS.md).
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
      health_penalty = 10,
    },
    graphics_set = {
      -- Placeholder art, but the DIRECTIONALITY is not placeholder. With
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
      scale = 0.25,
    },
  },
})
