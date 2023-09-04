def build_kite_variant(name, variants=None, slug=None, year=None):
    if variants is None:
        variants = []
    return {
        "name": name,
        "variants": variants,
        "slug": slug,
        "year": year
    }


brands_and_models = [
    {
        "slug": "airush",
        "name": "Airush",
        "variants": [],
        "kites": [
            build_kite_variant("Lift"),
            build_kite_variant("Lift V2"),
            build_kite_variant("Lift V3"),
            build_kite_variant("Lift V13"),
            build_kite_variant("Lithium Progression"),
            build_kite_variant("Lithium Progression V2"),
            build_kite_variant("Lithium V11"),
            build_kite_variant("Lithium V12"),
            build_kite_variant("Lithium V13"),
            build_kite_variant("One Progression"),
            build_kite_variant("One V2"),
            build_kite_variant("Razor V9"),
            build_kite_variant("Razor V10"),
            build_kite_variant("Session", ["session wave"]),
            build_kite_variant("Ultra Team",
                               ["Ultra Team Ho'okipa", "Ultra Team Hookipa"],
                               "ultra_team",
                               "2023"),
            build_kite_variant("Ultra V2"),
            build_kite_variant("Ultra V3"),
            build_kite_variant("Ultra V4"),
            build_kite_variant("Union"),
            build_kite_variant("Union V3", ["Union III"]),
            build_kite_variant("Union V4"),
            build_kite_variant("Union V5"),
            build_kite_variant("Union V6"),
            build_kite_variant("Wave V9"),
        ]
    },
    {
        "slug": "cabrinha",
        "name": "Cabrinha",
        "variants": [],
        "kites": [
            build_kite_variant("Contra Aether"),
            build_kite_variant("Contra"),
            build_kite_variant("Contra 1S", ["contra 1 strut", "contra 1strut", "contra s1"]),
            build_kite_variant("Contra 3S", ["contra 3 strut", "contra 3strut", "contra s3"]),
            build_kite_variant("Drifter"),
            build_kite_variant("Drifter Icon", ["drifter icon series"]),
            build_kite_variant("FX"),
            build_kite_variant("FX2", ["fx 2", "fx c3"]),
            build_kite_variant("Moto"),
            build_kite_variant("Moto X"),
            build_kite_variant("Nitro"),
            build_kite_variant("Nitro Apex"),
            build_kite_variant("Switchblade"),
        ]
    },
    {
        "slug": "core",
        "name": "Core",
        "variants": [],
        "kites": [
            build_kite_variant("GTS5", ["GTS 5"]),
            build_kite_variant("GTS6", ["gts 6"]),
            build_kite_variant("Impact 2"),
            build_kite_variant("Nexus 2"),
            build_kite_variant("Nexus 3"),
            build_kite_variant("Section 2"),
            build_kite_variant("Section 3"),
            build_kite_variant("Section 4"),
            build_kite_variant("XR5", ["xr 5"], "xr"),
            build_kite_variant("XR6", ["xr 6"], "xr"),
            build_kite_variant("XR7", ["xr 7"], "xr"),
            build_kite_variant("XR8", ["xr 8"], "xr"),
            build_kite_variant("XR Pro", ["xrpro"], "xr_pro"),
            build_kite_variant("XLite"),
            build_kite_variant("XLite 2", ["xlite2"]),
        ]
    },
    {
        "slug": "crazy_fly",
        "name": "Crazy Fly",
        "variants": ["CrazyFly"],
        "kites": [
            build_kite_variant("Sculp"),
            build_kite_variant("Hyper"),
        ]
    },
    {
        "slug": "duotone",
        "name": "Duotone",
        "variants": [],
        "kites": [
            build_kite_variant("Capa"),
            build_kite_variant("Dice"),
            build_kite_variant("Dice SLS", ["dicesls"]),
            build_kite_variant("Evo"),
            build_kite_variant("Evo SLS", ["evosls"]),
            build_kite_variant("Evo D/Lab", [
                "evo dlab",
                "evodlab",
                "evo d_lab"], "2023"),  # note: for now
            build_kite_variant("Juice"),
            build_kite_variant("Juice SLS", ["juicesls"]),
            build_kite_variant("Juice D/Lab", [
                "juice dlab",
                "juice d lab",
                "juicedlab",
                "juice d-lab"]),
            build_kite_variant("Mono"),
            build_kite_variant("Neo"),
            build_kite_variant("Neo SLS", ["neosls",
                                           "neo_sls",
                                           "neo-sls"]),
            build_kite_variant("Neo D/Lab", [
                "neo dlab",
                "neo d lab",
                "neodlab",
                "neo d-lab"]),
            build_kite_variant("Rebel"),
            build_kite_variant("Rebel SLS", ["rebelsls"]),
            build_kite_variant("Vegas"),
        ]
    },
    {
        "slug": "eleveight",
        "name": "Eleveight",
        "variants": [],
        "kites": [
            build_kite_variant("FS"),
            build_kite_variant("FS V4", ["fsv4"], "fs"),
            build_kite_variant("FS V5", ["fsv5"], "fs"),
            build_kite_variant("FS V6", ["fsv6"], "fs"),
            build_kite_variant("OS", [], "os"),
            build_kite_variant("OS V2", ["osv2"], "os"),
            build_kite_variant("OS V3", ["osv3"], "os"),
            build_kite_variant("OS V4", ["osv4"], "os"),
            build_kite_variant("OS V5", ["osv5"], "os"),
            build_kite_variant("PS", [], "ps"),
            build_kite_variant("PS V5", ["psv5"], "ps"),
            build_kite_variant("PS V6", ["psv6"], "ps"),
            build_kite_variant("PS V7", ["psv7"], "ps"),
            build_kite_variant("RS", [], "rs"),
            build_kite_variant("RS V2", ["rsv2"], "rs"),
            build_kite_variant("RS V3", ["rsv3"], "rs"),
            build_kite_variant("RS V4", ["rsv4"], "rs"),
            build_kite_variant("RS V5", ["rsv5"], "rs"),
            build_kite_variant("RS V6", ["rsv6"], "rs"),
            build_kite_variant("RS V7", ["rsv7"], "rs"),
            build_kite_variant("WS", [], "ws"),
            build_kite_variant("WS V2", ["wsv2"], "ws"),
            build_kite_variant("WS V3", ["wsv3"], "ws"),
            build_kite_variant("WS V4", ["wsv4"], "ws"),
            build_kite_variant("WS V5", ["wsv5"], "ws"),
            build_kite_variant("WS V6", ["wsv6"], "ws"),
            build_kite_variant("WS V7", ["wsv7"], "ws"),
            build_kite_variant("XS", [], "xs"),
            build_kite_variant("XS V2", ["xsv2"], "xs"),
            build_kite_variant("XS V3", ["xsv3"], "xs"),
            build_kite_variant("XS V4", ["xsv4"], "xs"),
            build_kite_variant("XS V5", ["xsv5"], "xs"),
        ]
    },
    {
        "slug": "f_one",
        "name": "F-One",
        "variants": ["fone", "f one"],
        "kites": [
            build_kite_variant("Bandit", [], "bandit"),
            build_kite_variant("Bandit XV", [], "bandit"),
            build_kite_variant("Bandit XVI", [], "bandit"),
            build_kite_variant("Bandit S", [], 'bandit_s'),
            build_kite_variant("Bandit S2", [], 'bandit_s'),
            build_kite_variant("Bandit S3", [], 'bandit_s'),
            build_kite_variant("Bandit S4", [], 'bandit_s'),
            build_kite_variant("Breeze V4", ["breeze v.4"], 'breeze'),
            build_kite_variant("Bullit V2", [], 'bullit'),
            build_kite_variant("One V2", [], 'one'),
            build_kite_variant("Trigger", [], 'trigger'),
            build_kite_variant("Diablo V5", [], 'diablo'),
            build_kite_variant("WTF?! V2", [], 'wtf'),
        ]
    },
    {
        "slug": "flysurfer",
        "name": "Flysurfer",
        "variants": [],
        "kites": [
            build_kite_variant("Boost 3", [], "boost"),
            build_kite_variant("Boost 4", [], "boost"),
            build_kite_variant("Hybrid"),
            build_kite_variant("Peak 4", ["peak v4"], "peak"),
            build_kite_variant("Peak 5", ["peak v5"], "peak"),
            build_kite_variant("Stroke 2", ["stroke v2"], "stroke"),
            build_kite_variant("Sonic 3", ["sonic v3"], "sonic"),
            build_kite_variant("Sonic 4", ["sonic v4"], "sonic"),
            build_kite_variant("Sonic Race", [], "sonic_race"),
            build_kite_variant("Soul", [], "soul"),
            build_kite_variant("Soul 2", ["soul v2"], "soul"),
            build_kite_variant("Stoke", [], "stoke"),
            build_kite_variant("Stoke 2", ["stoke v2"], "stoke"),
            build_kite_variant("Stoke 3", ["stoke v3"], "stoke"),
            build_kite_variant("VMG 2", ["vmg v2"], "vmg"),
            build_kite_variant("Viron 3", ["viron v3"], "viron"),
        ]
    },
    {
        "slug": "ga",
        "name": "GA",
        "variants": [
            "Gaastra"
        ],
        "kites": [
            build_kite_variant("IQ"),
            build_kite_variant("One"),
            build_kite_variant("Pure"),
            build_kite_variant("Spark"),
        ]
    },
    {
        "slug": "liquid_force",
        "name": "Liquid Force",
        "variants": [],
        "kites": [
            build_kite_variant("NV"),
            build_kite_variant("WOW v3", ["wow 3"], "wow", "2018"),
            build_kite_variant("WOW v4", ["wow 4"], "wow"),
        ]
    },
    {
        "slug": "naish",
        "name": "Naish",
        "variants": [],
        "kites": [
            build_kite_variant("Boxer", [], "boxer"),
            build_kite_variant("Boxer S25", ["boxer s 25", "s25 boxer"], "boxer", "2021"),
            build_kite_variant("Boxer S26", ["boxer s 26", "s26 boxer"], "boxer", "2022"),
            build_kite_variant("Boxer S27", ["boxer s 27", "s27 boxer"], "boxer", "2023"),
            build_kite_variant("Dash", [], "dash"),
            build_kite_variant("Dash S25", ["dash s 25", "s25 dash"], "dash", "2021"),
            build_kite_variant("Dash S26", ["dash s 26", "s26 dash"], "dash", "2022"),
            build_kite_variant("Dash S27", ["dash s 27", "s27 dash"], "dash", "2023"),
            build_kite_variant("Dash LE", [], "dash_le"),
            build_kite_variant("Dash LE S27", ["dash le s 27"], "dash_le"),
            build_kite_variant("Pivot", [], "pivot"),
            build_kite_variant("Pivot S25", ["pivot s 25", "s25 pivot"], "pivot", "2021"),
            build_kite_variant("Pivot S26", ["pivot s 26", "s26 pivot"], "pivot", "2022"),
            build_kite_variant("Pivot S27", ["pivot s 27", "s27 pivot"], "pivot", "2023"),
            build_kite_variant("Pivot LE", [], "pivot_le"),
            build_kite_variant("Pivot LE S27", ["pivot le s 27", "s27 pivot le"], "pivot_le", "2023"),
            build_kite_variant("Phoenix", [], "phoenix"),
            build_kite_variant("Slash", [], "slash"),
            build_kite_variant("Triad", [], "triad"),
            build_kite_variant("Triad S25", ["triad s 25", "s25 triad"], "triad"),
            build_kite_variant("Triad S26", ["triad s 26", "s26 triad"], "triad"),
            build_kite_variant("Triad S27", ["triad s 27", "s27 triad"], "triad"),
            build_kite_variant("Torch", [], "torch"),
            build_kite_variant("Torch S25", ["s25 torch", "torch s 25"], "torch"),
            build_kite_variant("Torch S26", ["s26 torch", "torch s 26"], "torch"),
            build_kite_variant("Torch S27", ["s27 torch", "torch s 27"], "torch"),
        ]
    },
    {
        "slug": "north",
        "name": "North",
        "variants": [],
        "kites": [
            build_kite_variant("Carve"),
            build_kite_variant("Reach"),
            build_kite_variant("Code Zero"),
            build_kite_variant("Orbit"),
            build_kite_variant("Pulse"),
        ]
    },
    {
        "slug": "ocean_rodeo",
        "name": "Ocean Rodeo",
        "variants": [],
        "kites": [
            build_kite_variant("Crave HL", ["cravehl", "crave-hl"], "crave_hl"),
            build_kite_variant("Roam HL", ["roamhl", "roam-hl"], "roam_hl"),
            build_kite_variant("Flite HL", ["flitehl", "flite-hl"], "flite_hl"),
            build_kite_variant("Crave A", ["cravea", "crave-a", "crave a-series", "crave alula"], "crave_a"),
            build_kite_variant("Roam A", ["roama", "roam-a", "roam a-series", "roam alula"], "roam_a"),
            build_kite_variant("Flite A", ["flitea", "flite-a", "flite a-series", "flite alula"], "flite_a"),
        ]
    },
    {
        "slug": "ozone",
        "name": "Ozone",
        "variants": []  # todo kites
    },
    {
        "slug": "plkb",
        "name": "PLKB",
        "variants": [
            "Peter Lynn",
            "Peter Lynn Kiteboarding"
        ],
        "kites": [
            build_kite_variant("Escape V8", [], "escape"),
            build_kite_variant("Gambit V2", [], "gambit"),
            build_kite_variant("Hook V2", [], "hook"),
            build_kite_variant("Swell V4", [], "swell"),
        ]
    },
    {
        "slug": "rrd",
        "name": "RRD",
        "variants": [
            "Roberto Ricci"
        ],
        "kites": [
            build_kite_variant("Emotion Y26", ["emotion 26"], "emotion"),
            build_kite_variant("Obsession Y26", ["obsession 26"], "obsession"),
            build_kite_variant("Obsession Y27", ["obsession 27"], "obsession"),
            build_kite_variant("Obsession Big Air Y28",
                               ["obsession y28", "obsession big air y28", "big air obsession y28"],
                               "obsession_big_air"),
            build_kite_variant("Religion Y27", [], "religion"),
            build_kite_variant("Vision Y27", [], "vision"),
        ]
    },
    {
        "slug": "reedin",
        "name": "Reedin",
        "variants": []
    },
    {
        "slug": "slingshot",
        "name": "Slingshot",
        "variants": []
    },
]
