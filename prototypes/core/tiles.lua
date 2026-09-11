-- Whisker beds: ground made from dross, and the only surface metal will grow on.
--
local derive = require("prototypes.derive")
local item_sounds = require("__base__.prototypes.item_sounds")

-- A floor the player lays, so it keeps a floor's filing, mining and sounds --
-- but not stone path's +30% walking speed. A bed of grit is not a footpath.
local bed = derive.tile_from("stone-path", "sae-whisker-bed")
bed.subgroup = "artificial-tiles"
bed.mined_sound = table.deepcopy(data.raw.tile["stone-path"].mined_sound)
bed.build_sound = table.deepcopy(data.raw.tile["stone-path"].build_sound)

-- Its own terrain, at last. The bed kept stone path's graphics for six phases,
-- which meant a whisker farm on the Core was indistinguishable from a concrete
-- pad -- on a planet where this is the only ground anything grows in.
--
-- The sheets are vanilla's geometry recoloured by tools/build-whisker-bed-tile.py
-- rather than new art, and that is deliberate: a Factorio tile is three main
-- sheets at 1x/2x/4x with sixteen variants each plus five transition groups and
-- their masks, all of which have to tile seamlessly against each other and
-- against every neighbouring tile. Vanilla's satisfy that contract exactly, so
-- the contract is kept and only the material changes -- dark iron-nickel grit
-- with whisker glints through it, measured at luminance 60 against the Core's
-- basalt at 22, so the pad reads at a glance.
--
-- Repointed structurally rather than by listing files: `variants` nests main,
-- transitions and masks several levels deep, and enumerating them by hand would
-- break silently the first time one is added.
local STONE = "__base__/graphics/terrain/stone%-path/stone%-path"
local BED = "__space-age-extended__/graphics/terrain/whisker-bed/whisker-bed"
local function repoint(t)
  for k, v in pairs(t) do
    if type(v) == "table" then
      repoint(v)
    elseif type(v) == "string" and v:find(STONE) then
      t[k] = v:gsub(STONE, BED)
    end
  end
end
repoint(bed.variants)
bed.order = "z[sae]-a[whisker-bed]"
bed.minable = { mining_time = 0.2, result = "sae-whisker-bed" }
bed.map_color = { r = 0.42, g = 0.40, b = 0.36 }
bed.can_be_part_of_blueprint = true
data:extend({ bed })

-- The crust's lit cracks. Vulcanus's hot crack tile carries a real light
-- layer -- the one thing no Alien Biomes tile has -- so the Core takes its
-- art through derive and places it by its own rule: `sae_core_glow`, a noise
-- expression map-gen.lua defines from the selected palette's dark shape, so
-- the glow runs exactly along the joints of the crust and nowhere else.
-- Vulcanus's own autoplace is gone with the copy; only the sheets remain.
--
-- Two colours of it. Ember is the art as it ships; arc is the same sheets with
-- the embers' hue rotated to blue by tools/build-crust-glow-tile.py, main and
-- light sheet alike, so the night glow matches the day paint. The palette
-- says which one the crust wears (`glow.colour`), and map-gen.lua lists it.
local function glow_tile(name, order, map_color, sheets)
  local glow = derive.tile_from("volcanic-cracks-hot", name)
  glow.subgroup = "sae-core-tiles"
  glow.order = order
  glow.layer_group = "ground-natural"
  -- The copy says its sprites are only wanted on Vulcanus; the Core wants them.
  glow.sprite_usage_surface = "any"
  glow.map_color = map_color
  glow.autoplace = { probability_expression = "sae_core_glow" }
  if sheets then
    -- Repointed structurally, as the whisker bed is: the main sheet and the
    -- light sheet each appear once, under `variants`.
    local function repoint(t)
      for k, v in pairs(t) do
        if type(v) == "table" then repoint(v)
        elseif type(v) == "string" then
          if v == "__space-age__/graphics/terrain/vulcanus/volcanic-cracks-hot.png" then t[k] = sheets.main
          elseif v == "__space-age__/graphics/terrain/vulcanus/volcanic-cracks-hot-light.png" then t[k] = sheets.light end
        end
      end
    end
    repoint(glow.variants)
  end
  return glow
end

data:extend({
  glow_tile("sae-crust-glow", "b[crust-glow]", { r = 0.85, g = 0.45, b = 0.20 }),
  glow_tile("sae-crust-glow-arc", "c[crust-glow-arc]", { r = 0.35, g = 0.55, b = 0.95 },
    { main = "__space-age-extended__/graphics/terrain/crust-glow/arc.png",
      light = "__space-age-extended__/graphics/terrain/crust-glow/arc-light.png" })
})

data:extend({
  {
    type = "item",
    name = "sae-whisker-bed",
    icon = "__space-age-extended__/graphics/icons/whisker-bed.png",
    subgroup = "terrain",
    order = "z[sae]-a[whisker-bed]",
    inventory_move_sound = item_sounds.brick_inventory_move,
    pick_sound = item_sounds.brick_inventory_pickup,
    drop_sound = item_sounds.brick_inventory_move,
    stack_size = 100,
    weight = 0.5 * kg,
    place_as_tile =
    {
      result = "sae-whisker-bed",
      condition_size = 1,
      condition = { layers = { water_tile = true } }
    }
  }
})
