-- The arc storms are gone, and with them the Arc Mast.
--
-- A save carried across keeps whatever its forces had researched, so the
-- technology effects have to be re-applied: `sae-arc-masts` no longer exists,
-- the Ignition Array is priced in superconducting stores rather than masts, and
-- a force that had researched the old technology would otherwise keep a recipe
-- for a building the mod no longer defines.
--
-- Entities and items whose prototypes are gone are removed by the engine on
-- load; this only fixes what the forces believe they can build.

for _, force in pairs(game.forces) do
  force.reset_technology_effects()
end
