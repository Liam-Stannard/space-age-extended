-- Pure thermal/efficiency math for the Thermionic Generator.
-- See design/vulcanus-fulgora.md §9.3 for the five behaviours this module
-- must reproduce (self-heating, ice-driven cooling, gradual decline above
-- the optimal band, a sharp-but-non-fatal drop past overheat, and a load-
-- vs-cooling equilibrium).
--
-- Zero dependency on `game`/`script`/`storage`/any Factorio API -- this file
-- must be `require`-able and callable from a plain Lua 5.2+ REPL outside the
-- game engine (this repo has no unit-test framework; this is the
-- established substitute, see PROGRESS.md). scripts/thermionic-generator.lua
-- is the only thing that wires this into actual entities/events.
--
-- "Temperature" here is an abstract internal scale, NOT a Factorio
-- heat-network degree value -- this generator deliberately has no heat-pipe
-- interface (design doc §9.2), so there is no real physical unit to match.
-- 0 represents cold/idle; larger numbers are hotter.

local M = {}

-- ---------------------------------------------------------------------
-- Provisional balance constants (design doc §9.4, "open questions for
-- this technology"). All of these are sane, non-degenerate placeholders,
-- not final-tuned numbers -- see design/framework.md §7.5 ("tune the
-- Thermionic Generator only once several capabilities exist to draw on
-- it").
-- ---------------------------------------------------------------------

-- Peak electrical output. Must sit meaningfully below fusion's 50MW
-- (verified against the real fusion-generator prototype: output_flow_limit
-- = "50MW"). 4MW is in the low-single-digit-MW range the design doc's open
-- questions call for -- roughly 12.5x below fusion, comfortably filling the
-- "solar stops working, Aquilo not reached yet" gap (§9.1) without
-- competing with fusion on density.
M.PEAK_POWER_W = 4 * 1000 * 1000 -- 4 MW

-- The plateau of full efficiency. OPTIMAL_MIN is documentation of the
-- band's lower edge (nothing in §9.3 penalises running cold, only running
-- hot) -- only OPTIMAL_MAX is actually branched on below.
M.OPTIMAL_MIN = 400
M.OPTIMAL_MAX = 600

-- Past this point the decline stops being gradual and becomes the sharp,
-- non-fatal drop described in §9.3 point 4.
M.OVERHEAT_THRESHOLD = 800

-- Efficiency at the two named points on the curve.
M.OVERHEAT_FLOOR_EFFICIENCY = 0.5 -- efficiency right at OVERHEAT_THRESHOLD, end of the gradual decline
M.MIN_EFFICIENCY = 0.08 -- the "barely worth its footprint" floor -- never destroyed, never zero (design doc §9.3 point 4; framework.md §4.5 rule 3, "degrade, don't destroy")

-- A soft ceiling on stored temperature, purely so an unattended generator
-- left burning fuel with no ice for a very long time doesn't accumulate an
-- unbounded number in `storage`. It has no effect on the efficiency curve
-- itself, which already saturates at MIN_EFFICIENCY well before this.
M.MAX_TEMPERATURE = 5000
M.AMBIENT_TEMPERATURE = 0

-- Heat added per unit of Magmatic Core consumed, and heat removed per unit
-- of Ice consumed, in one update interval.
M.HEAT_PER_FUEL_UNIT = 50
M.HEAT_REMOVED_PER_ICE_UNIT = 40

-- Maximum whole units of each input the generator can draw from its hopper
-- in a single update interval (scripts/thermionic-generator.lua calls
-- M.consume against the hopper's actual contents each interval, so an
-- undersupplied hopper naturally throttles below these caps). At the
-- default 60-tick (1 second) update interval this is roughly a 1 Magmatic
-- Core/sec fuel burn and a 2 Ice/sec coolant draw -- fast enough to be
-- observable within a short playtest, explicitly not tuned against real
-- Vulcanus export throughput (§9.4 open question).
M.MAX_FUEL_PER_INTERVAL = 1
M.MAX_ICE_PER_INTERVAL = 2

-- ---------------------------------------------------------------------
-- Pure functions
-- ---------------------------------------------------------------------

--- How many whole units of an input can actually be drawn this interval,
--- given how many are sitting in the hopper right now. Never more than the
--- available amount and never more than the per-interval cap.
function M.consume(available, max_rate)
  if available < max_rate then
    return available
  end
  return max_rate
end

--- Heat contributed by burning `fuel_consumed` units of Magmatic Core this
--- interval (design doc §9.3 point 1, "the generator self-heats as it
--- produces power").
function M.heat_from_fuel(fuel_consumed)
  return fuel_consumed * M.HEAT_PER_FUEL_UNIT
end

--- Heat removed by consuming `ice_consumed` units of Ice this interval
--- (design doc §9.3 point 2, "ice consumption removes heat").
function M.heat_removed_by_ice(ice_consumed)
  return ice_consumed * M.HEAT_REMOVED_PER_ICE_UNIT
end

--- How many whole units of Ice are actually useful to consume this
--- interval, given `current_temperature` (before this interval's step) and
--- `heat_in` (heat this interval's fuel burn is about to add). Temperature
--- never needs to go below AMBIENT_TEMPERATURE (`next_temperature` floors
--- there), so there is no thermal benefit to removing more heat than is
--- actually present above ambient plus what's about to arrive -- consuming
--- ice beyond that point would be pure waste. Never negative.
function M.max_useful_ice(current_temperature, heat_in)
  local heat_above_ambient = current_temperature - M.AMBIENT_TEMPERATURE
  if heat_above_ambient < 0 then
    heat_above_ambient = 0
  end
  local removable_heat = heat_above_ambient + heat_in
  if removable_heat <= 0 then
    return 0
  end
  return math.floor(removable_heat / M.HEAT_REMOVED_PER_ICE_UNIT)
end

--- Step the stored temperature forward by exactly one interval's worth of
--- physics, using only the previously-stored temperature and this
--- interval's heat in/out. Deliberately takes no notion of elapsed real
--- time or game.tick -- the caller is responsible for calling this once
--- per interval from storage-persisted state, which is what makes it
--- save/reload-safe (see the correctness rule in the phase 4 plan).
function M.next_temperature(current_temperature, heat_in, heat_out)
  local next_temperature = current_temperature + heat_in - heat_out
  if next_temperature < M.AMBIENT_TEMPERATURE then
    next_temperature = M.AMBIENT_TEMPERATURE
  elseif next_temperature > M.MAX_TEMPERATURE then
    next_temperature = M.MAX_TEMPERATURE
  end
  return next_temperature
end

--- The efficiency multiplier (0, 1] for a given stored temperature.
--- - At or below OPTIMAL_MAX: full efficiency (design doc §9.3 -- the
---   optimal band is a plateau, not a single point).
--- - Between OPTIMAL_MAX and OVERHEAT_THRESHOLD: gradual linear decline
---   from 1.0 down to OVERHEAT_FLOOR_EFFICIENCY -- "a warning the player
---   can act on" (§9.3 "why this shape").
--- - Above OVERHEAT_THRESHOLD: a sharp exponential drop (halving every
---   100 degrees past the threshold) toward MIN_EFFICIENCY, which it
---   never goes below -- "the machine keeps running but is barely worth
---   its footprint until it cools" (§9.3 point 4).
function M.efficiency_for_temperature(temperature)
  if temperature <= M.OPTIMAL_MAX then
    return 1.0
  elseif temperature <= M.OVERHEAT_THRESHOLD then
    local span = M.OVERHEAT_THRESHOLD - M.OPTIMAL_MAX
    local frac = (temperature - M.OPTIMAL_MAX) / span
    return 1.0 - frac * (1.0 - M.OVERHEAT_FLOOR_EFFICIENCY)
  else
    local degrees_over = temperature - M.OVERHEAT_THRESHOLD
    local decayed = M.OVERHEAT_FLOOR_EFFICIENCY * (0.5 ^ (degrees_over / 100))
    if decayed < M.MIN_EFFICIENCY then
      return M.MIN_EFFICIENCY
    end
    return decayed
  end
end

--- Electrical output for this interval. `load_fraction` is how much of the
--- maximum fuel draw was actually available (0..1) -- a starved generator
--- produces proportionally less regardless of temperature, and a
--- fuel-starved generator (load_fraction 0) produces nothing at all,
--- matching "determines power output" (§9.2).
function M.power_output(load_fraction, temperature)
  return M.PEAK_POWER_W * load_fraction * M.efficiency_for_temperature(temperature)
end

-- ---------------------------------------------------------------------
-- Worked examples (sanity-checked by eye, and via a real Lua interpreter --
-- see the phase 4 verification report for the actual run). Load this file
-- in a plain `lua` REPL and evaluate these to check the curve by hand:
--
--   local curve = require("scripts.thermionic-curve")
--
-- 1. Cold start, no heat yet:
--      curve.efficiency_for_temperature(0)   --> 1.0   (full efficiency)
--
-- 2. Inside the optimal band:
--      curve.efficiency_for_temperature(500) --> 1.0   (full efficiency)
--
-- 3. Above optimal, below overheat (gradual decline, the "warning"):
--      curve.efficiency_for_temperature(700) --> 0.75
--      -- span = 800-600 = 200; frac = (700-600)/200 = 0.5
--      -- eff  = 1.0 - 0.5 * (1.0 - 0.5) = 0.75
--
-- 4. Just past overheat (sharp drop, non-fatal):
--      curve.efficiency_for_temperature(900) --> 0.25
--      -- degrees_over = 100; decayed = 0.5 * 0.5^(100/100) = 0.25
--
-- 5. Deep in overheat (floored, never destroyed):
--      curve.efficiency_for_temperature(1200) --> 0.08 (MIN_EFFICIENCY floor)
--      -- degrees_over = 400; decayed = 0.5 * 0.5^4 = 0.03125 < 0.08, so floored
--
-- 6. Equilibrium/self-heating check, full fuel + full ice (oversized
--    cooling holds the generator cool and at full efficiency):
--      curve.next_temperature(500, curve.heat_from_fuel(1), curve.heat_removed_by_ice(2))
--      --> 500 + 50 - 80 = 470  (temperature falls, plateaus near ambient
--          over repeated intervals -- an oversized ice supply wins)
--
-- 7. Full fuel, lean ice (heat wins, temperature climbs each interval --
--    a lean platform settles at a lower steady-state *output*, not
--    necessarily a stable temperature, matching §9.3 point 5):
--      curve.next_temperature(500, curve.heat_from_fuel(1), curve.heat_removed_by_ice(1))
--      --> 500 + 50 - 40 = 510
--
-- 8. Fuel-starved (no heat generated, ice still cools if fed -- the two
--    streams are genuinely independent, per §9.2):
--      curve.power_output(0, 700) --> 0  (no fuel, no output, regardless of temperature)
--
-- 9. Idle at ambient with no fuel (don't burn ice for zero thermal
--    benefit, §9.3's ice-throughput tunable):
--      curve.max_useful_ice(curve.AMBIENT_TEMPERATURE, curve.heat_from_fuel(0)) --> 0
--      -- heat_above_ambient = 0; heat_in = 0; removable_heat = 0 --> 0 ice useful
--
-- 10. Warm and still fuelled (some ice still useful, capped below the
--     2/interval rate cap by what's actually there to remove):
--      curve.max_useful_ice(30, curve.heat_from_fuel(1)) --> 2
--      -- heat_above_ambient = 30; heat_in = 50; removable_heat = 80;
--      -- floor(80/40) = 2 (still gets clamped further by the 2/interval
--      -- rate cap in scripts/thermionic-generator.lua, so no change here)
-- ---------------------------------------------------------------------

return M
