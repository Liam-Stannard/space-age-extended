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
-- Visuals reuse vanilla nuclear reactor's own sprite files -- honestly,
-- since the entity really is a reactor-type building -- and use the
-- reactor-type animated fields (heat glow, working light, connection
-- patches) so they actually play, not just the static body. Vanilla
-- builds its glow layers through a base-internal local helper
-- (`apply_heat_pipe_glow` in base/prototypes/entity/entities.lua) that a
-- dependent mod can't call; its output is inlined here instead. The
-- connection-patch sheets are this mod's own, generated from vanilla's by
-- tools/generate-thermionic-graphics.py (see the comment at the field).
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
    -- Visuals: vanilla nuclear reactor's own sprite files, with every
    -- value copied from base/prototypes/entity/entities.lua's
    -- "nuclear-reactor" block (util.by_pixel shifts pre-divided by 32).
    -- The heated/glow layers are what vanilla's base-internal
    -- `apply_heat_pipe_glow` helper produces, written out longhand: the
    -- sprite tinted {0.5, 0.4, 0.3, 0.5}, plus a copy of it with
    -- draw_as_light = true and tint {1, 1, 1, 1} -- a mod can't call that
    -- local helper, so the shape is inlined rather than depended on.
    lower_layer_picture = {
      filename = "__base__/graphics/entity/nuclear-reactor/reactor-pipes.png",
      width = 320,
      height = 316,
      scale = 0.5,
      shift = { -0.03125, -0.15625 },
    },
    -- Drawn over lower_layer_picture as the pipes heat up (the engine
    -- fades it in from heat_buffer.minimum_glow_temperature).
    heat_lower_layer_picture = {
      layers = {
        {
          filename = "__base__/graphics/entity/nuclear-reactor/reactor-pipes-heated.png",
          width = 320,
          height = 316,
          scale = 0.5,
          shift = { -0.015625, -0.140625 },
          tint = { 0.5, 0.4, 0.3, 0.5 },
        },
        {
          filename = "__base__/graphics/entity/nuclear-reactor/reactor-pipes-heated.png",
          width = 320,
          height = 316,
          scale = 0.5,
          shift = { -0.015625, -0.140625 },
          tint = { 1, 1, 1, 1 },
          draw_as_light = true,
        },
      },
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
    -- The "running" light overlay, drawn (additively, as glow) while the
    -- burner is lit and pulsed by energy_source.light_flicker below --
    -- this is what makes vanilla's reactor visibly run. Vanilla's own
    -- sprite, whose lit pixels are uranium green.
    working_light_picture = {
      filename = "__base__/graphics/entity/nuclear-reactor/reactor-lights-color.png",
      blend_mode = "additive",
      draw_as_glow = true,
      width = 320,
      height = 320,
      scale = 0.5,
      shift = { -0.03125, -0.1875 },
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
      -- Vanilla reactor's values. This is what pulses working_light_picture
      -- while burning; the black colour means the burner itself casts no
      -- light of its own -- the visible glow is the working light.
      light_flicker = {
        color = { 0, 0, 0 },
        minimum_intensity = 0.7,
        maximum_intensity = 0.95,
      },
    },
    -- Real energy draw, matching the 4MW peak electrical output
    -- (scripts/thermionic-curve.lua's PEAK_POWER_W) so full-load fuel
    -- energy in equals peak electricity out at 100% efficiency. Together
    -- with Magmatic Core's fuel_value (800MJ, prototypes/item.lua) this
    -- gives a 200s burn per core -- the same as vanilla's uranium fuel
    -- cell. Together with specific_heat below it also sets the heating
    -- rate (consumption / specific_heat = 100°/s at full draw).
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
      -- sets the heating *rate*: consumption / specific_heat = 4MW / 40kJ
      -- = 100°/s at full draw (heat_buffer was verified in-engine, at the
      -- earlier 400kJ, to be exactly linear: ΔT = energy / specific_heat,
      -- to the degree). From cold that's 6s to the top of the optimal band
      -- (600) and 8s to the overheat threshold (800).
      --
      -- That is deliberately faster than Ice alone can hold. Ice removes at
      -- most MAX_ICE_PER_INTERVAL (2) x HEAT_REMOVED_PER_ICE_UNIT (40°) =
      -- 80°/s (scripts/thermionic-curve.lua), so under full load Ice can
      -- only *slow* the climb: net +20°/s at the 2 Ice/s cap, ~40s from
      -- cold to overheat with the tank draining flat out, and the 100-Ice
      -- coolant tank below lasts 50s at that rate. It can never hold the
      -- optimal band under full load by itself. The reactor's own heat-pipe
      -- channel (max_transfer 10MW, 2.5x the 4MW input) is the only cooling
      -- avenue that can -- and attached heat pipes also add their own
      -- thermal mass (vanilla heat pipe specific_heat = 1MJ each, 25x this
      -- buffer), so a connected network slows the climb enormously on top
      -- of whatever it dissipates. That is the point: the thermal block is
      -- the way to run this at full load (playtest feedback: "it should
      -- heat up a lot faster, so the thermal block is useful"). The
      -- previous 400kJ (10°/s: ~80s to overheat, 0.25 Ice/s to hold) was
      -- rejected in play -- it heated so slowly that Ice trivially held it
      -- and heat pipes were pointless.
      max_temperature = 2000,
      specific_heat = "40kJ",
      max_transfer = "10MW",
      default_temperature = 0,
      min_working_temperature = 0,
      -- Vanilla's value: the temperature the heated sprites
      -- (heat_lower_layer_picture, heat_picture, the heated connection
      -- patches) start fading in at. Presumably the glow ramps from here
      -- up toward max_temperature -- which is 2000 here against vanilla's
      -- 1000 -- so it may read dimmer in the 400-600 optimal band than
      -- vanilla's reactor does at the same temperature. Unverified; to be
      -- judged in-client.
      minimum_glow_temperature = 350,
      -- The heated body overlay, glow-wrapped exactly like
      -- heat_lower_layer_picture above.
      heat_picture = {
        layers = {
          {
            filename = "__base__/graphics/entity/nuclear-reactor/reactor-heated.png",
            width = 216,
            height = 256,
            scale = 0.5,
            shift = { 0.09375, -0.203125 },
            tint = { 0.5, 0.4, 0.3, 0.5 },
          },
          {
            filename = "__base__/graphics/entity/nuclear-reactor/reactor-heated.png",
            width = 216,
            height = 256,
            scale = 0.5,
            shift = { 0.09375, -0.203125 },
            tint = { 1, 1, 1, 1 },
            draw_as_light = true,
          },
        },
      },
      -- Four connection points per side of the 4x4 footprint, one per edge
      -- tile, each at that tile's *centre* (±0.5, ±1.5): every vanilla
      -- precedent puts heat connections at tile centres (the 5x5 nuclear
      -- reactor at ±2 with its edge at ±2.5; the 3x2 heat exchanger at
      -- {0, 0.5}), and this entity's earlier 3x3 layout -- the only one
      -- confirmed against real heat-pipe placement -- used ±1, also tile
      -- centres. The previous 4x4 layout put them at ±2, on the
      -- collision-box edge itself, which no precedent does and which
      -- would also have put the 1-tile connection patch (drawn at the
      -- connection position) straddling the boundary. Corners carry two
      -- connections facing different directions, like vanilla. Order is
      -- N,N,N,N,E,E,E,E,S,S,S,S,W,W,W,W, and the connection-patch sheets
      -- below are laid out in this same order. This tile-centre layout is
      -- still NOT verified against real heat-pipe placement in-engine --
      -- a tester will try it.
      connections = {
        { position = { -1.5, -1.5 }, direction = defines.direction.north },
        { position = { -0.5, -1.5 }, direction = defines.direction.north },
        { position = { 0.5, -1.5 }, direction = defines.direction.north },
        { position = { 1.5, -1.5 }, direction = defines.direction.north },
        { position = { 1.5, -1.5 }, direction = defines.direction.east },
        { position = { 1.5, -0.5 }, direction = defines.direction.east },
        { position = { 1.5, 0.5 }, direction = defines.direction.east },
        { position = { 1.5, 1.5 }, direction = defines.direction.east },
        { position = { 1.5, 1.5 }, direction = defines.direction.south },
        { position = { 0.5, 1.5 }, direction = defines.direction.south },
        { position = { -0.5, 1.5 }, direction = defines.direction.south },
        { position = { -1.5, 1.5 }, direction = defines.direction.south },
        { position = { -1.5, 1.5 }, direction = defines.direction.west },
        { position = { -1.5, 0.5 }, direction = defines.direction.west },
        { position = { -1.5, -0.5 }, direction = defines.direction.west },
        { position = { -1.5, -1.5 }, direction = defines.direction.west },
      },
    },
    -- Per-connection patch sprites, one variation per heat_buffer
    -- connection *in the same order* (the engine requires variation_count
    -- >= #connections). Vanilla's sheets are 12 columns for its 12
    -- connections, so they can't be used for 16; these are this mod's own
    -- 16-column (1024x128) sheets, generated from vanilla's by
    -- tools/generate-thermionic-graphics.py -- each side's four
    -- connections map onto vanilla's [corner, mid, mid, corner] patches
    -- for that side. Row 0 (y = 0) is connected, row 1 (y = 64) is
    -- disconnected; the heated sheets are drawn over these as the buffer
    -- warms, glow-wrapped like the other heated sprites.
    connection_patches_connected = {
      sheet = {
        filename = "__space-age-extended__/graphics/entity/thermionic-generator/connect-patches.png",
        width = 64,
        height = 64,
        variation_count = 16,
        scale = 0.5,
      },
    },
    connection_patches_disconnected = {
      sheet = {
        filename = "__space-age-extended__/graphics/entity/thermionic-generator/connect-patches.png",
        width = 64,
        height = 64,
        variation_count = 16,
        y = 64,
        scale = 0.5,
      },
    },
    heat_connection_patches_connected = {
      sheet = {
        layers = {
          {
            filename = "__space-age-extended__/graphics/entity/thermionic-generator/connect-patches-heated.png",
            width = 64,
            height = 64,
            variation_count = 16,
            scale = 0.5,
            tint = { 0.5, 0.4, 0.3, 0.5 },
          },
          {
            filename = "__space-age-extended__/graphics/entity/thermionic-generator/connect-patches-heated.png",
            width = 64,
            height = 64,
            variation_count = 16,
            scale = 0.5,
            tint = { 1, 1, 1, 1 },
            draw_as_light = true,
          },
        },
      },
    },
    heat_connection_patches_disconnected = {
      sheet = {
        layers = {
          {
            filename = "__space-age-extended__/graphics/entity/thermionic-generator/connect-patches-heated.png",
            width = 64,
            height = 64,
            variation_count = 16,
            y = 64,
            scale = 0.5,
            tint = { 0.5, 0.4, 0.3, 0.5 },
          },
          {
            filename = "__space-age-extended__/graphics/entity/thermionic-generator/connect-patches-heated.png",
            width = 64,
            height = 64,
            variation_count = 16,
            y = 64,
            scale = 0.5,
            tint = { 1, 1, 1, 1 },
            draw_as_light = true,
          },
        },
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
    -- Two Ice stacks (100) = 50s at the 2/s cap. Under full load that cap
    -- is the rate the tank actually drains at (Ice can't hold the 100°/s
    -- climb, see the reactor's heat_buffer comment, so a hot generator
    -- always draws Ice flat out) -- 50s is enough that a brief gap in
    -- asteroid capture doesn't remove Ice's contribution outright. A
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
