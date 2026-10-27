-- Space Age Extended -- runtime.
--
-- The mod is prototype-driven throughout. This file exists for two things the
-- data stage cannot express: what ends the game, and when the Core's day turns
-- to night.
--
-- Vanilla ends it when a platform reaches the Solar System Edge. This mod means
-- to end it at the Core instead, so vanilla's trigger is switched off. Nothing
-- has replaced it yet -- the Ignition Array went with the cut back to the
-- landing -- so the game does not end at all. That is the state of a rework in
-- progress, not a decision about the design.

local function disable_vanilla_victory()
  -- space_finish_script is registered by the freeplay scenario. If a scenario
  -- without it is running there is nothing to disable, and nothing to do.
  if remote.interfaces["space_finish_script"]
    and remote.interfaces["space_finish_script"]["set_no_victory"] then
    remote.call("space_finish_script", "set_no_victory", true)
  end
end

-- The Core's sky. The planet gives its surface a 3-minute cycle
-- (prototypes/core/planet.lua), and the engine runs it from that, ticks_per_day
-- included, which is never written here. When in the cycle it gets dark is the
-- surface's own setting, and a prototype cannot carry it: dusk and dawn sit
-- either side of noon, so the day is a brief flash and the rest is night. It is
-- set when the surface is made, and again on any configuration change, which
-- also reaches a Core surface already in a save.
local CORE = "sae-core"
local CORE_DAYTIME = { dusk = 0.02, evening = 0.10, morning = 0.90, dawn = 0.98 }

local function set_core_sky(surface)
  surface.daytime_parameters = CORE_DAYTIME
end

local function on_surface_created(event)
  local surface = game.get_surface(event.surface_index)
  if surface and surface.planet and surface.planet.name == CORE then
    set_core_sky(surface)
  end
end

local function on_configuration_changed()
  disable_vanilla_victory()
  local surface = game.planets[CORE].surface
  if surface then set_core_sky(surface) end
end

-- The engine keeps ONE handler per lifecycle event: a second script.on_init
-- replaces the first rather than adding to it, so everything that has to run at
-- start-up shares this one registration.
script.on_init(disable_vanilla_victory)
script.on_configuration_changed(on_configuration_changed)
script.on_event(defines.events.on_surface_created, on_surface_created)
