-- Space Age Extended -- data stage.
--
-- The Core (prototypes/core), the one cross-planet tree that is built
-- (prototypes/trees) and the corridor between them (prototypes/corridor.lua),
-- in dependency order: fluids and tiles before the machines that use them,
-- items before recipes, the planet before the technology that unlocks it.

require("prototypes.core.fluids")
require("prototypes.core.tiles")
require("prototypes.core.entities")
require("prototypes.core.items")
require("prototypes.core.storms")
require("prototypes.core.recipes")
require("prototypes.core.machines")
require("prototypes.core.crust-tap")
require("prototypes.core.resources")
require("prototypes.core.planet")
require("prototypes.core.intermediates")
require("prototypes.core.endgame")
require("prototypes.core.technology")
require("prototypes.trees.fulgora-aquilo")
require("prototypes.corridor")

-- Last, deliberately: it re-points every item and fluid the files above defined
-- into the Core's own subgroups, so it has to run after all of them exist.
require("prototypes.core.groups")

-- And the placeholder report, which has to be last for the same reason: a
-- building is only wearing borrowed sprites if nothing replaced them by the end.
require("prototypes.derive").log_placeholders()
