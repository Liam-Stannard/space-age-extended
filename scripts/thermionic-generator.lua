-- Runtime logic for the Thermionic Generator (design doc §9).
--
-- Architecture (Phase 4 spike, see PROGRESS.md; heat-pipe interface added
-- afterwards, see §9.2's "Output" section; reactor-based rework afterwards
-- still, see the commit that introduced this comment): the visible entity
-- (`sae-thermionic-generator`) is a real `reactor`-type entity -- Magmatic
-- Core burns in its genuine burner fuel slot, ignited and consumed by the
-- engine itself, giving real status/tooltip/fuel-gauge animation for free
-- (an earlier "furnace with an unreachable recipe category" version faked
-- fuel removal via script and never actually ignited anything, which is
-- why it permanently misreported itself as broken in real play). The
-- reactor's own real heat_buffer *is* the temperature this file's curve
-- math runs against -- no separate abstract number kept in `storage`
-- anymore, and no separate hidden heat-interface entity either, since a
-- reactor's own heat_buffer already gives a real heat-pipe connection
-- (design doc §9.2/§9.3) via its `connections` (prototypes/entity.lua).
--
-- A reactor produces heat, not electricity (same as vanilla nuclear), so
-- it's paired 1:1 with two further hidden entities:
--   - `sae-thermionic-generator-power-interface`, an
--     `electric-energy-interface` this script drives every update
--     interval via `power_production`, computed from the reactor's real
--     temperature through thermionic-curve.lua's efficiency curve. This
--     is the only thing that actually injects electricity onto the grid.
--   - `sae-thermionic-generator-coolant-tank`, a 1-slot filtered
--     `container` holding Ice (a reactor has no second item slot to hold
--     a filtered coolant item natively). Never opened directly -- reached
--     via the "Insert Ice" button in the generator's info panel below.
-- All three (generator, power interface, coolant tank) are linked in
-- `storage`, keyed by `unit_number`.
--
-- The generator's own native reactor GUI already shows real fuel/status/
-- temperature (see the reference screenshots that drove this rework) --
-- scripts/thermionic-generator.lua only adds a small player.gui.relative
-- panel beside it for the two things the native window can't know about
-- (this mod's efficiency % and electrical power output) plus the Ice
-- quick-insert control.
--
-- Correctness rule this file must never violate: all mutable state
-- lives either in `storage` or in native Factorio entity state (the
-- reactor's own real temperature, the coolant tank's real inventory) and
-- is stepped forward by exactly one interval's worth of physics from its
-- own previously-stored value each time `on_nth_tick` fires -- never
-- derived from `game.tick` or any other measure of elapsed time. A
-- save/load or an idle period must not cause temperature to jump as if
-- time had passed uniformly at full load.

local curve = require("scripts.thermionic-curve")

local GENERATOR_NAME = "sae-thermionic-generator"
local POWER_INTERFACE_NAME = "sae-thermionic-generator-power-interface"
local COOLANT_TANK_NAME = "sae-thermionic-generator-coolant-tank"

-- Idle guard (see step_generator): if the grid drew less than
-- IDLE_DEMAND_THRESHOLD of *full* output last interval, the reactor is
-- paused rather than burning fuel into nothing. While paused,
-- IDLE_PROBE_FRACTION of full output is still offered so returning demand
-- can register -- the probe must exceed the threshold, or a real load
-- could never draw enough to trip it. Consequence, deliberate: loads
-- under the threshold (~200kW at the 4MW peak -- a docked platform's
-- standby draw) are served by the unfuelled probe indefinitely. That's
-- exactly the standby case §9.1 says shouldn't cost a core, and it's
-- bounded at 5% of peak.
local IDLE_DEMAND_THRESHOLD = 0.05
local IDLE_PROBE_FRACTION = 0.10

local INFO_FRAME_NAME = "sae_thermionic_generator_info"
local ICE_INSERT_BUTTON_NAME = "sae_thermionic_generator_insert_ice"

-- Once per second at normal game speed. Deliberately not per-tick -- this
-- needs to scale to many platforms, and the physics step size is a
-- function of stored state, not of how often this happens to run.
local UPDATE_INTERVAL = 60

local function init_storage()
  storage.sae_thermionic_generators = storage.sae_thermionic_generators or {}
  storage.sae_thermionic_power_interfaces = storage.sae_thermionic_power_interfaces or {}
  storage.sae_thermionic_coolant_tanks = storage.sae_thermionic_coolant_tanks or {}
  -- player_index -> generator unit_number, for whichever players currently
  -- have this generator's info panel open (see open_info_panel below) --
  -- lets on_tick_interval refresh their labels without scanning every
  -- player's GUI state each interval.
  storage.sae_thermionic_open_players = storage.sae_thermionic_open_players or {}
end

--- Spills whatever items are still sitting in `entity`'s given inventory
--- type onto the ground at its position. No-op if the entity is already
--- invalid -- nothing left to read a position or inventory from at that
--- point.
local function spill_inventory(entity, inventory_type)
  if not (entity and entity.valid) then
    return
  end
  local inventory = entity.get_inventory(inventory_type)
  if not inventory then
    return
  end
  local surface = entity.surface
  local position = entity.position
  for _, item in pairs(inventory.get_contents()) do
    surface.spill_item_stack({
      position = position,
      stack = { name = item.name, count = item.count, quality = item.quality },
      allow_belts = false,
    })
  end
end

--- Clears a player's open-panel tracking entry, so on_tick_interval stops
--- refreshing it. Doesn't destroy the actual GUI frame -- unnecessary,
--- since its anchor (see ensure_info_panel below) is scoped with
--- `name = GENERATOR_NAME`, so Factorio itself only ever shows it while
--- that player has a Thermionic Generator open, and hides it (without
--- needing it destroyed/rebuilt) for anything else, including a generator
--- that's since become invalid. Safe to call for a player with nothing
--- open -- a simple nil check.
local function forget_open_panel(player)
  if not player then
    return
  end
  storage.sae_thermionic_open_players[player.index] = nil
end

--- Forgets the open-panel tracking for every player who currently has
--- `generator_unit_number`'s panel open. Called from every cleanup path
--- below, since a generator/power-interface/coolant-tank being destroyed
--- out from under an open panel would otherwise leave on_tick_interval
--- refreshing a now-dangling link until the player manually closes the
--- window.
local function forget_open_panel_for_generator(generator_unit_number)
  for player_index, open_generator_unit_number in pairs(storage.sae_thermionic_open_players) do
    if open_generator_unit_number == generator_unit_number then
      forget_open_panel(game.get_player(player_index))
    end
  end
end

local function cleanup_by_generator_unit_number(generator_unit_number)
  local link = storage.sae_thermionic_generators[generator_unit_number]
  if not link then
    return
  end
  storage.sae_thermionic_generators[generator_unit_number] = nil
  storage.sae_thermionic_power_interfaces[link.power_interface_unit_number] = nil
  storage.sae_thermionic_coolant_tanks[link.coolant_tank_unit_number] = nil
  forget_open_panel_for_generator(generator_unit_number)
  if link.power_interface and link.power_interface.valid then
    link.power_interface.destroy()
  end
  if link.coolant_tank and link.coolant_tank.valid then
    spill_inventory(link.coolant_tank, defines.inventory.chest)
    link.coolant_tank.destroy()
  end
end

--- Shared teardown for "one of the paired hidden entities died on its
--- own" (power interface or coolant tank) -- looks up the owning
--- generator via `lookup_table[unit_number]`, then destroys everything
--- else in the trio exactly like cleanup_by_generator_unit_number, just
--- without an already-valid generator entity to destroy first (the caller
--- destroys it directly since on_object_destroyed's dispatch already
--- knows it's not that).
local function cleanup_by_paired_entity(lookup_table, unit_number)
  local generator_unit_number = lookup_table[unit_number]
  if not generator_unit_number then
    return
  end
  local link = storage.sae_thermionic_generators[generator_unit_number]
  lookup_table[unit_number] = nil
  storage.sae_thermionic_generators[generator_unit_number] = nil
  if not link then
    return
  end
  storage.sae_thermionic_power_interfaces[link.power_interface_unit_number] = nil
  storage.sae_thermionic_coolant_tanks[link.coolant_tank_unit_number] = nil
  forget_open_panel_for_generator(generator_unit_number)
  if link.generator and link.generator.valid then
    link.generator.destroy()
  end
  if link.power_interface and link.power_interface.valid then
    link.power_interface.destroy()
  end
  if link.coolant_tank and link.coolant_tank.valid then
    spill_inventory(link.coolant_tank, defines.inventory.chest)
    link.coolant_tank.destroy()
  end
end

--- Spawns the hidden power interface and coolant tank for a newly-built
--- generator and records the link both directions. Safe to call more than
--- once for the same entity (e.g. if two build events somehow both fire)
--- -- it's a no-op if a link already exists.
local function on_generator_built(entity)
  if not (entity and entity.valid) or entity.name ~= GENERATOR_NAME then
    return
  end
  init_storage()
  if storage.sae_thermionic_generators[entity.unit_number] then
    return
  end

  local power_interface = entity.surface.create_entity({
    name = POWER_INTERFACE_NAME,
    position = entity.position,
    force = entity.force,
    create_build_effect_smoke = false,
  })
  if not power_interface then
    log("sae-thermionic-generator: failed to create power interface for unit " .. entity.unit_number)
    return
  end
  power_interface.destructible = false

  local coolant_tank = entity.surface.create_entity({
    name = COOLANT_TANK_NAME,
    position = entity.position,
    force = entity.force,
    create_build_effect_smoke = false,
  })
  if not coolant_tank then
    log("sae-thermionic-generator: failed to create coolant tank for unit " .. entity.unit_number)
    power_interface.destroy()
    return
  end
  coolant_tank.destructible = false
  local coolant_inventory = coolant_tank.get_inventory(defines.inventory.chest)
  for slot = 1, #coolant_inventory do
    coolant_inventory.set_filter(slot, "ice")
  end

  entity.temperature = curve.AMBIENT_TEMPERATURE

  storage.sae_thermionic_generators[entity.unit_number] = {
    generator = entity,
    power_interface = power_interface,
    power_interface_unit_number = power_interface.unit_number,
    coolant_tank = coolant_tank,
    coolant_tank_unit_number = coolant_tank.unit_number,
  }
  storage.sae_thermionic_power_interfaces[power_interface.unit_number] = entity.unit_number
  storage.sae_thermionic_coolant_tanks[coolant_tank.unit_number] = entity.unit_number

  -- Catch-all cleanup path (see on_object_destroyed below) -- covers every
  -- destruction route, including ones the explicit mined/died events below
  -- might not (e.g. a space platform being scrapped).
  script.register_on_object_destroyed(entity)
  script.register_on_object_destroyed(power_interface)
  script.register_on_object_destroyed(coolant_tank)
end

local function on_generator_removed(event)
  local entity = event.entity
  if not (entity and entity.valid) or entity.name ~= GENERATOR_NAME then
    return
  end
  cleanup_by_generator_unit_number(entity.unit_number)
end

local function on_object_destroyed(event)
  if event.type ~= defines.target_type.entity then
    return
  end
  local unit_number = event.useful_id
  if unit_number == 0 then
    return
  end
  if storage.sae_thermionic_generators[unit_number] then
    cleanup_by_generator_unit_number(unit_number)
  elseif storage.sae_thermionic_power_interfaces[unit_number] then
    cleanup_by_paired_entity(storage.sae_thermionic_power_interfaces, unit_number)
  elseif storage.sae_thermionic_coolant_tanks[unit_number] then
    cleanup_by_paired_entity(storage.sae_thermionic_coolant_tanks, unit_number)
  end
end

--- Refreshes an already-open info panel's labels from `link`'s current
--- state. Safe to call even if the panel/player no longer has it open --
--- silently does nothing in that case, since a per-interval refresh loop
--- (on_tick_interval below) doesn't want to fail just because a player
--- closed the window since the last tick. Doesn't show temperature -- the
--- reactor's own native GUI already displays that for real (see the file
--- header) -- only the two things it can't know about (this mod's
--- efficiency % and electrical power output) plus Ice.
local function update_info_panel(player, link)
  if not player or not player.valid then
    return
  end
  local frame = player.gui.relative[INFO_FRAME_NAME]
  if not (frame and frame.valid) then
    return
  end
  local efficiency = curve.efficiency_for_temperature(link.generator.temperature)
  -- Watts, kept by step_generator -- the entity's own `power_production`
  -- is joules per tick, not a display-ready figure.
  local power_watts = link.last_power_production or 0
  local ice_count = 0
  if link.coolant_tank and link.coolant_tank.valid then
    ice_count = link.coolant_tank.get_inventory(defines.inventory.chest).get_item_count("ice")
  end

  frame.efficiency_value.caption =
    { "sae-thermionic-generator-gui.efficiency", math.floor(efficiency * 100 + 0.5) }
  frame.power_value.caption =
    { "sae-thermionic-generator-gui.power-output", string.format("%.2f", power_watts / 1000000) }
  frame.coolant_flow.coolant_value.caption = { "sae-thermionic-generator-gui.ice-stored", ice_count }
end

--- Builds this player's info panel if it doesn't already exist, anchored
--- beside the generator's native reactor GUI via player.gui.relative.
--- The anchor's `name = GENERATOR_NAME` means Factorio itself only ever
--- shows this panel while a Thermionic Generator specifically is open
--- (see forget_open_panel above) -- so it only needs building once per
--- player, ever, not rebuilt on every open.
local function ensure_info_panel(player)
  local frame = player.gui.relative[INFO_FRAME_NAME]
  if frame and frame.valid then
    return frame
  end

  frame = player.gui.relative.add({
    type = "frame",
    name = INFO_FRAME_NAME,
    caption = { "sae-thermionic-generator-gui.panel-title" },
    direction = "vertical",
    anchor = {
      gui = defines.relative_gui_type.reactor_gui,
      position = defines.relative_gui_position.right,
      name = GENERATOR_NAME,
    },
  })
  frame.add({ type = "label", name = "efficiency_value" })
  frame.add({ type = "label", name = "power_value" })

  frame.add({ type = "line" })
  local coolant_flow = frame.add({ type = "flow", name = "coolant_flow", direction = "horizontal" })
  coolant_flow.add({ type = "label", name = "coolant_value" })
  coolant_flow.add({
    type = "sprite-button",
    name = ICE_INSERT_BUTTON_NAME,
    sprite = "item/ice",
    tooltip = { "sae-thermionic-generator-gui.insert-ice-tooltip" },
  })
  return frame
end

local function open_info_panel(player, link)
  ensure_info_panel(player)
  storage.sae_thermionic_open_players[player.index] = link.generator.unit_number
  update_info_panel(player, link)
end

--- Attaches the info panel whenever a player opens a Thermionic
--- Generator's own (now entirely native) GUI -- no more redirect to a
--- hidden entity needed, since the generator itself is a real reactor
--- with a real window.
local function on_gui_opened(event)
  if event.gui_type ~= defines.gui_type.entity then
    return
  end
  local entity = event.entity
  if not (entity and entity.valid) then
    return
  end
  local player = game.get_player(event.player_index)
  if not player then
    return
  end

  if entity.name == GENERATOR_NAME then
    local link = storage.sae_thermionic_generators[entity.unit_number]
    if link then
      open_info_panel(player, link)
    end
    return
  end

  -- Some other entity's GUI (e.g. a real vanilla reactor) -- the panel's
  -- own anchor name already keeps it hidden here regardless (see
  -- ensure_info_panel), this just stops on_tick_interval refreshing it
  -- pointlessly while it's not visible.
  forget_open_panel(player)
end

local function on_gui_closed(event)
  if event.gui_type ~= defines.gui_type.entity then
    return
  end
  forget_open_panel(game.get_player(event.player_index))
end

local function on_player_left_game(event)
  forget_open_panel(game.get_player(event.player_index))
end

--- Handles a click on the info panel's "Insert Ice" button: quick-transfers
--- as much Ice as the coolant tank has room for from the clicking player's
--- own inventory, mirroring the vanilla shift-click "insert fuel" quick
--- transfer other burner buildings support. Exists because the coolant
--- tank has no native GUI of its own to click into directly (see the
--- architecture comment at the top of this file).
local function on_gui_click(event)
  if event.element.name ~= ICE_INSERT_BUTTON_NAME then
    return
  end
  local player = game.get_player(event.player_index)
  if not player then
    return
  end
  local generator_unit_number = storage.sae_thermionic_open_players[player.index]
  local link = generator_unit_number and storage.sae_thermionic_generators[generator_unit_number]
  if not (link and link.coolant_tank and link.coolant_tank.valid) then
    return
  end
  local player_inventory = player.get_main_inventory()
  if not player_inventory then
    return
  end
  local coolant_inventory = link.coolant_tank.get_inventory(defines.inventory.chest)
  local available = player_inventory.get_item_count("ice")
  local room = coolant_inventory.get_insertable_count("ice")
  local to_transfer = math.min(available, room)
  if to_transfer > 0 then
    local removed = player_inventory.remove({ name = "ice", count = to_transfer })
    if removed > 0 then
      coolant_inventory.insert({ name = "ice", count = removed })
    end
  end
  update_info_panel(player, link)
end

--- Advances one generator by exactly one interval's worth of physics.
--- Fuel consumption and self-heating are entirely native now -- the
--- reactor's own burner really ignites Magmatic Core and its heat_buffer
--- really accumulates heat from that (design doc §9.3 point 1), so this
--- only has two jobs left: apply Ice's cooling directly to the reactor's
--- real temperature, and drive the paired power interface's electrical
--- output from the resulting efficiency.
local function step_generator(link)
  local ice_inventory = link.coolant_tank.get_inventory(defines.inventory.chest)
  local ice_available = ice_inventory.get_item_count("ice")
  local current_temperature = link.generator.temperature

  -- `heat_in`/`heat_out_network` are both 0 here -- unlike the old
  -- script-driven model, there's no "heat about to be added this
  -- interval" to account for: the reactor's real heat_buffer already
  -- reflects everything the engine added continuously since last
  -- interval, and any heat-pipe network draw already happened for real
  -- too (a reactor's heat_buffer connections are genuine, see
  -- prototypes/entity.lua), so `current_temperature` is already the
  -- true post-network figure -- nothing left for this file to add back in.
  local ice_rate_cap = math.min(curve.MAX_ICE_PER_INTERVAL, curve.max_useful_ice(current_temperature, 0, 0))
  local ice_consumed = curve.consume(ice_available, ice_rate_cap)
  if ice_consumed > 0 then
    ice_inventory.remove({ name = "ice", count = ice_consumed })
  end

  local heat_out = curve.heat_removed_by_ice(ice_consumed)
  local next_temperature = current_temperature - heat_out
  if next_temperature < curve.AMBIENT_TEMPERATURE then
    next_temperature = curve.AMBIENT_TEMPERATURE
  end
  link.generator.temperature = next_temperature

  local generator = link.generator
  local power_interface = link.power_interface

  -- Fuel availability is read directly from the burner rather than via
  -- `status` -- the idle guard below leaves status reading "disabled by
  -- script" even with a full fuel slot, and a paused-but-fuelled
  -- generator must still advertise its output (see IDLE_PROBE_FRACTION).
  local burner = generator.burner
  local has_fuel = burner.remaining_burning_fuel > 0
    or not generator.get_inventory(defines.inventory.fuel).is_empty()

  -- Idle guard (design doc §9.1's "no idle waste" advantage over nuclear).
  -- `scale_energy_usage = false` on the prototype keeps fuel draw
  -- independent of *heat* -- but on its own it would also burn a core
  -- every 200s with nothing drawing power, exactly the docked-platform
  -- waste §9.1 holds against fuel cells. So measure real demand: the
  -- power interface's buffer was zeroed last interval, so whatever the
  -- engine added since (last interval's power_production x 1s) minus
  -- what's still sitting there is what the grid actually took -- exact,
  -- since the buffer (prototypes/entity.lua, 8MJ) can't clamp within one
  -- interval at <=4MW. Pause the reactor when (almost) nothing was drawn;
  -- resume when demand returns. Deliberately on/off, not proportional --
  -- fuel rate is meant to be player-controlled (§9.2), not
  -- demand-throttled; this only stops it running into nothing.
  local interval_seconds = UPDATE_INTERVAL / 60
  local load_fraction = has_fuel and 1 or 0
  local full_watts = curve.power_output(load_fraction, next_temperature)

  -- `offered` is what was actually put on the grid last interval (full
  -- output, or just the probe while idle) -- that's what the buffer
  -- received, so it's the right baseline for `drawn`. But the *decision*
  -- compares `drawn` against what full output would have been, not
  -- against `offered`: measured relative to a 40kW probe, a platform
  -- hub's few-kW standby draw read as ">5% demand" and flipped the
  -- reactor back to full burn every other interval (caught in the
  -- headless test as fuel still creeping down while "idle"). Relative to
  -- the full 4MJ/interval, that same standby draw is ~0.1% and stays
  -- idle, while a real 300kW consumer is 7.5% and resumes.
  local offered = (link.last_power_production or 0) * interval_seconds
  local drawn = offered - power_interface.energy
  power_interface.energy = 0
  local demand_fraction = 0
  if full_watts > 0 then
    demand_fraction = drawn / (full_watts * interval_seconds)
  end
  local idle = has_fuel and demand_fraction < IDLE_DEMAND_THRESHOLD
  -- `disabled_by_script`, not `active` -- `active` is read-only in the 2.x
  -- API (verified against runtime-api.json; writing it crashed the
  -- headless test). A reactor is an UpdatableEntity, so it honours this.
  generator.disabled_by_script = idle
  if idle then
    generator.custom_status = {
      diode = defines.entity_status_diode.yellow,
      label = { "sae-thermionic-generator-gui.status-idle" },
    }
  else
    generator.custom_status = nil
  end

  local power_watts = full_watts
  if idle then
    power_watts = full_watts * IDLE_PROBE_FRACTION
  end
  -- `power_production` is joules per *tick*, not watts (verified in-engine:
  -- writing 40,000 filled the buffer by exactly 2,400,000J over 60 ticks).
  -- Everything else in this file -- the curve, `offered` above, the info
  -- panel -- works in watts, so `link.last_power_production` keeps the
  -- watt figure and only the write here converts. An earlier version
  -- wrote watts directly, i.e. 60x too much, silently masked from the
  -- grid by the prototype's 4MW output_flow_limit.
  power_interface.power_production = power_watts / 60
  link.last_power_production = power_watts
end

local function on_tick_interval()
  for generator_unit_number, link in pairs(storage.sae_thermionic_generators) do
    if not (link.generator and link.generator.valid and link.power_interface and link.power_interface.valid and link.coolant_tank and link.coolant_tank.valid) then
      -- Defensive only -- on_object_destroyed above should already have
      -- caught this. Never leave a dangling entry in storage.
      cleanup_by_generator_unit_number(generator_unit_number)
    else
      step_generator(link)
    end
  end

  for player_index, generator_unit_number in pairs(storage.sae_thermionic_open_players) do
    local link = storage.sae_thermionic_generators[generator_unit_number]
    local player = game.get_player(player_index)
    if link and player then
      update_info_panel(player, link)
    else
      storage.sae_thermionic_open_players[player_index] = nil
    end
  end
end

local function on_init()
  init_storage()
end

local function on_configuration_changed()
  init_storage()
end

script.on_init(on_init)
script.on_configuration_changed(on_configuration_changed)

script.on_event(defines.events.on_built_entity, function(event) on_generator_built(event.entity) end)
script.on_event(defines.events.on_robot_built_entity, function(event) on_generator_built(event.entity) end)
script.on_event(defines.events.script_raised_built, function(event) on_generator_built(event.entity) end)
script.on_event(defines.events.script_raised_revive, function(event) on_generator_built(event.entity) end)
script.on_event(defines.events.on_space_platform_built_entity, function(event) on_generator_built(event.entity) end)
-- Note: on_entity_cloned's new-entity field is `destination`, not `entity`.
script.on_event(defines.events.on_entity_cloned, function(event) on_generator_built(event.destination) end)

script.on_event(defines.events.on_player_mined_entity, on_generator_removed)
script.on_event(defines.events.on_robot_mined_entity, on_generator_removed)
script.on_event(defines.events.on_entity_died, on_generator_removed)
script.on_event(defines.events.script_raised_destroy, on_generator_removed)
script.on_event(defines.events.on_space_platform_mined_entity, on_generator_removed)

script.on_event(defines.events.on_object_destroyed, on_object_destroyed)
script.on_event(defines.events.on_gui_opened, on_gui_opened)
script.on_event(defines.events.on_gui_closed, on_gui_closed)
script.on_event(defines.events.on_gui_click, on_gui_click)
script.on_event(defines.events.on_player_left_game, on_player_left_game)

script.on_nth_tick(UPDATE_INTERVAL, on_tick_interval)
