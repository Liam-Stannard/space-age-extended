-- New items introduced by Space Age Extended.
-- See design/vulcanus-fulgora.md §6.

data:extend({
  {
    type = "item",
    name = "sae-copper-foil",
    icon = "__space-age-extended__/graphics/icons/copper-foil.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-e[copper-foil]",
    stack_size = 100,
  },
  {
    type = "item",
    name = "sae-catalyst-rod",
    icon = "__space-age-extended__/graphics/icons/catalyst-rod.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-f[catalyst-rod]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-depleted-catalyst-rod",
    icon = "__space-age-extended__/graphics/icons/depleted-catalyst-rod.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-g[depleted-catalyst-rod]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-resonant-circuit",
    icon = "__space-age-extended__/graphics/icons/resonant-circuit.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "fulgora-processes",
    order = "e[sae]-h[resonant-circuit]",
    stack_size = 100,
  },
  {
    -- The Vulcanus half of the capstone, shipped up to platforms (design
    -- doc §9.2). No fuel_category/fuel_value: a Magmatic Core is an
    -- *ingredient* of the quench recipes, not a fuel item. The earlier Thermionic
    -- Generator burned it in a real burner slot; the Quench Turbine consumes
    -- the vapour a quench recipe makes from it instead, which is what lets
    -- the recipe tier -- not the item -- decide how much electricity one core
    -- is worth. Leaving the fuel fields on would also let any future burner
    -- with a matching category burn cores directly and bypass the ladder.
    type = "item",
    name = "sae-magmatic-core",
    icon = "__space-age-extended__/graphics/icons/magmatic-core.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "vulcanus-processes",
    order = "e[sae]-i[magmatic-core]",
    stack_size = 50,
  },
  {
    type = "item",
    name = "sae-thermionic-assembly",
    icon = "__space-age-extended__/graphics/icons/thermionic-assembly.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "intermediate-product",
    order = "e[sae]-j[thermionic-assembly]",
    stack_size = 50,
  },
  {
    -- Verified: solar-panel/accumulator/fusion-generator all use the
    -- vanilla "energy" subgroup -- reuse it rather than inventing a new
    -- one (design doc §9.2, "no new building tiers" convention).
    type = "item",
    name = "sae-quench-turbine",
    icon = "__space-age-extended__/graphics/icons/quench-turbine.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "energy",
    order = "e[sae]-k[quench-turbine]",
    place_result = "sae-quench-turbine",
    stack_size = 10,
  },
})

-- Reactive Edge Plating (Phase 0 feasibility spike).
-- Throwaway-quality placeholder art and provisional numbers -- this block
-- exists to be measured against the real engine, not shipped as-is.
data:extend({
  {
    -- The plate's "charge": a real `ammo` item in a dedicated ammo-category
    -- (`sae-reactive-charge`, declared in prototypes/entity.lua), so nothing
    -- else can be loaded into a plate and a charge can't be loaded into any
    -- vanilla gun or turret. Same isolation trick, and the same reason, as
    -- the `sae-thermionic-fuel` fuel-category above.
    --
    -- Damage type is `physical`, not something more thematic, because
    -- vanilla asteroids are outright immune (percent = 100) to every damage
    -- type except impact/poison/acid plus the three they merely resist:
    -- physical, laser and explosion (space-age/prototypes/entity/asteroid.lua).
    -- Of those three, physical is the only one whose resistance doesn't
    -- scale to near-immunity with size (laser reaches percent = 99, as does
    -- explosion), which is exactly why vanilla's own anti-asteroid weapon --
    -- `railgun-ammo` -- is also flat physical.
    --
    -- 5000 physical is a deliberately chosen spike value, not a balance
    -- decision. Against the vanilla asteroid physical resistances
    -- (decrease = {0,0,0,2000,3000}, percent = {0,0,10,10,10}) it works out
    -- as: small 5000 vs 100hp, medium 4500 vs 400hp, big
    -- (5000-2000)*0.9 = 2700 vs 2000hp -- all one-charge kills -- but huge
    -- (5000-3000)*0.9 = 1800 vs 5000hp, which is deliberately NOT a kill.
    -- That single number is what makes the plate rateable per asteroid class
    -- without any control-stage logic at all.
    --
    -- `target_type = "entity"` with an `instant` action_delivery makes the
    -- shot hitscan -- no projectile travel time whatsoever. At the contact
    -- ranges this entity is built for, a travelling projectile would
    -- routinely lose the race against the asteroid it was fired at.
    type = "ammo",
    name = "sae-reactive-charge",
    -- Placeholder art: vanilla railgun ammo's icon.
    icon = "__space-age__/graphics/icons/railgun-ammo.png",
    icon_size = 64,
    icon_mipmaps = 4,
    ammo_category = "sae-reactive-charge",
    ammo_type = {
      target_type = "entity",
      action = {
        type = "direct",
        action_delivery = {
          type = "instant",
          target_effects = {
            {
              type = "damage",
              damage = { amount = 5000, type = "physical" },
            },
          },
        },
      },
    },
    subgroup = "ammo",
    order = "e[sae]-a[reactive-charge]",
    stack_size = 20,
    -- 10 kg, in grams (literal rather than `10 * kg`, since prototypes/ files
    -- keep `data` as their only global -- see .luacheckrc). Item weight here
    -- governs rocket cargo capacity ONLY. MEASURED: it contributes nothing to
    -- space platform mass, whether the charges sit in a chest or inside a
    -- plate's ammo slot -- see the note on the entity in prototypes/entity.lua.
    weight = 10000,
  },
  {
    type = "item",
    name = "sae-reactive-edge-plating",
    -- Placeholder art: vanilla gun turret's icon.
    icon = "__base__/graphics/icons/gun-turret.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "defensive-structure",
    order = "e[sae]-a[reactive-edge-plating]",
    place_result = "sae-reactive-edge-plating",
    stack_size = 50,
    -- 100 kg in grams. Rocket cargo only -- a placed plate adds nothing to
    -- the platform's mass (measured; see prototypes/entity.lua).
    weight = 100000,
  },
})
