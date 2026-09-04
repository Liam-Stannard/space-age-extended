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

-- Reactive Edge Plating.
--
-- Every number below is either measured on the running engine or carries a
-- one-line note saying what it is anchored to. Two things here are still
-- pending, and only two:
--   * ART -- the icons are vanilla stand-ins. Prompts for the real art are in
--     graphics/icon-prompts.md; that is its own work package.
--   * The RECIPES and the TECHNOLOGY (prototypes/recipe.lua,
--     prototypes/technology.lua) are the one deliberate provisional seam:
--     their real ingredient is Thermal-Shock Composite, which does not exist
--     yet. Nothing there is a stand-in for a number that has not been
--     decided; it is a stand-in for an item that has not been built.
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
    -- 5000 physical is ANCHORED TO THE LADDER IT PRODUCES, not picked. It is
    -- the round number just above the threshold that one-shots a metallic
    -- `big` and comfortably below the one that would one-shot a metallic
    -- `huge`: against decrease 2000 / percent 10 a `big` (2000 hp) needs
    -- (D - 2000) * 0.9 >= 2000, i.e. D >= 4223 (4222 gives 1999.8, which is
    -- short); against decrease 3000 a `huge` (5000 hp) would need D >= 8556.
    -- That window is what makes `huge` the class the player has to think
    -- about. Against the vanilla asteroid physical resistances
    -- (decrease = {0,0,0,2000,3000}, percent = {0,0,10,10,10}) it works out
    -- as: small 5000 vs 100hp, medium 4500 vs 400hp, big
    -- (5000-2000)*0.9 = 2700 vs 2000hp -- all one-charge kills -- but huge
    -- (5000-3000)*0.9 = 1800 vs 5000hp, which is deliberately NOT a kill.
    -- That single number is what makes the plate rateable per asteroid class
    -- without any control-stage logic at all.
    --
    -- CAUTION -- that ladder is for metallic/carbonic/oxide asteroids only.
    -- PROMETHIUM asteroids carry double health with the same resistances
    -- (space-age/prototypes/entity/asteroid.lua:143-144 builds them from
    -- shared_health * 2, i.e. 200/800/4000/10000) and double damage_per_hp.
    -- On the promethium route -- the whole corridor this capability exists
    -- for -- the same charge reads: small and medium still one-shot, big
    -- 2700 vs 4000hp is TWO charges, huge 1800 vs 10000hp is SIX.
    --
    -- MEASURED, and this is the part that matters: those two figures are
    -- exactly right and are the wrong number to plan with. They are the cost
    -- of killing the PARENT ROCK only -- confirmed on the rig, where a `huge`
    -- engaged in isolation read damage_dealt = 10800 = 6 x 1800 to the unit.
    -- What one ENCOUNTER costs is dominated by the CASCADE: every dying
    -- asteroid above `small` spawns exactly three of the next size down
    -- (asteroid.lua:255-278, a three-entry `offsets` list with a random
    -- offset_deviation of +/- collision_radius/2), and the plate shoots those
    -- too. Measured per encounter on the SHIPPED 3x2 rim, promethium: small 1
    -- charge, medium 4, big a deterministic 14, huge anywhere from 20 to 41 --
    -- `huge` did not reproduce across runs and is the one figure in this
    -- capability that should not be planned against as a point value. (For a
    -- LONE plate, big 8-10 and huge 6-10, but those runs ended with the
    -- magazine empty, so 10 is the magazine and not the demand.) Full tables,
    -- with plate/hull losses and the empty-plate controls, in PROGRESS.md --
    -- including the earlier 1x1-footprint figures, which are a different
    -- entity's numbers and are labelled as such there.
    --
    -- Anything that leaks also hits the plate hard, and MEASURED (T13, the
    -- million-hp probe build described in prototypes/entity.lua) exactly how
    -- hard: one promethium `small` deals 200 damage on contact, a `medium`
    -- 1280 and a `big` 9550. That is why `max_health` is 400 and there are no
    -- resistances -- reasoning on the entity.
    --
    -- `target_type = "entity"` with an `instant` action_delivery makes the
    -- shot hitscan -- no projectile travel time whatsoever. At the contact
    -- ranges this entity is built for, a travelling projectile would
    -- routinely lose the race against the asteroid it was fired at.
    type = "ammo",
    name = "sae-reactive-charge",
    -- ART PENDING: vanilla railgun ammo's icon stands in. The real icon is
    -- the "Reactive Charge" prompt in graphics/icon-prompts.md. Nothing numeric depends on this.
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
    -- One third of the ammo triple (the other two are `inventory_size` and
    -- `automated_ammo_count` on the entity, and all three were chosen
    -- together -- see the note there). Because the plate has
    -- `inventory_size = 1`, this number IS a plate's magazine.
    --
    -- 20 is at least twice the worst single-plate drain the runs bound: a lone
    -- plate EMPTIED a 10-charge magazine on a promethium `big` and again on a
    -- `huge`, so 10 is a lower bound on that encounter's demand rather than a
    -- measurement of it, and 20 is headroom rather than a proof that no
    -- encounter can dry a plate. What does pin the number is the entity: it
    -- equals `automated_ammo_count`, so with `inventory_size = 1` the
    -- guaranteed stock and the capacity are one number. 20 also keeps resupply
    -- a visible commitment rather than a rounding error: at `weight` 10 kg
    -- below, a stack is 200 kg, one rocket's 1000 kg lifts 100 charges, and
    -- stocking a 20x20 rim's 24 plates to full costs 480 charges = 4.8
    -- rockets. Vanilla's own heavy anti-asteroid round, railgun-ammo, is
    -- stack_size 10 at 200 kg apiece (space-age/prototypes/item.lua:643-644).
    stack_size = 20,
    -- 10 kg, in grams. Written as a literal rather than `10 * kg` because
    -- `kg` is not among the globals .luacheckrc declares for prototypes/ files
    -- (that entry lists `data` plus the three circuit-connector names
    -- prototypes/entity.lua reads, and a `files` entry replaces the top-level
    -- list rather than extending it). Item weight here
    -- governs rocket cargo capacity ONLY. MEASURED: it contributes nothing to
    -- space platform mass, whether the charges sit in a chest or inside a
    -- plate's ammo slot -- see the note on the entity in prototypes/entity.lua.
    weight = 10000,
  },
  {
    type = "item",
    name = "sae-reactive-edge-plating",
    -- ART PENDING: vanilla gun turret's icon stands in. The real icon is
    -- the "Reactive Edge Plating" prompt in graphics/icon-prompts.md. Nothing numeric depends on this.
    icon = "__base__/graphics/icons/gun-turret.png",
    icon_size = 64,
    icon_mipmaps = 4,
    subgroup = "defensive-structure",
    order = "e[sae]-a[reactive-edge-plating]",
    place_result = "sae-reactive-edge-plating",
    -- 50, vanilla gun-turret's own item stack size (base/prototypes/item.lua)
    -- and enough that one stack lays a whole 20x20 rim twice over (24 plates)
    -- or a 40x40 rim once (48) -- both counts MEASURED on the rig, not
    -- derived from the perimeter.
    stack_size = 50,
    -- 100 kg in grams. Rocket cargo only -- a placed plate adds nothing to
    -- the platform's mass (measured; see prototypes/entity.lua).
    weight = 100000,
  },
})
