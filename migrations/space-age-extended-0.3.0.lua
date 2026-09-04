-- Recipes and technologies have moved around a good deal during the rebuild,
-- and a save made against an earlier version keeps whatever its forces had
-- unlocked at the time. Resetting technology effects re-applies every unlock
-- from the current prototypes, so a save carried forward gets the recipes its
-- researched technologies now grant, and loses ones they no longer do.
--
-- Cheap, idempotent, and the standard remedy for exactly this.

for _, force in pairs(game.forces) do
  force.reset_technology_effects()
end
