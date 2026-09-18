-- Where the Core's things sit in the crafting menu.
--
-- Until this existed every `sae-*` prototype was filed into whatever vanilla
-- subgroup was nearest -- `raw-material`, `production-machine`, `energy`,
-- `intermediate-product` -- so a player hunting for Core content found it
-- interleaved with Nauvis's, one item at a time.
--
-- **Vanilla's own pattern is followed rather than invented.** Space Age does not
-- give a planet its own item *group*; it gives it a *subgroup* inside the
-- existing ones. `vulcanus-processes`, `fulgora-processes`, `agriculture-*` and
-- `aquilo-processes` all live under `intermediate-products`, ordered k, l, m, n,
-- o, p -- and each planet's machines stay in `production` beside every other
-- machine, because a player looking for an assembler wants them together.
--
-- So the Core takes:
--
--   * `sae-core-processes` under `intermediate-products` at order **q**, which
--     is the next letter after Aquilo's p. Everything the Core's chain makes.
--   * `sae-core-machines` under `production` at order **eb**, immediately after
--     `production-machine` (e), so the Core's buildings sit together at the end of
--     the machines the player already knows.
--
-- Ordering *within* each subgroup follows the production tree rather than the
-- alphabet: ore, then what crushing makes of it, then settling, then the fibre
-- line, then carbonyl, then the endgame. A player reading the menu top to bottom
-- reads the factory in the order they will build it.

data:extend({
  {
    type = "item-subgroup",
    name = "sae-core-processes",
    group = "intermediate-products",
    order = "q"
  },
  {
    type = "item-subgroup",
    name = "sae-core-machines",
    group = "production",
    order = "eb"
  },
  {
    type = "item-subgroup",
    name = "sae-core-tiles",
    group = "tiles",
    order = "z[sae]"
  }
})

--------------------------------------------------------------------------------
-- Re-point everything, in one pass, at the end of the data stage.
--
-- Done here rather than at each definition site on purpose: the ordering is a
-- single design decision about how the whole menu reads, and spreading it across
-- seven files is how one prototype ends up in the wrong place and nobody
-- notices. One table, one place to change it.
--
-- Anything not listed keeps whatever it has. That is deliberate for the three
-- tiles and the science pack: a tile belongs with tiles, and the geodynamic pack
-- belongs with the other science packs, because that is where a player looks for
-- them.
--------------------------------------------------------------------------------

--- name -> order suffix, in the order the factory is built.
local CHAIN =
{
  ["sae-kamacite-ore"] = "aa",
  ["sae-crushed-kamacite"] = "ab",
  ["sae-kamacite-fines"] = "ac",
  ["sae-kamacite-plate"] = "ad",

  ["sae-radiant-chunk"] = "ea",
  ["sae-radiant-fuel"] = "ec",

  ["sae-fluorinated-holmium"] = "fa",
  ["sae-superconducting-winding"] = "fb",
  ["sae-magnetar-alloy"] = "fc",
  ["sae-cultured-alloy"] = "fd",
  ["sae-bio-polymer"] = "fe"
}

--- The buildings, in the order the player unlocks them.
local MACHINES =
{
  ["sae-crust-tap"] = "aa",
  ["sae-crust-turbine"] = "ab",
  ["sae-ballast-drill"] = "ba",
  ["sae-drop-crusher"] = "bb",
  ["sae-vacuum-furnace"] = "bc",
  ["sae-vent-pump"] = "bd",
  ["sae-superconducting-store"] = "eb",
  ["sae-radiant-generator"] = "ec"
}

local function place(name, subgroup, suffix)
  -- Not every placeable thing is an `item`: the seed missile is `ammo`, the
  -- science pack is a `tool`. Look in each of the item-like tables rather than
  -- assuming, or the ones that are not plain items silently keep their old spot.
  local item
  for _, t in ipairs({ "item", "tool", "ammo", "capsule", "module", "gun" }) do
    item = data.raw[t] and data.raw[t][name]
    if item then break end
  end
  if not item then
    -- A name that does not resolve is a typo in the tables above, and a silent
    -- one: the prototype simply stays where it was and the menu looks almost
    -- right. Fail loudly instead.
    error("sae groups: no item named " .. name)
  end
  item.subgroup = subgroup
  item.order = "z[sae]-" .. suffix .. "[" .. name .. "]"
end

for name, suffix in pairs(CHAIN) do place(name, "sae-core-processes", suffix) end
for name, suffix in pairs(MACHINES) do place(name, "sae-core-machines", suffix) end

--- Recipes with more than one product have no main product to borrow a place
--- in the menu from, so the engine files them nowhere in particular. Each sits
--- beside the product it exists for, as vanilla files oil processing beside oil.
local RECIPES =
{
  ["sae-crushing"] = "ab",
  ["sae-radiant-crushing"] = "ec",
  ["sae-fluorinated-holmium"] = "fa",
  ["sae-superconducting-winding"] = "fb"
}

for name, suffix in pairs(RECIPES) do
  local recipe = data.raw.recipe[name] or error("sae groups: no recipe named " .. name)
  recipe.subgroup = "sae-core-processes"
  recipe.order = "z[sae]-" .. suffix .. "[" .. name .. "]"
end

-- The fluids too. They have their own group in the menu, so they only need
-- ordering relative to each other -- and the same chain order applies.
local FLUIDS =
{
  ["sae-molten-kamacite"] = "aa",
  ["sae-helium-3"] = "ac",
  ["sae-crust-gas"] = "ad",
  ["sae-radiant-solution"] = "ae",
  ["sae-cold-cryogen"] = "ca",
  ["sae-spent-cryogen"] = "cb",
  ["sae-cryoprotectant"] = "cc"
}
for name, suffix in pairs(FLUIDS) do
  local f = data.raw.fluid[name]
  if not f then error("sae groups: no fluid named " .. name) end
  f.order = "z[sae]-" .. suffix .. "[" .. name .. "]"
end
