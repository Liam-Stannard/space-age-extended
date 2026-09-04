-- The endgame: what the Core is for.
--
-- The Ignition Array is a rocket silo in everything but purpose. It behaves the
-- way the player already understands one -- parts accumulate, a bar fills, it
-- fires once -- because that familiarity is worth more here than novelty. What
-- it fires is a current through the crust, and what that restarts is the field
-- the planet lost.
--
-- Its part is the Field Coil Segment, and the segment is built from the Core's
-- own end products, three stages below the capstones. See design/04-the-core.md.

data:extend({
  {
    -- Its own category, so nothing else can be persuaded to make segments.
    type = "recipe-category",
    name = "sae-ignition"
  }
})

--------------------------------------------------------------------------------
-- TEMPORARY: stand-ins for the five capstone products.
--
-- Each of these is the end of a cross-planet tree that does not exist yet. They
-- are craftable from nothing so that the whole endgame is playable long before
-- the trees are built -- which is the earliest point at which anyone can find
-- out whether the Core is any good. Replacing a stub with a real chain later is
-- a recipe change and a migration, not a redesign.
--------------------------------------------------------------------------------

-- Fulgora <-> Aquilo is built, so its capstone is no longer among these.
local stub_items =
{
  { name = "sae-magnetar-alloy",          icon = "__space-age__/graphics/icons/tungsten-plate.png",   order = "b" },
  { name = "sae-cultured-alloy",          icon = "__space-age__/graphics/icons/bioflux.png",          order = "c" },
  { name = "sae-bio-polymer",             icon = "__base__/graphics/icons/plastic-bar.png",           order = "d" }
}

for _, s in pairs(stub_items) do
  data:extend({
    {
      type = "item",
      name = s.name,
      icon = s.icon,
      subgroup = "raw-material",
      order = "zz[sae-stub]-" .. s.order,
      stack_size = 50,
      weight = 2000
    },
    {
      type = "recipe",
      name = s.name .. "-stub",
      categories = { "crafting" },
      energy_required = 1,
      ingredients = { { type = "item", name = "iron-plate", amount = 1 } },
      results = { { type = "item", name = s.name, amount = 1 } },
      icon = s.icon,
      icon_size = 64,
      enabled = true
    }
  })
end

data:extend({
  {
    type = "fluid",
    name = "sae-cryoprotectant",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    subgroup = "fluid",
    order = "zz[sae-stub]-e",
    default_temperature = -50,
    base_color = { r = 0.45, g = 0.70, b = 0.85 },
    flow_color = { r = 0.70, g = 0.88, b = 1.0 }
  },
  {
    type = "recipe",
    name = "sae-cryoprotectant-stub",
    categories = { "crafting-with-fluid" },
    energy_required = 1,
    ingredients = { { type = "item", name = "iron-plate", amount = 1 } },
    results = { { type = "fluid", name = "sae-cryoprotectant", amount = 50 } },
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    icon_size = 64,
    enabled = true
  }
})

--------------------------------------------------------------------------------
-- The end products, and the segment built from them.
--
-- The items are permanent; their recipes here are temporary, and Phase 5
-- replaces them with the two-stage chain that runs through the intermediates.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "item",
    name = "sae-superconducting-winding",
    icon = "__space-age__/graphics/icons/superconductor.png",
    subgroup = "raw-material",
    order = "z[sae]-fa[d-winding]",
    stack_size = 50,
    weight = 2000
  },
  {
    type = "item",
    name = "sae-coil-assembly",
    icon = "__space-age__/graphics/icons/superconductor.png",
    subgroup = "intermediate-product",
    order = "z[sae]-a[coil-assembly]",
    stack_size = 20,
    weight = 10000
  },
  {
    type = "item",
    name = "sae-coolant-loop",
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    subgroup = "intermediate-product",
    order = "z[sae]-b[coolant-loop]",
    stack_size = 20,
    weight = 10000
  },
  {
    type = "item",
    name = "sae-field-coil-segment",
    icon = "__space-age__/graphics/icons/superconductor.png",
    subgroup = "intermediate-product",
    order = "z[sae]-c[field-coil-segment]",
    stack_size = 10,
    weight = 20000
  },

  {
    type = "recipe",
    name = "sae-coil-assembly",
    categories = { "crafting" },
    energy_required = 60,
    ingredients =
    {
      { type = "item", name = "sae-field-conductor", amount = 2 },
      { type = "item", name = "sae-magnetic-core-billet", amount = 2 },
      { type = "item", name = "sae-reinforced-frame", amount = 1 },
      { type = "item", name = "sae-insulation-sleeve", amount = 2 },
      { type = "item", name = "sae-welded-plate", amount = 4 }
    },
    results = { { type = "item", name = "sae-coil-assembly", amount = 1 } },
    surface_conditions = { { property = "pressure", max = 9 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-coolant-loop",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "sae-coolant-charge", amount = 2 },
      { type = "item", name = "sae-kamacite-plate", amount = 10 }
    },
    results = { { type = "item", name = "sae-coolant-loop", amount = 1 } },
    surface_conditions = { { property = "pressure", min = 1, max = 9 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-field-coil-segment",
    categories = { "sae-ignition" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "sae-coil-assembly", amount = 1 },
      { type = "item", name = "sae-coolant-loop", amount = 1 }
    },
    results = { { type = "item", name = "sae-field-coil-segment", amount = 1 } },
    enabled = false,
    hide_from_player_crafting = true
  }
})

--------------------------------------------------------------------------------
-- The Ignition Array.
--------------------------------------------------------------------------------

local array = table.deepcopy(data.raw["rocket-silo"]["rocket-silo"])
array.name = "sae-ignition-array"
array.icon = "__base__/graphics/icons/rocket-silo.png"
array.minable = { mining_time = 5, result = "sae-ignition-array" }
array.crafting_categories = { "sae-ignition" }
array.fixed_recipe = "sae-field-coil-segment"
array.rocket_parts_required = 100
array.energy_usage = "2MW"
-- An order of magnitude past vanilla's 3.99MW, so every megawatt the array
-- draws is melt that was not cast into the segments it also needs.
array.active_energy_usage = "50MW"
array.surface_conditions = { { property = "pressure", min = 1, max = 9 } }
-- It fires on command rather than at a platform's request: this is an ignition,
-- not a delivery.
array.launch_to_space_platforms = false
array.heating_energy = nil
array.fast_replaceable_group = nil
array.next_upgrade = nil
data:extend({ array })

--------------------------------------------------------------------------------
-- The sealed roboport.
--
-- Restricted to pressure 1-9, so it works on the Core and nowhere else in the
-- game: not on a platform (0), not on any vanilla world (Aquilo is lowest at
-- 300). It competes with nothing, which is why a second roboport is not a
-- second tier.
--------------------------------------------------------------------------------

local port = table.deepcopy(data.raw.roboport["roboport"])
port.name = "sae-sealed-roboport"
port.icon = "__base__/graphics/icons/roboport.png"
port.minable = { mining_time = 0.5, result = "sae-sealed-roboport" }
port.surface_conditions = { { property = "pressure", min = 1, max = 9 } }
port.energy_usage = "150kW"
port.fast_replaceable_group = nil
port.next_upgrade = nil
data:extend({ port })

data:extend({
  {
    type = "item",
    name = "sae-ignition-array",
    icon = "__base__/graphics/icons/rocket-silo.png",
    subgroup = "production-machine",
    order = "z[sae]-z[ignition-array]",
    place_result = "sae-ignition-array",
    stack_size = 1,
    weight = 500000
  },
  {
    type = "item",
    name = "sae-sealed-roboport",
    icon = "__base__/graphics/icons/roboport.png",
    subgroup = "logistic-network",
    order = "z[sae]-a[sealed-roboport]",
    place_result = "sae-sealed-roboport",
    stack_size = 10,
    weight = 40000
  },

  {
    type = "recipe",
    name = "sae-sealed-roboport",
    categories = { "crafting" },
    energy_required = 15,
    ingredients =
    {
      { type = "item", name = "sae-welded-plate", amount = 20 },
      { type = "item", name = "sae-kamacite-plate", amount = 30 },
      { type = "item", name = "processing-unit", amount = 20 },
      { type = "item", name = "sae-coolant-loop", amount = 2 }
    },
    results = { { type = "item", name = "sae-sealed-roboport", amount = 1 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-ignition-array",
    categories = { "crafting" },
    energy_required = 120,
    ingredients =
    {
      { type = "item", name = "sae-welded-plate", amount = 200 },
      { type = "item", name = "sae-kamacite-plate", amount = 500 },
      { type = "item", name = "sae-coil-assembly", amount = 10 },
      { type = "item", name = "processing-unit", amount = 200 },
      { type = "item", name = "sae-arc-mast", amount = 4 }
    },
    results = { { type = "item", name = "sae-ignition-array", amount = 1 } },
    enabled = false
  }
})
