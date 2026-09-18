-- Edits to vanilla prototypes.
--
-- The mod's rule is that it adds and does not alter, and this file holds the
-- only exception the rule cannot avoid: a new science pack is useless unless
-- something will consume it, and labs list the packs they accept explicitly.
--
-- Adding to that list takes nothing away. Every vanilla pack still works in
-- every lab exactly as before, and research still happens wherever the player
-- already researches -- what the mod restricts is where the pack can be *made*,
-- which is the Core and nowhere else.

-- Guarded, because this branch is the Core's landing and nothing past it: the
-- pack is on master, and a lab told to accept a tool that does not exist fails
-- the data stage. The day the pack returns, this runs again without edits.
if data.raw.tool["sae-geodynamic-science-pack"] then
  for _, lab in pairs(data.raw.lab) do
    if lab.inputs then
      table.insert(lab.inputs, "sae-geodynamic-science-pack")
    end
  end
end

-- The second exception, and the same argument.
--
-- `sae-cast-structure` and `sae-crust-propellant` are alternate routes to two
-- vanilla items, in the shape vanilla itself uses: Vulcanus has
-- `casting-low-density-structure` beside the assembled one, Gleba has
-- `rocket-fuel-from-jelly`. Vanilla lists *every* such alternate in the matching
-- productivity technology -- `low-density-structure-productivity` names both of
-- its recipes, `rocket-fuel-productivity` names three -- because a route the
-- research cannot reach is a route no one takes once they have the research.
--
-- Left out, the Core's alternates would silently become the worse option at the
-- exact point in the game the player is most likely to have those technologies
-- finished. This adds ours to the lists and changes nothing else about them.

local PRODUCTIVITY =
{
  ["low-density-structure-productivity"] = "sae-cast-structure",
  ["rocket-fuel-productivity"] = "sae-crust-propellant",
  ["processing-unit-productivity"] = "sae-valve-processor"
}

for tech_name, recipe_name in pairs(PRODUCTIVITY) do
  local tech = data.raw.technology[tech_name]
  -- The recipe check is the same guard as the lab's: all three alternates are
  -- on master, and a productivity effect naming a missing recipe is a load error.
  if not data.raw.recipe[recipe_name] then
    log("[sae] " .. recipe_name .. " is not on this branch; its productivity effect is skipped")
  elseif tech and tech.effects then
    table.insert(tech.effects,
      { type = "change-recipe-productivity", recipe = recipe_name, change = 0.1 })
  else
    log("[sae] " .. tech_name .. " is not present; " .. recipe_name
        .. " will not benefit from its productivity research")
  end
end
