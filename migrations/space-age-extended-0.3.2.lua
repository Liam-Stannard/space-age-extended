-- The Core scaled back to its landing.
--
-- This version keeps Crust tapping, Core survey and the radiant generator line,
-- and the five capstone products as items -- and removes everything past the
-- first plate: the melt line, the farm, the lift, the integrations, geodynamic
-- science, the carbonyl branch and the Ignition Array. They are on master.
--
-- A save carried across keeps whatever its forces had researched, so the
-- technology effects are re-applied: sixteen technologies no longer exist, and
-- one is new. Entities and items whose prototypes are gone are removed by the
-- engine on load. Nothing has been played, so nothing is lost.

for _, force in pairs(game.forces) do
  force.reset_technology_effects()
end
