-- The Core scaled back to its landing, and its power made locally.
--
-- Two changes meet in this version, and both move technology effects.
--
-- The cut. The mod keeps Crust tapping, Core survey and Radiant power, the
-- radiant generator line, and the five capstone products as items, and removes
-- everything past the first plate: the melt line, the farm, the lift, the
-- integrations, geodynamic science, the carbonyl branch and the Ignition Array.
-- Sixteen technologies no longer exist. Entities and items whose prototypes are
-- gone are removed by the engine on load; nothing has been played, so nothing
-- is lost.
--
-- Radiant power. `sae-radiant-power` is new, and it is where the Reaction
-- Plant, the radiant precipitation recipe, the radiant generator and radiant
-- crushing all unlock. The generator used to come from `sae-corridor-seeding`
-- and the recipe from `sae-orbital-lift`. The recipe also changed under the
-- same name -- `sae-radiant-precipitation` takes crust gas rather than helium-3
-- and runs in the new `sae-reaction` category, so it no longer fits a chemical
-- plant. Any plant standing with it set loses its recipe on load; the engine
-- does that, not this file.
--
-- A save carried across keeps whatever its forces had researched, so the
-- effects are re-applied. That is idempotent: it recomputes what each force may
-- build from the technologies it has researched, so running it twice reaches the
-- same state as running it once.

for _, force in pairs(game.forces) do
  force.reset_technology_effects()
end
