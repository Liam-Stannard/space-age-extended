-- 0.1.x -> 0.2.0: the Thermionic Generator became the Quench Turbine.
-- See prototypes/entity.lua for why the design changed.
--
-- The item and recipe renames are handled by the JSON migration alongside
-- this file, which is the only stage that can still see the old names --
-- by the time this Lua runs the old prototypes are gone, so asking for
-- "sae-thermionic-generator" here would raise "invalid item name".
--
-- What JSON cannot do is re-run technology effects, so a force that already
-- researched sae-thermionic-power would never be given the recipes that
-- technology now unlocks (sae-quench-turbine, sae-lean-quench).
--
-- Generators already *placed* on a platform cannot be recovered at all: the
-- engine removes entities whose prototype no longer exists while loading the
-- save, before any migration runs. Nothing here can see them, so the two
-- Thermionic Assemblies each one cost are lost. That is called out in
-- changelog.txt rather than papered over.

for _, force in pairs(game.forces) do
  local thermionic = force.technologies["sae-thermionic-power"]
  if thermionic and thermionic.researched then
    force.reset_technology_effects()
  end
end
