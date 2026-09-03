-- New entities introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §9 -- the Thermionic Generator, the mod's
-- one new building (justified per design/framework.md §2.3 by a
-- temperature-dependent efficiency curve nothing else in the game has).
--
-- Visible generator: `electric-energy-interface`, script-driven (see
-- scripts/thermionic-generator.lua). Visuals reuse vanilla nuclear
-- reactor's real static body/shadow/pipes sprite files directly (plain
-- Sprite layers, not reactor's own heat-pipe-*glow* or connection-graphics
-- machinery, which are base-mod-internal and reactor-type-specific) --
-- thematically closer to a heat-driven generator than the accumulator
-- placeholder this used to borrow from, and no new art pipeline needed
-- since reactor.png/reactor-shadow.png/reactor-pipes.png are just plain
-- static layers, same shape as accumulator's were. The static
-- reactor-pipes.png lower-layer is now honest -- the entity has a real
-- heat-pipe connection via its paired hidden heat-interface below.
-- Deliberately NOT using reactor-pipes-heated.png (the heat-reactive glow
-- variant) -- that requires reactor-type-specific heat_lower_layer_picture
-- machinery this entity, an electric-energy-interface, doesn't have; a
-- static pipes layer is enough for this pass.
--
-- Hidden hopper: a 2-slot `container`, spawned/paired 1:1 with the visible
-- generator at runtime, filtered to Magmatic Core / Ice. Never placed by
-- the player directly -- not in any item's place_result, no icon needed.
--
-- Hidden heat-interface: a `heat-interface`-type entity, also spawned/
-- paired 1:1 with the visible generator at runtime (see
-- scripts/thermionic-generator.lua), giving the generator a real,
-- script-driven heat-pipe connection (design doc §9.2/§9.3 -- reversed
-- from the original "electricity only" design once it was established
-- that Factorio's heat network is strictly surface-local and can never
-- bridge a space platform into a planet's own heat network regardless of
-- orbit, so the original Aquilo-trivialisation concern doesn't apply).

data:extend({
  {
    type = "electric-energy-interface",
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
    -- Collision/selection box sized to match the actual rendered body
    -- sprite below (vanilla reactor.png, 302x318 at scale 0.5 = 151x159px
    -- = ~2.36x2.48 tiles at 64px/tile) -- previously these were still
    -- sized for the old, much smaller vanilla-accumulator sprite this
    -- entity used before, so the reactor art overhung its own footprint.
    collision_box = { { -1.1, -1.1 }, { 1.1, 1.1 } },
    selection_box = { { -1.2, -1.2 }, { 1.2, 1.2 } },
    -- Visuals: vanilla nuclear reactor's own body/shadow sprite files,
    -- used directly as plain Sprite layers (values verified against
    -- base/prototypes/entity/entities.lua's own "reactor" picture field)
    -- rather than via base's internal heat-pipe-glow/connection-graphics
    -- helpers, which are reactor-type-specific and not something a
    -- dependent mod should rely on.
    -- lower_layer_picture: vanilla reactor's own real heat-pipe stub
    -- graphics (reactor-pipes.png), verified directly against base's own
    -- "reactor" entity prototype (base/prototypes/entity/entities.lua) --
    -- width/height/scale/shift copied from its lower_layer_picture field
    -- exactly (shift there is `util.by_pixel(-1, -5)`, i.e. {-1/32, -5/32}
    -- = {-0.03125, -0.15625}, reproduced as a literal here to match this
    -- file's existing style rather than pulling in the util lib).
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
    -- Electricity remains the primary output, driven entirely by script
    -- (see scripts/thermionic-generator.lua) -- energy_production/
    -- energy_usage are deliberately left at their defaults (0) since
    -- power_production is set every update interval instead of being a
    -- fixed rate. This entity itself still has NO heat energy source of
    -- its own (an electric-energy-interface can't have one) -- the real
    -- heat-pipe connection lives entirely on the paired hidden
    -- sae-thermionic-generator-heat-interface below, as a secondary
    -- cooling avenue alongside Ice, not a second power channel
    -- (design doc §9.2).
    energy_source = {
      type = "electric",
      usage_priority = "secondary-output",
      -- Peak output; see scripts/thermionic-curve.lua's PEAK_POWER_W
      -- comment for the full justification (meaningfully below fusion's
      -- 50MW, per design doc §9.1/§9.4).
      output_flow_limit = "4MW",
    },
    -- electric-energy-interface's gui_mode defaults to "none" (no GUI opens
    -- on click at all), which silently broke the on_gui_opened redirect in
    -- scripts/thermionic-generator.lua that sends the player into the
    -- hidden hopper's inventory to load fuel/coolant -- headless RCON
    -- testing missed this because it forces player.opened directly,
    -- bypassing the click-driven gui_mode gate entirely. Must be "all" so a
    -- real player's click actually opens something for on_gui_opened to
    -- catch.
    gui_mode = "all",
  },
  {
    type = "container",
    name = "sae-thermionic-generator-hopper",
    -- Never player-placed (no item has this as place_result) and never
    -- independently selectable -- spawned/despawned in lockstep with the
    -- visible generator by scripts/thermionic-generator.lua, which also
    -- sets destructible = false at runtime.
    -- scripts/thermionic-generator.lua's on_gui_opened redirects the
    -- player's GUI to open this hopper directly, so it needs a real
    -- window title -- borrow the visible generator's own locale string
    -- rather than adding a new one, same pattern as vanilla's
    -- hidden-electric-energy-interface borrowing item-name.solar-panel.
    localised_name = { "entity-name.sae-thermionic-generator" },
    icon = "__space-age-extended__/graphics/icons/thermionic-generator.png",
    icon_size = 64,
    icon_mipmaps = 4,
    flags = { "not-on-map", "not-blueprintable", "not-deconstructable", "hide-alt-info", "no-copy-paste" },
    hidden = true,
    hidden_in_factoriopedia = true,
    selectable_in_game = false,
    max_health = 300,
    collision_box = { { 0, 0 }, { 0, 0 } },
    selection_box = { { 0, 0 }, { 0, 0 } },
    collision_mask = { layers = {} },
    inventory_size = 2,
    inventory_type = "with_filters_and_bar",
    picture = {
      filename = "__core__/graphics/empty.png",
      priority = "extra-high",
      width = 1,
      height = 1,
    },
  },
  {
    type = "heat-interface",
    name = "sae-thermionic-generator-heat-interface",
    -- Never player-placed and never independently selectable -- spawned/
    -- despawned in lockstep with the visible generator by
    -- scripts/thermionic-generator.lua, exactly mirroring the hidden
    -- hopper above. gui_mode = "admins" matches vanilla's own
    -- heat-interface entity (base/prototypes/entity/entities.lua) --
    -- players never interact with this directly, it only needs to
    -- physically exist so nearby heat pipes can connect to it.
    flags = { "not-on-map", "not-blueprintable", "not-deconstructable", "hide-alt-info", "no-copy-paste" },
    hidden = true,
    hidden_in_factoriopedia = true,
    selectable_in_game = false,
    gui_mode = "admins",
    max_health = 300,
    -- collision_box deliberately matches the visible generator's own real
    -- footprint (not a degenerate {0,0} box the way the hidden hopper
    -- above uses) -- verified in-engine that a heat-interface with a
    -- zero-size collision_box silently drops any heat_buffer connection
    -- whose `position` isn't exactly {0,0}, which would make the edge
    -- connections below inert. collision_mask stays empty so this never
    -- actually blocks anything physically -- it only exists to give the
    -- connection math a real footprint to anchor to.
    collision_box = { { -1.1, -1.1 }, { 1.1, 1.1 } },
    selection_box = { { -1.1, -1.1 }, { 1.1, 1.1 } },
    collision_mask = { layers = {} },
    heat_buffer = {
      -- Provisional placeholders (design doc §9.4), same tone as
      -- scripts/thermionic-curve.lua's own balance constants -- not
      -- final-tuned. Chosen to be a meaningful heat sink, not a trivial
      -- instant dump (that would make Ice pointless): max_temperature
      -- comfortably covers the abstract efficiency curve's overheat range
      -- once mapped to Celsius (see
      -- scripts/thermionic-curve.lua's abstract_temperature_to_heat_buffer_celsius),
      -- and max_transfer (10MW) is a real throughput cap, not vanilla's
      -- effectively-unlimited 10GW, so "hotter drains faster" is a genuine
      -- consequence of temperature-gradient-driven conduction against a
      -- finite pipe, not a free pass.
      --
      -- specific_heat = 3MJ is *higher* than vanilla's own heat-pipe (1MJ)
      -- -- deliberately, and re-verified in-engine (headless RCON A/B
      -- test, see the commit that introduced this value): at 1MJ (matching
      -- a single heat-pipe segment's own thermal mass 1:1), even a handful
      -- of directly-touching heat pipes made this interface's own thermal
      -- inertia negligible next to the attached network's, so the network
      -- dominated the exchange and held the generator at full efficiency
      -- indefinitely on fuel alone -- heat pipes alone fully solved
      -- cooling with no meaningful investment, which contradicts the
      -- design intent (design doc §9.2/§9.3: heat pipes are a genuine but
      -- *additional* cooling avenue, not a substitute that trivialises
      -- Ice). Raising specific_heat makes the interface's own thermal mass
      -- dominant relative to a small/partial pipe attachment (touching
      -- only one or two of the twelve connection points below), so a
      -- minimal hookup barely helps; only wiring up most/all of the
      -- generator's exposed sides (using most/all twelve connection
      -- points) meaningfully slows the temperature climb -- and even then,
      -- it delays overheat rather than preventing it outright, since
      -- nothing downstream of this interface actually consumes/dissipates
      -- the heat it receives (plain heat pipes only redistribute it, they
      -- don't remove it) -- so a heat-pipe hookup, however large, is
      -- always a finite buffer, never a permanent substitute for Ice's
      -- real per-interval heat removal (scripts/thermionic-curve.lua's
      -- M.heat_removed_by_ice).
      max_temperature = 2000,
      specific_heat = "3MJ",
      max_transfer = "10MW",
      default_temperature = 0,
      min_working_temperature = 0,
      -- Connection points cover the edges of the *visible* generator's
      -- real 3x3-tile footprint (verified in-engine: tile_width/
      -- tile_height = 3, centered on the shared spawn position), not a
      -- single position = {0,0} point the way vanilla's own tiny 1-tile
      -- heat-interface does -- {0,0} alone would place the only
      -- connection point on the generator's own center tile, which the
      -- visible generator's collision box already occupies, so no real
      -- heat pipe could ever physically reach it. This instead lets a
      -- heat pipe connect from any tile touching any of the generator's
      -- four sides, mirroring how vanilla's own (5-wide) reactor lays its
      -- connection points around its actual footprint rather than at a
      -- single central point.
      connections = {
        { position = { -1, -1 }, direction = defines.direction.north },
        { position = { 0, -1 }, direction = defines.direction.north },
        { position = { 1, -1 }, direction = defines.direction.north },
        { position = { 1, -1 }, direction = defines.direction.east },
        { position = { 1, 0 }, direction = defines.direction.east },
        { position = { 1, 1 }, direction = defines.direction.east },
        { position = { 1, 1 }, direction = defines.direction.south },
        { position = { 0, 1 }, direction = defines.direction.south },
        { position = { -1, 1 }, direction = defines.direction.south },
        { position = { -1, 1 }, direction = defines.direction.west },
        { position = { -1, 0 }, direction = defines.direction.west },
        { position = { -1, -1 }, direction = defines.direction.west },
      },
    },
  },
})
