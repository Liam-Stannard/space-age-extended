-- Pure thermal/efficiency math for the Thermionic Generator.
-- See design/vulcanus-fulgora.md §9.3 for the behaviours this module must
-- reproduce (gradual efficiency decline above the optimal band, a sharp-
-- but-non-fatal drop past overheat, and a load-vs-cooling equilibrium).
--
-- Zero dependency on `game`/`script`/`storage`/any Factorio API -- this file
-- must be `require`-able and callable from a plain Lua 5.2+ REPL outside the
-- game engine (this repo has no unit-test framework; this is the
-- established substitute, see PROGRESS.md). scripts/thermionic-generator.lua
-- is the only thing that wires this into actual entities/events.
--
-- "Temperature" here is the real temperature of the Thermionic Generator's
-- own heat_buffer (it's a genuine `reactor`-type entity, prototypes/
-- entity.lua) -- unlike an earlier version of this module, there's no
-- separate abstract number kept in `storage` to translate to/from real
-- degrees anymore. Self-heating from burning Magmatic Core, and heat-pipe
-- network exchange, both now happen for real via the reactor's own native
-- physics (the engine ignites/consumes fuel itself, and its heat_buffer's
-- `connections` are genuine heat-pipe connection points) -- this module
-- only still needs to (a) apply Ice's cooling directly against that real
-- temperature, and (b) turn a temperature + fuel-availability reading into
-- an efficiency multiplier and an electrical output figure for the paired
-- power-interface entity to actually push onto the grid, since a reactor
-- cannot emit electricity itself. 0 represents cold/idle; larger numbers
-- are hotter.

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

M.AMBIENT_TEMPERATURE = 0

-- Heat removed per unit of Ice consumed, in one update interval. (Heat
-- added per unit of fuel is no longer a constant this module tracks --
-- the reactor's real heat_buffer accumulates that natively from actual
-- fuel combustion; see prototypes/entity.lua's `consumption`/
-- `specific_heat` for the values that now govern it.)
M.HEAT_REMOVED_PER_ICE_UNIT = 40

-- Maximum whole units of Ice the generator can draw from its coolant tank
-- in a single update interval (scripts/thermionic-generator.lua calls
-- M.consume against the tank's actual contents each interval, so an
-- undersupplied tank naturally throttles below this cap). At the default
-- 60-tick (1 second) update interval this is roughly a 2 Ice/sec coolant
-- draw -- fast enough to be observable within a short playtest, explicitly
-- not tuned against real Vulcanus export throughput (§9.4 open question).
M.MAX_ICE_PER_INTERVAL = 2

-- ---------------------------------------------------------------------
-- Pure functions
-- ---------------------------------------------------------------------

--- How many whole units of an input can actually be drawn this interval,
--- given how many are sitting in the tank right now. Never more than the
--- available amount and never more than the per-interval cap.
function M.consume(available, max_rate)
  if available < max_rate then
    return available
  end
  return max_rate
end

--- Heat removed by consuming `ice_consumed` units of Ice this interval
--- (design doc §9.3 point 2, "ice consumption removes heat").
function M.heat_removed_by_ice(ice_consumed)
  return ice_consumed * M.HEAT_REMOVED_PER_ICE_UNIT
end

--- How many whole units of Ice are actually useful to consume this
--- interval, given `current_temperature` (the reactor's real temperature,
--- already reflecting any real fuel-burn heating and real heat-pipe
--- network exchange since last interval). `heat_in`/`heat_out_network` are
--- accepted for callers that still have a nonzero figure for either (kept
--- as parameters rather than dropped so the formula stays self-documenting
--- and this function stays testable in isolation) -- scripts/
--- thermionic-generator.lua currently always passes 0 for both, since
--- both effects are now already baked into `current_temperature` by the
--- time this runs. Temperature never needs to go below AMBIENT_TEMPERATURE,
--- so there is no thermal benefit to removing more heat than is actually
--- present above ambient, plus what's about to arrive from fuel, minus
--- what the network is already removing (or plus what it's pushing in, if
--- `heat_out_network` is negative) -- consuming ice beyond that point
--- would be pure waste. Never negative.
function M.max_useful_ice(current_temperature, heat_in, heat_out_network)
  heat_in = heat_in or 0
  heat_out_network = heat_out_network or 0
  local heat_above_ambient = current_temperature - M.AMBIENT_TEMPERATURE
  if heat_above_ambient < 0 then
    heat_above_ambient = 0
  end
  local removable_heat = heat_above_ambient + heat_in - heat_out_network
  if removable_heat <= 0 then
    return 0
  end
  return math.floor(removable_heat / M.HEAT_REMOVED_PER_ICE_UNIT)
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

--- Electrical output for this interval. `load_fraction` is whether the
--- reactor is actually burning fuel right now (1 if its real status is
--- "working", 0 if it's genuinely out of fuel -- see
--- scripts/thermionic-generator.lua) -- a fuel-starved generator produces
--- nothing at all, regardless of temperature, matching "determines power
--- output" (§9.2).
function M.power_output(load_fraction, temperature)
  return M.PEAK_POWER_W * load_fraction * M.efficiency_for_temperature(temperature)
end

-- ---------------------------------------------------------------------
-- Worked examples (sanity-checked by eye, and via a real Lua interpreter).
-- Load this file in a plain `lua` REPL and evaluate these to check the
-- curve by hand:
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
-- 6. Fuel-starved (no fuel, no output, regardless of temperature):
--      curve.power_output(0, 700) --> 0
--
-- 7. Full output at optimal temperature:
--      curve.power_output(1, 500) --> 4000000  (PEAK_POWER_W, full efficiency)
--
-- 8. Idle at ambient with nothing to cool (don't burn ice for zero
--    thermal benefit, §9.3's ice-throughput tunable):
--      curve.max_useful_ice(curve.AMBIENT_TEMPERATURE, 0, 0) --> 0
--      -- heat_above_ambient = 0; removable_heat = 0 --> 0 ice useful
--
-- 9. Warm reactor, some ice still useful (capped below the 2/interval
--    rate cap by what's actually there to remove):
--      curve.max_useful_ice(90, 0, 0) --> 2
--      -- heat_above_ambient = 90; removable_heat = 90; floor(90/40) = 2
--      -- (still clamped further by the 2/interval rate cap in
--      -- scripts/thermionic-generator.lua, so no change here)
-- ---------------------------------------------------------------------

return M
