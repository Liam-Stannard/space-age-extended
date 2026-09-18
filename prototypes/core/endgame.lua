-- The five capstone products: what the cross-planet trees deliver to the Core.
--
-- One is real -- the superconducting winding, from prototypes/trees -- and four
-- are stubs that craft from one iron plate, so the items exist to be freighted
-- long before their trees do. What the Core makes *of* them is on master, not
-- here: this branch is the landing, and the capstones arrive to a planet that
-- can receive them and not yet use them.

local item_sounds = require("__base__.prototypes.item_sounds")

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
      inventory_move_sound = item_sounds.metal_small_inventory_move,
      pick_sound = item_sounds.metal_small_inventory_pickup,
      drop_sound = item_sounds.metal_small_inventory_move,
      stack_size = 50,
      weight = 2 * kg
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
    -- Barrelled on purpose. This is a capstone, and a capstone has to reach
    -- the Core (principles §8); a fluid travels in barrels or not at all. The
    -- Core's own fluids say auto_barrel = false because they must never leave;
    -- this one says the opposite for the same reason.
    auto_barrel = true,
    default_temperature = -50,
    base_color = { r = 0.45, g = 0.70, b = 0.85 },
    flow_color = { r = 0.70, g = 0.88, b = 1.0 }
  },
  {
    type = "recipe",
    name = "sae-cryoprotectant-stub",
    categories = { "chemistry" },
    energy_required = 1,
    ingredients = { { type = "item", name = "iron-plate", amount = 1 } },
    results = { { type = "fluid", name = "sae-cryoprotectant", amount = 50 } },
    icon = "__space-age__/graphics/icons/fluid/fluoroketone-cold.png",
    icon_size = 64,
    enabled = true
  }
})

--------------------------------------------------------------------------------
-- The one real capstone's item. Its recipe is in prototypes/trees.
--------------------------------------------------------------------------------

data:extend({
  {
    type = "item",
    name = "sae-superconducting-winding",
    icon = "__space-age-extended__/graphics/icons/superconducting-winding.png",
    subgroup = "raw-material",
    order = "z[sae]-fa[d-winding]",
    inventory_move_sound = item_sounds.wire_inventory_move,
    pick_sound = item_sounds.wire_inventory_pickup,
    drop_sound = item_sounds.wire_inventory_move,
    stack_size = 50,
    weight = 2 * kg
  }
})
