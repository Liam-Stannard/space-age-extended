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

-- on_rocket_launch_ordered, not on_rocket_launched.
--
-- The player fires it, from the silo GUI's Launch button -- confirmed in a real
-- game, where the button sits disabled with "Rocket is not ready" until progress
-- reaches 100%. launch_to_space_platforms = false removes the destination, not
-- the trigger, so nothing here needs to launch the rocket on the player's behalf.
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
  end,

  -- What the charge display is actually doing. Same reason as above: the render
  -- objects belong to this mod, so a console command cannot see them, and
  -- "the glow is drawing" is otherwise only checkable by looking at a screenshot.
  arrays = function()
    local out = {}
    for unit_number, r in pairs(storage.sae_arrays or {}) do
      local e = r.entity
      local required = (e and e.valid) and e.prototype.rocket_parts_required or 0
      out[#out + 1] =
      {
        unit_number = unit_number,
        valid = e and e.valid or false,
        parts = (e and e.valid) and e.rocket_parts or 0,
        required = required,
        progress = (e and e.valid) and e.crafting_progress or 0,
        charge = (e and e.valid and required > 0)
          and math.min(1, (e.rocket_parts + e.crafting_progress) / required) or 0,
        glow = (r.glow and r.glow.valid) and r.glow.color.a or nil,
        light = (r.light and r.light.valid) and r.light.intensity or nil
      }
    end
    return out
  end
})

--------------------------------------------------------------------------------
-- The Ignition Array's charge.
--
-- The Array assembles a hundred `sae-field-coil-segment`s before it can fire,
-- which is a long and expensive investment, and until now the building said
-- nothing about it. This draws it.
--
-- **It has to live here, and that was established rather than assumed.** No
-- prototype field can hold cumulative state: `red_lights_back_sprites` is a
-- blink cycle driven by `light_blinking_speed` and `times_to_blink`, not a
-- counter, and 2.1.17's `LuaEntity` has no `disabled_working_visualisations`, so
-- named working visualisations cannot be switched per entity from script either.
-- Both were probed on a live server. `rendering.draw_sprite`, `draw_animation`
-- and `draw_light` all exist, and a drawn object's properties are settable after
-- creation, so a charge can ramp continuously instead of stepping.
--
-- The level comes straight off the entity:
--
--     (rocket_parts + crafting_progress) / prototype.rocket_parts_required
--
-- `crafting_progress` is the segment currently in flight, so this is a smooth
-- nought to one across the whole build rather than a hundred discrete clicks.
--------------------------------------------------------------------------------

local ARRAY = "sae-ignition-array"
local CHARGE_TICKS = 20                      -- three updates a second is plenty

--- Registry of live Arrays, kept by event rather than by rescanning surfaces.
-- A whole-surface `find_entities_filtered` once a second to maintain a handful
-- of endgame buildings is work the map does not need to do.
local function registry()
  storage.sae_arrays = storage.sae_arrays or {}
  return storage.sae_arrays
end

local function forget(unit_number)
  local r = registry()[unit_number]
  if not r then return end
  for _, obj in pairs({ r.glow, r.light }) do
    if obj and obj.valid then obj.destroy() end
  end
  registry()[unit_number] = nil
end

local function remember(entity)
  if not (entity and entity.valid and entity.name == ARRAY) then return end
  registry()[entity.unit_number] = { entity = entity }
end

local function rescan()
  for _, r in pairs(registry()) do
    if r.glow and r.glow.valid then r.glow.destroy() end
    if r.light and r.light.valid then r.light.destroy() end
  end
  storage.sae_arrays = {}
  for _, surface in pairs(game.surfaces) do
    for _, e in pairs(surface.find_entities_filtered{ name = ARRAY }) do remember(e) end
  end
end

-- The engine keeps ONE handler per lifecycle event: a second script.on_init
-- replaces the first rather than adding to it. Registered separately, the
-- start-up jobs silently fell to the last one -- the Array registry was
-- rebuilt and vanilla's Edge victory was never switched off. So they share a
-- single registration, here, after the last of them is defined.
local function on_start()
  disable_vanilla_victory()
  rescan()
end

script.on_init(on_start)
script.on_configuration_changed(on_start)

for _, ev in ipairs({
  defines.events.on_built_entity, defines.events.on_robot_built_entity,
  defines.events.script_raised_built, defines.events.script_raised_revive,
  defines.events.on_space_platform_built_entity,
}) do
  script.on_event(ev, function(event) remember(event.entity) end,
                  { { filter = "name", name = ARRAY } })
end

for _, ev in ipairs({
  defines.events.on_entity_died, defines.events.on_player_mined_entity,
  defines.events.on_robot_mined_entity, defines.events.script_raised_destroy,
  defines.events.on_space_platform_mined_entity,
}) do
  script.on_event(ev, function(event)
    if event.entity and event.entity.unit_number then forget(event.entity.unit_number) end
  end, { { filter = "name", name = ARRAY } })
end

script.on_nth_tick(CHARGE_TICKS, function()
  for unit_number, r in pairs(registry()) do
    local e = r.entity
    if not (e and e.valid) then
      forget(unit_number)
    else
      local required = e.prototype.rocket_parts_required
      local charge = 0
      if required and required > 0 then
        charge = (e.rocket_parts + e.crafting_progress) / required
        if charge < 0 then charge = 0 elseif charge > 1 then charge = 1 end
      end

      if charge <= 0.001 then
        -- Nothing glows at rest. Drawn objects are destroyed rather than faded
        -- to zero, so a dormant Array costs the renderer nothing.
        if r.glow and r.glow.valid then r.glow.destroy() end
        if r.light and r.light.valid then r.light.destroy() end
        r.glow, r.light = nil, nil
      else
        if not (r.glow and r.glow.valid) then
          r.glow = rendering.draw_sprite
          {
            sprite = "sae-ignition-charge-glow",
            surface = e.surface,
            target = e,
            render_layer = "higher-object-above"
          }
        end
        if not (r.light and r.light.valid) then
          r.light = rendering.draw_light
          {
            sprite = "utility/light_medium",
            surface = e.surface,
            target = e,
            scale = 6,
            color = { r = 0.62, g = 0.48, b = 1.0 }
          }
        end
        -- Ramp the plate's alpha rather than swapping frames: the glow is one
        -- image and the charge is continuous, so there is nothing to step.
        r.glow.color = { r = 1, g = 1, b = 1, a = charge }
        r.light.intensity = 0.15 + 0.55 * charge
      end
    end
  end
end)
