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
-- is legitimate to reuse: open/close and working sounds, circuit connector
-- sprites, corpses and explosions. Reusing vanilla audio is ordinary modding.

local util = require("util")

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

  return p
end

--- Point a machine at another prototype's art, deliberately and visibly.
---
--- Stand-in art is not the same thing as an inherited leftover: the Vent Pump
--- wears the pumpjack's sprites on purpose and says so. This marks that choice
--- in one place so a later audit can find every building still wearing borrowed
--- art by grepping for one call rather than by eye.
--- @param p     table   the prototype
--- @param note  string  why, for the reader
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
