-- Runtime logic for the Thermionic Generator (design doc §9).
--
-- Architecture (Phase 4 spike, see PROGRESS.md; heat-pipe interface added
-- afterwards, see §9.2's "Output" section): a visible
-- `electric-energy-interface` entity (`sae-thermionic-generator`) whose
-- `power_production` this script drives every update interval, paired 1:1
-- with two hidden entities -- a 2-slot `container`
-- (`sae-thermionic-generator-hopper`) that holds the Magmatic Core / Ice
-- inputs, and a `heat-interface` (`sae-thermionic-generator-heat-interface`)
-- that gives the generator a real heat-pipe connection as a secondary
-- cooling avenue alongside Ice. All three are linked in `storage`, keyed
-- by `unit_number`.
--
-- Correctness rule this file must never violate: all mutable state
-- (temperature, the link table itself) lives in `storage` and is stepped
-- forward by exactly one interval's worth of physics from its own
-- previously-stored value each time `on_nth_tick` fires -- never derived
-- from `game.tick` or any other measure of elapsed time. A save/load or an
-- idle period must not cause temperature to jump as if time had passed
-- uniformly at full load. The heat-interface's own real `temperature` is
-- native entity state Factorio persists automatically across save/reload
-- on its own -- no separate storage bookkeeping needed for it beyond the
-- link itself, same as the hopper's inventory contents.

local curve = require("scripts.thermionic-curve")

local GENERATOR_NAME = "sae-thermionic-generator"
local CONTAINER_NAME = "sae-thermionic-generator-hopper"
local HEAT_INTERFACE_NAME = "sae-thermionic-generator-heat-interface"

local MAGMATIC_CORE_SLOT = 1
local ICE_SLOT = 2

-- Once per second at normal game speed. Deliberately not per-tick -- this
-- needs to scale to many platforms, and the physics step size is a
-- function of stored state, not of how often this happens to run.
local UPDATE_INTERVAL = 60

local function init_storage()
  storage.sae_thermionic_generators = storage.sae_thermionic_generators or {}
  storage.sae_thermionic_containers = storage.sae_thermionic_containers or {}
  storage.sae_thermionic_heat_interfaces = storage.sae_thermionic_heat_interfaces or {}
end

--- Spills whatever Magmatic Core / Ice is still sitting in a hopper's
--- inventory onto the ground at its position, so destroying a generator
--- (and its paired hopper) with it doesn't silently discard stored fuel/
--- coolant. No-op if the container is already invalid -- nothing left to
--- read a position or inventory from at that point.
local function spill_container_contents(container)
  if not (container and container.valid) then
    return
  end
  local inventory = container.get_inventory(defines.inventory.chest)
  if not inventory then
    return
  end
  local surface = container.surface
  local position = container.position
  for _, item in pairs(inventory.get_contents()) do
    surface.spill_item_stack({
      position = position,
      stack = { name = item.name, count = item.count, quality = item.quality },
      allow_belts = false,
    })
  end
end

local function cleanup_by_generator_unit_number(generator_unit_number)
  local link = storage.sae_thermionic_generators[generator_unit_number]
  if not link then
    return
  end
  storage.sae_thermionic_generators[generator_unit_number] = nil
  storage.sae_thermionic_containers[link.container_unit_number] = nil
  if link.heat_interface_unit_number then
    storage.sae_thermionic_heat_interfaces[link.heat_interface_unit_number] = nil
  end
  if link.container and link.container.valid then
    spill_container_contents(link.container)
    link.container.destroy()
  end
  if link.heat_interface and link.heat_interface.valid then
    link.heat_interface.destroy()
  end
end

local function cleanup_by_container_unit_number(container_unit_number)
  local generator_unit_number = storage.sae_thermionic_containers[container_unit_number]
  if not generator_unit_number then
    return
  end
  local link = storage.sae_thermionic_generators[generator_unit_number]
  storage.sae_thermionic_containers[container_unit_number] = nil
  storage.sae_thermionic_generators[generator_unit_number] = nil
  if link then
    if link.heat_interface_unit_number then
      storage.sae_thermionic_heat_interfaces[link.heat_interface_unit_number] = nil
    end
    spill_container_contents(link.container)
    if link.generator and link.generator.valid then
      link.generator.destroy()
    end
    if link.heat_interface and link.heat_interface.valid then
      link.heat_interface.destroy()
    end
  end
end

local function cleanup_by_heat_interface_unit_number(heat_interface_unit_number)
  local generator_unit_number = storage.sae_thermionic_heat_interfaces[heat_interface_unit_number]
  if not generator_unit_number then
    return
  end
  local link = storage.sae_thermionic_generators[generator_unit_number]
  storage.sae_thermionic_heat_interfaces[heat_interface_unit_number] = nil
  storage.sae_thermionic_generators[generator_unit_number] = nil
  if link then
    storage.sae_thermionic_containers[link.container_unit_number] = nil
    if link.container and link.container.valid then
      spill_container_contents(link.container)
      link.container.destroy()
    end
    if link.generator and link.generator.valid then
      link.generator.destroy()
    end
  end
end

--- Spawns a new heat-interface entity positioned on `entity` (the visible
--- generator), seeded at `seed_abstract_temperature` (mapped through the
--- same abstract-to-Celsius conversion used everywhere else). Factored out
--- so both on_generator_built (fresh generator, seeds at
--- AMBIENT_TEMPERATURE) and ensure_heat_interface below (legacy-save
--- backfill, seeds at the link's own already-established temperature) go
--- through identical spawn logic. Returns nil, nil if entity creation
--- failed. snap_to_grid = false is required here -- by default a zero-
--- size-footprint entity like this one snaps to the nearest whole-tile
--- corner rather than the exact position given, which would silently
--- offset it from the visible generator's own center and break the
--- heat_buffer connection math in prototypes/entity.lua (verified
--- in-engine).
local function spawn_heat_interface(entity, seed_abstract_temperature)
  local heat_interface = entity.surface.create_entity({
    name = HEAT_INTERFACE_NAME,
    position = entity.position,
    force = entity.force,
    create_build_effect_smoke = false,
    snap_to_grid = false,
  })
  if not heat_interface then
    return nil, nil
  end
  heat_interface.destructible = false
  local seed_celsius = curve.abstract_temperature_to_heat_buffer_celsius(seed_abstract_temperature)
  heat_interface.temperature = seed_celsius
  return heat_interface, seed_celsius
end

--- Lazily creates and links a heat-interface for a link that predates the
--- heat-pipe feature (see on_tick_interval below): a
--- storage.sae_thermionic_generators entry written before this feature
--- existed has a valid generator and container, but no heat_interface
--- field at all -- that field simply didn't exist yet when it was written.
--- Treating that as "something is broken" (the old behaviour) tore down an
--- otherwise-perfectly-healthy generator+hopper pair on every pre-existing
--- save; this instead backfills a fresh heat-interface in place, exactly
--- as if the generator had just gained a heat-pipe connection for the
--- first time. Seeds the new interface at the link's own current abstract
--- temperature (not AMBIENT_TEMPERATURE) so a generator that's already
--- running hot on a legacy save doesn't present as falsely cold to
--- anything already connected, and resets pushed_heat_interface_celsius to
--- match so this interval's M.heat_removed_by_network reads a zero network
--- contribution rather than comparing against a stale/absent value.
--- Returns true if the link has a valid heat_interface afterwards (either
--- backfilled here or already present) -- false only if entity creation
--- itself failed, in which case the caller should leave the link alone and
--- retry next interval rather than tearing anything down.
local function ensure_heat_interface(generator_unit_number, link)
  if link.heat_interface and link.heat_interface.valid then
    return true
  end
  local heat_interface, seed_celsius = spawn_heat_interface(link.generator, link.temperature)
  if not heat_interface then
    log("sae-thermionic-generator: failed to backfill heat-interface for unit " .. generator_unit_number)
    return false
  end
  if link.heat_interface_unit_number then
    storage.sae_thermionic_heat_interfaces[link.heat_interface_unit_number] = nil
  end
  link.heat_interface = heat_interface
  link.heat_interface_unit_number = heat_interface.unit_number
  link.pushed_heat_interface_celsius = seed_celsius
  storage.sae_thermionic_heat_interfaces[heat_interface.unit_number] = generator_unit_number
  script.register_on_object_destroyed(heat_interface)
  return true
end

--- Spawns the hidden hopper for a newly-built generator and records the
--- link both directions. Safe to call more than once for the same entity
--- (e.g. if two build events somehow both fire) -- it's a no-op if a link
--- already exists.
local function on_generator_built(entity)
  if not (entity and entity.valid) or entity.name ~= GENERATOR_NAME then
    return
  end
  init_storage()
  if storage.sae_thermionic_generators[entity.unit_number] then
    return
  end

  local container = entity.surface.create_entity({
    name = CONTAINER_NAME,
    position = entity.position,
    force = entity.force,
    create_build_effect_smoke = false,
  })
  if not container then
    log("sae-thermionic-generator: failed to create hopper for unit " .. entity.unit_number)
    return
  end
  container.destructible = false

  local inventory = container.get_inventory(defines.inventory.chest)
  inventory.set_filter(MAGMATIC_CORE_SLOT, "sae-magmatic-core")
  inventory.set_filter(ICE_SLOT, "ice")

  local heat_interface, initial_heat_interface_celsius = spawn_heat_interface(entity, curve.AMBIENT_TEMPERATURE)
  if not heat_interface then
    log("sae-thermionic-generator: failed to create heat-interface for unit " .. entity.unit_number)
    container.destroy()
    return
  end

  storage.sae_thermionic_generators[entity.unit_number] = {
    generator = entity,
    container = container,
    container_unit_number = container.unit_number,
    heat_interface = heat_interface,
    heat_interface_unit_number = heat_interface.unit_number,
    temperature = curve.AMBIENT_TEMPERATURE,
    -- What was last pushed onto the heat-interface, in Celsius -- compared
    -- against the interface's own current (real, network-driven)
    -- temperature each interval to work out how much a connected heat-pipe
    -- network actually moved (see step_generator below).
    pushed_heat_interface_celsius = initial_heat_interface_celsius,
  }
  storage.sae_thermionic_containers[container.unit_number] = entity.unit_number
  storage.sae_thermionic_heat_interfaces[heat_interface.unit_number] = entity.unit_number

  -- Catch-all cleanup path (see on_object_destroyed below) -- covers every
  -- destruction route, including ones the explicit mined/died events below
  -- might not (e.g. a space platform being scrapped).
  script.register_on_object_destroyed(entity)
  script.register_on_object_destroyed(container)
  script.register_on_object_destroyed(heat_interface)
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
  elseif storage.sae_thermionic_containers[unit_number] then
    cleanup_by_container_unit_number(unit_number)
  elseif storage.sae_thermionic_heat_interfaces[unit_number] then
    cleanup_by_heat_interface_unit_number(unit_number)
  end
end

--- Redirects the player's GUI from the visible (fuel/coolant-only, no
--- inventory of its own) generator to its hidden hopper, so a normal
--- player can insert Magmatic Core / Ice just by clicking the building.
local function on_gui_opened(event)
  if event.gui_type ~= defines.gui_type.entity then
    return
  end
  local entity = event.entity
  if not (entity and entity.valid) or entity.name ~= GENERATOR_NAME then
    return
  end
  local link = storage.sae_thermionic_generators[entity.unit_number]
  if not (link and link.container and link.container.valid) then
    return
  end
  local player = game.get_player(event.player_index)
  if player then
    player.opened = link.container
  end
end

--- Advances one generator by exactly one interval's worth of physics,
--- using only currently-available inputs (the hopper's current contents,
--- the previously-stored temperature).
local function step_generator(link)
  local inventory = link.container.get_inventory(defines.inventory.chest)
  local fuel_available = inventory.get_item_count("sae-magmatic-core")
  local ice_available = inventory.get_item_count("ice")

  local fuel_consumed = curve.consume(fuel_available, curve.MAX_FUEL_PER_INTERVAL)
  local heat_in = curve.heat_from_fuel(fuel_consumed)

  -- Read the heat-interface's *current* real temperature before deciding
  -- how much ice to draw this interval -- this reflects whatever a
  -- connected heat-pipe network did to it since the value this same
  -- function pushed last interval (could be lower, if a colder network
  -- pulled heat away; could even be higher, if something hotter pushed
  -- heat in via the same network -- both are real physics and both are
  -- allowed to feed back into the abstract model below, deliberately not
  -- special-cased away). Deliberately computed *before* the ice decision,
  -- not after -- the network's contribution this interval is already fully
  -- knowable at this point, so the ice-consumption cap below can account
  -- for it instead of burning ice at a pre-network rate regardless of
  -- what the network already handled (design doc §9.3's "player controls
  -- fuel rate and cooling rate independently").
  local heat_out_network = curve.heat_removed_by_network(link.pushed_heat_interface_celsius, link.heat_interface.temperature)

  -- Don't draw more ice than can actually still have a cooling effect
  -- this interval -- e.g. an idle generator already floored at
  -- AMBIENT_TEMPERATURE with no fuel has nothing left to cool, so burning
  -- ice for it would be pure waste, and the same is true of heat the
  -- network is already removing this interval (design doc §9.3/§9.4).
  local ice_rate_cap = math.min(curve.MAX_ICE_PER_INTERVAL, curve.max_useful_ice(link.temperature, heat_in, heat_out_network))
  local ice_consumed = curve.consume(ice_available, ice_rate_cap)

  if fuel_consumed > 0 then
    inventory.remove({ name = "sae-magmatic-core", count = fuel_consumed })
  end
  if ice_consumed > 0 then
    inventory.remove({ name = "ice", count = ice_consumed })
  end

  local heat_out = curve.heat_removed_by_ice(ice_consumed)

  link.temperature = curve.next_temperature(link.temperature, heat_in, heat_out, heat_out_network)

  -- Push the newly-computed abstract temperature back onto the
  -- heat-interface (same conversion used to read it), so next interval's
  -- read-back reflects real network activity since *this* push, not
  -- against a stale value.
  local pushed_celsius = curve.abstract_temperature_to_heat_buffer_celsius(link.temperature)
  link.heat_interface.temperature = pushed_celsius
  link.pushed_heat_interface_celsius = pushed_celsius

  local load_fraction = fuel_consumed / curve.MAX_FUEL_PER_INTERVAL
  link.generator.power_production = curve.power_output(load_fraction, link.temperature)
end

local function on_tick_interval()
  for generator_unit_number, link in pairs(storage.sae_thermionic_generators) do
    if not (link.generator and link.generator.valid and link.container and link.container.valid) then
      -- Defensive only -- on_object_destroyed above should already have
      -- caught this. Never leave a dangling entry in storage.
      cleanup_by_generator_unit_number(generator_unit_number)
    elseif ensure_heat_interface(generator_unit_number, link) then
      -- A missing/invalid heat_interface alone (generator and container
      -- both otherwise healthy) is NOT torn down -- see
      -- ensure_heat_interface's own comment. It's either a legacy save
      -- predating this field, or the interface died independently of the
      -- generator+hopper it's paired with; either way the right recovery
      -- is a fresh heat-interface, not destroying a healthy trio.
      step_generator(link)
    end
    -- else: heat-interface creation just failed (e.g. a transient
    -- can't-place-here condition) -- leave the link untouched and retry
    -- next interval rather than tearing down an otherwise-healthy
    -- generator+hopper pair over it.
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

script.on_nth_tick(UPDATE_INTERVAL, on_tick_interval)
