-- Vulcanus <-> Fulgora, runtime: the two things its prototypes cannot do alone.
--
-- THE OZONE COLLECTOR. A lightning attractor has no fluid box, and no trigger
-- effect adds fluid (T02 (a)), so the building is two entities: the attractor
-- the player builds, and a hidden storage tank on the same tiles that holds
-- the ozone and has the pipe connection (prototypes/trees/vulcanus-fulgora.lua).
-- This file keeps the two together: a tank goes down when a collector is built,
-- in `storage` under the collector's unit number, and goes when the collector
-- does -- unless a collector built on the same tiles has taken it over, which
-- is how a replaced collector (a quality upgrade, a fast-replace) keeps its
-- ozone. Every lightning's attractor_hit_effect raises a script effect with the
-- attractor hit as its target, and a hit on an ozone collector adds 100 ozone
-- to its tank, which holds 1,000. Nothing runs per tick: one lookup and one
-- insert per strike.
--
-- OBSIDIAN ON AN OLD VULCANUS. A resource added to a vanilla planet's map gen
-- reaches new games only: a save's surface keeps the map gen settings it was
-- made with, so even its new chunks get no obsidian (T02 (b)). Once, when the
-- mod configuration changes, the obsidian entries the planet's prototype has
-- are added to Vulcanus's surface if they are missing. Ground already
-- generated keeps what it has; obsidian appears only on new ground.

local vf = {}

local COLLECTOR = "sae-ozone-collector"
local TANK = "sae-ozone-collector-tank"
local OZONE = "sae-ozone"
-- The script effect's id, as prototypes/trees/vulcanus-fulgora.lua gives it.
local STRIKE = "sae-ozone-strike"
local PER_STRIKE = 100

local OBSIDIAN = "sae-obsidian"

--------------------------------------------------------------------------------
-- The ozone collector.
--------------------------------------------------------------------------------

-- Who owns which tank: storage.sae_ozone_tanks maps a collector's unit number
-- to its tank, and storage.sae_ozone_owner a tank's unit number back to the
-- collector that owns it. A tank is destroyed only by its owner going.

-- Give a collector its tank: the one already on its tiles if there is one (a
-- replaced collector's, a cloned area's, or the one a reconcile finds), or a
-- new one. Taking over a tank takes it from the collector that had it.
local function attach(collector)
  local tank = collector.surface.find_entity(TANK, collector.position)
  if not tank then
    tank = collector.surface.create_entity({ name = TANK, position = collector.position, force = collector.force })
  end
  if not tank then return nil end
  tank.destructible = false
  local unit = collector.unit_number
  local previous = storage.sae_ozone_owner[tank.unit_number]
  if previous and previous ~= unit then storage.sae_ozone_tanks[previous] = nil end
  storage.sae_ozone_owner[tank.unit_number] = unit
  storage.sae_ozone_tanks[unit] = tank
  script.register_on_object_destroyed(collector)
  return tank
end

local function on_built(event)
  local collector = event.entity or event.destination
  if collector and collector.valid and collector.name == COLLECTOR then attach(collector) end
end

-- A collector has gone, however it went (mined, died, replaced, destroyed by
-- script): the engine says so here, by unit number, at the end of the tick it
-- went or the next. That is after any collector built in its place in the same
-- tick (a quality upgrade or a fast-replace removes the old one and builds the
-- new one together), so by now that one owns the tank and it stays, ozone and
-- all. A tank nobody took over goes.
local function on_object_destroyed(event)
  if event.type ~= defines.target_type.entity then return end
  local unit = event.useful_id
  local tank = storage.sae_ozone_tanks[unit]
  if tank == nil then return end
  storage.sae_ozone_tanks[unit] = nil
  if tank.valid and storage.sae_ozone_owner[tank.unit_number] == unit then
    storage.sae_ozone_owner[tank.unit_number] = nil
    tank.destroy()
  end
end

local function on_strike(event)
  if event.effect_id ~= STRIKE then return end
  local collector = event.target_entity
  if not (collector and collector.valid and collector.name == COLLECTOR) then return end
  local tank = storage.sae_ozone_tanks[collector.unit_number]
  if not (tank and tank.valid) then tank = attach(collector) end
  if tank then tank.insert_fluid({ name = OZONE, amount = PER_STRIKE }) end
end

-- Every collector has its tank and every tank its collector. Run on a
-- configuration change, so a save whose `storage` and entities disagree (the
-- script added to a save, a tank lost) is put right without a per-tick check.
local function reconcile()
  storage.sae_ozone_owner = {}
  local kept = {}
  for _, surface in pairs(game.surfaces) do
    for _, collector in pairs(surface.find_entities_filtered({ name = COLLECTOR })) do
      local tank = attach(collector)
      if tank then kept[tank.unit_number] = true end
    end
  end
  -- By unit number: two references to one entity are not the same table key.
  for unit_number, tank in pairs(storage.sae_ozone_tanks) do
    if not (tank.valid and kept[tank.unit_number]) then storage.sae_ozone_tanks[unit_number] = nil end
  end
  for _, surface in pairs(game.surfaces) do
    for _, tank in pairs(surface.find_entities_filtered({ name = TANK })) do
      if not kept[tank.unit_number] then tank.destroy() end
    end
  end
end

--------------------------------------------------------------------------------
-- Obsidian on a Vulcanus generated before the tree existed.
--------------------------------------------------------------------------------

-- The planet prototype's obsidian entries (its control, its entity setting and
-- the expression names that place it), added to Vulcanus's surface where
-- missing. Nothing happens when there is no Vulcanus surface yet: a surface
-- made now takes the planet's settings, obsidian included.
local function add_obsidian_to_vulcanus()
  local planet = game.planets["vulcanus"]
  local surface = planet and planet.surface
  if not surface then return end
  local proto = planet.prototype.map_gen_settings
  if not proto then return end
  local mgs = surface.map_gen_settings
  local changed = false

  local control = proto.autoplace_controls and proto.autoplace_controls[OBSIDIAN]
  if control then
    mgs.autoplace_controls = mgs.autoplace_controls or {}
    if mgs.autoplace_controls[OBSIDIAN] == nil then
      mgs.autoplace_controls[OBSIDIAN] = control
      changed = true
    end
  end

  local entities = proto.autoplace_settings and proto.autoplace_settings.entity
  local setting = entities and entities.settings and entities.settings[OBSIDIAN]
  if setting then
    mgs.autoplace_settings = mgs.autoplace_settings or {}
    mgs.autoplace_settings.entity = mgs.autoplace_settings.entity or {}
    mgs.autoplace_settings.entity.settings = mgs.autoplace_settings.entity.settings or {}
    if mgs.autoplace_settings.entity.settings[OBSIDIAN] == nil then
      mgs.autoplace_settings.entity.settings[OBSIDIAN] = setting
      changed = true
    end
  end

  local prefix = "entity:" .. OBSIDIAN .. ":"
  for key, expression in pairs(proto.property_expression_names or {}) do
    if key:sub(1, #prefix) == prefix then
      mgs.property_expression_names = mgs.property_expression_names or {}
      if mgs.property_expression_names[key] == nil then
        mgs.property_expression_names[key] = expression
        changed = true
      end
    end
  end

  if changed then
    surface.map_gen_settings = mgs
    log("[sae] obsidian added to the Vulcanus surface's map gen settings; it appears on ground generated from now on")
  end
end

--------------------------------------------------------------------------------
-- Wiring. control.lua owns the lifecycle handlers (the engine keeps one per
-- mod) and calls these from them; the events below are this file's alone.
--------------------------------------------------------------------------------

function vf.on_init()
  storage.sae_ozone_tanks = {}
  storage.sae_ozone_owner = {}
  add_obsidian_to_vulcanus()
end

function vf.on_configuration_changed()
  storage.sae_ozone_tanks = storage.sae_ozone_tanks or {}
  storage.sae_ozone_owner = storage.sae_ozone_owner or {}
  reconcile()
  add_obsidian_to_vulcanus()
end

function vf.register_events()
  local only = { { filter = "name", name = COLLECTOR } }
  for _, id in ipairs({
    defines.events.on_built_entity,
    defines.events.on_robot_built_entity,
    defines.events.on_space_platform_built_entity,
    defines.events.script_raised_built,
    defines.events.script_raised_revive,
    defines.events.on_entity_cloned
  }) do
    script.on_event(id, on_built, only)
  end
  -- No mined or died handlers: every way a collector goes ends here, and
  -- waiting for it is what lets a replacement keep the tank.
  script.on_event(defines.events.on_object_destroyed, on_object_destroyed)
  script.on_event(defines.events.on_script_trigger_effect, on_strike)
end

return vf
