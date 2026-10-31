-- Vulcanus <-> Fulgora's edits to vanilla prototypes that other mods may also
-- define or replace: run from data-final-fixes.lua, after every mod's data and
-- data-updates, so lightning added or reassigned there is covered too.

local derive = require("prototypes.derive")

local OZONE_COLLECTOR = "sae-ozone-collector"
-- The script effect's id; scripts/trees/vulcanus-fulgora.lua matches it.
local OZONE_STRIKE = "sae-ozone-strike"

-- Every strike on an attractor raises the script effect, with the attractor
-- hit as its target (T02: under target_effects; under source_effects it carries
-- only the lightning). Appended to every lightning, beside whatever it already
-- does; the script acts only on a hit whose target is an ozone collector.
for _, lightning in pairs(data.raw.lightning or {}) do
  local hits = {}
  for _, trigger in ipairs(derive.each(lightning.attractor_hit_effect)) do hits[#hits + 1] = trigger end
  hits[#hits + 1] =
  {
    type = "direct",
    action_delivery = { type = "instant", target_effects = { { type = "script", effect_id = OZONE_STRIKE } } }
  }
  lightning.attractor_hit_effect = hits
end

-- Fulgora's lightning seeks the ozone collector as it seeks the vanilla one:
-- the same bonus, ranked straight after the vanilla collector's rule and so
-- ahead of the catch-all attractor rule. Here rather than in the data stage
-- proper because it is placed relative to another rule, so it goes in once the
-- list has its final shape (a mod replacing Fulgora's lightning properties in
-- its data-updates would otherwise drop it).
local fulgora = data.raw.planet["fulgora"]
local rules = fulgora and fulgora.lightning_properties and fulgora.lightning_properties.priority_rules
if rules then
  local at, bonus = 1, 10000
  for i, rule in ipairs(rules) do
    if rule.type == "id" and rule.string == "lightning-collector" then
      at, bonus = i + 1, rule.priority_bonus
      break
    end
  end
  table.insert(rules, at, { type = "id", string = OZONE_COLLECTOR, priority_bonus = bonus })
else
  log("[sae] Fulgora has no lightning priority rules; the ozone collector gets no priority there")
end
