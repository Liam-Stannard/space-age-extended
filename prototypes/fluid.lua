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
    -- built by tools/derive-fluid-icons.py. Not the warm colour an earlier
    -- draft used: the mod's other fluid icons already occupy hue 0-40 twice
    -- over (molten scrap, molten non-ferrous, contaminated acid), so a warm
    -- vapour was a third orange drop in the same list. Teal is the set's one
    -- free slot and ties the fluid to its machine.
    base_color = { 0.10, 0.42, 0.46 },
    flow_color = { 0.35, 0.80, 0.84 },
    draw_as_glow = true,
    auto_barrel = false,
  },
  {
    -- The Quench Turbine's coolant loop, cold half.
    --
    -- This exists instead of using Fluoroketone directly, and the reason is a
    -- vanilla-balance one worth not undoing. Vanilla deliberately gives you no
    -- way to re-cool Fluoroketone in space: its own fluoroketone-cooling
    -- recipe is in the "cryogenics" category, and a cryogenic plant demands
    -- pressure >= 10, so it cannot be built on a platform. That is why vanilla
    -- fusion platforms must ship coolant up in barrels. An earlier draft of
    -- this tree added a vacuum-only recipe that re-cooled Fluoroketone itself,
    -- which made this mod the only in-space source of fluoroketone-cold and
    -- so quietly removed vanilla fusion's coolant logistics for anyone with
    -- the mod installed -- a clear breach of framework.md §2.3.
    --
    -- Running the platform loop on the mod's own coolant keeps vanilla's
    -- economy untouched while still letting the loop close in space, which is
    -- what the design wants: coolant that stays hot forever makes no sense.
    -- Aquilo is still the gate, because the only recipe that makes this needs
    -- Fluoroketone (prototypes/recipe.lua).
    --
    -- Two fluids rather than one fluid at two temperatures, mirroring
    -- vanilla's own Fluoroketone split, and for a concrete reason: barrels do
    -- not preserve temperature (verified -- empty-fluoroketone-cold-barrel
    -- returns its fluid with no temperature, i.e. at the default). A single
    -- temperature-carrying coolant could therefore be barrelled hot and
    -- emptied cold, laundering the whole radiator step away. Two fluids make
    -- that impossible to express.
    type = "fluid",
    name = "sae-quench-coolant",
    icon = "__space-age-extended__/graphics/icons/fluid/quench-coolant.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fluid",
    order = "e[sae]-g[quench-coolant]",
    default_temperature = -100,
    heat_capacity = "1kJ",
    base_color = { 0.16, 0.34, 0.72 },
    flow_color = { 0.45, 0.62, 0.95 },
    draw_as_glow = false,
    -- Barrelable on purpose: this is what ships up from Aquilo as the loop's
    -- initial fill. The spent half below is not -- it never needs to leave.
  },
  {
    -- The same coolant, hot, on its way to the radiators. See above for why
    -- this is a separate fluid rather than a temperature.
    type = "fluid",
    name = "sae-spent-quench-coolant",
    icon = "__space-age-extended__/graphics/icons/fluid/spent-quench-coolant.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fluid",
    order = "e[sae]-h[spent-quench-coolant]",
    default_temperature = 150,
    heat_capacity = "1kJ",
    base_color = { 0.55, 0.30, 0.16 },
    flow_color = { 0.85, 0.52, 0.28 },
    draw_as_glow = false,
    auto_barrel = false,
  },
})
