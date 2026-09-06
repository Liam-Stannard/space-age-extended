-- Fulgora <-> Aquilo: holmium in the cold.
--
-- THE ANCHOR. Both legs are forced by fluids that have no barrel, so neither
-- can be dodged by moving a machine:
--
--   Fulgora -> Aquilo   holmium plate, because fluorine cannot leave Aquilo
--   Aquilo -> Fulgora   fluorinated holmium, because electrolyte cannot leave
--                       Fulgora
--
-- THE MECHANIC: the cold loop. Every step of this chain takes cold cryogen in
-- and hands spent cryogen back, so its layouts are loops rather than lines and
-- the chiller is an overhead that scales with machine count. Re-chilling needs
-- ammonia, which also has no barrel -- so cryogen is either made on Aquilo or
-- shipped cold, and running the chain elsewhere means paying freight forever.
--
-- THE CAPSTONE: the superconducting winding, which becomes the field coil's
-- conductor on the Core, and the superconducting store, which is what a world
-- of spikes has always needed.

data:extend({
  {
    type = "fluid",
    name = "sae-cold-cryogen",
    icon = "__space-age-extended__/graphics/icons/fluid/cold-cryogen.png",
    subgroup = "fluid",
    order = "z[sae]-fa[a-cold-cryogen]",
    default_temperature = -140,
    base_color = { r = 0.40, g = 0.65, b = 0.90 },
    flow_color = { r = 0.65, g = 0.85, b = 1.0 }
  },
  {
    type = "fluid",
    name = "sae-spent-cryogen",
    icon = "__space-age-extended__/graphics/icons/fluid/spent-cryogen.png",
    subgroup = "fluid",
    order = "z[sae]-fa[b-spent-cryogen]",
    default_temperature = 20,
    base_color = { r = 0.70, g = 0.60, b = 0.55 },
    flow_color = { r = 0.85, g = 0.78, b = 0.70 }
  },

  {
    type = "item",
    name = "sae-fluorinated-holmium",
    icon = "__space-age-extended__/graphics/icons/fluorinated-holmium.png",
    subgroup = "raw-material",
    order = "z[sae]-fa[c-fluorinated-holmium]",
    stack_size = 100,
    weight = 2000
  },

  -- Aquilo only: ammonia has no barrel.
  {
    type = "recipe",
    name = "sae-cryogen",
    categories = { "chemistry" },
    energy_required = 6,
    ingredients =
    {
      { type = "fluid", name = "ammonia", amount = 50 },
      { type = "item", name = "lithium-plate", amount = 1 }
    },
    results = { { type = "fluid", name = "sae-cold-cryogen", amount = 100 } },
    enabled = false
  },
  {
    type = "recipe",
    name = "sae-cryogen-recovery",
    categories = { "chemistry" },
    energy_required = 4,
    ingredients =
    {
      { type = "fluid", name = "sae-spent-cryogen", amount = 100 },
      { type = "fluid", name = "ammonia", amount = 10 }
    },
    results = { { type = "fluid", name = "sae-cold-cryogen", amount = 90 } },
    enabled = false
  },

  -- Aquilo only: fluorine has no barrel. This is what the holmium is shipped
  -- out for.
  {
    type = "recipe",
    name = "sae-fluorinated-holmium",
    categories = { "chemistry" },
    energy_required = 8,
    ingredients =
    {
      { type = "item", name = "holmium-plate", amount = 2 },
      { type = "fluid", name = "fluorine", amount = 20 },
      { type = "fluid", name = "sae-cold-cryogen", amount = 20 }
    },
    results =
    {
      { type = "item", name = "sae-fluorinated-holmium", amount = 1 },
      { type = "fluid", name = "sae-spent-cryogen", amount = 20 }
    },
    icon = "__space-age-extended__/graphics/icons/fluorinated-holmium.png",
    icon_size = 64,
    allow_productivity = true,
    enabled = false
  },

  -- Fulgora only: electrolyte has no barrel. This is what comes back.
  {
    type = "recipe",
    name = "sae-superconducting-winding",
    categories = { "electromagnetics" },
    energy_required = 12,
    ingredients =
    {
      { type = "item", name = "sae-fluorinated-holmium", amount = 2 },
      { type = "fluid", name = "electrolyte", amount = 20 },
      { type = "fluid", name = "sae-cold-cryogen", amount = 20 },
      { type = "item", name = "copper-cable", amount = 8 }
    },
    results =
    {
      { type = "item", name = "sae-superconducting-winding", amount = 1 },
      { type = "fluid", name = "sae-spent-cryogen", amount = 20 }
    },
    icon = "__space-age-extended__/graphics/icons/superconducting-winding.png",
    icon_size = 64,
    allow_productivity = true,
    enabled = false
  }
})

-- The capstone building. A world of spikes -- Fulgora's lightning when it is
-- earned, the Core's arc storms at the end -- has always wanted somewhere to
-- put a surge that arrives faster than anything can spend it.
local store = table.deepcopy(data.raw.accumulator["accumulator"])
store.name = "sae-superconducting-store"
store.icon = "__space-age-extended__/graphics/icons/superconducting-store.png"
store.minable = { mining_time = 0.5, result = "sae-superconducting-store" }
store.energy_source =
{
  type = "electric",
  buffer_capacity = "500MJ",
  usage_priority = "tertiary",
  input_flow_limit = "20MW",
  output_flow_limit = "20MW"
}
-- Art. `chargable_graphics` is a coupled set -- a base `picture` plus the two
-- overlays drawn on top of it -- so all four are replaced together. Vanilla's
-- overlays are shaped for the accumulator's flat-fronted box and light its front
-- panel; landing those on a drum would read as two machines lit at once. The
-- overlays were cleared when the prototype was written precisely so that whoever
-- set `picture` could not forget them, and this is that commit.
--
-- Every number is measured off the cut plate. The drum's visible content is
-- exactly 128 px -- 2.00 tiles -- so a row of stores touches rather than
-- overlaps. See graphics/building-spec-superconducting-store.md sections 9 and 13.
local SCS = "__space-age-extended__/graphics/entity/superconducting-store/"
local scs_plate = function(name, w, h, shift)
  return { filename = SCS .. name, priority = "high",
           width = w, height = h, shift = shift, scale = 0.5 }
end
store.chargable_graphics =
{
  picture =
  {
    layers =
    {
      scs_plate("base.png", 160, 164, { 0, -0.03125 }),
      -- The shadow leans up and right, so it is wider than the colour plate and
      -- carries its own x shift; both come out of process-building-art.py.
      (function ()
        local s = scs_plate("base-shadow.png", 279, 164, { 0.92969, -0.03125 })
        s.draw_as_shadow = true
        return s
      end)(),
      -- The ring, lit, always.
      --
      -- This is in `picture` rather than in the animations because the engine
      -- gives an accumulator nowhere else to put it. `chargable_graphics` has
      -- exactly `picture`, `charge_animation` and `discharge_animation`, and the
      -- two animations are **one-shots fired on charge and discharge events** --
      -- there is no charge-level slot. So a store sitting full and idle plays
      -- nothing, which is why the first in-game test showed four stores reading
      -- "Fully charged, 500 MJ/500 MJ" with the channel completely dark. Vanilla
      -- accumulators behave the same way; vanilla can afford it because its
      -- charge read is a panel on a box, and ours is the entire design.
      --
      -- So the ring idles lit at 90% and the charge sweep brightens it further. The cost
      -- is that an empty store glows too, which is wrong but is the lesser of
      -- the two errors the prototype allows.
      (function ()
        local s = scs_plate("ring-idle.png", 160, 164, { 0, -0.03125 })
        s.blend_mode = "additive"
        s.draw_as_glow = true
        return s
      end)()
    }
  },
  -- The ring channel, lit. The light travels *around* the channel rather than
  -- filling it like a bar, because a current going round a loop is what this
  -- building physically is -- section 9. Charge runs one way and discharge the
  -- other, at a little over half the brightness, so the direction reads.
  charge_animation =
  {
    layers =
    {
      {
        filename = SCS .. "charge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 160, height = 164,
        frame_count = 20, line_length = 5,
        shift = { 0, -0.03125 },
        scale = 0.5
      }
    }
  },
  charge_cooldown = 30,
  discharge_animation =
  {
    layers =
    {
      {
        filename = SCS .. "discharge.png",
        priority = "high",
        blend_mode = "additive",
        draw_as_glow = true,
        width = 160, height = 164,
        frame_count = 20, line_length = 5,
        shift = { 0, -0.03125 },
        scale = 0.5
      }
    }
  },
  discharge_cooldown = 60
}

-- No water tile can place on the Core, so the inherited reflection is dead
-- weight -- section 6.
store.water_reflection = nil

store.fast_replaceable_group = nil
store.next_upgrade = nil
data:extend({ store })

data:extend({
  {
    type = "item",
    name = "sae-superconducting-store",
    icon = "__space-age-extended__/graphics/icons/superconducting-store.png",
    subgroup = "energy",
    order = "z[sae]-c[superconducting-store]",
    place_result = "sae-superconducting-store",
    stack_size = 20,
    weight = 20000
  },
  {
    type = "recipe",
    name = "sae-superconducting-store",
    categories = { "crafting" },
    energy_required = 20,
    ingredients =
    {
      { type = "item", name = "sae-superconducting-winding", amount = 10 },
      { type = "item", name = "accumulator", amount = 2 },
      { type = "item", name = "steel-plate", amount = 20 }
    },
    results = { { type = "item", name = "sae-superconducting-store", amount = 1 } },
    enabled = false
  }
})
