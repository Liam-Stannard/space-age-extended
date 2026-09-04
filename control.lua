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
