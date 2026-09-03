-- New entities introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §9 -- the Thermionic Generator, the mod's
-- one new building (justified per design/framework.md §2.3 by a
-- temperature-dependent efficiency curve nothing else in the game has).
--
-- Visible generator: a real `reactor`-type entity (`sae-thermionic-generator`).
-- Magmatic Core burns in its genuine burner fuel slot -- the engine itself
-- ignites/consumes it, exactly like vanilla's nuclear reactor -- giving
-- real status, tooltip, and fuel-gauge animation for free, instead of the
-- earlier "furnace with an unreachable recipe category" hack that faked
-- fuel removal via script and left the entity permanently misreporting
-- itself as broken (confirmed in real play: a stuck "no fuel"-style alert
-- and a burn gauge that never animated). `scale_energy_usage = false` so
-- the reactor always draws fuel at its full declared `consumption` rate
-- regardless of current heat -- keeping fuel rate and cooling rate
-- genuinely independent (design doc §9.2's explicit rule), rather than
-- vanilla reactor's own "throttle down near max temperature" behaviour.
-- The reactor's real heat_buffer *is* the temperature now (no separate
-- abstract number in `storage` to keep in sync) -- scripts/
-- thermionic-generator.lua subtracts from it directly for Ice cooling,
-- the same way it used to write to the old heat-interface's `.temperature`.
-- Its `connections` below are a real heat-pipe interface natively -- the
-- old hidden `sae-thermionic-generator-heat-interface` entity and its
-- bespoke 12-point connection math are gone entirely; a reactor's own
-- heat_buffer already does this.
--
-- A reactor has no electric energy_source of its own (same as vanilla
-- nuclear reactor -- it produces heat, not power), so it still can't push
-- electricity onto the grid by itself. That job stays on a hidden, paired
-- `electric-energy-interface` (`sae-thermionic-generator-power-interface`)
-- exactly as before, with `render_no_power_icon = false` -- confirmed via
-- Factorio's own prototype docs (`BaseEnergySource.render_no_power_icon`)
-- that this is the flag governing the "no power"/"no fuel" alert icon;
-- since this hidden interface's `power_production` is entirely
-- script-driven per interval rather than a fixed declared rate, leaving
-- the default on made it misreport as constantly underpowered even while
-- correctly producing (this is what the red flashing icon in real play
-- turned out to be).
--
-- Visuals still reuse vanilla nuclear reactor's own body/shadow/pipes
-- sprite files directly (plain Sprite layers) -- now honestly, since the
-- entity really is a reactor-type building.
--
-- Hidden coolant tank: a 1-slot filtered `container`, spawned/paired 1:1
-- with the visible generator, holding Ice. Never opened directly by a
-- player -- reached via an "Insert Ice" button in the generator's info
-- panel (see scripts/thermionic-generator.lua), since reactor has no
-- second item slot to hold a filtered coolant item natively.
--
-- Neither hidden entity is placed by the player directly -- not in any
-- item's place_result, no icon needed for either.

data:extend({
  {
    type = "fuel-category",
    name = "sae-thermionic-fuel",
  },
  {
    type = "reactor",
    name = "sae-thermionic-generator",
    icon = "__space-age-extended__/graphics/icons/thermionic-generator.png",
    icon_size = 64,
    icon_mipmaps = 4,
    flags = { "placeable-neutral", "placeable-player", "player-creation" },
    minable = { mining_time = 0.2, result = "sae-thermionic-generator" },
    max_health = 300,
    fast_replaceable_group = "sae-thermionic-generator",
    -- Space-platform-only placement via a genuine physical surface
    -- property (zero pressure/vacuum), exactly mirroring vanilla's own
    -- `thruster` -- not an arbitrary planet-name check, so it doesn't run
    -- afoul of framework.md §2.3's "no building-placement gimmicks" rule.
    surface_conditions = {
      { property = "pressure", min = 0, max = 0 },
    },
    -- 4x4 tile footprint (larger than the rendered body sprite below,
    -- which is closer to 2.4x2.5 tiles at its current scale -- the extra
    -- room is deliberate footprint, not a sprite-fit calculation, per
    -- explicit request). Even-width box, so the entity snaps to grid
    -- intersections rather than tile centers.
    collision_box = { { -2, -2 }, { 2, 2 } },
    selection_box = { { -2.1, -2.1 }, { 2.1, 2.1 } },
    -- Visuals: vanilla nuclear reactor's own body/shadow sprite files,
    -- used directly as plain Sprite layers (values verified against
    -- base/prototypes/entity/entities.lua's own "reactor" picture field)
    -- rather than via base's internal heat-pipe-glow/connection-graphics
    -- helpers, which are reactor-type-specific rendering machinery a
    -- dependent mod shouldn't rely on staying stable.
    lower_layer_picture = {
      filename = "__base__/graphics/entity/nuclear-reactor/reactor-pipes.png",
      width = 320,
      height = 316,
      scale = 0.5,
      shift = { -0.03125, -0.15625 },
    },
    picture = {
      layers = {
        {
          filename = "__base__/graphics/entity/nuclear-reactor/reactor.png",
          width = 302,
          height = 318,
          scale = 0.5,
          shift = { -0.15625, -0.21875 },
        },
        {
          filename = "__base__/graphics/entity/nuclear-reactor/reactor-shadow.png",
          width = 525,
          height = 323,
          scale = 0.5,
          shift = { 1.625, 0 },
          draw_as_shadow = true,
        },
      },
    },
    -- Real burner fuel slot -- the engine itself ignites/consumes
    -- Magmatic Core, giving a real fuel gauge, status, and tooltip.
    -- fuel_categories restricted to our own category (not vanilla
    -- "chemical") so this can't burn ordinary fuel and vanilla burners
    -- can't burn Magmatic Core.
    energy_source = {
      type = "burner",
      fuel_categories = { "sae-thermionic-fuel" },
      fuel_inventory_size = 1,
      effectivity = 1,
      emissions_per_minute = { pollution = 0 },
    },
    -- Real energy draw, matching the 4MW peak electrical output
    -- (scripts/thermionic-curve.lua's PEAK_POWER_W) so full-load fuel
    -- energy in equals peak electricity out at 100% efficiency. Together
    -- with Magmatic Core's fuel_value (800MJ, prototypes/item.lua) this
    -- gives a 200s burn per core -- the same as vanilla's uranium fuel
    -- cell. Together with specific_heat below it also sets the heating
    -- rate (consumption / specific_heat = 10°/s at full draw).
    consumption = "4MW",
    -- Keep fuel rate and cooling rate genuinely independent (design doc
    -- §9.2) -- without this, vanilla reactor behaviour throttles fuel
    -- draw down as heat_buffer nears max_temperature, which would make
    -- Ice's cooling *increase* fuel consumption by freeing up thermal
    -- headroom, backwards from the intended relationship.
    scale_energy_usage = false,
    heat_buffer = {
      -- max_temperature/max_transfer are the values the old heat-interface
      -- entity used, still provisional (design doc §9.4). specific_heat
      -- sets the heating *rate*: consumption / specific_heat = 4MW / 400kJ
      -- = 10°/s at full draw (verified in-engine: heat_buffer really is a
      -- linear ΔT = energy / specific_heat, to the degree). From cold
      -- that's ~60s to the top of the optimal band (600) and ~80s to the
      -- overheat threshold (800), and holding temperature needs 0.25 Ice/s
      -- (scripts/thermionic-curve.lua's HEAT_REMOVED_PER_ICE_UNIT = 40) --
      -- a rate a platform's asteroid capture can realistically sustain.
      -- An earlier 80kJ value (50°/s) overheated in ~16s and needed
      -- 1.25 Ice/s just to hold, against a 200s core burn -- far too
      -- twitchy relative to how long one core lasts.
      max_temperature = 2000,
      specific_heat = "400kJ",
      max_transfer = "10MW",
      default_temperature = 0,
      min_working_temperature = 0,
      -- Rescaled from the original 3x3-footprint version's 12-point
      -- pattern (3 points per side) to this entity's new 4x4 footprint (4
      -- points per side, at the quarter/three-quarter positions along
      -- each edge) -- same shape, one more point per side to match the
      -- extra tile of edge length. NOT yet re-verified in-engine the way
      -- the original 3x3 layout was (that one was confirmed against real
      -- heat-pipe placement before being trusted) -- needs the same
      -- verification pass after the footprint change.
      connections = {
        { position = { -1.5, -2 }, direction = defines.direction.north },
        { position = { -0.5, -2 }, direction = defines.direction.north },
        { position = { 0.5, -2 }, direction = defines.direction.north },
        { position = { 1.5, -2 }, direction = defines.direction.north },
        { position = { 2, -1.5 }, direction = defines.direction.east },
        { position = { 2, -0.5 }, direction = defines.direction.east },
        { position = { 2, 0.5 }, direction = defines.direction.east },
        { position = { 2, 1.5 }, direction = defines.direction.east },
        { position = { 1.5, 2 }, direction = defines.direction.south },
        { position = { 0.5, 2 }, direction = defines.direction.south },
        { position = { -0.5, 2 }, direction = defines.direction.south },
        { position = { -1.5, 2 }, direction = defines.direction.south },
        { position = { -2, 1.5 }, direction = defines.direction.west },
        { position = { -2, 0.5 }, direction = defines.direction.west },
        { position = { -2, -0.5 }, direction = defines.direction.west },
        { position = { -2, -1.5 }, direction = defines.direction.west },
      },
    },
    -- No neighbour_bonus -- stacking generators together isn't part of
    -- this design (unlike vanilla nuclear reactors, which reward
    -- clustering). Deliberately no meltdown_action either: framework.md
    -- §4.5 rule 3 is "degrade, don't destroy" -- this building must never
    -- explode, only run at reduced efficiency (scripts/thermionic-curve.lua's
    -- MIN_EFFICIENCY floor).
    neighbour_bonus = 0,
  },
  {
    type = "electric-energy-interface",
    name = "sae-thermionic-generator-power-interface",
    -- Never player-placed and never independently selectable -- spawned/
    -- despawned in lockstep with the visible generator by
    -- scripts/thermionic-generator.lua, which sets destructible = false
    -- and drives `power_production` every interval from the efficiency
    -- curve. gui_mode = "admins" matches vanilla's own hidden
    -- electric-energy-interface entities -- players never interact with
    -- this directly.
    flags = { "not-on-map", "not-blueprintable", "not-deconstructable", "hide-alt-info", "no-copy-paste" },
    hidden = true,
    hidden_in_factoriopedia = true,
    selectable_in_game = false,
    gui_mode = "admins",
    max_health = 300,
    collision_box = { { 0, 0 }, { 0, 0 } },
    selection_box = { { 0, 0 }, { 0, 0 } },
    collision_mask = { layers = {} },
    energy_source = {
      type = "electric",
      usage_priority = "secondary-output",
      -- Peak output; see scripts/thermionic-curve.lua's PEAK_POWER_W
      -- comment for the full justification (meaningfully below fusion's
      -- 50MW, per design doc §9.1/§9.4).
      output_flow_limit = "4MW",
      -- Sized so one interval's peak output (4MW x 1s = 4MJ) fits without
      -- clamping: scripts/thermionic-generator.lua zeroes this buffer each
      -- interval and reads back what's left to measure exactly how much
      -- the grid actually drew -- the signal for its idle guard (design
      -- doc §9.1's "no idle waste"). 2x margin over the 4MJ minimum.
      buffer_capacity = "8MJ",
      -- Since `power_production` is entirely script-driven per interval
      -- rather than a fixed declared rate, Factorio's own "not producing
      -- at capacity" alert logic doesn't apply meaningfully here -- left
      -- on, this rendered a permanent "no power" icon even while this
      -- interface was correctly producing (confirmed via
      -- prototypes:BaseEnergySource.render_no_power_icon, and by real
      -- play -- this is what the flashing red icon turned out to be).
      render_no_power_icon = false,
    },
  },
  {
    type = "container",
    name = "sae-thermionic-generator-coolant-tank",
    -- Ice's own hidden storage -- see the file header for why this is a
    -- separate entity rather than a slot on the reactor. Never opened
    -- directly by a player -- unlike the earlier furnace-based fuel tank
    -- this design replaced, nothing ever redirects a player's click here,
    -- so this entity doesn't need a window title of its own; it's reached
    -- only via the "Insert Ice" button scripts/thermionic-generator.lua
    -- adds to the generator's own (now entirely native) info panel.
    flags = { "not-on-map", "not-blueprintable", "not-deconstructable", "hide-alt-info", "no-copy-paste" },
    hidden = true,
    hidden_in_factoriopedia = true,
    selectable_in_game = false,
    max_health = 300,
    collision_box = { { 0, 0 }, { 0, 0 } },
    selection_box = { { 0, 0 }, { 0, 0 } },
    collision_mask = { layers = {} },
    -- Two Ice stacks (100) = 400s of cooling at the 0.25/s equilibrium
    -- draw, or 50s at the 2/s cap -- enough buffer that a brief gap in
    -- asteroid capture doesn't immediately start a temperature climb. A
    -- single slot (50 Ice) was 25s at the cap.
    inventory_size = 2,
    inventory_type = "with_filters_and_bar",
    picture = {
      filename = "__core__/graphics/empty.png",
      priority = "extra-high",
      width = 1,
      height = 1,
    },
  },
})
