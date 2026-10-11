-- Deriving a prototype from a vanilla one, without dragging its life along.
--
-- Every building in this mod that starts as a `table.deepcopy` has, at some
-- point, shipped something that belonged to the machine it was copied from. The
-- B3 audit found nine separate instances of it and they were all the same shape:
-- a field nobody looked at, describing machinery the new building does not have,
-- silently correct enough to load.
--
-- What that audit found, and what this file exists to stop happening again:
--
--   * The Ignition Array kept the rocket silo's crafting animation -- an engine
--     and two steam plumes, on a world where nothing burns -- plus its launch
--     alarms, its clamp sounds and its Aquilo frozen sprites.
--   * The Whisker Plant was called "Tree". An inherited `localised_name` beats
--     the locale file, so strings.cfg said one thing and the game said another.
--   * The Arc Mast's Factoriopedia page built a vanilla lightning collector and
--     struck it with vanilla lightning, because the preview is a *script* that
--     names its entities.
--   * The Bed Tender vented spores and the Vent Pump vented pollution, on a
--     planet that sets no `pollutant_type` at all.
--   * The Coil Separator arrived with the electromagnetic plant's **+50% base
--     productivity**, because `effect_receiver` is inherited and invisible.
--     That one was caught by reviewing a dump of this very file's output.
--
-- None of it was visible from the Lua. All of it was visible in a data dump.
--
-- `derive` clears each of those classes up front, so a new building starts from
-- the vanilla art and nothing else. What it does *not* touch is the stuff that
-- is legitimate to reuse: open/close and working sounds, corpses and
-- explosions. Reusing vanilla audio is ordinary modding.
--
-- Two inherited fields are left alone on purpose, and each building checks them
-- itself:
--
--   * `heating_energy` -- vanilla sets it on nearly every entity for Aquilo's
--     sake. Nothing here can stand on Aquilo, so it never fires, and stripping
--     it would make our prototypes the odd ones out for no gain.
--   * `circuit_connector` -- its sprites are placed for the *source's*
--     footprint. Right when the footprint is kept, wrong when it is not (the
--     Gas Pump is 2x2 on a 3x3 pumpjack's connector), and only the building's
--     own file knows which.

local derive = {}

--- Copy a vanilla prototype and strip what belongs to the original.
--- @param base_type string   the data.raw key, e.g. "assembling-machine"
--- @param base_name string   the vanilla prototype to copy
--- @param new_name  string   this mod's name for it
function derive.from(base_type, base_name, new_name)
  local p = table.deepcopy(data.raw[base_type][base_name])
  assert(p, base_type .. "/" .. base_name .. " does not exist")
  p.name = new_name

  -- The locale trap. A hardcoded localised name silently beats strings.cfg, so
  -- a building can carry the wrong name for its whole life without a warning.
  p.localised_name = nil
  p.localised_description = nil

  -- Upgrade planners and fast-replace should never bridge a vanilla machine and
  -- a Core one: they are not tiers of each other.
  p.next_upgrade = nil
  p.fast_replaceable_group = nil

  -- The Factoriopedia preview is a script that names the entity it builds, so
  -- inherited it shows the *vanilla* machine on this building's own page.
  p.factoriopedia_simulation = nil

  -- Aquilo's second, iced copy of the building. Every machine here is locked to
  -- pressure ranges that exclude Aquilo, so these can never draw correctly.
  for _, k in ipairs({ "frozen_patch", "graphics_set_frozen" }) do
    p[k] = nil
  end

  -- A silhouette mirrored in water, for a set of buildings on worlds with none.
  p.water_reflection = nil

  -- A built-in effect bonus belongs to the machine it was designed for, and it
  -- is invisible in Lua. Found by review rather than by reading: the Coil
  -- Separator, copied from the electromagnetic plant for its art, silently
  -- carried that plant's **+50% base productivity** into the Core's endgame.
  -- Nothing in the file said so; it took a data dump to see it.
  p.effect_receiver = nil

  -- The Core sets no `pollutant_type`, and neither do platforms, so an inherited
  -- emissions figure is a tooltip line about an atmosphere that is not there.
  if p.energy_source then
    p.energy_source.emissions_per_minute = nil
  end

  -- A plume of exhaust belongs to the combustion that made it. The steam
  -- turbine's `smoke` rode along on the Crust Turbine for months -- a steam
  -- cloud on a world with no air -- and was only seen in a data dump.
  p.smoke = nil

  return p
end

--- Copy a vanilla tile and strip what belongs to the original.
---
--- A tile carries less life than a machine, but what it carries is worse: the
--- two Core tiles were cut from `stone-path` and kept its `frozen_variant`, so a
--- vent could freeze over into a paving slab; its **+30% walking speed**, so a
--- bed of grit was a footpath; and its `artificial-tiles` filing, so a natural
--- vent sat in the menu beside concrete. The terrain sheets and the sounds are
--- what the copy is for -- a tile is three sheets, sixteen variants and five
--- transition groups that have to seam against every neighbour, and vanilla's
--- already do -- so those are kept and everything that says *stone path* goes.
---
--- The caller then says what the tile *is*: its `subgroup`, `order`,
--- `layer_group`, and `minable` if a player can lift it.
--- @param base_name string  the vanilla tile to copy
--- @param new_name  string  this mod's name for it
function derive.tile_from(base_name, new_name)
  local t = table.deepcopy(data.raw.tile[base_name])
  assert(t, "tile/" .. base_name .. " does not exist")
  t.name = new_name
  t.localised_name = nil
  t.localised_description = nil
  -- Aquilo's iced twin of the original, which would draw the wrong tile.
  t.frozen_variant = nil
  -- What made the original a floor rather than ground.
  t.minable = nil
  t.mined_sound = nil
  t.build_sound = nil
  t.walking_speed_modifier = nil
  t.decorative_removal_probability = nil
  -- Where it sat in the menu; the caller files it.
  t.subgroup = nil
  t.order = nil
  return t
end

--- Prototypes still wearing somebody else's sprites, by name.
---
--- **Recorded rather than logged on the spot, and that is the fix.** This used
--- to log the moment it was called, which is before the building's own plates
--- are attached -- so five buildings that had shipped art were still announcing
--- themselves as placeholders at every load, and the one thing this log exists
--- for (grep finds every one of them) had quietly stopped being true.
--- `derive.own_graphics` strikes a name off, and `derive.log_placeholders`
--- reports whoever is left at the end of the data stage.
derive.pending = {}

--- Point a machine at another prototype's art, deliberately and visibly.
---
--- Stand-in art is not the same thing as an inherited leftover: the Vent Pump
--- wears the pumpjack's sprites on purpose and says so. This marks that choice
--- in one place so a later audit can find every building still wearing borrowed
--- art by grepping for one call rather than by eye.
--- @param p     table   the prototype
--- @param note  string  why, for the reader
function derive.placeholder_art(p, note)
  derive.pending[p.name] = note
  return p
end

--- Log the buildings that finished the data stage still wearing borrowed art.
--- Called last from data.lua, once everything has had its chance to replace it.
function derive.log_placeholders()
  local names = {}
  for name in pairs(derive.pending) do names[#names + 1] = name end
  table.sort(names)
  for _, name in ipairs(names) do
    log("[sae] placeholder art: " .. name .. " -- " .. derive.pending[name])
  end
  log("[sae] " .. #names .. " prototype(s) still wear borrowed sprites")
end

--- Give a derived machine its own graphics set, and take the old one's audio
--- cues with the art they were cued to.
---
--- `working_sound.sound_accents` name the working visualisation each accent
--- plays for -- `play_for_working_visualisation = "warm-up"`, and a frame number
--- to fire on. The names refer to the *vanilla* set, so the moment a derived
--- machine replaces `graphics_set` the accents point at animations that no
--- longer exist, and the game refuses to load:
---
---     Error while loading entity prototype "sae-coil-separator"
---     (assembling-machine): Working visualisation "warm-up" doesn't exist
---
--- The Ignition Array hit exactly this with the rocket silo's welder accents and
--- it was fixed there by hand. It is not a one-off: it is what happens to every
--- building in this file the day its plate arrives, so it belongs here.
---
--- `main_sounds` are gated the same way, through
--- `play_for_working_visualisations`, and that is the half that is easy to miss:
--- the electromagnetic plant's warm-up, loop and cool-down are each tied to a
--- named vanilla animation, so clearing only the accents leaves the load error
--- exactly where it was.
---
--- Both are stripped here. A gated sound cannot survive the art it was cued to,
--- and the alternative -- ungating them -- plays a warm-up, a loop and a
--- cool-down all at once, for ever. If a derived machine should hum, its own
--- file says so explicitly, which is better than inheriting three loops and
--- hoping.
--- @param p table            the prototype
--- @param set table          its new graphics_set
function derive.own_graphics(p, set)
  p.graphics_set = set
  -- This building has its own art now, so it is no longer a placeholder.
  derive.pending[p.name] = nil
  -- The ground decal under the vanilla machine was drawn for the vanilla plate.
  -- The Ballast Drill shipped the big mining drill's for a while, under a plate
  -- that draws its own base.
  p.integration_patch = nil
  p.integration_patch_render_layer = nil
  local ws = p.working_sound
  if ws then
    ws.sound_accents = nil
    if ws.main_sounds then
      local kept = {}
      for _, sound in ipairs(ws.main_sounds) do
        if sound.play_for_working_visualisations == nil
           and sound.play_for_working_visualisation == nil then
          kept[#kept + 1] = sound
        else
          log("[sae] " .. p.name .. ": dropped a working sound cued to a "
              .. "vanilla working visualisation")
        end
      end
      ws.main_sounds = #kept > 0 and kept or nil
    end
    if ws.main_sounds == nil and ws.sound == nil then p.working_sound = nil end
  end
  return p
end

-- The length of one animation cycle, in frames: what an accent's `frame` counts
-- in. `frame_sequence` replaces the sheet's order and so its length, and
-- `repeat_count` stretches a layer to a longer cycle (AnimationParameters, in
-- the prototype docs); the layers of one animation share one clock, so the
-- cycle is the longest layer's. That an accent's frame counts in that cycle,
-- a sequence's frames rather than the sheet's, is an assumption no client has
-- measured; every vanilla accent, 67 on 12 machines, passes the check below
-- counted this way (2026-10-11).
local function cycle_frames(anim)
  if anim.layers then
    local most = 0
    for _, layer in ipairs(anim.layers) do
      most = math.max(most, cycle_frames(layer))
    end
    return most
  end
  local frames = anim.frame_sequence and #anim.frame_sequence or anim.frame_count or 1
  return frames * (anim.repeat_count or 1)
end

local DIRECTIONS = { "north", "east", "south", "west" }

-- What an accent can be cued to on one graphics set, by the name it is cued
-- with, each as a list of { direction, frames }. The main animation is filed
-- under `false`, since an accent cued to it names no visualisation. Also how
-- many working visualisations have no `name`, which nothing can be cued to.
--
-- The main animation is an Animation4Way: a plain Animation for every
-- direction, or one per direction, a missing one falling back to north. A
-- working visualisation carries `animation` for every direction or
-- `<direction>_animation` for each.
local function cue_targets(set)
  local targets, unnamed = {}, 0
  local main = set.animation
  if main then
    local frames = {}
    if main.north then
      for _, d in ipairs(DIRECTIONS) do
        frames[#frames + 1] = { d, cycle_frames(main[d] or main.north) }
      end
    else
      frames[1] = { "every direction", cycle_frames(main) }
    end
    targets[false] = frames
  end
  for _, vis in ipairs(set.working_visualisations or {}) do
    if vis.name then
      local frames = {}
      if vis.animation then
        frames[#frames + 1] = { "every direction", cycle_frames(vis.animation) }
      end
      for _, d in ipairs(DIRECTIONS) do
        local anim = vis[d .. "_animation"]
        if anim then frames[#frames + 1] = { d, cycle_frames(anim) } end
      end
      targets[vis.name] = frames
    else
      unnamed = unnamed + 1
    end
  end
  return targets, unnamed
end

--- Give a machine a working sound: a bed, and accents cued to animation frames.
---
--- **The bed** is the loop that plays while the machine works -- `sound` on the
--- WorkingSound, which inherits MainSound's fields. **An accent** is a one-shot
--- the engine fires each time an animation reaches a frame: `SoundAccent` in
--- the prototype docs, `frame` plus `play_for_working_visualisation`, which is
--- how vanilla's big mining drill lands its start sound on frame 8 of
--- "drill-animation" (space-age/prototypes/entity/big-mining-drill.lua).
---
--- **An accent on the main `animation`, rather than a working visualisation,**
--- is one with no `play_for_working_visualisation` at all. The docs do not say
--- what such an accent counts; vanilla implies it. Assembling machine 1 cues
--- four with no visualisation, on frames 4, 13, 38 and 43
--- (base/prototypes/entity/entities.lua). Its main animation is 64 frames -- a
--- 64-frame `-anim` layer over a base and shadow repeated 64 times
--- (base/prototypes/entity/assembler-pictures.lua) -- and its one working
--- visualisation, the status light, also runs to 64 by `repeat_count` but has
--- no `name`, so no accent can be cued to it: the frames are the main
--- animation's. The recycler's six (recycler/data.lua) are cued the same way.
--- Here that is an accent with `visualisation` left out.
---
--- **The cue is checked here, at the data stage, and a wrong one is an error.**
--- The engine refuses an accent naming a visualisation the machine does not
--- have, with a message about the visualisation and none about the sound; and
--- an accent whose frame the animation never reaches would simply never play,
--- which no load would ever say. So: the name must be a working visualisation
--- of the machine's `graphics_set` (and of `wet_mining_graphics_set`, if it has
--- one), and the frame must be inside that animation's cycle in every
--- direction it draws, counting from 0 -- sfx.py's `frame` counts the same way.
---
--- **Call it after `derive.own_graphics`**, which strips every accent it finds:
--- they are checked against the graphics they are cued to, and that has to be
--- the building's own.
---
---     derive.working_sound(drill, {
---       bed = { filename = SND .. "winch-loop.ogg", volume = 0.5 },
---       accents = {
---         { sound = { filename = SND .. "landing.ogg" }, visualisation = "stroke", frame = 5 },
---         { sound = { filename = SND .. "tick.ogg" }, frame = 23 },  -- main animation
---       },
---       fade_in_ticks = 4, fade_out_ticks = 20,
---     })
---
--- Any other key is copied onto the WorkingSound as it is.
--- @param p    table  the prototype, its graphics_set already its own
--- @param spec table  `bed` (a Sound), `accents` (each: `sound`, `frame`,
---                    optional `visualisation` and `directions`), and any other
---                    WorkingSound field
function derive.working_sound(p, spec)
  local function fail(msg)
    error("[sae] " .. p.name .. " working sound: " .. msg, 3)
  end
  if not spec.bed then fail("no bed; `bed` is the loop it plays while working") end

  local sets = {}
  for _, key in ipairs({ "graphics_set", "wet_mining_graphics_set" }) do
    if p[key] then
      local targets, unnamed = cue_targets(p[key])
      sets[#sets + 1] = { key, targets, unnamed }
    end
  end

  local accents = {}
  for i, accent in ipairs(spec.accents or {}) do
    local name = accent.visualisation
    local what = name and ("working visualisation \"" .. name .. "\"") or "the main animation"
    local frame = accent.frame
    if not accent.sound then fail("accent " .. i .. " has no sound") end
    if type(frame) ~= "number" or frame ~= math.floor(frame) then
      fail("accent " .. i .. " on " .. what .. " needs a whole `frame`, got " .. tostring(frame))
    end
    if #sets == 0 then fail("accent " .. i .. ": the prototype has no graphics_set to cue it to") end
    for _, entry in ipairs(sets) do
      local key, targets, unnamed = entry[1], entry[2], entry[3]
      local frames = targets[name or false]
      if not frames then
        local names = {}
        for n in pairs(targets) do
          if n then names[#names + 1] = "\"" .. n .. "\"" end
        end
        table.sort(names)
        fail("accent " .. i .. " is cued to " .. what .. ", which " .. key .. " does not have"
             .. " (its named working visualisations: " .. (#names > 0 and table.concat(names, ", ") or "none")
             .. (unnamed > 0 and ("; " .. unnamed .. " more have no `name`, and only a named one can be cued to")
                 or "") .. ")")
      end
      if #frames == 0 then
        fail("accent " .. i .. ": " .. what .. " in " .. key .. " draws no animation to count frames in")
      end
      for _, df in ipairs(frames) do
        if frame < 0 or frame >= df[2] then
          fail("accent " .. i .. " is cued to frame " .. frame .. " of " .. what .. ", which has "
               .. df[2] .. " frames (0 to " .. (df[2] - 1) .. ") in " .. key .. ", " .. df[1])
        end
      end
    end
    accents[#accents + 1] =
    {
      sound = accent.sound,
      frame = frame,
      play_for_working_visualisation = name,
      play_for_directions = accent.directions
    }
  end

  local ws = { sound = spec.bed, sound_accents = #accents > 0 and accents or nil }
  for k, v in pairs(spec) do
    if k ~= "bed" and k ~= "accents" then ws[k] = v end
  end
  p.working_sound = ws
  return p
end

--- Vanilla's own pipe covers, for a fluid box that wants the engine to cap it.
---
--- **Every vanilla machine has these and four of ours did not.** The cover is
--- the little flange the engine stamps over an unconnected fluid port, and
--- `always_draw_covers = false` is what stops it doubling up once a pipe is
--- actually joined: capped when nothing is connected, gone when something is.
---
--- **This is the foundry's arrangement, and the foundry is worth reading before
--- copying.** It carries its own drawn stub art in `pipe_picture` *and* the
--- generic covers *and* `always_draw_covers = false`. The two are not
--- alternatives: the machine's own art says what the fitting looks like, and the
--- cover says what an unused one looks like. A building that draws its own
--- flange and omits the covers has simply left the second job undone -- which is
--- what four of ours were doing.
---
--- `pipecoverspictures` is a global the vanilla file defines as a side effect;
--- the file returns nothing, so this requires it for the side effect and calls
--- the global.
function derive.pipe_covers()
  require("__base__.prototypes.entity.pipecovers")
  return pipecoverspictures()
end

return derive
