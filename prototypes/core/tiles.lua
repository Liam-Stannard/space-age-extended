-- Whisker beds: ground made from dross, and the only surface metal will grow on.
--
local derive = require("prototypes.derive")

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

data:extend({
  {
    type = "item",
    name = "sae-whisker-bed",
    icon = "__space-age-extended__/graphics/icons/whisker-bed.png",
    subgroup = "terrain",
    order = "z[sae]-a[whisker-bed]",
    stack_size = 100,
    weight = 500,
    place_as_tile =
    {
      result = "sae-whisker-bed",
      condition_size = 1,
      condition = { layers = { water_tile = true } }
    }
  }
})
