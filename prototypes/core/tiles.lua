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

-- Tiles that glow. Vulcanus's hot crack tile carries a real light layer --
-- the one thing no Alien Biomes tile has -- so the Core's lit tiles take
-- their structure from it through derive and wear their own sheets, main and
-- light alike, so the night glow matches the day paint. Vulcanus's own
-- autoplace is gone with the copy; each tile is placed by a rule of its own.
local function glow_tile(name, order, map_color, sheets)
  local glow = derive.tile_from("volcanic-cracks-hot", name)
  glow.subgroup = "sae-core-tiles"
  glow.order = order
  glow.layer_group = "ground-natural"
  -- The copy says its sprites are only wanted on Vulcanus; the Core wants them.
  glow.sprite_usage_surface = "any"
  glow.map_color = map_color
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
  return glow
end

-- Shards of the crust: vanilla's medium, small and tiny rocks in the Core's
-- material (tools/build-core-rocks.py), as the Core's own decoratives with the
-- Core's own placement -- so the scatter no longer depends on an optional pack
-- and no longer arrives in another planet's colours. map-gen.lua includes
-- them by the "sae-crust" pattern.
local function shards(kind, probability)
  local d = derive.from("optimized-decorative", kind, "sae-crust-shards-" .. kind:gsub("%-rock$", ""))
  local FROM = "__base__/graphics/decorative/" .. kind .. "/"
  local TO = "__space-age-extended__/graphics/decorative/crust-shards/"
  local function repoint(t)
    for k, v in pairs(t) do
      if type(v) == "table" then repoint(v)
      elseif type(v) == "string" and v:sub(1, #FROM) == FROM then t[k] = TO .. v:sub(#FROM + 1) end
    end
  end
  repoint(d.pictures)
  d.autoplace =
  {
    order = "z[sae]-shards",
    -- Gathered rather than even: a short noise gates a flat chance, so shards
    -- lie in drifts with bare ground between.
    probability_expression = string.format(
      "%s * clamp(2 * multioctave_noise{x = x, y = y, seed0 = map_seed, seed1 = 6101, octaves = 2, persistence = 0.6, input_scale = 1/9, output_scale = 1}, 0, 1)",
      probability)
  }
  return d
end
data:extend({ shards("medium-rock", 0.012), shards("small-rock", 0.05), shards("tiny-rock", 0.09) })

-- The radiant pool: the corridor's isotope pooled in the Core's low ground,
-- lava's tile and shader in Cherenkov blue. Impassable and unbuildable, as
-- lava is; bridged with foundation. Its SHORE is a buildable ring of lit
-- crust, carrying the crust vent's collision layer and the pool's fluid, so a
-- Crust Tap stands on the shore and draws the brine exactly as it draws crust
-- gas from a vent. map-gen.lua places both from its basin term.
-- The shader draws its own colour texture, so the pool gets lava's shader
-- with that texture turned to blue (tools/build-crust-glow-tile.py --sheet),
-- the noise texture copied unchanged, and lava's own specular and foam
-- figures shifted cool.
data:extend({
  {
    type = "tile-effect",
    name = "sae-radiant",
    shader = "water",
    water =
    {
      shader_variation = "lava",
      textures =
      {
        { filename = "__space-age-extended__/graphics/terrain/radiant-pool/effect-noise.png" },
        { filename = "__space-age-extended__/graphics/terrain/radiant-pool/effect.png" }
      },
      texture_variations_columns = 1,
      texture_variations_rows = 1,
      secondary_texture_variations_columns = 4,
      secondary_texture_variations_rows = 2,
      animation_speed = 1.2,
      animation_scale = { 0.7, 0.7 },
      tick_scale = 1,
      specular_lightness = { 17, 30, 55 },
      foam_color = { 10, 30, 70 },
      foam_color_multiplier = 1.3,
      dark_threshold = { 0.755, 0.755 },
      reflection_threshold = { 1, 1 },
      specular_threshold = { 0.889, 0.291 },
      near_zoom = 0.0625,
      far_zoom = 0.0625
    }
  }
})

local pool = derive.tile_from("lava-hot", "sae-radiant-pool")
pool.effect = "sae-radiant"
pool.subgroup = "sae-core-tiles"
pool.order = "d[radiant-pool]"
pool.sprite_usage_surface = "any"
pool.allowed_neighbors = nil
pool.fluid = "sae-radiant-brine"
pool.effect_color = { r = 30, g = 100, b = 255 }
pool.effect_color_secondary = { r = 8, g = 24, b = 60 }
pool.particle_tints = { primary = { r = 120, g = 170, b = 255 }, secondary = { r = 30, g = 100, b = 255 } }
pool.map_color = { r = 0.12, g = 0.39, b = 1.0 }
pool.autoplace = { probability_expression = "sae_core_pool" }
pool.ambient_sounds = nil
-- Most of what the player sees is the tile's own sheet under the shader:
-- lava-hot's, turned to blue with the same rotation the arc glow tile had.
for _, v in pairs(pool.variants.main) do
  if v.picture == "__space-age__/graphics/terrain/vulcanus/lava-hot.png" then
    v.picture = "__space-age-extended__/graphics/terrain/radiant-pool/pool.png"
  end
end

-- The shore is the lit border of the body: Vulcanus's cooler lava crust --
-- dark plates with the melt showing between them, half the sheet alight --
-- turned to blue, with a light sheet cut from it by the glow tool's --light
-- mode, since that sheet ships without one. The crack art was tried here
-- first and read as a black road with sparks in it.
local shore = glow_tile("sae-radiant-shore", "e[radiant-shore]", { r = 0.30, g = 0.45, b = 0.80 },
  { main = "__space-age-extended__/graphics/terrain/radiant-pool/shore.png",
    light = "__space-age-extended__/graphics/terrain/radiant-pool/shore-light.png" })
shore.fluid = "sae-radiant-brine"
shore.collision_mask = { layers = { ground_tile = true, ["sae-crust-vent"] = true } }
shore.autoplace = { probability_expression = "sae_core_shore" }

-- Where the lit crust meets the pool it draws Vulcanus's ground-to-lava
-- lip -- a dark crust edge with lit seams and its own lightmap -- turned to
-- blue the way the rest of the art was. The copy's transition names lava-hot
-- and lava; the pool is a third name, so it is added, and the sheets repointed.
local function border_pool(tile)
  for _, t in ipairs(tile.transitions or {}) do
    local to_lava = false
    for _, name in ipairs(t.to_tiles or {}) do if name == "lava-hot" then to_lava = true end end
    if to_lava then
      table.insert(t.to_tiles, "sae-radiant-pool")
      t.spritesheet = "__space-age-extended__/graphics/terrain/radiant-pool/lip.png"
      if t.lightmap_layout then
        t.lightmap_layout.spritesheet = "__space-age-extended__/graphics/terrain/radiant-pool/lip-light.png"
      end
    end
  end
  return tile
end
border_pool(shore)
data:extend({ pool, shore })

-- The Core's cliff: Fulgora's geometry -- twenty seamed orientations nobody
-- should redraw -- in the Core's material, the sheets rebuilt by
-- tools/build-core-cliff.py. Shadows are shape, not material, so they stay
-- vanilla's. map-gen.lua names it in `cliff_settings`.
local cliff = derive.from("cliff", "cliff-fulgora", "sae-cliff-core")
cliff.map_color = { r = 0.33, g = 0.37, b = 0.42 }
do
  local FROM = "__space-age__/graphics/terrain/cliffs/fulgora/cliff-fulgora-"
  local TO = "__space-age-extended__/graphics/terrain/cliff-core/cliff-"
  local function repoint(t)
    for k, v in pairs(t) do
      if type(v) == "table" then repoint(v)
      elseif type(v) == "string" and v:sub(1, #FROM) == FROM and not v:find("shadow", 1, true) then
        t[k] = TO .. v:sub(#FROM + 1)
      end
    end
  end
  repoint(cliff.orientations)
end
data:extend({ cliff })

-- The crust's lit cracks: Vulcanus's hot-crack sheets with the embers' hue
-- rotated to arc blue by tools/build-crust-glow-tile.py, placed by
-- `sae_core_glow` down the middle of the dark rims and nowhere else.
data:extend({
  border_pool(glow_tile("sae-crust-glow-arc", "c[crust-glow-arc]", { r = 0.35, g = 0.55, b = 0.95 },
    { main = "__space-age-extended__/graphics/terrain/crust-glow/arc.png",
      light = "__space-age-extended__/graphics/terrain/crust-glow/arc-light.png" }))
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
