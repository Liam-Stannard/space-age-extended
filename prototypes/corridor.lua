-- The corridor: the route past the Shattered Planet, and the one thing that
-- grows out there.
--
-- Vanilla's far field is barren by design -- the useful chunks stop and
-- promethium replaces them, and promethium has no crushing recipe at all. This
-- mod adds exactly one asteroid type and leaves the barrenness intact. Carbon,
-- ice and ore remain freight from the inner system, which is what keeps the
-- corridor carrying something every hour of the endgame.
--
-- Same rock, two harvests. Shoot it plainly for the power material; fire a seed
-- missile into it first and it becomes a crop instead. Using the wrong weapon
-- destroys it and yields nothing, because its dying effect is terminal -- the
-- field punishes reflexes and rewards intent.

--------------------------------------------------------------------------------
-- Chunks. A chunk needs BOTH an asteroid-chunk prototype and an item of the
-- same name: the first is the thing that floats, the second is what a collector
-- puts in its hold. Copying only the first gives a chunk with no item form.
--------------------------------------------------------------------------------

local radiant_chunk = table.deepcopy(data.raw["asteroid-chunk"]["promethium-asteroid-chunk"])
radiant_chunk.name = "sae-radiant-chunk"
radiant_chunk.order = "z[sae]-a[radiant]"
radiant_chunk.minable = { mining_time = 0.5, results = { { type = "item", name = "sae-radiant-chunk", amount = 1 } } }
data:extend({ radiant_chunk })

local seeded_chunk = table.deepcopy(data.raw["asteroid-chunk"]["carbonic-asteroid-chunk"])
seeded_chunk.name = "sae-seeded-chunk"
seeded_chunk.order = "z[sae]-b[seeded]"
seeded_chunk.minable = { mining_time = 0.5, results = { { type = "item", name = "sae-seeded-chunk", amount = 1 } } }
data:extend({ seeded_chunk })

local radiant_item = table.deepcopy(data.raw.item["promethium-asteroid-chunk"])
radiant_item.name = "sae-radiant-chunk"
radiant_item.order = "z[sae]-a[radiant]"
data:extend({ radiant_item })

local seeded_item = table.deepcopy(data.raw.item["carbonic-asteroid-chunk"])
seeded_item.name = "sae-seeded-chunk"
seeded_item.order = "z[sae]-b[seeded]"
data:extend({ seeded_item })

--------------------------------------------------------------------------------
-- The asteroids themselves.
--------------------------------------------------------------------------------

local radiant = table.deepcopy(data.raw.asteroid["small-promethium-asteroid"])
radiant.name = "sae-radiant-asteroid"
-- Terminal on purpose: destroyed by ordinary fire it leaves nothing behind.
radiant.dying_trigger_effect =
{
  { type = "create-explosion", entity_name = "promethium-asteroid-explosion-2", only_when_visible = true }
}
data:extend({ radiant })

local seeded = table.deepcopy(data.raw.asteroid["small-promethium-asteroid"])
seeded.name = "sae-seeded-asteroid"
seeded.dying_trigger_effect =
{
  { type = "create-explosion", entity_name = "promethium-asteroid-explosion-2", only_when_visible = true },
  {
    type = "create-asteroid-chunk",
    asteroid_name = "sae-seeded-chunk",
    offset_deviation = { { -0.25, -0.25 }, { 0.25, 0.25 } },
    offsets = { { -0.125, -0.0625 }, { 0.125, -0.0625 } }
  }
}
data:extend({ seeded })

--------------------------------------------------------------------------------
-- The seed missile. Its action destroys the rock and puts a seeded one in its
-- place, in a single trigger and with no script.
--------------------------------------------------------------------------------

local missile = table.deepcopy(data.raw.projectile["rocket"])
missile.name = "sae-seed-missile"
missile.action =
{
  type = "direct",
  action_delivery =
  {
    type = "instant",
    target_effects =
    {
      { type = "damage", damage = { amount = 2000, type = "explosion" } },
      { type = "create-entity", entity_name = "sae-seeded-asteroid" }
    }
  }
}
data:extend({ missile })

data:extend({
  {
    type = "ammo",
    name = "sae-seed-missile",
    icon = "__base__/graphics/icons/rocket.png",
    subgroup = "ammo",
    order = "z[sae]-a[seed-missile]",
    ammo_category = "rocket",
    stack_size = 100,
    weight = 4000,
    ammo_type =
    {
      target_type = "entity",
      action =
      {
        type = "direct",
        action_delivery =
        {
          type = "projectile",
          projectile = "sae-seed-missile",
          starting_speed = 0.3,
          max_range = 40
        }
      }
    }
  },

  -- The payload is the Gleba/Aquilo chain's frozen culture, so the corridor's
  -- biology traces to a planet that cannot be relocated. Light out, heavy back:
  -- ship seed rather than hauling organics two million kilometres.
  {
    type = "recipe",
    name = "sae-seed-missile",
    categories = { "crafting-with-fluid" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "rocket", amount = 1 },
      { type = "fluid", name = "sae-cryoprotectant", amount = 20 }
    },
    results = { { type = "item", name = "sae-seed-missile", amount = 1 } },
    enabled = false
  },

  -- What the two harvests are worth.
  {
    type = "recipe",
    name = "sae-radiant-crushing",
    categories = { "crushing" },
    energy_required = 3,
    ingredients = { { type = "item", name = "sae-radiant-chunk", amount = 1 } },
    results =
    {
      { type = "item", name = "sae-radiant-fuel", amount = 2 },
      { type = "item", name = "sae-radiant-chunk", amount = 1, independent_probability = 0.2, ignored_by_stats = 1 }
    },
    icon = "__space-age__/graphics/icons/promethium-asteroid-chunk.png",
    icon_size = 64,
    allow_productivity = true,
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-seeded-crushing",
    categories = { "crushing" },
    energy_required = 3,
    ingredients = { { type = "item", name = "sae-seeded-chunk", amount = 1 } },
    results =
    {
      { type = "item", name = "carbon", amount = 4 },
      { type = "item", name = "spoilage", amount = 2 }
    },
    icon = "__space-age__/graphics/icons/carbonic-asteroid-chunk.png",
    icon_size = 64,
    allow_productivity = true,
    enabled = false
  },

  -- The corridor's power. Solar is nil out here, nothing burns, and vanilla's
  -- answer does not travel: a fusion cell needs 100 ammonia, which has no
  -- barrel, so cells can only be made on Aquilo and freighted the whole way.
  -- This is made where it is consumed, from the one thing the far field has.
  {
    type = "item",
    name = "sae-radiant-fuel",
    icon = "__space-age__/graphics/icons/fusion-power-cell.png",
    subgroup = "intermediate-product",
    order = "z[sae]-c[radiant-fuel]",
    stack_size = 50,
    weight = 2000,
    fuel_category = "sae-radiant",
    fuel_value = "2GJ",
    fuel_emissions_multiplier = 0
  },
  {
    type = "fuel-category",
    name = "sae-radiant"
  }
})

--------------------------------------------------------------------------------
-- What burns it.
--
-- Nothing else will: the fuel has its own category, so a radiant cell cannot be
-- shovelled into anything that already exists, and this generator will take
-- nothing else. It works in vacuum and on the Core, which is the whole point --
-- it is the one power source that is made where it is spent.
--------------------------------------------------------------------------------

local gen = table.deepcopy(data.raw["burner-generator"]["burner-generator"])
gen.name = "sae-radiant-generator"
gen.icon = "__space-age__/graphics/icons/fusion-reactor.png"
gen.minable = { mining_time = 1, result = "sae-radiant-generator" }
gen.max_power_output = "10MW"
gen.energy_source = { type = "electric", usage_priority = "primary-output" }
gen.burner =
{
  type = "burner",
  fuel_categories = { "sae-radiant" },
  effectivity = 1,
  fuel_inventory_size = 2,
  burnt_inventory_size = 0
}
gen.surface_conditions = { { property = "pressure", max = 9 } }
gen.fast_replaceable_group = nil
gen.next_upgrade = nil
gen.hidden = false
gen.hidden_in_factoriopedia = false
data:extend({ gen })

data:extend({
  {
    type = "item",
    name = "sae-radiant-generator",
    icon = "__space-age__/graphics/icons/fusion-reactor.png",
    subgroup = "energy",
    order = "z[sae]-b[radiant-generator]",
    place_result = "sae-radiant-generator",
    stack_size = 10,
    weight = 40000
  },
  {
    type = "recipe",
    name = "sae-radiant-generator",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "processing-unit", amount = 20 },
      { type = "item", name = "low-density-structure", amount = 20 },
      { type = "item", name = "steel-plate", amount = 40 }
    },
    results = { { type = "item", name = "sae-radiant-generator", amount = 1 } },
    enabled = false
  }
})

--------------------------------------------------------------------------------
-- Where it spawns: on the connection the mod adds, and nowhere else. The far
-- field stays as barren as vanilla left it.
--------------------------------------------------------------------------------

local spawn =
{
  {
    asteroid = "sae-radiant-asteroid",
    spawn_points =
    {
      { distance = 0.0, probability = 0.00, speed = 0.05, angle_when_stopped = 0.4 },
      { distance = 0.2, probability = 0.02, speed = 0.05, angle_when_stopped = 0.4 },
      { distance = 1.0, probability = 0.06, speed = 0.05, angle_when_stopped = 0.4 }
    }
  }
}

for _, connection in pairs(data.raw["space-connection"]) do
  if connection.name == "sae-shattered-planet-core" then
    local defs = connection.asteroid_spawn_definitions or {}
    for _, d in pairs(spawn) do table.insert(defs, d) end
    connection.asteroid_spawn_definitions = defs
  end
end
