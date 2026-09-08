-- N8. The Crust Tap, its vent, and the turbine that burns what it draws.
--
-- graphics/building-spec-crust-tap.md. The largest of the nine, because it is
-- not one prototype: it is a fluid, a sited tile, a collision layer to identify
-- that tile, the tap itself and a companion generator.
--
-- **This is the Core's landing-day power**, and it should stay small. Roughly one
-- turbine per tap and about 1.8 MW for the pair -- a foothold, not a power
-- strategy. A player who tiles fifty taps should still find the melt-and-steam
-- line the better answer by a wide margin, or the Core's central tension is
-- undercut by its own tutorial.
--
-- Two measurements from spike S10 shape everything here, and both are the kind
-- that pass every check in the repo while being wrong:
--
--   1. **An offshore pump draws from the tile beneath it, not from its own fluid
--      box filter.** Built on bare ground it reports `status = working` and
--      produces nothing at all; `get_fluid_source_fluid()` returns nil. So the
--      tap is *sited* -- it needs a vent tile carrying the fluid, which makes it
--      a fourth sited resource beside ore, melt vents and gas vents rather than
--      something the player tiles at will. That is the better design as well as
--      the working one: power becomes a place you go, and the cap is enforced by
--      the map instead of by a tuning number.
--
--   2. **`burns_fluid` ignores temperature entirely**, taking its power from the
--      fluid's `fuel_value`. Measured: a turbine burning gas at 25 degrees with
--      `fuel_value = "200kJ"` produced exactly its declared 1.80 MW under load.
--      That is why the gas needs no temperature and the tap never declares one --
--      which matters, because an offshore pump *has no field* to set an output
--      temperature and would emit vanilla steam at its 15-degree default, where
--      a steam turbine wants 500.
--
--   3. **`maximum_temperature` is mandatory on a generator even so.** Leaving it
--      out fails the data stage outright. It does no work in this mode; it still
--      has to be declared.
--
-- Proven end to end on the rig, because none of it is visible from the data
-- stage: a tap on a vent, piped to a turbine, under load, produced exactly
-- **1,800,000 W** -- the declared figure to the watt. Three things had to be
-- fixed to get there, and each looked fine until it was measured:
--
--   * `fluid_source_offset` at { 0, 0 } lands on the corner where the four
--     footprint tiles meet, and the tap drew nothing at all while reporting
--     `working`. It has to sit squarely inside one tile.
--   * An offshore pump does not buffer. Unconnected it reads 0.0 fluid for ever
--     and looks broken; piped to a tank it filled at 0.5/tick as declared. The
--     zero was the test, not the tap.
--   * The vent tile has to be listed in the planet's `autoplace_settings.tile`
--     whitelist in map-gen.lua. Its own autoplace is not enough -- sixteen
--     chunks generated exactly zero vents until that line existed.
--
-- And one that turned out to be the *test* being wrong rather than the building:
-- `can_place_entity` defaults to a lenient check that ignores tile buildability
-- entirely, so the tap appeared to be buildable on bare ground. Checked the way
-- a player actually builds -- `build_check_type = manual` -- it is refused off a
-- vent and accepted on one. Anything testing a buildability rule has to pass
-- that, or it is not testing the rule.

local derive = require("prototypes.derive")

--------------------------------------------------------------------------------
-- A collision layer, so the tap can require its own ground.
--
-- `tile_buildability_rules` identifies tiles by collision layer, and vanilla's
-- offshore pump uses `water_tile` -- which is no use here, because the vent is
-- dry ground on a planet with no water at all. A private layer is the only way
-- to say "this tile and no other".
--------------------------------------------------------------------------------

data:extend({
  { type = "collision-layer", name = "sae-crust-vent" }
})

--------------------------------------------------------------------------------
-- The gas.
--
-- No temperature anywhere, by design -- see the burns_fluid note above. The
-- fuel value is what the turbine reads, and it is the number that sets the
-- foothold's size.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "fluid",
    name = "sae-crust-gas",
    icon = "__space-age-extended__/graphics/icons/fluid/helium-3.png",
    subgroup = "fluid",
    order = "z[sae]-e[crust-gas]",
    default_temperature = 25,
    base_color = { r = 0.55, g = 0.48, b = 0.30 },
    flow_color = { r = 0.75, g = 0.68, b = 0.45 },
    fuel_value = "200kJ",
    auto_barrel = false
  }
})

--------------------------------------------------------------------------------
-- The vent tile.
--
-- `fluid` is the whole point of it: that field, and not the tap's fluid box, is
-- where an offshore pump gets what it pumps.
--
-- The art is a stand-in. A Factorio tile is three sheets at 1x/2x/4x with
-- sixteen variants each, plus five transition groups and their masks, all of
-- which must tile seamlessly against every neighbour -- so vanilla's geometry is
-- borrowed whole and only the map colour distinguishes it for now.
-- `tools/build-whisker-bed-tile.py` and the whisker bed are the precedent for
-- doing this properly later.
--------------------------------------------------------------------------------

local vent = table.deepcopy(data.raw.tile["stone-path"])
vent.name = "sae-crust-vent"
derive.placeholder_art(vent, "wears stone-path's terrain sheets until its own exist")
vent.localised_name = nil
vent.localised_description = nil
vent.order = "z[sae]-b[crust-vent]"
vent.fluid = "sae-crust-gas"
vent.minable = nil                       -- a vent is terrain, not a floor tile
vent.can_be_part_of_blueprint = false
vent.map_color = { r = 0.50, g = 0.42, b = 0.22 }
vent.collision_mask =
{
  layers = { ground_tile = true, ["sae-crust-vent"] = true }
}
vent.autoplace =
{
  -- Rare and clustered, and decisive where it does fire. Tiles compete on
  -- probability and the highest wins, so a gentle bump above zero loses to
  -- whatever ground the temperature/moisture/aux system already wanted. Below
  -- the threshold this is strongly negative and the vent never appears; above
  -- it, it wins outright. The result is patches a player travels to rather than
  -- a texture spread across the crust.
  probability_expression = "(sae_core_crust_vent - 1.38) * 1000"
}
data:extend({ vent })

data:extend({
  {
    type = "noise-expression",
    name = "sae_core_crust_vent",
    expression = "multioctave_noise{x = x,\z
                                    y = y,\z
                                    seed0 = map_seed,\z
                                    seed1 = 6427,\z
                                    octaves = 2,\z
                                    persistence = 0.5,\z
                                    input_scale = 1/40,\z
                                    output_scale = 1}"
  }
})

--------------------------------------------------------------------------------
-- The tap.
--
-- 2x2 and sited on the vent. `fluid_source_offset` is {0, 0} rather than
-- vanilla's {0, -1}: vanilla's pump stands on the shore and reaches into the
-- water beside it, while this one stands directly on what it is drawing from.
--------------------------------------------------------------------------------

local tap = derive.from("offshore-pump", "offshore-pump", "sae-crust-tap")
derive.placeholder_art(tap, "wears offshore-pump's sprites until its plate exists")
tap.minable = { mining_time = 0.3, result = "sae-crust-tap" }
tap.collision_box = { { -0.9, -0.9 }, { 0.9, 0.9 } }
tap.selection_box = { { -1, -1 }, { 1, 1 } }
tap.tile_width = 2
tap.tile_height = 2
tap.pumping_speed = 0.5                  -- ~30/s, per the spec
-- Squarely inside one of the four footprint tiles, not on the corner they meet
-- at. Measured: at { 0, 0 } the offset lands on the point where four tiles meet
-- and the tap drew nothing at all -- `status = working`, fluid 0.0, which is
-- precisely the S10 silent failure this building was redesigned to avoid.
tap.fluid_source_offset = { 0.5, 0.5 }
tap.surface_conditions = { { property = "gravity", min = 45 } }
tap.fluid_box =
{
  volume = 1000,
  pipe_covers = tap.fluid_box.pipe_covers,
  pipe_connections =
  {
    -- On a 2x2 the tile centres are at +/-0.5, and a pipe connection has to sit
    -- inside the bounding box rather than on its edge.
    { flow_direction = "output", direction = defines.direction.north, position = { 0.5, -0.5 } }
  }
}
-- Buildable only on a vent, and this is the rule that makes the tap sited. The
-- area is the footprint itself, because the tap stands on its source.
tap.tile_buildability_rules =
{
  {
    area = { { -0.9, -0.9 }, { 0.9, 0.9 } },
    required_tiles = { layers = { ["sae-crust-vent"] = true } },
    colliding_tiles = { layers = {} }
  }
}
data:extend({ tap })

--------------------------------------------------------------------------------
-- The turbine.
--
-- `burns_fluid`, so it reads the gas's `fuel_value` and ignores temperature --
-- see the S10 note at the top. Filtered to crust gas alone: it is not a general
-- fluid burner, and letting it take anything with a fuel value would make it a
-- better answer than the melt line it is meant to be worse than.
--------------------------------------------------------------------------------

local turbine = derive.from("generator", "steam-turbine", "sae-crust-turbine")
derive.placeholder_art(turbine, "wears steam-turbine's sprites until its plate exists")
turbine.minable = { mining_time = 0.3, result = "sae-crust-turbine" }
turbine.burns_fluid = true
turbine.max_power_output = "1800kW"
turbine.effectivity = 1
turbine.fluid_usage_per_tick = 0.15      -- 9/s at 200 kJ = 1.8 MW
-- Mandatory even with burns_fluid, where it does nothing at all. Omitting it
-- fails the data stage with `Key "maximum_temperature" not found`.
turbine.maximum_temperature = 1000
turbine.surface_conditions = { { property = "pressure", max = 9 } }
turbine.fluid_box = table.deepcopy(turbine.fluid_box)
turbine.fluid_box.filter = "sae-crust-gas"
turbine.fluid_box.volume = 200
data:extend({ turbine })

--------------------------------------------------------------------------------
-- Items and build recipes.
--
-- Both are cheap and early on purpose: this is the pair a player builds on
-- landing day, before there is a smelter to make anything better with.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "item",
    name = "sae-crust-tap",
    icon = data.raw["item"]["offshore-pump"].icon,
    subgroup = "energy",
    order = "z[sae]-b[crust-tap]",
    place_result = "sae-crust-tap",
    stack_size = 20,
    weight = 20000
  },
  {
    type = "recipe",
    name = "sae-crust-tap",
    categories = { "crafting" },
    energy_required = 4,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-plate", amount = 10 },
      { type = "item", name = "pipe", amount = 10 },
      { type = "item", name = "iron-gear-wheel", amount = 10 }
    },
    results = { { type = "item", name = "sae-crust-tap", amount = 1 } },
    enabled = false
  },
  {
    type = "item",
    name = "sae-crust-turbine",
    icon = data.raw["item"]["steam-turbine"].icon,
    subgroup = "energy",
    order = "z[sae]-c[crust-turbine]",
    place_result = "sae-crust-turbine",
    stack_size = 20,
    weight = 40000
  },
  {
    type = "recipe",
    name = "sae-crust-turbine",
    categories = { "crafting" },
    energy_required = 6,
    ingredients =
    {
      { type = "item", name = "sae-kamacite-plate", amount = 20 },
      { type = "item", name = "pipe", amount = 10 },
      { type = "item", name = "iron-gear-wheel", amount = 20 }
    },
    results = { { type = "item", name = "sae-crust-turbine", amount = 1 } },
    enabled = false
  }
})
