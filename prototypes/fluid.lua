-- New fluids introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §1-6 for the Fulgora refining fluids and
-- §9 for Quench Vapour. All use auto_barrel = false: the refining fluids
-- never need to leave Fulgora, and Quench Vapour is made and consumed on
-- the same platform (barrelling it would let a platform import energy
-- ready-made, which is the whole point of the Vulcanus fuel line).

data:extend({
  {
    type = "fluid",
    name = "sae-molten-scrap",
    icon = "__space-age-extended__/graphics/icons/fluid/molten-scrap.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-a[molten-scrap]",
    default_temperature = 1200,
    base_color = { 0.28, 0.25, 0.22 },
    flow_color = { 0.55, 0.5, 0.45 },
    draw_as_glow = true,
    auto_barrel = false,
  },
  {
    type = "fluid",
    name = "sae-molten-ferrous-metal",
    icon = "__space-age-extended__/graphics/icons/fluid/molten-ferrous-metal.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-b[molten-ferrous-metal]",
    default_temperature = 1300,
    base_color = { 0.35, 0.38, 0.43 },
    flow_color = { 0.6, 0.66, 0.75 },
    draw_as_glow = true,
    auto_barrel = false,
  },
  {
    type = "fluid",
    name = "sae-molten-non-ferrous-metal",
    icon = "__space-age-extended__/graphics/icons/fluid/molten-non-ferrous-metal.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-c[molten-non-ferrous-metal]",
    default_temperature = 1300,
    base_color = { 0.62, 0.35, 0.15 },
    flow_color = { 0.85, 0.55, 0.3 },
    draw_as_glow = true,
    auto_barrel = false,
  },
  {
    type = "fluid",
    name = "sae-holmium-rich-residue",
    icon = "__space-age-extended__/graphics/icons/fluid/holmium-rich-residue.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-d[holmium-rich-residue]",
    default_temperature = 60,
    base_color = { 0.45, 0.25, 0.55 },
    flow_color = { 0.65, 0.45, 0.75 },
    draw_as_glow = false,
    auto_barrel = false,
  },
  {
    type = "fluid",
    name = "sae-contaminated-sulfuric-acid",
    icon = "__space-age-extended__/graphics/icons/fluid/contaminated-sulfuric-acid.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-e[contaminated-sulfuric-acid]",
    default_temperature = 25,
    base_color = { 0.45, 0.42, 0.12 },
    flow_color = { 0.6, 0.55, 0.2 },
    draw_as_glow = false,
    auto_barrel = false,
  },
  {
    -- The Quench Turbine's working fluid (design doc §9). A quench recipe
    -- sets its temperature; the turbine converts flow x heat_capacity x
    -- (temperature - default_temperature) into electricity and *clips*
    -- anything above its own maximum_temperature (315), which is what makes
    -- the lean recipe wasteful and the later, richer recipes worth
    -- unlocking. heat_capacity 5kJ against the turbine's 0.2 fluid/tick
    -- (12/s) gives 1.5MJ per unit at the cap = 18MW per turbine.
    --
    -- max_temperature 1000 is headroom for the lean recipe's 900 degrees --
    -- deliberately above the turbine's cap so the waste is visible in the
    -- fluid tooltip rather than silently clamped at production time.
    type = "fluid",
    name = "sae-quench-vapour",
    icon = "__space-age-extended__/graphics/icons/fluid/quench-vapour.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fluid",
    order = "e[sae]-f[quench-vapour]",
    default_temperature = 15,
    max_temperature = 1000,
    heat_capacity = "5kJ",
    -- Cyan-teal, matching the Quench Turbine that consumes it and the icon
    -- built by tools/derive-vapour-icon.py. Not the warm colour an earlier
    -- draft used: the mod's other fluid icons already occupy hue 0-40 twice
    -- over (molten scrap, molten non-ferrous, contaminated acid), so a warm
    -- vapour was a third orange drop in the same list. Teal is the set's one
    -- free slot and ties the fluid to its machine.
    base_color = { 0.10, 0.42, 0.46 },
    flow_color = { 0.35, 0.80, 0.84 },
    draw_as_glow = true,
    auto_barrel = false,
  },
})
