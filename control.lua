-- Space Age Extended -- runtime.
--
-- The mod is prototype-driven throughout. This file exists for one thing the
-- data stage cannot express: what ends the game.
--
-- Vanilla ends it when a platform reaches the Solar System Edge. This mod means
-- to end it at the Core instead, so vanilla's trigger is switched off. On this
-- branch nothing has replaced it yet -- the Ignition Array is on master, not
-- here -- so the game does not end at all. That is the state of a slice, not a
-- decision about the design.

local function disable_vanilla_victory()
  -- space_finish_script is registered by the freeplay scenario. If a scenario
  -- without it is running there is nothing to disable, and nothing to do.
  if remote.interfaces["space_finish_script"]
    and remote.interfaces["space_finish_script"]["set_no_victory"] then
    remote.call("space_finish_script", "set_no_victory", true)
  end
end

-- The engine keeps ONE handler per lifecycle event: a second script.on_init
-- replaces the first rather than adding to it, so everything that has to run at
-- start-up shares this one registration.
script.on_init(disable_vanilla_victory)
script.on_configuration_changed(disable_vanilla_victory)
