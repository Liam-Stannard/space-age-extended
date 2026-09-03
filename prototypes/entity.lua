-- New entities introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §9 -- the Thermionic Generator, the mod's
-- one new building (justified per design/framework.md §2.3 by a
-- temperature-dependent efficiency curve nothing else in the game has).
--
-- Visible generator: `electric-energy-interface`, script-driven (see
-- scripts/thermionic-generator.lua). Visuals reuse vanilla nuclear
-- reactor's real static body/shadow sprite files directly (plain Sprite
-- layers, not reactor's own heat-pipe-glow or connection-graphics
-- machinery, which are base-mod-internal and reactor-type-specific) --
-- thematically closer to a heat-driven generator than the accumulator
-- placeholder this used to borrow from, and no new art pipeline needed
-- since reactor.png/reactor-shadow.png are just plain static layers, same
-- shape as accumulator's were. Deliberately NOT using reactor's
-- reactor-pipes.png/reactor-pipes-heated.png lower-layer graphics -- those
-- read visually as literal heat-pipe plumbing across the reactor's face,
-- which would be misleading given this entity has NO heat-pipe interface
-- of its own (design doc §9.2, and see the energy_source comment below).
--
-- Hidden hopper: a 2-slot `container`, spawned/paired 1:1 with the visible
-- generator at runtime, filtered to Magmatic Core / Ice. Never placed by
-- the player directly -- not in any item's place_result, no icon needed.

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
    -- Electricity-only output, driven entirely by script (see
    -- scripts/thermionic-generator.lua) -- energy_production/energy_usage
    -- are deliberately left at their defaults (0) since power_production
    -- is set every update interval instead of being a fixed rate.
    -- Deliberately NO heat energy source and NO heat-pipe connection of
    -- any kind (design doc §9.2) -- this must never become a way to dump
    -- heat near Aquilo.
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
})
