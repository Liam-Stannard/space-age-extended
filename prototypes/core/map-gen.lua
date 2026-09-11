-- Terrain for the Core.
--
-- The elevation expression never dips below sea level, so no water tile can
-- ever place -- which is how "no fluids on the surface" is enforced by the
-- terrain rather than by a rule.
--
-- Everything else here is one choice: which palette the crust wears. Four are
-- defined below and one is selected by PALETTE; they differ in their tile lists
-- *and* in the climate that selects those tiles, because a tile list on its own
-- decides nothing. Tiles choose themselves by temperature, moisture and aux, so
-- naming a tile that no point on the surface qualifies for simply means it
-- never appears -- which is exactly how an earlier version of this file ended
-- up all snow while listing no snow at all.
--
-- To try another one: change PALETTE, then generate a *new* surface. Map
-- generation applies only to chunks that do not exist yet, so an existing save
-- keeps whatever terrain it was born with, and nothing you do here will change
-- ground you have already walked on.

local PALETTE = "core-crust"

-- Two sources, and they are not the same promise. The volcanic-* tiles ship
-- with Space Age (they are Vulcanus's ground) and are always there; the
-- mineral-*, frozen-snow-* and *-heat-* tiles come from Alien Biomes and are
-- there only when it is installed. Keeping them in separate lists means a
-- palette degrades to its Space Age half rather than to a guess -- and it
-- replaces the old "if fewer than half the names exist, assume the pack is
-- missing" heuristic, which could not tell an absent pack from a renamed tile.
--
-- Every name is still checked against data.raw before use: an optional
-- dependency that silently assumes its own presence is not optional.
--
-- The Alien Biomes names below were taken from the pack's own tile set. To
-- re-check them against an install, run this in-game:
--   /c local t = {} for n in pairs(prototypes.tile) do
--        if n:find("mineral") or n:find("volcanic") or n:find("frozen") then
--          t[#t+1] = n end end
--      table.sort(t) game.print(table.concat(t, " "))
--
-- Decoratives are not listed at all -- see core_decoratives() below, which asks
-- data.raw what exists rather than naming anything. To see what it selected,
-- standing on the Core:
--   /c local s = game.player.surface.map_gen_settings.autoplace_settings
--                    .decorative.settings
--      local t = {} for n in pairs(s) do t[#t+1] = n end
--      table.sort(t) game.print(#t .. ": " .. table.concat(t, " "))

local palettes =
{
  -- Heat-treated iron shows temper colours -- straw, brown, purple, blue -- so
  -- the ground itself says metal that has been hot. Brown body, violet and
  -- purple blooms where aux runs high, straw-tan where it runs low.
  ["tempered-steel"] =
  {
    temperature = { centre = 78, amplitude = 14, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- First render at 0.55 +/- 0.34 never reached violet's 0.85 +/- 0.05 and
    -- came out tan and brown; the range now sits on the brown/violet boundary.
    aux         = { centre = 0.72, amplitude = 0.24, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.5, drop = 0.9, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-brown-dirt-1", "mineral-brown-dirt-2", "mineral-brown-dirt-3", "mineral-brown-sand-1",
      "mineral-violet-dirt-1", "mineral-violet-dirt-2", "mineral-violet-dirt-3", "mineral-purple-dirt-1",
      "mineral-tan-dirt-1", "mineral-tan-sand-1", "mineral-tan-sand-3",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2",
      "volcanic-blue-heat-1", "volcanic-purple-heat-1"
    }
  },

  -- The ore's own colour. A shattered iron core oxidised at the surface: red
  -- and dusty-rose body, plates of tan where the crust is scoured bare, and
  -- cooler dips that go dustyrose. Warm, dark, unmistakably iron.
  ["rust-iron"] =
  {
    temperature = { centre = 72, amplitude = 22, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.70, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 1.2, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-red-dirt-1", "mineral-red-dirt-2", "mineral-red-dirt-3", "mineral-red-sand-1",
      "mineral-dustyrose-dirt-1", "mineral-dustyrose-dirt-2", "mineral-dustyrose-sand-1",
      "mineral-brown-dirt-1", "mineral-tan-sand-1", "mineral-tan-dirt-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1"
    }
  },

  -- The design's own first tile list had a slag flat in it. Black glassy slag
  -- for a body, and plates of pale warm slag foam -- cream, not white -- that
  -- warm themselves into the mid band so cream answers rather than white.
  ["slag-flats"] =
  {
    temperature = { centre = 14, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.45, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.86, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 1.4, warm = 70, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-black-dirt-1", "mineral-black-dirt-2", "mineral-black-dirt-3",
      "mineral-black-sand-1", "mineral-black-sand-3",
      "mineral-cream-dirt-1", "mineral-cream-dirt-3", "mineral-cream-sand-1", "mineral-beige-dirt-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1"
    }
  },

  -- A cut meteorite: bronze-brown with crystalline banding. The bands come
  -- from stretching the colour noise along one axis, so tan and red run in
  -- streaks through the brown rather than pooling.
  ["meteorite-face"] =
  {
    temperature = { centre = 76, amplitude = 16, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.16, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.42, amplitude = 0.34, octaves = 2, persistence = 0.5, scale = 220, stretch = 0.18 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-brown-dirt-1", "mineral-brown-dirt-2", "mineral-brown-dirt-3", "mineral-brown-sand-1",
      "mineral-tan-dirt-1", "mineral-tan-dirt-3", "mineral-tan-sand-1",
      "mineral-red-dirt-1", "mineral-red-sand-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1"
    }
  },

  -- The cool dark of a core whose field died. Aubergine and violet body in
  -- the mid band, dustyrose plates, black where the ground dips cold, and the
  -- seams come up blue because aux runs high. The most alien of the set, and
  -- the one the machines' copper has to warm.
  ["dead-dynamo"] =
  {
    temperature = { centre = 42, amplitude = 16, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.88, amplitude = 0.08, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 0.35, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-aubergine-dirt-1", "mineral-aubergine-dirt-2", "mineral-aubergine-dirt-3", "mineral-aubergine-sand-1",
      "mineral-dustyrose-dirt-1", "mineral-dustyrose-dirt-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-purple-heat-1", "volcanic-orange-heat-1"
    }
  },

  -- Warm pale neutral: beige regolith with dusty-rose plates and black where the ground dips cold. The quietest of the set.
  ["beige-regolith"] =
  {
    temperature = { centre = 44, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.5, amplitude = 0.16, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.5, drop = -0.35, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-beige-dirt-1",
      "mineral-beige-dirt-2",
      "mineral-beige-dirt-3",
      "mineral-beige-sand-1",
      "mineral-dustyrose-dirt-1",
      "mineral-dustyrose-dirt-3",
      "mineral-black-dirt-1",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  -- Pale cream flats -- the brightest ground the tiles offer -- with beige shading and aubergine hollows. A bleached world.
  ["cream-flats"] =
  {
    temperature = { centre = 45, amplitude = 10, octaves = 2, persistence = 0.5, scale = 480 },
    -- The body sits at 45, so a seam needs only +55 to reach the heat window
    -- and the standard 0.035 band came out three times as wide as on a cold
    -- body (10% of the ground, in dark strips). Narrowed to match.
    veins       = { width = 0.022, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.22, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.5, drop = -0.65, warm = -45, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-cream-dirt-1",
      "mineral-cream-dirt-2",
      "mineral-cream-dirt-3",
      "mineral-cream-sand-1",
      "mineral-beige-dirt-1",
      "mineral-beige-dirt-2",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  ["cream-flats-iron"] =
  {
    temperature = { centre = 45, amplitude = 10, octaves = 2, persistence = 0.5, scale = 480 },
    -- The body sits at 45, so a seam needs only +55 to reach the heat window
    -- and the standard 0.035 band came out three times as wide as on a cold
    -- body (10% of the ground, in dark strips). Narrowed to match.
    veins       = { width = 0.022, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.22, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.5, drop = -0.25, warm = 40, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-cream-dirt-1",
      "mineral-cream-dirt-2",
      "mineral-cream-dirt-3",
      "mineral-cream-sand-1",
      "mineral-beige-dirt-1",
      "mineral-beige-dirt-2",
      "mineral-brown-dirt-1", "mineral-brown-dirt-2",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  -- Violet body -- the hot band's darkest colour -- with purple where it deepens and red-brown where it cools. Tempered metal all the way through.
  ["violet-bloom"] =
  {
    temperature = { centre = 80, amplitude = 14, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.86, amplitude = 0.06, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.5, drop = 0.25, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-violet-dirt-1",
      "mineral-violet-dirt-2",
      "mineral-violet-dirt-3",
      "mineral-violet-sand-1",
      "mineral-purple-dirt-1",
      "mineral-purple-dirt-2",
      "mineral-red-dirt-1",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  -- Purple ground with tan plates cut into it -- the two ends of the hot band's colour axis side by side.
  ["deep-purple"] =
  {
    temperature = { centre = 80, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.95, amplitude = 0.04, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 1.0, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-purple-dirt-1",
      "mineral-purple-dirt-2",
      "mineral-purple-dirt-3",
      "mineral-purple-sand-1",
      "mineral-tan-dirt-1",
      "mineral-tan-sand-1",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  -- Dusty rose body with cream plates and aubergine hollows: a mauve world, warm-grey without grey.
  ["mauve-dust"] =
  {
    temperature = { centre = 45, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.72, amplitude = 0.08, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = 0.6, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-dustyrose-dirt-1",
      "mineral-dustyrose-dirt-2",
      "mineral-dustyrose-dirt-3",
      "mineral-dustyrose-sand-1",
      "mineral-cream-dirt-1",
      "mineral-aubergine-dirt-1",
      "mineral-aubergine-dirt-2",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  -- Straw-tan body with red plates -- the light end of the hot band, with iron showing through.
  ["straw-tan"] =
  {
    temperature = { centre = 80, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.16, amplitude = 0.1, octaves = 3, persistence = 0.5, scale = 340 },
    plates      = { threshold = 0.45, drop = -0.6, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-tan-dirt-1",
      "mineral-tan-dirt-2",
      "mineral-tan-dirt-3",
      "mineral-tan-sand-1",
      "mineral-tan-sand-3",
      "mineral-red-dirt-1",
      "mineral-red-sand-1",
      "volcanic-orange-heat-1",
      "volcanic-blue-heat-1"
    }
  },

  -- The whole body in the heat window, so Alien Biomes' GREEN heat tiles are the ground -- an unlit acid-green crust with orange where aux runs low. Nothing else in the game is this colour.
  ["green-heat"] =
  {
    -- Three green shades: heat-1 at 110, -2 at 127, -3 at 140, so the body has
    -- to range across them or it is one tile everywhere, which the first
    -- render was.
    temperature = { centre = 126, amplitude = 16, octaves = 2, persistence = 0.5, scale = 300 },
    -- Seams run COLD here: a negative gain drops the temperature into the mid
    -- band along the contours, where dustyrose answers at this aux -- mauve
    -- fractures through dark green.
    veins       = { width = 0.035, gain = -2400, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- Green heat is a narrow aux window, 0.75 +/- 0.05; anything wider is orange.
    aux         = { centre = 0.75, amplitude = 0.04, octaves = 3, persistence = 0.5, scale = 340 },
    -- Plates dip aux toward the orange window: darker, warmer patches.
    plates      = { threshold = 0.5, drop = 0.5, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "volcanic-green-heat-1",
      "volcanic-green-heat-2",
      "volcanic-green-heat-3",
      "volcanic-green-heat-4",
      "mineral-dustyrose-dirt-1", "mineral-dustyrose-dirt-2", "mineral-black-dirt-1",
      "volcanic-orange-heat-1",
      "volcanic-orange-heat-2"
    }
  },

  ["blue-heat"] =
  {
    -- Three green shades: heat-1 at 110, -2 at 127, -3 at 140, so the body has
    -- to range across them or it is one tile everywhere, which the first
    -- render was.
    temperature = { centre = 126, amplitude = 16, octaves = 2, persistence = 0.5, scale = 300 },
    -- Seams run COLD here: a negative gain drops the temperature into the mid
    -- band along the contours, where dustyrose answers at this aux -- mauve
    -- fractures through dark green.
    veins       = { width = 0.035, gain = -2400, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- Blue heat is a narrow aux window, 0.85 +/- 0.05.
    aux         = { centre = 0.85, amplitude = 0.04, octaves = 3, persistence = 0.5, scale = 340 },
    -- Plates dip aux toward the orange window: darker, warmer patches.
    plates      = { threshold = 0.5, drop = 0.5, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "volcanic-blue-heat-1",
      "volcanic-blue-heat-2",
      "volcanic-blue-heat-3",
      "volcanic-blue-heat-4",
      "mineral-aubergine-dirt-1", "mineral-aubergine-dirt-2", "mineral-black-dirt-1",
      "volcanic-orange-heat-1",
      "volcanic-orange-heat-2"
    }
  },

  -- Nauvis's red desert and dry dirt: rust-orange and khaki, no pack required.
  ["red-desert"] =
  {
    temperature = { centre = 15, amplitude = 15, octaves = 2, persistence = 0.5, scale = 480 },
    -- Nauvis places red desert where it is dry and aux runs high; the first
    -- render at moisture 0.5 and aux 0.5 gave 70% plain dirt and no red at all.
    moisture    = { centre = 0.15, amplitude = 0.12, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.85, amplitude = 0.12, octaves = 3, persistence = 0.5, scale = 300 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    -- Space Age's own tiles, placed by their own autoplace; the climate above
    -- only matters where those expressions read it.
    tiles = { "red-desert-0", "red-desert-1", "red-desert-2", "red-desert-3", "dry-dirt", "dirt-5", "dirt-7", "sand-3" },
    without_pack = {},
    alien_tiles = {}
  },

  -- Fulgora's ground without its ruins: dust, sand, rock and dunes in dusty red-brown. No pack required.
  ["fulgoran-dust"] =
  {
    temperature = { centre = 15, amplitude = 15, octaves = 2, persistence = 0.5, scale = 480 },
    moisture    = { centre = 0.5, amplitude = 0.2, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.5, amplitude = 0.3, octaves = 3, persistence = 0.5, scale = 300 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    -- Space Age's own tiles, placed by their own autoplace; the climate above
    -- only matters where those expressions read it.
    tiles = { "fulgoran-dust", "fulgoran-sand", "fulgoran-rock", "fulgoran-dunes" },
    without_pack = {},
    alien_tiles = {}
  },

  -- Vulcanus's soil and stone without its ash or lava: olive-black basalt, smooth stone, folds. No pack required.
  ["basalt-soil"] =
  {
    -- Vulcanus's tiles read our aux and moisture on top of their own biome
    -- noise: smooth stone and dark soil want aux LOW, pumice and folds want it
    -- HIGH, and soil and pumice both want moisture high. The first render
    -- varied aux at the 300-tile scale and came out as biome-sized flats; a
    -- short scale mixes stone and pumice at the scale a player walks.
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    -- Seams: Alien Biomes' heat tiles along the contours, as on the coloured
    -- palettes -- the one thing here the Vulcanus set cannot supply.
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.70, amplitude = 0.15, octaves = 3, persistence = 0.5, scale = 200 },
    aux         = { centre = 0.50, amplitude = 0.38, octaves = 3, persistence = 0.6, scale = 120 },
    -- Vulcanus sizes its biomes from this slider; at 1 the flats are hundreds of
    -- tiles across whatever our own noise does. 6 is the slider's maximum.
    controls    = { vulcanus_volcanism = { frequency = 6, size = 1, richness = 1 } },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },
    -- Space Age's own tiles, placed by their own autoplace; the climate above
    -- only matters where those expressions read it.
    tiles = { "volcanic-soil-dark", "volcanic-soil-light", "volcanic-smooth-stone", "volcanic-folds", "volcanic-folds-flat", "volcanic-jagged-ground", "volcanic-pumice-stones" },
    without_pack = {},
    alien_tiles = { "volcanic-orange-heat-1", "volcanic-orange-heat-2", "volcanic-blue-heat-1" }
  },

  -- White ground, blue heat. The bare-metal white of the cold band as the
  -- whole crust, and the blue heat tiles -- dark slate -- as both the seams and
  -- the plates: the seams carry their own colour axis so they land on blue
  -- rather than orange, and the plates lift both axis and temperature into the
  -- blue window. Rocks are the pack's white and black only; the cliff is
  -- Fulgora's dark stone rather than Nauvis's sandstone; the boulder is tinted
  -- slate to sit with the seams.
  ["white-and-blue"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The colour axis moves at 0.42 and the temperature at 0.56, so between the
    -- two thresholds the ground is cold at high aux -- black dirt -- and every
    -- plate wears a dark rim. The feather breaks the rim into fingers.
    plates      = { threshold = 0.42, warm_threshold = 0.56, drop = -0.72, warm = 100,
                    octaves = 2, persistence = 0.6, scale = 48, seed = 7781,
                    feather = { amplitude = 0.35, octaves = 2, persistence = 0.6, scale = 7 } },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-hollows"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- Blobs: the shape the plates term made, for reference.
    dark        = { shape = "hollows", amount = 0.72, threshold = 0.45, scale = 48, octaves = 2, persistence = 0.6, feather = { amplitude = 0.15, octaves = 2, persistence = 0.6, scale = 7 } },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-rims"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- Rings: a band either side of a noise threshold, interiors left white.
    dark        = { shape = "rims", amount = 0.72, threshold = 0.45, width = 0.08, scale = 48, octaves = 2, persistence = 0.6, feather = { amplitude = 0.12, octaves = 2, persistence = 0.6, scale = 7 } },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-cracks"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- A fracture network: the zero contours of a long noise, jagged.
    dark        = { shape = "cracks", amount = 0.72, width = 0.045, scale = 260, octaves = 3, persistence = 0.5, feather = { amplitude = 0.10, octaves = 2, persistence = 0.6, scale = 9 } },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-cells"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- A jointed crust: Voronoi cell borders as black joints between white plates.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.10, jitter = 0.8 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-craters"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- Round pits at Voronoi cell centres, sized by the grid.
    dark        = { shape = "craters", amount = 0.72, grid = 40, level = 0.15, jitter = 0.9 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-basins"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- Dark low ground: below an elevation contour, so it agrees with the cliffs.
    dark        = { shape = "basins", amount = 0.72, level = 139, softness = 6 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-strata"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- Long parallel bands: the hollows noise stretched along one axis.
    dark        = { shape = "hollows", amount = 0.72, threshold = 0.40, scale = 90, octaves = 2, persistence = 0.5, stretch = 0.12 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-grit"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- Salt and pepper: a very short noise above a high threshold.
    dark        = { shape = "hollows", amount = 0.72, threshold = 0.55, sharpness = 20, scale = 4, octaves = 2, persistence = 0.6 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-gradient"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The crust darkens with distance from the landing site.
    dark        = { shape = "gradient", amount = 0.72, from = 100, over = 260 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-plates"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- A jointed crust with wide joints: the pyramid noise below a width.
    dark        = { shape = "plates", amount = 0.72, grid = 40, width = 0.22, jitter = 0.9 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-cells-glow"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2 },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wb-cells-arc"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose" },
    cliff       = "cliff-fulgora",
    boulder_tint = { r = 0.32, g = 0.40, b = 0.50, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbc-cliff-nauvis"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "cliff",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbc-cliff-vulcanus"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "cliff-vulcanus",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbc-cliff-gleba"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "cliff-gleba",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbc-cliff-fulgora"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbr-black-rocks"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    -- Rocks: black only.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-white" },
    cliff       = "sae-cliff-core",
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbr-white-rocks"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    -- Rocks: white only.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbr-no-rocks"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    -- Rocks: none; craters only.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-white", "-black", "rock", "stone" },
    cliff       = "sae-cliff-core",
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbr-black-boulder"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    -- Rocks black, boulder tinted near-black to match the joints.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-white" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.18, g = 0.20, b = 0.24, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["wbr-pale-boulder"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    -- Rocks white, boulder tinted pale to sit with the crust.
    dark        = { shape = "cells", amount = 0.72, grid = 28, width = 0.14, jitter = 0.8 },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    boulder_tint = { r = 0.85, g = 0.88, b = 0.92, a = 1 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["core-crust"] =
  {
    temperature = { centre = 15, amplitude = 12, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, aux = 0.72, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.50, amplitude = 0.14, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.15, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 340 },
    -- The jointed crust, lit: the joints are black dirt at their edges and the
    -- Core's own hot-crack tile down the middle, which glows at night -- in arc blue.
    -- The facet noise is normalised, not in tiles: 2.5 blackened everything.
    -- Rims rather than cells (the cells version is wb-cells-arc): a band either
    -- side of a noise threshold, so the dark -- and the glow down its middle --
    -- rings the plates and leaves their interiors whole.
    dark        = { shape = "rims", amount = 0.72, threshold = 0.45, width = 0.10, scale = 48, octaves = 2, persistence = 0.6, feather = { amplitude = 0.12, octaves = 2, persistence = 0.6, scale = 7 } },
    glow        = { gain = 3, cut = 1.2, colour = "arc" },
    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost",
                    "grey", "-red", "-tan", "-beige", "-brown", "-cream", "-purple", "-violet", "-aubergine", "-dustyrose", "-black", "-rock-", "-rock" },
    cliff       = "sae-cliff-core",
    -- The basins hold radiant brine; the band above the waterline is the
    -- shore, in lit crust, so each body is ringed by the glow. Twelve units
    -- of the basin term is a ring about three tiles wide (four gave one).
    -- Level 76 is 6-30% brine over the rig's region by seed, 15% in the middle.
    pool        = { level = 76, shore = 12 },
    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-white-dirt-1", "mineral-white-dirt-2", "mineral-white-dirt-3",
      "mineral-white-sand-1", "mineral-white-sand-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-blue-heat-3", "volcanic-blue-heat-4"
    }
  },

  ["scoured-nickel"] =
  {
    temperature = { centre = 16, amplitude = 24, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- Grey-to-black body, and the range starts above white dirt's window
    -- (0.15 +/- 0.15) on purpose: a render centred at 0.52 let white in as
    -- continents covering a quarter of the ground. Pale here comes only from
    -- the plates term below. Orange heat wants aux below 0.7 and blue above
    -- 0.8, so seams come out a mix of the two -- and neither glows: Alien
    -- Biomes' heat tiles carry no light, so at night a seam is a black line.
    -- Lit fissures need the Core's own tile art.
    aux         = { centre = 0.58, amplitude = 0.26, octaves = 3, persistence = 0.5, scale = 340 },
    -- Bare plates: a short-wavelength noise whose peaks pull aux down toward
    -- white dirt's 0.15 window, in patches a few tiles across.
    plates      = { threshold = 0.45, drop = 1.2, octaves = 2, persistence = 0.6, scale = 48, seed = 7781 },

    decoratives = {},
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium", "snow", "ice", "frost" },

    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "mineral-white-dirt-1", "mineral-white-dirt-3",
      "mineral-grey-sand-1", "mineral-grey-sand-3",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2", "volcanic-purple-heat-1"
    }
  },

  ["frosted-iron"] =
  {
    -- Centre 14, swing 30: mostly inside the dirts' 0..30, dipping under zero
    -- for frost about a third of the time. The veins are the zero contours of
    -- a second noise: within `width` of a crossing, temperature climbs by up
    -- to `gain` * width -- +120 here -- into the orange heat's window. Contours
    -- always exist, so the seams always appear; a peak-above-threshold version
    -- gave 3% heat on one seed and none at all on the next.
    -- Three renders in: amplitude 30 put a quarter of one seed under frost,
    -- width 0.06 put 7% of the ground in the heat window. Both narrowed.
    temperature = { centre = 16, amplitude = 26, octaves = 2, persistence = 0.5, scale = 480 },
    veins       = { width = 0.035, gain = 3500, octaves = 2, persistence = 0.5, scale = 380, seed = 4471 },
    -- Dirt wants 0.5 +/- 0.1; sand wants 0.2 +/- 0.2. A 0.14 swing keeps it
    -- dirt with the odd sand flat.
    -- First render: 0.50 +/- 0.14 gave 38% sand, a paler ground than the brief.
    moisture    = { centre = 0.55, amplitude = 0.10, octaves = 3, persistence = 0.5, scale = 260 },
    -- Aux is the colour axis: white at 0.15, grey at 0.5, black at 0.85. Leaning
    -- past the middle keeps white dirt rare (23% in the first render) and lets
    -- black through, which is where the brief's dark metal comes from.
    aux         = { centre = 0.58, amplitude = 0.32, octaves = 3, persistence = 0.5, scale = 340 },

    -- Craters and frost only; the brown volcanic rocks, sulfur crusts and
    -- Fulgora stones are what made the other four read as borrowed ground.
    decoratives = { "snow", "frost" },
    -- "vulcanus" as well as "volcanic": the large rock decal is named after the
    -- planet. And Aquilo's lithium icebergs answer to "ice" -- 56,000 of them in
    -- 256 chunks on the first render, on a world with no lithium.
    refuse      = { "volcanic", "vulcanus", "sulfur", "fulgora", "lithium" },

    tiles = {},
    without_pack = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-cracks" },
    alien_tiles =
    {
      -- No white dirt: on one seed it covered a third of the ground and read as
      -- a snowfield. The pale in this palette is frost, in patches, on metal.
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-black-dirt-1", "mineral-black-dirt-2",
      "mineral-grey-sand-1", "mineral-grey-sand-3",
      "frozen-snow-0", "frozen-snow-1", "frozen-snow-3",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2"
    }
  },

  -- Grey worked metal, cool unlit cracks, and a rare scorch where the dead
  -- dynamo still earths itself. The accent is electrical rather than molten,
  -- which ties the ground to the arc storms instead of to volcanism, and keeps
  -- the Core from reading as a second Vulcanus.
  ["struck-nickel"] =
  {
    -- Cool base, tall peaks: the centre sits far below the heat tiles' window
    -- so glowing ground is the exception, and the long input scale gathers what
    -- little there is into veins rather than scattering it as speckle.
    temperature = { centre = 30, amplitude = 90, octaves = 2, persistence = 0.45, scale = 520 },
    moisture    = { centre = 0.50, amplitude = 0.16, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.35, amplitude = 0.20, octaves = 3, persistence = 0.5, scale = 300 },

    -- Nothing warm-looking scattered on it: the ground is cold worked metal,
    -- and the only heat on this world should be the heat the player made.
    decoratives = {},

    tiles       = { "volcanic-cracks", "volcanic-ash-dark", "volcanic-ash-flats" },
    alien_tiles =
    {
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-grey-sand-1", "mineral-grey-sand-3",
      "mineral-white-dirt-1", "mineral-white-dirt-3",
      "volcanic-blue-heat-1", "volcanic-blue-heat-2",
      "volcanic-purple-heat-1"
    }
  },

  -- Black and grey ground, dark ash, and no lit tile anywhere: heat exists on
  -- this world only where the player has built for it. The darkest of the four,
  -- and the one belts and foundries stand out hardest against.
  ["iron-crust"] =
  {
    -- Capped below the heat window on purpose -- nothing here should ever glow.
    temperature = { centre = 35, amplitude = 35, octaves = 3, persistence = 0.55, scale = 340 },
    moisture    = { centre = 0.50, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.30, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 300 },

    decoratives = { "ash" },

    tiles       = { "volcanic-ash-dark", "volcanic-ash-flats", "volcanic-ash-cracks" },
    alien_tiles =
    {
      "mineral-black-dirt-1", "mineral-black-dirt-2", "mineral-black-dirt-3",
      "mineral-grey-dirt-1", "mineral-grey-dirt-2", "mineral-grey-dirt-3",
      "mineral-grey-sand-1"
    }
  },

  -- The design document's own sentence, made visible: a frozen crust over a
  -- still-hot interior. Cold ground in the majority, cut by hot veins where the
  -- interior comes close -- which is terrain that tells the player something.
  ["frozen-crust"] =
  {
    -- The widest swing of the four, so both ends of the tile range are reached:
    -- frozen ground at the troughs, lit cracks at the peaks, and the long scale
    -- keeps each of them a region rather than a fleck.
    temperature = { centre = 25, amplitude = 100, octaves = 2, persistence = 0.5, scale = 600 },
    moisture    = { centre = 0.45, amplitude = 0.22, octaves = 3, persistence = 0.5, scale = 280 },
    aux         = { centre = 0.40, amplitude = 0.22, octaves = 3, persistence = 0.5, scale = 300 },

    decoratives = { "snow", "frozen", "ice" },

    tiles       = { "volcanic-cracks", "volcanic-cracks-warm", "volcanic-ash-dark" },
    alien_tiles =
    {
      "frozen-snow-0", "frozen-snow-1", "frozen-snow-3",
      "mineral-grey-sand-1", "mineral-grey-sand-3", "mineral-grey-dirt-1",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2"
    }
  },

  -- Ash and lit cracks, hot everywhere. The most dramatic and the least
  -- distinct: it is Vulcanus's palette, and orange ground competes with the arc
  -- flashes, which are the surface's actual event.
  ["ashen-furnace"] =
  {
    -- Centred inside the heat window rather than below it, which is what makes
    -- lit ground common instead of rare.
    temperature = { centre = 85, amplitude = 45, octaves = 3, persistence = 0.55, scale = 300 },
    moisture    = { centre = 0.35, amplitude = 0.18, octaves = 3, persistence = 0.5, scale = 260 },
    aux         = { centre = 0.45, amplitude = 0.20, octaves = 3, persistence = 0.5, scale = 300 },

    decoratives = { "ash", "cinder", "lava" },

    tiles =
    {
      "volcanic-ash-dark", "volcanic-ash-light", "volcanic-ash-flats",
      "volcanic-ash-cracks", "volcanic-cracks", "volcanic-cracks-warm",
      "volcanic-orange-heat-1", "volcanic-orange-heat-2",
      "volcanic-orange-heat-3", "volcanic-orange-heat-4"
    },
    alien_tiles =
    {
      "mineral-black-dirt-1", "mineral-black-dirt-3",
      "mineral-grey-dirt-1"
    }
  },

}

local palette = palettes[PALETTE]
if not palette then
  error("prototypes/core/map-gen.lua: unknown PALETTE '" .. tostring(PALETTE) .. "'")
end

-- Alien Biomes' temperature scale is far wider than vanilla's -- its orange
-- heat tiles peak at 110, where vanilla's whole range stops well short of that.
-- The clamp keeps every palette inside the band the tiles actually cover, so a
-- tall amplitude buys rare extremes rather than ground no tile answers for.
local TEMPERATURE_RANGE = { -15, 125 }

local function noise(field, seed)
  -- `stretch` squeezes the noise along y, so a field of blobs becomes a field
  -- of bands -- the crystalline banding of a cut meteorite.
  return string.format(
    "multioctave_noise{x = x,\z
                       y = y * %s,\z
                       seed0 = map_seed,\z
                       seed1 = %d,\z
                       octaves = %d,\z
                       persistence = %s,\z
                       input_scale = 1/%d,\z
                       output_scale = 1}",
    field.stretch or 1, seed, field.octaves, field.persistence, field.scale)
end

-- The plates' driving noise, optionally feathered: a second, short-wavelength
-- noise added before the threshold breaks the plate's contour into fingers and
-- islands instead of a smooth blob, which is most of what makes an edge read
-- as ground rather than as a stencil.
local function plate_noise(pl)
  local n = noise(pl, pl.seed)
  if pl.feather then
    local f = pl.feather
    n = string.format("(%s + %s * %s)", n, f.amplitude, noise(f, f.seed or (pl.seed + 1)))
  end
  return n
end

-- A palette's `dark` term: a 0..1 mask of some SHAPE, laid onto the colour
-- axis by `amount`, so that inside the shape a different tile answers -- on a
-- white cold body, +0.72 lands on black dirt. The shapes:
--   hollows   blobs above a threshold of a noise
--   rims      a band either side of that threshold: rings, interiors untouched
--   cracks    a band about the noise's zero contours: a fracture network
--   cells     the borders of a Voronoi tiling, thin: a crazed, jointed crust
--   plates    the same borders from the pyramid noise, joints as wide as `width`
--   craters   the centres of a Voronoi tiling: round pits, sized by the grid
--   basins    below an elevation contour: dark low ground the cliffs already bound
--   gradient  by distance from the landing site: the crust darkens outward
-- `stretch` and `feather` apply to the noise-driven shapes as they do to plates.
local function dark_mask(dk)
  local n = dk.scale and noise(dk, dk.seed or 9931) or nil
  if n and dk.feather then
    local f = dk.feather
    n = string.format("(%s + %s * %s)", n, f.amplitude, noise(f, f.seed or 9932))
  end
  local shape = dk.shape
  if shape == "hollows" then
    return string.format("clamp((%s - %s) * %s, 0, 1)", n, dk.threshold, dk.sharpness or 8)
  elseif shape == "rims" then
    return string.format("clamp((%s - abs(%s - %s)) / %s * 3, 0, 1)", dk.width, n, dk.threshold, dk.width)
  elseif shape == "cracks" then
    return string.format("clamp((%s - abs(%s)) / %s * 3, 0, 1)", dk.width, n, dk.width)
  elseif shape == "cells" then
    return string.format("clamp((%s - voronoi_facet_noise{x = x, y = y, seed0 = map_seed, seed1 = %d, grid_size = %s, distance_type = 'euclidean', jitter = %s}) / %s, 0, 1)",
      dk.width, dk.seed or 9933, dk.grid, dk.jitter or 0.8, dk.width)
  elseif shape == "plates" then
    -- The pyramid noise is 1 at a cell's centre and falls to 0 at its border,
    -- so "below width" is the joint between plates. (Measured: the first cut
    -- assumed the opposite and drew the joints while asking for pits.)
    return string.format("clamp((%s - voronoi_pyramid_noise{x = x, y = y, seed0 = map_seed, seed1 = %d, grid_size = %s, distance_type = 'euclidean', jitter = %s}) / %s, 0, 1)",
      dk.width, dk.seed or 9934, dk.grid, dk.jitter or 0.8, dk.width)
  elseif shape == "craters" then
    -- Measured, not documented: the pyramid noise peaks near 0.25 at a cell's
    -- centre, so `level` is a value on that scale (0.15 gives pits about half
    -- a cell wide) and `sharpness` hardens the pit's edge.
    return string.format("clamp((voronoi_pyramid_noise{x = x, y = y, seed0 = map_seed, seed1 = %d, grid_size = %s, distance_type = 'euclidean', jitter = %s} - %s) * %s, 0, 1)",
      dk.seed or 9934, dk.grid, dk.jitter or 0.8, dk.level, dk.sharpness or 30)
  elseif shape == "basins" then
    return string.format("clamp((%s - sae_core_elevation) / %s, 0, 1)", dk.level, dk.softness or 12)
  elseif shape == "gradient" then
    return string.format("clamp((distance - %s) / %s, 0, 1)", dk.from, dk.over)
  end
  error("map-gen: unknown dark shape " .. tostring(shape))
end

-- Where the palette's pool lies, as a 0..1 mask, so the crust's own shapes
-- can stop at the waterline: a liquid is not jointed.
local function pool_mask(pal)
  if not pal.pool then return "0" end
  return string.format("clamp((%s - sae_core_basin) * 4, 0, 1)", pal.pool.level + pal.pool.shore)
end

local function clamped(field, seed, low, high)
  return string.format("clamp(%s + %s * %s, %s, %s)",
    field.centre, field.amplitude, noise(field, seed), low, high)
end

-- Temperature, with a palette's hot veins added if it has them: along the
-- zero contours of a second noise, within `width` of the crossing, up to
-- `gain` * `width` degrees are laid on top -- so a cold crust still reaches
-- the heat tiles' window along a few thin seams.
-- The colour axis, with a palette's bare plates cut into it if it has them: a
-- short-wavelength noise whose peaks above `threshold` pull aux down by up to
-- `drop`, so small patches land in the pale tiles' window without the whole
-- region going pale.
local function aux_expression(pal, seed)
  local base = string.format("%s + %s * %s", pal.aux.centre, pal.aux.amplitude, noise(pal.aux, seed))
  if pal.plates then
    local p = pal.plates
    base = string.format("%s - max(0, %s - %s) * %s", base, plate_noise(p), p.threshold, p.drop)
  end
  if pal.dark then
    base = string.format("%s + %s * %s * (1 - %s)", base, pal.dark.amount, dark_mask(pal.dark), pool_mask(pal))
  end
  -- A seam may carry its own colour: `veins.aux` shifts the colour axis along
  -- the same contours the temperature spike follows, so a seam can land on a
  -- heat colour the body's aux would never reach -- blue seams through white.
  if pal.veins and pal.veins.aux then
    local v = pal.veins
    base = string.format("%s + max(0, %s - abs(%s)) / %s * %s", base, v.width, noise(v, v.seed), v.width, v.aux)
  end
  return string.format("clamp(%s, 0, 1)", base)
end

local function temperature_expression(pal, seed, low, high)
  local base = string.format("%s + %s * %s", pal.temperature.centre,
    pal.temperature.amplitude, noise(pal.temperature, seed))
  if pal.veins then
    local v = pal.veins
    base = string.format("%s + max(0, %s - abs(%s)) * %s", base, v.width, noise(v, v.seed), v.gain)
  end
  -- Plates may warm as well as pale: the mid-temperature colours (cream,
  -- beige, dustyrose, aubergine) sit in a 30..60 window a cold body never
  -- reaches, so a plate that wants one of them lifts its own temperature.
  -- `warm_threshold`, if higher than `threshold`, makes the temperature climb
  -- inside a band where the colour axis has already moved: the tile that answers
  -- to the new axis at the OLD temperature appears as a rim around the plate --
  -- the cold band's black around a blue-heat plate on white.
  if pal.plates and pal.plates.warm then
    local pl = pal.plates
    base = string.format("%s + max(0, %s - %s) * %s", base, plate_noise(pl), pl.warm_threshold or pl.threshold, pl.warm)
  end
  return string.format("clamp(%s, %s, %s)", base, low, high)
end

data:extend({
  {
    -- Where the crust's lit cracks go: the palette's dark shape, scaled so it
    -- beats every ground tile where the mask is strong and loses where it is
    -- weak -- so a joint is black dirt at its edges and lit down its centre.
    -- The floor is deep for the reason the pool's is (below); at -1.2 the glow
    -- tile won along the heat seams, where ground tiles go negative.
    -- Palettes without `glow` set it below every tile, so it never places.
    type = "noise-expression",
    name = "sae_core_glow",
    expression = (palette.glow and palette.dark)
      and string.format("(%s + 8) * %s * (1 - %s) - %s - 8", palette.glow.gain or 3, dark_mask(palette.dark), pool_mask(palette), palette.glow.cut or 1.2)
      or "-1000"
  },
  {
    -- Where the brine lies: a noise of its own, not the elevation's broad
    -- term. Tied to that term (520 tiles, then 320) the sea was one basin
    -- wider than the whole region the rig looks at, and the landing site came
    -- out under 0%, 45%, 72% or 98% brine by seed. At 160 tiles the pool is
    -- bodies -- lakes a hundred tiles across, several in any region -- and
    -- the share barely moves between seeds. The last term lifts the crust
    -- around the landing site, as Nauvis does, so nobody lands in the brine:
    -- the full lift out to 32 tiles, gone by 96.
    type = "noise-expression",
    name = "sae_core_basin",
    expression = "140 + 90 * multioctave_noise{x = x,\z
                                               y = y,\z
                                               seed0 = map_seed,\z
                                               seed1 = 8419,\z
                                               octaves = 3,\z
                                               persistence = 0.5,\z
                                               input_scale = 1/80,\z
                                               output_scale = 1}\z
                  + 40 * clamp((96 - distance) / 64, 0, 1)"
  },
  {
    -- The radiant pool fills the basins: below `level` on the basin term it
    -- beats every ground tile outright, and a `shore`-wide band above it is the
    -- buildable rim. Palettes without `pool` place neither.
    --
    -- The floors are deep on purpose. The engine places the tile with the
    -- highest probability even when every probability is negative, and along
    -- the seams and joints every ground tile IS negative -- the temperature
    -- spike and the colour shift push them out of their windows. A floor of -1
    -- won there, and the sea came out jointed; measured with
    -- calculate_tile_properties, which said "pool" at none of 961 samples while
    -- 157 of them were pool.
    type = "noise-expression",
    name = "sae_core_pool",
    expression = palette.pool
      and string.format("clamp((%s - sae_core_basin) * 4, 0, 1) * 16 - 10", palette.pool.level)
      or "-1000"
  },
  {
    -- The shore has no ramp on its inner side: it holds 5 right down to the
    -- waterline and lets the pool's 6 take over below it. A ramp there gave
    -- the ground tiles the last tile before the liquid, and the sea was rimmed
    -- in white dirt with no lip drawn, since the ground art knows no pool.
    type = "noise-expression",
    name = "sae_core_shore",
    expression = palette.pool
      and string.format("clamp((%s - sae_core_basin) * 4, 0, 1) * 15 - 10",
                        palette.pool.level + palette.pool.shore)
      or "-1000"
  },
  {
    type = "noise-expression",
    name = "sae_core_temperature",
    expression = temperature_expression(palette, 2291, TEMPERATURE_RANGE[1], TEMPERATURE_RANGE[2])
  },
  {
    type = "noise-expression",
    name = "sae_core_moisture",
    -- Not water: on Alien Biomes' scale this is one of the axes a tile picks
    -- itself by, and the mineral grounds want the middle of it. Measured: at
    -- 0.06 -- the honest figure for a world where no water has ever been --
    -- nothing but snow qualified.
    expression = clamped(palette.moisture, 771, 0, 1)
  },
  {
    type = "noise-expression",
    name = "sae_core_aux",
    -- Aux is the axis the mineral grounds separate their colours along, so this
    -- is what decides grey against black against white within a palette.
    expression = aux_expression(palette, 5183)
  },
  {
    type = "noise-expression",
    name = "sae_core_elevation",
    -- Always well above zero: a crust with relief, and no coastline anywhere.
    -- Shared by every palette; the look is in the climate, not the shape.
    --
    -- Two scales of relief. The first cut was one noise at 55 over a cliff
    -- interval of 40, which drew a cliff line every few hundred tiles and read
    -- as flat. A broad term now carries the big rises and falls, a finer one
    -- the local steps, and the cliff interval is tightened -- so the crust
    -- terraces, the way a fractured metal surface would.
    expression = "140 + 90 * multioctave_noise{x = x,\z
                                               y = y,\z
                                               seed0 = map_seed,\z
                                               seed1 = 8417,\z
                                               octaves = 3,\z
                                               persistence = 0.55,\z
                                               input_scale = 1/520,\z
                                               output_scale = 1}\z
                  + 35 * multioctave_noise{x = x,\z
                                           y = y,\z
                                           seed0 = map_seed,\z
                                           seed1 = 8418,\z
                                           octaves = 4,\z
                                           persistence = 0.6,\z
                                           input_scale = 1/140,\z
                                           output_scale = 1}"
  }
})

local function core_tiles()
  local settings, found = {}, 0

  local function add(list)
    for _, name in pairs(list or {}) do
      if data.raw.tile[name] then
        settings[name] = {}
        found = found + 1
      end
    end
  end

  add(palette.tiles)
  if mods["alien-biomes"] then
    add(palette.alien_tiles)
  else
    -- A palette that leans on the pack says what it wears without it.
    add(palette.without_pack)
  end

  -- Only if a palette somehow contributed nothing at all: vanilla's Aquilo
  -- ground is the wrong colour for this place, but it is ground.
  if found == 0 then
    add({ "snow-flat", "snow-crests", "snow-lumpy", "snow-patchy",
          "ice-rough", "ice-smooth" })
  end

  -- The radiant pool and its shore, when the palette carries them.
  if palette.pool then
    settings["sae-radiant-pool"] = {}
    settings["sae-radiant-shore"] = {}
  end

  -- The lit cracks, when the palette asks for them, in the colour it asks for.
  if palette.glow then
    settings[palette.glow.colour == "arc" and "sae-crust-glow-arc" or "sae-crust-glow"] = {}
  end

  -- The crust vent is ours and always present, whatever tile pack is installed.
  -- It has to be listed here or it never places at all: a planet's
  -- `autoplace_settings["tile"]` is a whitelist, and a tile absent from it is
  -- excluded no matter what its own autoplace says. Measured: sixteen chunks
  -- generated exactly zero vents until this line existed.
  settings["sae-crust-vent"] = {}

  return settings
end

-- Rock and mineral scatter.
--
-- Selected by name pattern rather than by list, because the decorative names
-- are the one part of an optional pack that cannot be checked from outside the
-- game -- and a list of guesses would fail silently, which is exactly the
-- failure this file has already had once. A pattern asks data.raw what exists
-- instead of telling it.
--
-- Two filters do the work beyond the patterns. Only decoratives that actually
-- carry an autoplace are enabled, since one without it would sit in the
-- settings doing nothing and inflate the count that reports success. And every
-- palette's climate still has the final say: a decorative places only where its
-- own conditions are met, so listing the whole rock family gets the grey ones
-- on struck-nickel and the ash ones on ashen-furnace without either being
-- named. That is the same mechanism the tiles use, and it is why this is safe
-- to cast wide.
--
-- Decoratives only. The big rocks are simple-entities rather than decoratives,
-- and vanilla's are refused here on purpose: they yield stone and coal, and a
-- world whose whole point is that it has no carbon should not have coal lying
-- on the ground to be picked up. The Core has its own boulder instead --
-- sae-core-boulder, in resources.lua -- which is enabled through the entity
-- settings below, where an autoplaced entity belongs.
local DECORATIVE_WANTED =
{
  -- The Core's own shards first; the rest are the pack's, by family.
  "sae-crust",
  "rock", "stone", "pebble", "boulder", "gravel", "mineral", "crater", "pumice"
}

-- Nothing that ever lived. The Core has no organics at all, so a stray tuft of
-- grass would contradict the planet rather than decorate it -- and vanilla's
-- decorative names are not tidily separated by planet, so this list is what
-- keeps Nauvis and Gleba off the surface.
local DECORATIVE_REFUSED =
{
  "grass", "plant", "tree", "flower", "bush", "shrub", "fungus", "moss",
  "lichen", "weed", "garballo", "carpet", "leaf", "root", "vegetation",
  "water", "mud", "puddle", "oil", "scrap", "egg", "nest", "spawn"
}

local function matches_any(name, patterns)
  for _, pattern in pairs(patterns) do
    if string.find(name, pattern, 1, true) then return true end
  end
  return false
end

local function core_decoratives()
  local wanted, refused = {}, {}
  for _, pattern in pairs(DECORATIVE_WANTED) do wanted[#wanted + 1] = pattern end
  for _, pattern in pairs(palette.decoratives or {}) do wanted[#wanted + 1] = pattern end
  for _, pattern in pairs(DECORATIVE_REFUSED) do refused[#refused + 1] = pattern end
  for _, pattern in pairs(palette.refuse or {}) do refused[#refused + 1] = pattern end

  local settings = {}
  -- 2.0 renamed the type: decoratives are `optimized-decorative` in data.raw.
  -- Under the old key this loop ran over nothing and the ground stayed bare.
  for name, decorative in pairs(data.raw["optimized-decorative"] or {}) do
    if decorative.autoplace
       and matches_any(name, wanted)
       and not matches_any(name, refused) then
      settings[name] = {}
    end
  end

  return settings
end

local function settings()
  local controls =
  {
    ["sae-kamacite-ore"] = {},
    ["sae-melt-vent"] = {},
    ["sae-gas-vent"] = {},
    ["sae-core-rock"] = {}
  }
  for name, setting in pairs(palette.controls or {}) do controls[name] = setting end
  return
  {
    property_expression_names =
    {
      elevation = "sae_core_elevation",
      temperature = "sae_core_temperature",
      moisture = "sae_core_moisture",
      aux = "sae_core_aux",
      cliffiness = "cliffiness_basic",
      cliff_elevation = "cliff_elevation_from_elevation"
    },
    -- Which cliff the cliffiness above places. Vanilla planets each name their
    -- own; the Core has none yet, so this states the default that was being
    -- taken silently -- Nauvis's cliff, at Nauvis's spacing -- rather than
    -- leaving it implied. A metallic ridge of the Core's own is outstanding.
    cliff_settings =
    {
      -- A palette may name the cliff that suits its ground; Nauvis's sandstone
      -- is the default the engine was taking anyway.
      name = palette.cliff or "cliff",
      cliff_elevation_0 = 10,
      cliff_elevation_interval = 28,
      richness = 1
    },
    -- Palettes may carry extra controls: the Vulcanus tile set reads
    -- `vulcanus_volcanism`'s frequency to size its biomes, and turning it up is
    -- the only lever on how big its flats come out.
    autoplace_controls = controls,
    autoplace_settings =
    {
      ["tile"] = { settings = core_tiles() },
      ["decorative"] = { settings = core_decoratives() },
      ["entity"] =
      {
        settings =
        {
          ["sae-kamacite-ore"] = {},
          ["sae-melt-vent"] = {},
          ["sae-gas-vent"] = {},
          ["sae-core-boulder"] = {}
        }
      }
    }
  }
end

-- The planet takes `settings()`; resources.lua reads `palette` for the boulder's
-- tint, so the rock on the ground matches the ground it lies on.
return { settings = settings, palette = palette }
