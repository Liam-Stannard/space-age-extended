-- Space Age Extended -- runtime.
--
-- The mod is prototype-driven throughout. This file exists for one thing the
-- data stage cannot express: the win condition.
--
-- Vanilla ends the game when a platform reaches the Solar System Edge. This mod
-- ends it when the Ignition Array fires and the Core's dead field restarts, so
-- vanilla's trigger is switched off and ours takes its place. That is the only
-- change the mod makes to anything vanilla does.

local function disable_vanilla_victory()
  -- space_finish_script is registered by the freeplay scenario. If a scenario
  -- without it is running there is nothing to disable, and nothing to do.
  if remote.interfaces["space_finish_script"]
    and remote.interfaces["space_finish_script"]["set_no_victory"] then
    remote.call("space_finish_script", "set_no_victory", true)
  end
end

script.on_init(disable_vanilla_victory)
script.on_configuration_changed(disable_vanilla_victory)

-- Hold the Core at midnight, permanently.
--
-- Measured against the engine, not assumed: lightning is generated only while
-- a surface is dark. With surface_properties["day-night-cycle"] = 0 there is no
-- night, and a mast sat through 729 chunks and 7000 ticks catching nothing;
-- forced to darkness it charged inside 370. Arc storms are the Core's only
-- power source and its only hazard, so that silence was fatal.
--
-- The planet therefore declares a long cycle -- night has to be reachable --
-- and this pins it at midnight and freezes it. The design's "sky that does not
-- move" survives: it simply never moves off night, which suits a dead world
-- with solar-power = 0.
local function hold_the_core_at_night(surface)
  if surface and surface.valid and surface.name == "sae-core" then
    surface.always_day = false
    surface.daytime = 0.5
    surface.freeze_daytime = true
  end
end

local function hold_all_cores()
  for _, surface in pairs(game.surfaces) do hold_the_core_at_night(surface) end
end

script.on_init(hold_all_cores)
script.on_configuration_changed(hold_all_cores)
script.on_event(defines.events.on_surface_created, function(event)
  hold_the_core_at_night(game.surfaces[event.surface_index])
end)

-- on_rocket_launch_ordered, not on_rocket_launched.
--
-- Measured: the Array raises "ordered" and never raises "launched". A vanilla
-- rocket completes its launch by delivering cargo to space, and the Array
-- delivers nothing -- it fires a current into the crust. The order is the
-- firing, so that is the moment the game is won.
script.on_event(defines.events.on_rocket_launch_ordered, function(event)
  storage.sae_launch_ordered = (storage.sae_launch_ordered or 0) + 1
  local silo = event.rocket_silo
  if not (silo and silo.valid and silo.name == "sae-ignition-array") then return end

  -- Fire once. A player who keeps building segments afterwards should not
  -- retrigger the ending.
  if storage.sae_ignition_fired then return end
  storage.sae_ignition_fired = true

  game.set_game_state
  {
    game_finished = true,
    player_won = true,
    can_continue = true,
    victorious_force = silo.force
  }
end)

-- A window into the mod's own runtime state. Console commands run in the
-- scenario's script context, not the mod's, so without this there is no way to
-- ask whether an event ever reached us.
remote.add_interface("sae",
{
  state = function()
    return
    {
      fired = storage.sae_ignition_fired,
      launch_ordered = storage.sae_launch_ordered or 0
    }
  end
})
