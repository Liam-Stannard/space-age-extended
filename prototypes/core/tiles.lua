-- The Core's ground: the lit cracks, the shards, the pool and its shore, the cliff.
local derive = require("prototypes.derive")

--- Walks `t` and every table under it, handing each string to `replacement_for`
--- and putting what comes back in its place. Return nil to leave the string
--- where it is; every repoint in this file is this walk with its own rule.
local function repoint(t, replacement_for)
  for k, v in pairs(t) do
    if type(v) == "table" then
      repoint(v, replacement_for)
    elseif type(v) == "string" then
      local replacement = replacement_for(v)
      if replacement then t[k] = replacement end
    end
  end
end

-- Tiles that glow. Vulcanus's hot crack tile carries a real light layer --
-- the one thing no Alien Biomes tile has -- so the Core's lit tiles take
-- their structure from it through derive and wear their own sheets, main and
-- light alike, so the night glow matches the day paint. Vulcanus's own
-- autoplace is gone with the copy; each tile is placed by a rule of its own.
local function glow_tile(name, order, map_color, sheets)
  -- Checked here rather than left to the repoint below, which leaves a string
  -- alone when it is handed nothing to put there: a missing sheet would then
  -- keep Vulcanus's path and ship a Core tile wearing Vulcanus art, quietly.
  assert(sheets.main, name .. ": no main sheet")
  assert(sheets.light, name .. ": no light sheet")
  local glow = derive.tile_from("volcanic-cracks-hot", name)
  glow.subgroup = "sae-core-tiles"
  glow.order = order
  glow.layer_group = "ground-natural"
  -- The copy says its sprites are only wanted on Vulcanus; the Core wants them.
  glow.sprite_usage_surface = "any"
  glow.map_color = map_color
  -- Repointed structurally rather than by listing files: the main sheet and the
  -- light sheet each appear once, under `variants`.
  repoint(glow.variants, function(v)
    if v == "__space-age__/graphics/terrain/vulcanus/volcanic-cracks-hot.png" then return sheets.main
    elseif v == "__space-age__/graphics/terrain/vulcanus/volcanic-cracks-hot-light.png" then return sheets.light end
  end)
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
  repoint(d.pictures, function(v)
    if v:sub(1, #FROM) == FROM then return TO .. v:sub(#FROM + 1) end
  end)
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
-- crust. The solution is drawn as lava is on Vulcanus: an offshore pump on the
-- shore, reaching into the pool, which keeps lava's `water_tile` layer for
-- exactly that. map-gen.lua places both from its basin term.
-- Its art is Vulcanus's lava re-graded by
-- concept/radiant-look-pool-icons/pool_look_b.py rather than hue-turned: a
-- turn kept lava's values and read as flat blue paint. Each pixel is graded by
-- how hot the lava was: its melt onto a blue ramp (#02081A > #04103A > #0B2A8C >
-- #1F63FF > #5A9CFF), its crust to a cool near-black, so the pool is a dark
-- liquid lit from below. The shader draws its own colour texture, so the pool
-- gets lava's shader with that image texture (effect.png, from
-- lava-textures/lava.png) re-graded the same way. Its two noise textures carry
-- no colour, so it reads space-age's own, as vanilla lava declares them; the
-- shader wants exactly two since 2.1.22, and the variation counts it once took
-- are now derived from the image texture's size.
data:extend({
  {
    type = "tile-effect",
    name = "sae-radiant",
    shader = "water",
    water =
    {
      shader_variation = "lava",
      noise_textures =
      {
        {
          filename = "__space-age__/graphics/terrain/vulcanus/lava-textures/lava-noise-1.png",
          size = 512,
          color_channels = 2
        },
        {
          filename = "__space-age__/graphics/terrain/vulcanus/lava-textures/lava-noise-2.png",
          size = 512,
          color_channels = 1
        }
      },
      image_textures =
      {
        { filename = "__space-age-extended__/graphics/terrain/radiant-pool/effect.png" }
      },
      animation_speed = 1.2,
      animation_scale = { 0.7, 0.7 },
      tick_scale = 1,
      -- Highlights and foam sit at the dark end of the ramp the pool's sheets are
      -- graded on, so the liquid reads dark and lit from below.
      specular_lightness = { 6, 20, 70 },
      foam_color = { 4, 16, 58 },
      foam_color_multiplier = 1.3,
      -- In the lava shader (core/graphics/shaders/tiles-lava-effect.frag) these two
      -- only add lava's hot rim at the shore, into red and half green -- an orange
      -- band round a blue pool -- so both are 0 here. lightmap_alpha = 0 and a light
      -- layer on the pool's variants were tried and measured the same in a client
      -- with and without: the shader draws the pool at night.
      dark_threshold = { 0, 0 },
      reflection_threshold = { 1, 1 },
      specular_threshold = { 0, 0 },
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
pool.fluid = "sae-radiant-solution"
pool.effect_color = { r = 30, g = 100, b = 255 }
-- The secondary effect colour and the particle tints are stops of the same ramp
-- as the sheets: its dark blue, and its two brightest.
pool.effect_color_secondary = { r = 4, g = 16, b = 58 }
pool.particle_tints = { primary = { r = 90, g = 156, b = 255 }, secondary = { r = 31, g = 99, b = 255 } }
pool.map_color = { r = 0.12, g = 0.39, b = 1.0 }
pool.autoplace = { probability_expression = "sae_core_pool" }
pool.ambient_sounds = nil
-- Most of what the player sees is the tile's own sheet under the shader:
-- lava-hot's, re-graded as above.
for _, v in pairs(pool.variants.main) do
  if v.picture == "__space-age__/graphics/terrain/vulcanus/lava-hot.png" then
    v.picture = "__space-age-extended__/graphics/terrain/radiant-pool/pool.png"
  end
end

-- The shore is the lit border of the body: Vulcanus's cooler lava crust --
-- dark plates with the melt showing between them, half the sheet alight --
-- re-graded as above with the plates a cool dark rock, and a light sheet made
-- in the same pass from the melt alone, since that sheet ships without one.
-- The crack art was tried here first and read as a black road with sparks in it.
local shore = glow_tile("sae-radiant-shore", "e[radiant-shore]", { r = 0.30, g = 0.45, b = 0.80 },
  { main = "__space-age-extended__/graphics/terrain/radiant-pool/shore.png",
    light = "__space-age-extended__/graphics/terrain/radiant-pool/shore-light.png" })
-- Plain ground. It used to carry the old wellhead's private collision layer and
-- the pool's fluid, so that an offshore pump standing on it drew solution; that
-- pump is now the Gas Pump, a mining drill that stands on vents, and the layer
-- went with it. The pool itself is where the solution is drawn from now.
shore.collision_mask = { layers = { ground_tile = true } }
shore.autoplace = { probability_expression = "sae_core_shore" }

-- Where the lit crust meets the pool it draws Vulcanus's ground-to-lava
-- lip -- a dark crust edge with lit seams and its own lightmap -- re-graded as
-- above, its crust the shore's rock and its lightmap mapped by brightness onto
-- the same blues rising from black. The copy's transition names lava-hot and
-- lava; the pool is a third name, so it is added, and the sheets repointed.
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
  repoint(cliff.orientations, function(v)
    if v:sub(1, #FROM) == FROM and not v:find("shadow", 1, true) then
      return TO .. v:sub(#FROM + 1)
    end
  end)
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
