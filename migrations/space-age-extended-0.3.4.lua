-- Vulcanus <-> Fulgora is built: magnetar alloy is made for real, and its stub
-- recipe is gone.
--
-- **The item stays.** It keeps the stub's name, sae-magnetar-alloy, so the
-- engine has nothing to migrate: whatever a save holds -- in chests,
-- inventories, on belts, in a rocket -- is still magnetar alloy. What no longer
-- exists is the recipe `sae-magnetar-alloy-stub`, which crafted it from one iron
-- plate; an assembler that was set to it loses its recipe on load, which the
-- engine does, not this file.
--
-- **The unlocks moved too.** Ozone capture now unlocks the ozone collector and
-- Induction foundry the induction foundry, so a force that had researched
-- either gets its building. Re-applying technology effects recomputes what each
-- force may craft from what it has researched; running it twice reaches the
-- same state as once.
--
-- Obsidian on a Vulcanus the save had already generated is not done here but
-- in scripts/trees/vulcanus-fulgora.lua, on the configuration change, because
-- the surface's map gen settings are the thing to change and that check runs on
-- every later change too.

for _, force in pairs(game.forces) do
  force.reset_technology_effects()
end
