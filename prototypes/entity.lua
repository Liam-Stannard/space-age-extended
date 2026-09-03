-- New entities introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §9 -- the Thermionic Generator, the mod's
-- one new building (justified per design/framework.md §2.3 by a
-- temperature-dependent efficiency curve nothing else in the game has).
--
-- Visible generator: `electric-energy-interface`, script-driven (see
-- scripts/thermionic-generator.lua). Placeholder visuals reuse vanilla
-- accumulator's actual sprite files directly (not its charge/discharge
-- animation machinery, which is base-mod-internal) -- no new art pipeline
-- yet, matching this repo's established convention.
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
    -- Placeholder collision/selection box, reused from vanilla accumulator.
    collision_box = { { -0.9, -0.9 }, { 0.9, 0.9 } },
    selection_box = { { -1, -1 }, { 1, 1 } },
    -- Placeholder visuals: vanilla accumulator's own sprite files, used
    -- directly as a plain Sprite rather than via base's internal
    -- charge/discharge animation helpers (those are local functions in
    -- base's entities.lua, not something a dependent mod should rely on).
    picture = {
      layers = {
        {
          filename = "__base__/graphics/entity/accumulator/accumulator.png",
          priority = "high",
          width = 130,
          height = 189,
          shift = { 0, -0.34375 },
          scale = 0.5,
        },
        {
          filename = "__base__/graphics/entity/accumulator/accumulator-shadow.png",
          priority = "high",
          width = 234,
          height = 106,
          shift = { 0.90625, 0.1875 },
          draw_as_shadow = true,
          scale = 0.5,
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
