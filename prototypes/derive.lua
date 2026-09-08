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
function derive.placeholder_art(p, note)
  log("[sae] placeholder art: " .. p.name .. " -- " .. note)
  return p
end

return derive
