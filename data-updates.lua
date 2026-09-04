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

for _, lab in pairs(data.raw.lab) do
  if lab.inputs then
    table.insert(lab.inputs, "sae-geodynamic-science-pack")
  end
end
