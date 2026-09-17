-- The Core precipitates its own fuel now, and three effects changed hands.
--
-- `sae-radiant-power` is new, and it is where the Reaction Plant, the radiant
-- precipitation recipe and the radiant generator all unlock. Two of those three
-- came from somewhere else: the generator from `sae-corridor-seeding` and the
-- recipe from `sae-orbital-lift`. A save carried across keeps whatever its
-- forces had researched, so without this a force that had finished Corridor
-- Seeding would keep a generator recipe the technology no longer grants, and a
-- force that finishes the new technology would not be given it.
--
-- The recipe itself changed under the same name -- `sae-radiant-precipitation`
-- takes crust gas rather than helium-3 and runs in the new `sae-reaction`
-- category, so it no longer fits a chemical plant. Any plant standing with it
-- set loses its recipe on load; the engine does that, not this file.
--
-- Re-applying effects is idempotent: it recomputes what each force may build
-- from the technologies it has researched, so running it twice reaches the
-- same state as running it once.

for _, force in pairs(game.forces) do
  force.reset_technology_effects()
end
