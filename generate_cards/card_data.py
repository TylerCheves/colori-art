"""Load and expand card data from cards.yaml or inline definitions."""

import os
from pathlib import Path

# Package root: this directory (generate_cards/)
PKG_DIR = Path(__file__).resolve().parent

# Card dimensions
WIDTH, HEIGHT = 750, 1050

# Directories
BG_DIR = PKG_DIR / "backgrounds"
BASE_BG_DIR = PKG_DIR / "backgrounds" / "base"
ARTWORK_DIR = PKG_DIR / "backgrounds" / "artwork"
COMPOSED_DIR = PKG_DIR / "composed"
ICON_DIR = PKG_DIR / "iconography"
PIG_DIR = ICON_DIR / "pigments"
PRINT_DIR = PKG_DIR / "print"


# ── Dye cards ────────────────────────────────────────────────────────────────

DYE_CARDS = [
    # Starters -- Sell, 1 pigment
    {
        "name": "basic-red", "title": "Red", "ability": "sell",
        "pigments": ["red-pigment"], "color": (160, 30, 30),
        "bg_color": "deep crimson red",
        "touchup_color_desc": "deep red/crimson",
        "art": "A simple clay bowl filled with a generic red dye bath. Plain and functional -- a beginner's tool. The bowl is chipped and well-used.",
    },
    {
        "name": "basic-yellow", "title": "Yellow", "ability": "sell",
        "pigments": ["yellow-pigment"], "color": (160, 120, 10),
        "bg_color": "warm golden yellow",
        "touchup_color_desc": "warm golden yellow",
        "art": "A simple clay bowl filled with a generic yellow dye bath. Plain and functional -- a beginner's tool. The bowl is chipped and well-used.",
    },
    {
        "name": "basic-blue", "title": "Blue", "ability": "sell",
        "pigments": ["blue-pigment"], "color": (30, 70, 150),
        "bg_color": "rich cerulean blue",
        "touchup_color_desc": "rich blue",
        "art": "A simple clay bowl filled with a generic blue dye bath. Plain and functional -- a beginner's tool. The bowl is chipped and well-used.",
    },
    # Pure primaries -- Destroy Cards x1, 3 same-color pigments
    {
        "name": "kermes", "title": "Kermes", "ability": "destroyCards",
        "pigments": ["red-pigment"] * 3, "color": (150, 25, 25),
        "bg_color": "scarlet red and crimson",
        "touchup_color_desc": "scarlet red",
        "art": "A gnarled Mediterranean oak branch crawling with tiny scarlet insects. A dyer's hand reaches in with a small brush, carefully sweeping the precious creatures into a ceramic bowl already stained deep crimson.",
    },
    {
        "name": "weld", "title": "Weld", "ability": "destroyCards",
        "pigments": ["yellow-pigment"] * 3, "color": (155, 125, 10),
        "bg_color": "electric yellow and gold",
        "touchup_color_desc": "golden yellow",
        "art": "Tall spikes of tiny yellow-green flowers bundled and hanging upside down to dry from workshop rafters. Below them, a dye bath glows an almost electric yellow, a skein of wool being lifted out with a wooden rod, dripping brilliant gold.",
    },
    {
        "name": "woad", "title": "Woad", "ability": "destroyCards",
        "pigments": ["blue-pigment"] * 3, "color": (25, 50, 120),
        "bg_color": "deep indigo blue and blue-black",
        "touchup_color_desc": "deep indigo blue",
        "art": "Broad green leaves being crushed in a stone trough by wooden mallets, the pulp formed into dark balls set out to dry on wooden racks. A fermentation vat in the background bubbles with a foul-smelling blue-black liquor, a copper-blue sheen on its surface.",
    },
    # Primaries -- Workshop x3, 2+1 mixed primary pigments
    {
        "name": "lac", "title": "Lac", "ability": "workshop3",
        "pigments": ["red-pigment", "red-pigment", "yellow-pigment"],
        "color": (155, 35, 40),
        "bg_color": "deep crimson red with golden amber undertones",
        "touchup_color_desc": "warm crimson red",
        "art": "Tiny lac insects cluster on thin tropical branches, their resinous secretion forming thick glossy crusts of deep crimson. A dyer cracks off strips of the shellac, crushing them in a stone mortar to release brilliant red-gold pigment that pools in a ceramic dish.",
    },
    {
        "name": "brazilwood", "title": "Brazilwood", "ability": "workshop3",
        "pigments": ["red-pigment", "red-pigment", "blue-pigment"],
        "color": (140, 30, 70),
        "bg_color": "deep crimson-violet and rich red-purple",
        "touchup_color_desc": "deep red-violet",
        "art": "Heavy logs of dark reddish heartwood stacked in a Venice warehouse, fresh sawdust on the floor glowing an impossible scarlet. A dyer planes thin shavings into a copper pot of simmering water, the liquid turning a rich crimson-violet as the wood surrenders its color.",
    },
    {
        "name": "pomegranate", "title": "Pomegranate", "ability": "workshop3",
        "pigments": ["yellow-pigment", "yellow-pigment", "red-pigment"],
        "color": (175, 110, 20),
        "bg_color": "warm golden-yellow with rosy undertones",
        "touchup_color_desc": "warm golden",
        "art": "Split pomegranates reveal their jeweled seeds, but the thick leathery rinds are the dyer's prize. Dried rinds pile on a workshop table, their tannin-rich flesh being boiled in a copper pot to produce a warm golden-yellow bath that deepens to amber.",
    },
    {
        "name": "sumac", "title": "Sumac", "ability": "workshop3",
        "pigments": ["yellow-pigment", "yellow-pigment", "blue-pigment"],
        "color": (130, 140, 30),
        "bg_color": "lemony yellow with olive-green undertones",
        "touchup_color_desc": "warm yellow-green",
        "art": "Fuzzy dark red sumac berry clusters dry on wooden racks alongside their serrated leaves. A dyer crushes the dried berries between millstones, the resulting powder producing a bright lemony-yellow dye bath with hints of olive green swirling at the edges.",
    },
    {
        "name": "elderberry", "title": "Elderberry", "ability": "workshop3",
        "pigments": ["blue-pigment", "blue-pigment", "red-pigment"],
        "color": (60, 30, 120),
        "bg_color": "deep blue-violet and dark purple",
        "touchup_color_desc": "deep blue-violet",
        "art": "Cascades of tiny dark purple elderberries hang heavy from their stems, juice already staining the picker's fingers a deep indigo. In the workshop, crushed berries steep in a clay vat, producing a rich blue-violet liquor that shifts between purple and blue in the light.",
    },
    {
        "name": "turnsole", "title": "Turnsole", "ability": "workshop3",
        "pigments": ["blue-pigment", "blue-pigment", "yellow-pigment"],
        "color": (35, 85, 120),
        "bg_color": "blue-violet with cool green undertones",
        "touchup_color_desc": "cool blue-violet",
        "art": "Small grey-green seeds of the turnsole plant spread on linen cloths, their juice pressed out by heavy stones. The pale green liquid oxidizes in the air, transforming to a vibrant blue-violet that the dyer captures in cloth strips hung to dry on wooden frames.",
    },
    # Secondaries -- Mix Colors x2, 2 pigments
    {
        "name": "madder", "title": "Madder", "ability": "mix2",
        "pigments": ["orange-pigment", "red-pigment"], "color": (155, 45, 30),
        "bg_color": "ruddy orange-red and deep red",
        "touchup_color_desc": "warm red-orange",
        "art": "Thick ruddy roots being pulled from dark earth by weathered hands, soil still clinging to them. A cutting board nearby shows sliced cross-sections of the root revealing rings of deepening red toward the center.",
    },
    {
        "name": "turmeric", "title": "Turmeric", "ability": "mix2",
        "pigments": ["orange-pigment", "yellow-pigment"], "color": (180, 110, 15),
        "bg_color": "bright orange and deep yellow",
        "touchup_color_desc": "rich amber orange",
        "art": "Knobbly orange-yellow roots freshly cut, their interior a shocking bright orange that stains everything it touches. A merchant's hands are permanently yellowed from handling the spice. Powder spills from a cloth sack onto a market stall.",
    },
    {
        "name": "dyers-greenweed", "title": "Dyer's Greenweed", "ability": "mix2",
        "pigments": ["green-pigment", "yellow-pigment"], "color": (80, 120, 20),
        "bg_color": "bright yellow-green and chartreuse",
        "touchup_color_desc": "earthy green",
        "art": "Low bushy shrubs covered in small bright yellow flowers growing along a stone wall. A dyer's apprentice gathers armfuls of the flowering branches, their apron already stained yellow from the morning's harvest.",
    },
    {
        "name": "verdigris", "title": "Verdigris", "ability": "mix2",
        "pigments": ["green-pigment", "blue-pigment"], "color": (15, 110, 100),
        "bg_color": "brilliant blue-green and teal",
        "touchup_color_desc": "teal blue-green",
        "art": "Copper plates stacked with grape skins and pomace in a sealed clay pot, pulled open to reveal the metal surfaces crusted with a brilliant blue-green patina. A craftsman carefully scrapes the vivid green powder into a glass bottle.",
    },
    {
        "name": "orchil", "title": "Orchil", "ability": "mix2",
        "pigments": ["purple-pigment", "red-pigment"], "color": (130, 40, 90),
        "bg_color": "reddish-purple and violet",
        "touchup_color_desc": "reddish purple",
        "art": "Crusts of pale grey-green lichen being scraped from coastal rocks into a basket. In a workshop, the lichen ferments in covered clay pots, the lid lifted to reveal a vivid reddish-purple paste. Stained rags hang on a line behind.",
    },
    {
        "name": "logwood", "title": "Logwood", "ability": "mix2",
        "pigments": ["purple-pigment", "blue-pigment"], "color": (70, 35, 120),
        "bg_color": "deep blue-violet and purple",
        "touchup_color_desc": "deep blue-purple",
        "art": "Dark heartwood chips steeping in a copper cauldron, the liquid a deep blue-violet that shifts color as it catches the light. A dyer tests the shade by dipping a white linen strip, pulling it out to reveal a rich purple-blue stain spreading through the fibers.",
    },
    # Tertiaries -- Sell, 1 tertiary pigment
    {
        "name": "vermilion", "title": "Vermilion", "ability": "sell",
        "pigments": ["vermilion-pigment"], "color": (190, 55, 20),
        "bg_color": "brilliant orange-red and scarlet",
        "touchup_color_desc": "vivid red-orange",
        "art": "Brilliant orange-red crystals of cinnabar in a lined wooden box, glowing almost unnaturally bright. An apothecary grinds them carefully with a cloth over his mouth, the resulting powder a shocking scarlet against the dark stone mortar.",
    },
    {
        "name": "saffron", "title": "Saffron", "ability": "sell",
        "pigments": ["amber-pigment"], "color": (185, 100, 15),
        "bg_color": "red-orange and amber gold",
        "touchup_color_desc": "warm amber",
        "art": "Delicate purple crocus flowers laid open on a marble table, their precious red-orange stigmas being plucked with tweezers by careful hands. Only a tiny pile of threads sits in a golden dish -- a fortune's worth of the rarest spice.",
    },
    {
        "name": "persian-berries", "title": "Persian Berries", "ability": "sell",
        "pigments": ["chartreuse-pigment"], "color": (90, 115, 15),
        "bg_color": "chartreuse yellow-green",
        "touchup_color_desc": "yellow-green",
        "art": "Small clusters of dark green-to-black berries on thorny branches, being sorted by a merchant who has laid them out on a woven tray. Some crushed berries in a ceramic bowl show their bright chartreuse-yellow juice against the white glaze.",
    },
    {
        "name": "azurite", "title": "Azurite", "ability": "sell",
        "pigments": ["teal-pigment"], "color": (20, 90, 150),
        "bg_color": "vivid sky blue and teal",
        "touchup_color_desc": "bright teal blue",
        "art": "A rough chunk of brilliant blue mineral with botryoidal surface, sitting on a vendecolori's shop counter alongside scales and small brass weights. The stone seems to glow from within, a vivid sky blue against the dark wood.",
    },
    {
        "name": "indigo", "title": "Indigo", "ability": "sell",
        "pigments": ["indigo-pigment"], "color": (35, 30, 105),
        "bg_color": "deep blue-black and iridescent metallic blue",
        "touchup_color_desc": "deep indigo violet",
        "art": "A merchant opens a tightly wrapped bundle from the East, revealing dense cakes of dark blue-black pigment. He snaps a piece and the fracture line gleams an iridescent metallic blue. Bolts of deep blue silk hang in the background.",
    },
    {
        "name": "cochineal", "title": "Cochineal", "ability": "sell",
        "pigments": ["magenta-pigment"], "color": (170, 25, 70),
        "bg_color": "brilliant carmine-red and magenta",
        "touchup_color_desc": "vivid magenta-pink",
        "art": "A cactus pad covered in white cottony clusters, split open to reveal brilliant carmine-red insects beneath. In the background, a Spanish galleon sits in Venice's harbor, barrels of dried cochineal being unloaded onto the dock.",
    },
]


# ── Action cards ─────────────────────────────────────────────────────────────

ACTION_CARDS = [
    {
        "name": "alum", "title": "Alum",
        "ability": "destroyCards",
        "bottom": {"type": "coin"},
        "bg_color": "pale translucent whites, warm golds, and soft cream tones",
        "touchup_color_desc": "white",
        "art": (
            "A pale, translucent crystalline rock sitting on a merchant's scale, one side freshly broken "
            "to reveal a glassy interior. Gold ducats are stacked beside it on the counter -- the two "
            "commodities practically interchangeable in Venice. A ledger book lies open, recording the transaction."
        ),
    },
    {
        "name": "cream-of-tartar", "title": "Cream of Tartar",
        "ability": "destroyCards",
        "bottom": {"type": "draw_cards", "count": "+3"},
        "bg_color": "reddish-pink crystals, dark wood tones, and pale sparkling whites",
        "touchup_color_desc": "white",
        "art": (
            "Reddish crystalline crusts being chipped from the inside of a dark wine barrel with a small "
            "chisel. The scraped crystals collect in a linen cloth below, pale pink and sparkling. Empty "
            "wine barrels are stacked high in a Venetian cellar, an endless supply of this useful byproduct."
        ),
    },
    {
        "name": "gum-arabic", "title": "Gum Arabic",
        "ability": "destroyCards",
        "bottom": {"type": "pigment_choice", "pigments": ["orange-pigment", "green-pigment", "purple-pigment"]},
        "bg_color": "amber-golden resin, warm honey tones, and rich orange-green-purple accents",
        "touchup_color_desc": "white",
        "art": (
            "Amber-golden lumps of dried tree resin spread on a marble slab, some already ground to a fine "
            "powder in a stone mortar. A craftsman presses the sticky powder into a wooden mold alongside "
            "concentrated dye, forming a dense colored block. Finished blocks in orange, green, and purple "
            "dry on a shelf behind."
        ),
    },
    {
        "name": "potash", "title": "Potash",
        "ability": "draw2",
        "bottom": {"type": "workshop_picks", "count": "3"},
        "bg_color": "coarse grey-white, warm earth tones, and muted browns",
        "touchup_color_desc": "white",
        "art": (
            "A coarse grey-white powder being scooped from a heavy burlap sack with a wooden ladle, clouds "
            "of fine dust rising in the workshop air. Three dye vats stand in a row behind, each receiving "
            "a measure. A brick kiln for burning wood to ash smolders in the courtyard beyond the door."
        ),
    },
    {
        "name": "chalk", "title": "Chalk",
        "ability": "sell",
        "bottom": {"type": "pigment_choice", "pigments": ["red-pigment", "yellow-pigment", "blue-pigment"]},
        "bg_color": "soft white, with red, yellow, and blue pigment accents",
        "touchup_color_desc": "white",
        "art": (
            "A crumbling block of soft white chalk on a worn workbench, shavings and dust scattered around it. "
            "Three small piles of freshly made pigment powder sit nearby -- red, yellow, and blue -- each made "
            "by grinding chalk with a different raw colorant. A flat grinding stone shows streaks of all three colors."
        ),
    },
    {
        "name": "vinegar", "title": "Vinegar",
        "ability": "destroyCards",
        "bottom": {"type": "swap"},
        "bg_color": "amber liquid tones, warm copper, and dark glass greens",
        "touchup_color_desc": "white",
        "art": (
            "A row of dark glass bottles filled with amber and reddish vinegar on a wooden shelf in a Venice "
            "dye workshop. One bottle is uncorked, its sharp contents being poured into a shallow ceramic dish "
            "alongside soaking fabric. Copper funnels and stained linen cloths hang nearby."
        ),
    },
    {
        "name": "linseed-oil", "title": "Linseed Oil",
        "ability": "destroyCards",
        "bottom": {"type": "mix", "count": "2"},
        "bg_color": "warm golden-amber oil, dark glass bottles, rich honey tones",
        "touchup_color_desc": "white",
        "art": (
            "A heavy dark glass bottle of golden linseed oil being poured into a shallow ceramic dish, "
            "the thick amber liquid catching warm candlelight. Flax seeds are scattered on the workbench "
            "beside a small hand press. Stained rags and brushes lie nearby in a Venice workshop."
        ),
    },
]


# ── Material cards ──────────────────────────────────────────────────────

MATERIAL_CARDS = [
    # Starters (not in draft deck -- each player gets one)
    {
        "name": "ceramics", "title": "Ceramics",
        "material_types": ["ceramic"], "ability": "workshop3",
        "color_pips": [], "bg_type": "ceramic",
    },
    {
        "name": "paintings", "title": "Paintings",
        "material_types": ["painting"], "ability": "workshop4",
        "color_pips": [], "bg_type": "painting",
    },
    {
        "name": "textiles", "title": "Textiles",
        "material_types": ["textile"], "ability": "workshop2",
        "color_pips": [], "bg_type": "textile",
    },
    # Double materials
    {
        "name": "fine-ceramics", "title": "Fine Ceramics",
        "material_types": ["ceramic", "ceramic"], "ability": "sell",
        "color_pips": [], "bg_type": "ceramic",
    },
    {
        "name": "fine-paintings", "title": "Fine Paintings",
        "material_types": ["painting", "painting"], "ability": "sell",
        "color_pips": [], "bg_type": "painting",
    },
    {
        "name": "fine-textiles", "title": "Fine Textiles",
        "material_types": ["textile", "textile"], "ability": "sell",
        "color_pips": [], "bg_type": "textile",
    },
    # Material + color pip
    {
        "name": "terra-cotta", "title": "Terra Cotta",
        "material_types": ["ceramic"], "ability": "workshop2",
        "color_pips": ["red"], "bg_type": "ceramic",
    },
    {
        "name": "ochre-ware", "title": "Ochre Ware",
        "material_types": ["ceramic"], "ability": "workshop2",
        "color_pips": ["yellow"], "bg_type": "ceramic",
    },
    {
        "name": "cobalt-ware", "title": "Cobalt Ware",
        "material_types": ["ceramic"], "ability": "workshop2",
        "color_pips": ["blue"], "bg_type": "ceramic",
    },
    {
        "name": "cinnabar-canvas", "title": "Cinnabar & Canvas",
        "material_types": ["painting"], "ability": "workshop2",
        "color_pips": ["red"], "bg_type": "painting",
    },
    {
        "name": "orpiment-canvas", "title": "Orpiment & Canvas",
        "material_types": ["painting"], "ability": "workshop2",
        "color_pips": ["yellow"], "bg_type": "painting",
    },
    {
        "name": "ultramarine-canvas", "title": "Ultramarine & Canvas",
        "material_types": ["painting"], "ability": "workshop2",
        "color_pips": ["blue"], "bg_type": "painting",
    },
    {
        "name": "alizarin-fabric", "title": "Alizarin & Fabric",
        "material_types": ["textile"], "ability": "workshop2",
        "color_pips": ["red", "red"], "bg_type": "textile",
    },
    {
        "name": "fustic-fabric", "title": "Fustic & Fabric",
        "material_types": ["textile"], "ability": "workshop2",
        "color_pips": ["yellow", "yellow"], "bg_type": "textile",
    },
    {
        "name": "pastel-fabric", "title": "Pastel & Fabric",
        "material_types": ["textile"], "ability": "workshop2",
        "color_pips": ["blue", "blue"], "bg_type": "textile",
    },
    # Dual materials
    {
        "name": "clay-canvas", "title": "Clay & Canvas",
        "material_types": ["ceramic", "painting"], "ability": "sell",
        "color_pips": [], "bg_type": "ceramic",
    },
    {
        "name": "clay-fabric", "title": "Clay & Fabric",
        "material_types": ["ceramic", "textile"], "ability": "sell",
        "color_pips": [], "bg_type": "ceramic",
    },
    {
        "name": "canvas-fabric", "title": "Canvas & Fabric",
        "material_types": ["painting", "textile"], "ability": "sell",
        "color_pips": [], "bg_type": "painting",
    },
]


# ── Buyer/Project cards ─────────────────────────────────────────────────────

# Material icon filenames
MATERIAL_ICON = {
    "textile": "textile.png",
    "ceramic": "ceramics.png",
    "painting": "painting.png",
}

# Cost (star value) per material type
BUYER_COST = {
    "textile": 2,
    "ceramic": 3,
    "painting": 4,
}

# All 51 buyer card names
BUYER_CARDS = [
    # Textiles (18)
    "vermilion-textile", "amber-textile", "chartreuse-textile",
    "teal-textile", "indigo-textile", "magenta-textile",
    "orange-red-textile", "orange-yellow-textile", "orange-blue-textile",
    "green-red-textile", "green-yellow-textile", "green-blue-textile",
    "purple-red-textile", "purple-yellow-textile", "purple-blue-textile",
    "red-red-red-textile", "yellow-yellow-yellow-textile", "blue-blue-blue-textile",
    # Ceramics (18)
    "vermilion-red-ceramic", "vermilion-yellow-ceramic", "vermilion-blue-ceramic",
    "amber-red-ceramic", "amber-yellow-ceramic", "amber-blue-ceramic",
    "chartreuse-red-ceramic", "chartreuse-yellow-ceramic", "chartreuse-blue-ceramic",
    "teal-red-ceramic", "teal-yellow-ceramic", "teal-blue-ceramic",
    "indigo-red-ceramic", "indigo-yellow-ceramic", "indigo-blue-ceramic",
    "magenta-red-ceramic", "magenta-yellow-ceramic", "magenta-blue-ceramic",
    # Paintings (18)
    "vermilion-orange-painting", "vermilion-green-painting", "vermilion-purple-painting",
    "amber-orange-painting", "amber-green-painting", "amber-purple-painting",
    "chartreuse-orange-painting", "chartreuse-green-painting", "chartreuse-purple-painting",
    "teal-orange-painting", "teal-green-painting", "teal-purple-painting",
    "indigo-orange-painting", "indigo-green-painting", "indigo-purple-painting",
    "magenta-orange-painting", "magenta-green-painting", "magenta-purple-painting",
]


# ── Print layout copy counts ────────────────────────────────────────────────

DYE_PRINT_COPIES = [
    # Starters: 5 copies (one per player, up to 5 players)
    ("basic-red", 5), ("basic-yellow", 5), ("basic-blue", 5),
    # Pure primaries: 3 copies each
    ("kermes", 3), ("weld", 3), ("woad", 3),
    # Primaries: 3 copies each
    ("lac", 3), ("brazilwood", 3), ("pomegranate", 3),
    ("sumac", 3), ("elderberry", 3), ("turnsole", 3),
    # Secondaries: 3 copies each
    ("madder", 3), ("turmeric", 3), ("dyers-greenweed", 3),
    ("verdigris", 3), ("orchil", 3), ("logwood", 3),
    # Tertiaries: 3 copies each
    ("vermilion", 3), ("saffron", 3), ("persian-berries", 3),
    ("azurite", 3), ("indigo", 3), ("cochineal", 3),
]

ACTION_PRINT_COPIES = [
    ("chalk", 5),  # Starter: 1 per player
    ("alum", 4), ("cream-of-tartar", 4),
    ("gum-arabic", 4), ("potash", 4),
    ("vinegar", 4), ("linseed-oil", 4),
]

MATERIAL_PRINT_COPIES = [
    # Starters: 5 copies (one per player, up to 5 players)
    ("ceramics", 5), ("paintings", 5), ("textiles", 5),
    # Draft materials: 1 copy each
    ("fine-ceramics", 1), ("fine-paintings", 1), ("fine-textiles", 1),
    ("terra-cotta", 1), ("ochre-ware", 1), ("cobalt-ware", 1),
    ("cinnabar-canvas", 1), ("orpiment-canvas", 1), ("ultramarine-canvas", 1),
    ("alizarin-fabric", 1), ("fustic-fabric", 1), ("pastel-fabric", 1),
    ("clay-canvas", 1), ("clay-fabric", 1), ("canvas-fabric", 1),
]


def parse_buyer_name(name):
    """Parse buyer card name into (colors_list, material_string)."""
    parts = name.split("-")
    material = parts[-1]
    colors = parts[:-1]
    return colors, material


def get_all_cards(card_type=None):
    """Return flat list of card dicts/names filtered by type.

    card_type: 'dye', 'action', 'buyer', or None for all.
    Returns dict with keys: dye, action, buyer.
    """
    result = {}
    if card_type is None or card_type == "dye":
        result["dye"] = list(DYE_CARDS)
    if card_type is None or card_type == "action":
        result["action"] = list(ACTION_CARDS)
    if card_type is None or card_type == "material":
        result["material"] = list(MATERIAL_CARDS)
    if card_type is None or card_type == "buyer":
        result["buyer"] = list(BUYER_CARDS)
    return result


def filter_cards_by_name(cards, names):
    """Filter a list of card dicts or name strings by a set of names."""
    if names is None:
        return cards
    name_set = set(names)
    if cards and isinstance(cards[0], dict):
        return [c for c in cards if c["name"] in name_set]
    return [c for c in cards if c in name_set]
